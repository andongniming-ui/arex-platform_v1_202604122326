import asyncio
import json
import uuid
from datetime import datetime

import httpx
from sqlalchemy import select

from database import async_session_factory
from models.application import Application
from models.compare import CompareResult, CompareRun
from models.recording import Recording
from models.test_case import TestCaseRecording
from utils.diff import compute_diff


async def run_compare(run_id: str, req):
    try:
        async with async_session_factory() as db:
            run = await db.get(CompareRun, run_id)
            if not run:
                return
            app_a = await db.get(Application, run.app_a_id)
            app_b = await db.get(Application, run.app_b_id)
            if not app_a or not app_b:
                run.status = "FAILED"
                run.finished_at = datetime.utcnow()
                await db.commit()
                return

            result = await db.execute(
                select(TestCaseRecording)
                .where(TestCaseRecording.case_id == run.case_id)
                .order_by(TestCaseRecording.sort_order)
            )
            links = result.scalars().all()
            recording_ids = [link.recording_id for link in links]

            ignore_fields = run.ignore_fields or []
            diff_rules = run.diff_rules or []
            run.total_count = len(recording_ids)
            await db.commit()

        ignore_patterns = [rf".*\['{field}'\].*" for field in ignore_fields]
        sem = asyncio.Semaphore(req.concurrency or 1)

        async def replay_both(recording_id: str):
            async with sem:
                if req.delay_ms:
                    await asyncio.sleep(req.delay_ms / 1000)

                async with async_session_factory() as db:
                    recording = await db.get(Recording, recording_id)
                if not recording:
                    return None

                req_info: dict = {}
                if recording.request_body:
                    try:
                        req_info = json.loads(recording.request_body)
                    except Exception:
                        pass

                method = (req_info.get("method") or "GET").upper()
                send_body = req_info.get("body") if method not in ("GET", "DELETE", "HEAD") else None
                headers: dict = {}
                content_type = req_info.get("contentType")
                if content_type and send_body:
                    headers["Content-Type"] = content_type

                from urllib.parse import urlparse

                uri = req_info.get("uri") or ""
                if uri.startswith("http"):
                    parsed = urlparse(uri)
                    replay_path = parsed.path + ("?" + parsed.query if parsed.query else "")
                elif uri and uri.upper() not in {"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"}:
                    replay_path = uri
                else:
                    replay_path = recording.path or "/"

                async def http_replay(app: Application):
                    host = f"http://{app.ssh_host}:{app.repeater_port}"
                    url = host + replay_path
                    try:
                        async with httpx.AsyncClient(timeout=30.0) as client:
                            resp = await client.request(method, url, content=send_body, headers=headers)
                        return {"body": resp.text, "status_code": resp.status_code, "error": None}
                    except httpx.RequestError as exc:
                        return {"body": None, "status_code": None, "error": str(exc)}

                start_a = datetime.utcnow()
                resp_a_data = await http_replay(app_a)
                dur_a = int((datetime.utcnow() - start_a).total_seconds() * 1000)

                start_b = datetime.utcnow()
                resp_b_data = await http_replay(app_b)
                dur_b = int((datetime.utcnow() - start_b).total_seconds() * 1000)

                body_a = resp_a_data.get("body")
                body_b = resp_b_data.get("body")

                _, score_a = compute_diff(recording.response_body, body_a, ignore_patterns, diff_rules)
                _, score_b = compute_diff(recording.response_body, body_b, ignore_patterns, diff_rules)
                diff_ab, score_ab = compute_diff(body_a, body_b, ignore_patterns, diff_rules)

                status_a = "PASS" if score_a == 0.0 else "FAIL"
                status_b = "PASS" if score_b == 0.0 else "FAIL"

                async with async_session_factory() as db:
                    db.add(
                        CompareResult(
                            id=str(uuid.uuid4()),
                            run_id=run_id,
                            recording_id=recording_id,
                            path=recording.path,
                            entry_type=recording.entry_type,
                            status_a=status_a,
                            resp_a=body_a,
                            diff_score_a=score_a,
                            duration_a_ms=dur_a,
                            status_b=status_b,
                            resp_b=body_b,
                            diff_score_b=score_b,
                            duration_b_ms=dur_b,
                            diff_a_vs_b=diff_ab,
                            diff_score_a_vs_b=score_ab,
                        )
                    )
                    await db.commit()

                return status_a == status_b

        results = await asyncio.gather(
            *[replay_both(recording_id) for recording_id in recording_ids],
            return_exceptions=True,
        )

        agreed = sum(1 for result in results if result is True)
        diverged = sum(1 for result in results if result is False)

        async with async_session_factory() as db:
            run = await db.get(CompareRun, run_id)
            if run:
                run.agreed_count = agreed
                run.diverged_count = diverged
                run.status = "DONE"
                run.finished_at = datetime.utcnow()
                await db.commit()

    except Exception as exc:
        print(f"[compare] _run_compare failed for run {run_id}: {exc}")
        try:
            async with async_session_factory() as db:
                run = await db.get(CompareRun, run_id)
                if run and run.status == "RUNNING":
                    run.status = "FAILED"
                    run.finished_at = datetime.utcnow()
                    await db.commit()
        except Exception:
            pass
