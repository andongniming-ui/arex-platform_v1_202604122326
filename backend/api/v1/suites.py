"""
Replay Suite management — group multiple test cases and run them in one shot.
"""
import asyncio
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models.suite import ReplaySuite, SuiteRun
from models.test_case import TestCase
from models.application import Application
from schemas.suite import SuiteCreate, SuiteUpdate, SuiteOut, SuiteRunRequest, SuiteRunOut
from services.suite_service import run_suite as _run_suite

router = APIRouter(prefix="/suites", tags=["suites"])

_background_tasks: set = set()

def _fire(coro):
    task = asyncio.create_task(coro)
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)


# ── CRUD ──────────────────────────────────────────────────────────────────────

@router.post("", response_model=SuiteOut, status_code=201)
async def create_suite(body: SuiteCreate, db: AsyncSession = Depends(get_db)):
    suite = ReplaySuite(id=str(uuid.uuid4()), **body.model_dump())
    db.add(suite)
    await db.commit()
    await db.refresh(suite)
    return suite


@router.get("", response_model=list[SuiteOut])
async def list_suites(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ReplaySuite).order_by(ReplaySuite.created_at.desc()))
    return result.scalars().all()


@router.get("/{suite_id}", response_model=SuiteOut)
async def get_suite(suite_id: str, db: AsyncSession = Depends(get_db)):
    suite = await db.get(ReplaySuite, suite_id)
    if not suite:
        raise HTTPException(404, "Suite not found")
    return suite


@router.put("/{suite_id}", response_model=SuiteOut)
async def update_suite(suite_id: str, body: SuiteUpdate, db: AsyncSession = Depends(get_db)):
    suite = await db.get(ReplaySuite, suite_id)
    if not suite:
        raise HTTPException(404, "Suite not found")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(suite, field, value)
    suite.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(suite)
    return suite


@router.delete("/{suite_id}", status_code=204)
async def delete_suite(suite_id: str, db: AsyncSession = Depends(get_db)):
    suite = await db.get(ReplaySuite, suite_id)
    if not suite:
        raise HTTPException(404, "Suite not found")
    await db.delete(suite)
    await db.commit()


# ── Suite Runs ────────────────────────────────────────────────────────────────

@router.post("/{suite_id}/runs", response_model=SuiteRunOut, status_code=201)
async def run_suite(
    suite_id: str,
    body: SuiteRunRequest,
    db: AsyncSession = Depends(get_db),
):
    suite = await db.get(ReplaySuite, suite_id)
    if not suite:
        raise HTTPException(404, "Suite not found")

    # Resolve effective target app: per-run override > suite default
    target_app_id = body.target_app_id or suite.default_target_app_id
    # Build effective case_app_map: suite-level map merged with run-level overrides
    effective_case_app_map: dict[str, str] = {}
    if suite.case_app_map:
        effective_case_app_map.update(suite.case_app_map)
    if body.case_app_map:
        effective_case_app_map.update(body.case_app_map)

    # Ensure every case has a resolvable target app
    if not target_app_id and suite.case_ids:
        missing = [cid for cid in suite.case_ids if cid not in effective_case_app_map]
        if missing:
            raise HTTPException(
                400,
                f"No target_app_id for case(s): {missing}. "
                "Provide target_app_id or case_app_map covering all cases."
            )

    # Validate global target app if provided
    if target_app_id:
        app = await db.get(Application, target_app_id)
        if not app:
            raise HTTPException(404, "Target application not found")

    if not suite.case_ids:
        raise HTTPException(400, "Suite has no test cases")

    # Validate all cases exist
    for case_id in suite.case_ids:
        tc = await db.get(TestCase, case_id)
        if not tc:
            raise HTTPException(400, f"Test case {case_id} not found")

    run = SuiteRun(
        id=str(uuid.uuid4()),
        suite_id=suite_id,
        target_app_id=target_app_id,
        status="RUNNING",
        total_cases=len(suite.case_ids),
        started_at=datetime.utcnow(),
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)

    _fire(_run_suite(run.id, suite_id, body, effective_case_app_map))
    return run


@router.get("/{suite_id}/runs", response_model=list[SuiteRunOut])
async def list_suite_runs(suite_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(SuiteRun)
        .where(SuiteRun.suite_id == suite_id)
        .order_by(SuiteRun.created_at.desc())
        .limit(20)
    )
    return result.scalars().all()


@router.get("/{suite_id}/runs/{run_id}", response_model=SuiteRunOut)
async def get_suite_run(suite_id: str, run_id: str, db: AsyncSession = Depends(get_db)):
    run = await db.get(SuiteRun, run_id)
    if not run or run.suite_id != suite_id:
        raise HTTPException(404, "Suite run not found")
    return run
