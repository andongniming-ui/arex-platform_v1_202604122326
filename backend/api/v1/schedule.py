"""
Scheduled replay management — create/list/update/delete cron-based replay jobs.
Uses APScheduler (AsyncIOScheduler) to fire replays at configured times.
"""
import uuid
from datetime import datetime
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from database import get_db, async_session_factory
from models.schedule import ScheduledReplay
from models.test_case import TestCase
from models.application import Application
from models.replay import ReplayJob
from schemas.schedule import ScheduleCreate, ScheduleUpdate, ScheduleOut
from core.scheduler import scheduler
from services.replay_service import run_replay_job

router = APIRouter(prefix="/schedules", tags=["schedules"])


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_trigger(cron_expr: str):
    from apscheduler.triggers.cron import CronTrigger
    parts = cron_expr.strip().split()
    if len(parts) != 5:
        raise ValueError(f"Invalid cron expression '{cron_expr}': must have 5 fields (min hour day month weekday)")
    minute, hour, day, month, weekday = parts
    return CronTrigger(
        minute=minute, hour=hour,
        day=day, month=month, day_of_week=weekday,
        timezone="Asia/Shanghai",
    )


def _register_job(s: ScheduledReplay):
    """Add or replace an APScheduler job for this schedule."""
    if not s.enabled:
        return
    try:
        trigger = _make_trigger(s.cron_expr)
        scheduler.add_job(
            _run_scheduled_replay,
            trigger=trigger,
            id=f"sched_{s.id}",
            args=[s.id],
            replace_existing=True,
            misfire_grace_time=300,
        )
    except Exception as e:
        print(f"[scheduler] Failed to register job for schedule {s.id}: {e}")


def _unregister_job(schedule_id: str):
    try:
        scheduler.remove_job(f"sched_{schedule_id}")
    except Exception:
        pass  # job didn't exist


async def _run_scheduled_replay(schedule_id: str):
    """Coroutine called by APScheduler when cron fires."""
    async with async_session_factory() as db:
        s = await db.get(ScheduledReplay, schedule_id)
        if not s or not s.enabled:
            return
        tc = await db.get(TestCase, s.case_id)
        if not tc or tc.status == "DELETED":
            print(f"[scheduler] Test case {s.case_id} not found or deleted, disabling schedule {s.id}")
            s.enabled = False
            await db.commit()
            _unregister_job(schedule_id)
            return
        if not tc.recording_count:
            print(f"[scheduler] Test case {s.case_id} has no recordings, skipping schedule {s.id}")
            return

        job_id = str(uuid.uuid4())
        job = ReplayJob(
            id=job_id,
            case_id=s.case_id,
            target_app_id=s.target_app_id,
            total_count=tc.recording_count,
            concurrency=s.concurrency,
            delay_ms=s.delay_ms,
            ignore_fields=s.ignore_fields,
            diff_rules=s.diff_rules,
            assertions=s.assertions,
            perf_threshold_ms=s.perf_threshold_ms,
            override_host=s.override_host,
            webhook_url=s.webhook_url,
            notify_type=s.notify_type,
            environment=s.environment or "scheduled",
            created_by=f"schedule:{s.id}",
        )
        db.add(job)
        s.last_run_at = datetime.utcnow()
        s.last_job_id = job_id
        await db.commit()

    print(f"[scheduler] Running schedule '{s.name}' → job {job_id}")
    await run_replay_job(job_id)


# ── Load schedules on startup ─────────────────────────────────────────────────

async def load_all_schedules():
    """Called from main.py lifespan to restore APScheduler jobs from DB."""
    async with async_session_factory() as db:
        result = await db.execute(
            select(ScheduledReplay).where(ScheduledReplay.enabled == True)
        )
        schedules = result.scalars().all()
    for s in schedules:
        _register_job(s)
    if schedules:
        print(f"[scheduler] Loaded {len(schedules)} scheduled replay(s)")


# ── CRUD ──────────────────────────────────────────────────────────────────────

@router.post("", response_model=ScheduleOut, status_code=201)
async def create_schedule(body: ScheduleCreate, db: AsyncSession = Depends(get_db)):
    # Validate cron expression
    try:
        _make_trigger(body.cron_expr)
    except ValueError as e:
        raise HTTPException(400, str(e))

    tc = await db.get(TestCase, body.case_id)
    if not tc:
        raise HTTPException(404, "Test case not found")
    app = await db.get(Application, body.target_app_id)
    if not app:
        raise HTTPException(404, "Target application not found")

    s = ScheduledReplay(id=str(uuid.uuid4()), **body.model_dump())
    db.add(s)
    await db.commit()
    await db.refresh(s)
    _register_job(s)
    return s


@router.get("", response_model=list[ScheduleOut])
async def list_schedules(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ScheduledReplay).order_by(ScheduledReplay.created_at.desc())
    )
    return result.scalars().all()


@router.get("/{schedule_id}", response_model=ScheduleOut)
async def get_schedule(schedule_id: str, db: AsyncSession = Depends(get_db)):
    s = await db.get(ScheduledReplay, schedule_id)
    if not s:
        raise HTTPException(404, "Schedule not found")
    return s


@router.put("/{schedule_id}", response_model=ScheduleOut)
async def update_schedule(
    schedule_id: str, body: ScheduleUpdate, db: AsyncSession = Depends(get_db)
):
    s = await db.get(ScheduledReplay, schedule_id)
    if not s:
        raise HTTPException(404, "Schedule not found")

    if body.cron_expr is not None:
        try:
            _make_trigger(body.cron_expr)
        except ValueError as e:
            raise HTTPException(400, str(e))

    for field, value in body.model_dump(exclude_none=True).items():
        setattr(s, field, value)
    s.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(s)

    # Re-register or remove from scheduler depending on enabled state
    _unregister_job(schedule_id)
    if s.enabled:
        _register_job(s)
    return s


@router.post("/{schedule_id}/run-now", response_model=dict)
async def run_now(
    schedule_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Manually trigger a scheduled replay immediately."""
    s = await db.get(ScheduledReplay, schedule_id)
    if not s:
        raise HTTPException(404, "Schedule not found")
    background_tasks.add_task(_run_scheduled_replay, schedule_id)
    return {"triggered": True, "schedule_id": schedule_id}


@router.delete("/batch", status_code=204)
async def batch_delete_schedules(body: dict, db: AsyncSession = Depends(get_db)):
    """Delete multiple schedules by ID. Body: {"ids": [...]}"""
    ids = body.get("ids") or []
    if not ids:
        return
    for schedule_id in ids:
        _unregister_job(schedule_id)
    await db.execute(delete(ScheduledReplay).where(ScheduledReplay.id.in_(ids)))
    await db.commit()


@router.delete("/{schedule_id}", status_code=204)
async def delete_schedule(schedule_id: str, db: AsyncSession = Depends(get_db)):
    s = await db.get(ScheduledReplay, schedule_id)
    if not s:
        raise HTTPException(404, "Schedule not found")
    _unregister_job(schedule_id)
    await db.delete(s)
    await db.commit()
