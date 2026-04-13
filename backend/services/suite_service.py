import asyncio
import uuid
from datetime import datetime

from sqlalchemy import select

from database import async_session_factory
from models.replay import ReplayJob
from models.suite import ReplaySuite, SuiteRun
from models.test_case import TestCase, TestCaseRecording
from services.replay_service import run_replay_job


async def run_suite(run_id: str, suite_id: str, req, case_app_map: dict[str, str] | None = None):
    job_ids: list[str] = []
    try:
        async with async_session_factory() as db:
            run = await db.get(SuiteRun, run_id)
            suite = await db.get(ReplaySuite, suite_id)
            if not run or not suite:
                return

            concurrency = req.concurrency or suite.default_concurrency or 1
            ignore_fields = req.ignore_fields or suite.default_ignore_fields or []
            diff_rules = req.diff_rules or suite.default_diff_rules or []
            assertions = req.assertions or suite.default_assertions or []
            perf_threshold_ms = req.perf_threshold_ms or suite.default_perf_threshold_ms
            environment = req.environment or suite.default_environment
            override_host = req.override_host or suite.default_override_host
            delay_ms = suite.default_delay_ms or 0

            for case_id in list(suite.case_ids):
                tc = await db.get(TestCase, case_id)
                if not tc:
                    continue
                has_recs = await db.execute(
                    select(TestCaseRecording).where(TestCaseRecording.case_id == case_id).limit(1)
                )
                if not has_recs.scalars().first():
                    continue

                effective_app_id = (
                    (case_app_map or {}).get(case_id)
                    or req.target_app_id
                    or suite.default_target_app_id
                )
                if not effective_app_id:
                    print(f"[suite] No target app for case {case_id}, skipping")
                    continue

                job_id = str(uuid.uuid4())
                db.add(
                    ReplayJob(
                        id=job_id,
                        case_id=case_id,
                        target_app_id=effective_app_id,
                        total_count=tc.recording_count,
                        concurrency=concurrency,
                        delay_ms=delay_ms,
                        ignore_fields=ignore_fields,
                        diff_rules=diff_rules,
                        assertions=assertions,
                        perf_threshold_ms=perf_threshold_ms,
                        override_host=override_host,
                        environment=environment or "suite",
                        created_by=f"suite_run:{run_id}",
                    )
                )
                job_ids.append(job_id)

            run.job_ids = job_ids
            run.total_cases = len(job_ids)
            await db.commit()

        await asyncio.gather(*[run_replay_job(job_id) for job_id in job_ids], return_exceptions=True)

        async with async_session_factory() as db:
            run = await db.get(SuiteRun, run_id)
            if not run:
                return

            total_requests = 0
            passed_requests = 0
            passed_cases = 0
            failed_cases = 0

            for job_id in job_ids:
                job = await db.get(ReplayJob, job_id)
                if not job:
                    continue
                sent = job.sent_count or 0
                success = job.success_count or 0
                total_requests += sent
                passed_requests += success
                if sent > 0 and success == sent:
                    passed_cases += 1
                else:
                    failed_cases += 1

            run.total_requests = total_requests
            run.passed_requests = passed_requests
            run.passed_cases = passed_cases
            run.failed_cases = failed_cases
            run.overall_pass_rate = passed_requests / total_requests if total_requests else 0.0
            run.status = "DONE"
            run.finished_at = datetime.utcnow()
            await db.commit()
    except Exception as exc:
        print(f"[suite] _run_suite failed for run {run_id}: {exc}")
        try:
            async with async_session_factory() as db:
                run = await db.get(SuiteRun, run_id)
                if run and run.status == "RUNNING":
                    run.status = "FAILED"
                    run.finished_at = datetime.utcnow()
                    await db.commit()
        except Exception:
            pass
