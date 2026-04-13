"""
CI Integration API — blocking replay endpoint for Jenkins/GitLab pipeline use.

Usage:
  curl -s -X POST http://localhost:8000/api/v1/ci/replay \
    -H 'Content-Type: application/json' \
    -d '{"case_id":"...", "target_app_id":"...", "pass_threshold":1.0, "timeout_seconds":300}'

Returns HTTP 200 with {"passed": true/false, ...} when done.
Returns HTTP 504 if timeout exceeded.
"""
import asyncio
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from database import get_db, async_session_factory
from models.replay import ReplayJob
from models.test_case import TestCase
from models.application import Application
from services.replay_service import cancel_replay_job, run_replay_job as _run_replay_job

router = APIRouter(prefix="/ci", tags=["ci"])


class CIReplayRequest(BaseModel):
    case_id: str
    target_app_id: str
    ignore_fields: list[str] | None = None
    diff_rules: list[dict] | None = None   # Smart Diff Rules
    assertions: list[dict] | None = None   # Assertion Rules
    pass_threshold: float = Field(default=1.0, ge=0.0, le=1.0,
                                  description="Minimum pass rate to consider the run successful (0.0–1.0)")
    timeout_seconds: int = Field(default=300, ge=10, le=1800,
                                 description="Max seconds to wait before returning timeout")
    concurrency: int = Field(default=1, ge=1, le=20)
    delay_ms: int = Field(default=0, ge=0)
    override_host: str | None = None
    environment: str | None = None


class CIReplayResponse(BaseModel):
    passed: bool
    timed_out: bool = False
    job_id: str
    status: str
    total_count: int
    success_count: int
    fail_count: int
    error_count: int
    pass_rate: float
    pass_threshold: float
    duration_seconds: float
    report_url: str | None = None   # relative URL to HTML report


@router.post("/replay", response_model=CIReplayResponse)
async def ci_replay(body: CIReplayRequest, db: AsyncSession = Depends(get_db)):
    """
    Create a replay job and block until it finishes (or timeout).
    Designed for CI pipeline integration — returns a single response with pass/fail verdict.
    """
    tc = await db.get(TestCase, body.case_id)
    if not tc:
        raise HTTPException(404, "Test case not found")
    if tc.recording_count == 0:
        raise HTTPException(400, "Test case has no recordings")
    target_app = await db.get(Application, body.target_app_id)
    if not target_app:
        raise HTTPException(404, "Target application not found")

    job_id = str(uuid.uuid4())
    job = ReplayJob(
        id=job_id,
        case_id=body.case_id,
        target_app_id=body.target_app_id,
        total_count=tc.recording_count,
        concurrency=body.concurrency,
        delay_ms=body.delay_ms,
        override_host=body.override_host,
        ignore_fields=body.ignore_fields,
        diff_rules=body.diff_rules,
        assertions=body.assertions,
        environment=body.environment or "ci",
        created_by="ci",
    )
    db.add(job)
    await db.commit()

    # Launch replay in background task
    task = asyncio.create_task(_run_replay_job(job_id))

    loop = asyncio.get_running_loop()
    start = loop.time()
    deadline = start + body.timeout_seconds
    timed_out = False

    # Poll until done or timeout
    while True:
        await asyncio.sleep(2)
        async with async_session_factory() as poll_db:
            j = await poll_db.get(ReplayJob, job_id)
            if j and j.status in ("DONE", "FAILED", "CANCELLED"):
                break
        if loop.time() >= deadline:
            timed_out = True
            task.cancel()
            await cancel_replay_job(job_id, status="CANCELLED")
            break

    duration = loop.time() - start

    async with async_session_factory() as final_db:
        final_job = await final_db.get(ReplayJob, job_id)

    if not final_job:
        raise HTTPException(500, "Replay job lost after execution")

    sent = final_job.sent_count or 0
    success = final_job.success_count or 0
    fail = final_job.fail_count or 0
    error = max(sent - success - fail, 0)
    pass_rate = success / sent if sent else 0.0
    passed = (not timed_out) and (pass_rate >= body.pass_threshold)

    if timed_out:
        raise HTTPException(
            504,
            detail={
                "message": f"Replay timed out after {body.timeout_seconds}s",
                "job_id": job_id,
                "pass_rate": pass_rate,
            },
        )

    return CIReplayResponse(
        passed=passed,
        timed_out=False,
        job_id=job_id,
        status=final_job.status,
        total_count=final_job.total_count,
        success_count=success,
        fail_count=fail,
        error_count=error,
        pass_rate=pass_rate,
        pass_threshold=body.pass_threshold,
        duration_seconds=round(duration, 1),
        report_url=f"/api/v1/replays/{job_id}/report",
    )
