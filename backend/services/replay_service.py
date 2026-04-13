import asyncio
import json
import re
import uuid
from datetime import datetime

import httpx
from sqlalchemy import select

from config import settings
from database import async_session_factory
from integration.arex_client import ArexClient, ArexClientError
from models.application import Application
from models.recording import Recording
from models.replay import ReplayJob, ReplayResult
from models.test_case import TestCaseRecording
from utils.assertions import assertions_all_passed, evaluate_assertions
from utils.diff import compute_diff
from utils.failure_analyzer import analyze_failure


def extract_service_id(text: str | None) -> str | None:
    """从 XML 文本中提取 <service_id> 标签内容。"""
    if not text:
        return None
    match = re.search(r"<service_id>(.*?)</service_id>", text)
    return match.group(1).strip() if match else None


def match_xml_template(
    xml_tpl: str,
    response_body: str | None,
    request_body: str | None = None,
) -> str | None:
    """
    Match an XML request template based on service_id.

    xml_tpl can be:
      - A JSON map: {"OPEN_ACCOUNT": "<request>...</request>", "QUERY_BALANCE": "..."}
      - A plain XML string (only returned when its service_id matches the recording)
    """
    service_id = extract_service_id(request_body) or extract_service_id(response_body)

    try:
        tpl_map = json.loads(xml_tpl)
        if isinstance(tpl_map, dict) and tpl_map:
            if service_id and service_id in tpl_map:
                return tpl_map[service_id]
            if "*" in tpl_map:
                return tpl_map["*"]
            if "default" in tpl_map:
                return tpl_map["default"]
            if len(tpl_map) == 1:
                return next(iter(tpl_map.values()))
            return None
    except (json.JSONDecodeError, TypeError):
        pass

    tpl_service_id = extract_service_id(xml_tpl)
    if tpl_service_id and service_id and tpl_service_id != service_id:
        return None
    return xml_tpl.strip()


def apply_header_transforms(headers: dict, transforms: list[dict]) -> dict:
    """应用请求头转换规则。"""
    if not transforms:
        return headers

    result = dict(headers)
    for transform in transforms:
        t_type = transform.get("type", "")
        key = transform.get("key", "")
        if not key:
            continue
        if t_type == "replace":
            result[key] = transform.get("value", "")
        elif t_type == "remove":
            result.pop(key, None)
        elif t_type == "add" and key not in result:
            result[key] = transform.get("value", "")
    return result


async def cancel_replay_job(job_id: str, status: str = "CANCELLED") -> None:
    async with async_session_factory() as db:
        job = await db.get(ReplayJob, job_id)
        if not job:
            return
        if job.status in ("DONE", "FAILED", "CANCELLED"):
            return
        job.status = status
        job.finished_at = datetime.utcnow()
        await db.commit()


async def run_replay_job(job_id: str):
    child_tasks: list[asyncio.Task] = []

    async with async_session_factory() as db:
        job = await db.get(ReplayJob, job_id)
        if not job or job.status == "CANCELLED":
            return

        job.status = "RUNNING"
        job.started_at = datetime.utcnow()
        await db.commit()

        target_app = await db.get(Application, job.target_app_id)
        if not target_app:
            job.status = "FAILED"
            job.finished_at = datetime.utcnow()
            await db.commit()
            return

        result = await db.execute(
            select(TestCaseRecording)
            .where(TestCaseRecording.case_id == job.case_id)
            .order_by(TestCaseRecording.sort_order)
        )
        links = result.scalars().all()

        job_id_snap = job.id
        job_delay = job.delay_ms
        job_ignore = job.ignore_fields or []
        job_diff_rules = job.diff_rules or []
        job_assertions = job.assertions or []
        job_override_host = job.override_host
        job_perf_threshold = job.perf_threshold_ms
        job_use_mocks = job.use_sub_invocation_mocks
        job_concurrency = job.concurrency or 1
        job_smart_noise = job.smart_noise_reduction
        job_header_transforms = job.header_transforms or []
        job_retry_count = job.retry_count or 0
        job_repeat_count = job.repeat_count or 1
        recording_ids = [link.recording_id for link in links]

    expanded_recording_ids: list[str] = []
    for recording_id in recording_ids:
        expanded_recording_ids.extend([recording_id] * job_repeat_count)

    sem = asyncio.Semaphore(job_concurrency)
    child_tasks = [
        asyncio.create_task(
            replay_one(
                job_id_snap,
                recording_id,
                target_app,
                sem,
                job_delay,
                job_ignore,
                job_override_host,
                job_diff_rules,
                job_assertions,
                job_perf_threshold,
                job_use_mocks,
                job_smart_noise,
                job_header_transforms,
                job_retry_count,
            )
        )
        for recording_id in expanded_recording_ids
    ]

    try:
        results = await asyncio.gather(*child_tasks, return_exceptions=True)
    except asyncio.CancelledError:
        for task in child_tasks:
            task.cancel()
        if child_tasks:
            await asyncio.gather(*child_tasks, return_exceptions=True)
        await cancel_replay_job(job_id, status="CANCELLED")
        raise

    async with async_session_factory() as db:
        job = await db.get(ReplayJob, job_id)
        if not job or job.status == "CANCELLED":
            return

        success = sum(
            1 for result in results
            if (isinstance(result, tuple) and result[0] == "PASS") or result == "PASS"
        )
        fail = sum(
            1 for result in results
            if (isinstance(result, tuple) and result[0] == "FAIL") or result == "FAIL"
        )
        sent_n = len(expanded_recording_ids)

        job.sent_count = sent_n
        job.success_count = success
        job.fail_count = fail
        job.status = "DONE"
        job.finished_at = datetime.utcnow()
        await db.commit()

        if job.webhook_url:
            pass_rate = round(success / sent_n, 4) if sent_n else 0.0
            error_count = max(sent_n - success - fail, 0)
            generic_payload = {
                "job_id": job_id,
                "status": "DONE",
                "total_count": job.total_count,
                "sent_count": sent_n,
                "success_count": success,
                "fail_count": fail,
                "error_count": error_count,
                "pass_rate": pass_rate,
                "finished_at": job.finished_at.isoformat(),
            }
            notify_type = job.notify_type or "generic"
            emoji = "✅" if pass_rate >= 0.9 else "❌"
            pct = f"{pass_rate * 100:.1f}%"
            if notify_type == "dingtalk":
                text = (
                    f"## {emoji} 回放任务完成\n\n"
                    f"- **通过率**: {pct}\n"
                    f"- **通过**: {success} &nbsp; **失败**: {fail} &nbsp; **错误**: {error_count}\n"
                    f"- **总计**: {sent_n} 条 &nbsp; 任务ID: `{job_id[:8]}`"
                )
                payload = {
                    "msgtype": "markdown",
                    "markdown": {"title": f"回放完成 — 通过率 {pct}", "text": text},
                }
            elif notify_type == "wecom":
                text = (
                    f"## 回放任务完成 {emoji}\n"
                    f"> 通过率：**{pct}**\n"
                    f"> 通过：{success} | 失败：{fail} | 错误：{error_count}\n"
                    f"> 总计：{sent_n} 条 | 任务ID：`{job_id[:8]}`"
                )
                payload = {
                    "msgtype": "markdown",
                    "markdown": {"content": text},
                }
            else:
                payload = generic_payload
            try:
                async with httpx.AsyncClient(timeout=10) as client:
                    await client.post(job.webhook_url, json=payload)
            except Exception as exc:
                print(f"[replay] webhook POST failed: {exc}")


async def replay_one(
    job_id: str,
    recording_id: str,
    target_app: Application,
    sem: asyncio.Semaphore,
    delay_ms: int,
    ignore_fields: list,
    override_host: str | None,
    diff_rules: list | None = None,
    assertions: list | None = None,
    perf_threshold_ms: int | None = None,
    use_sub_invocation_mocks: bool = False,
    smart_noise_reduction: bool = False,
    header_transforms: list | None = None,
    retry_count: int = 0,
) -> tuple[str, str, str]:
    async with sem:
        if delay_ms:
            await asyncio.sleep(delay_ms / 1000)

        start = datetime.utcnow()
        status = "ERROR"
        replayed_body = None
        error_msg = None
        diff_json = None
        diff_score = None
        original_response = None
        replayed_status_code = None
        assertion_results = None

        try:
            async with async_session_factory() as db:
                recording = await db.get(Recording, recording_id)
            if not recording:
                error_msg = "Recording not found in DB"
                raise ValueError(error_msg)

            original_response = recording.response_body

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
            if content_type:
                headers["Content-Type"] = content_type

            if not send_body and method in ("POST", "PUT", "PATCH"):
                xml_tpl = getattr(target_app, "xml_request_template", None)
                if xml_tpl and xml_tpl.strip():
                    matched_body = match_xml_template(xml_tpl, recording.response_body, send_body)
                    if matched_body:
                        send_body = matched_body
                        if "Content-Type" not in headers:
                            headers["Content-Type"] = "application/xml"

            if header_transforms:
                headers = apply_header_transforms(headers, header_transforms)

            from urllib.parse import urlparse

            uri = req_info.get("uri") or ""
            if uri.startswith("http"):
                parsed = urlparse(uri)
                replay_path = parsed.path + ("?" + parsed.query if parsed.query else "")
            elif uri and uri.upper() not in {"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"}:
                replay_path = uri
            else:
                replay_path = recording.path or "/"

            final_status = None
            last_error = None
            arex = ArexClient(settings.arex_storage_url)

            if use_sub_invocation_mocks and recording.trace_id and recording.sub_invocations:
                try:
                    await arex.cache_load_mock(recording.trace_id)
                except ArexClientError as exc:
                    print(f"[replay] cache_load_mock failed (non-fatal): {exc}")

            for attempt in range(max(1, retry_count + 1)):
                if attempt > 0:
                    await asyncio.sleep(0.5 * attempt)

                try:
                    host = override_host or f"http://{target_app.ssh_host}:{target_app.repeater_port}"
                    url = host.rstrip("/") + replay_path

                    if use_sub_invocation_mocks and recording.trace_id and recording.sub_invocations:
                        mock_headers = dict(headers)
                        mock_headers["arex-record-id"] = recording.trace_id
                        try:
                            async with httpx.AsyncClient(timeout=30.0) as client:
                                resp = await client.request(method, url, content=send_body, headers=mock_headers)
                            replay_resp = {
                                "body": resp.text,
                                "status_code": resp.status_code,
                                "error": None,
                            }
                        except httpx.RequestError as exc:
                            replay_resp = {"body": None, "status_code": None, "error": str(exc)}
                        try:
                            await arex.cache_remove_mock(recording.trace_id)
                        except ArexClientError:
                            pass
                    else:
                        try:
                            async with httpx.AsyncClient(timeout=30.0) as client:
                                resp = await client.request(method, url, content=send_body, headers=headers)
                            replay_resp = {
                                "body": resp.text,
                                "status_code": resp.status_code,
                                "error": None,
                            }
                        except httpx.RequestError as exc:
                            replay_resp = {"body": None, "status_code": None, "error": str(exc)}

                    replayed_body = replay_resp.get("body")
                    replayed_status_code = replay_resp.get("status_code")
                    error_msg = replay_resp.get("error")
                    if not error_msg:
                        final_status = "SUCCESS"
                        break
                    last_error = error_msg
                except Exception as exc:
                    last_error = str(exc)
                    if attempt < retry_count:
                        continue
                    error_msg = last_error

            if final_status != "SUCCESS" and last_error:
                error_msg = last_error

            ignore_patterns = [rf".*\['{field}'\].*" for field in ignore_fields]
            diff_json, diff_score = compute_diff(
                recording.response_body,
                replayed_body,
                ignore_patterns,
                diff_rules or [],
                smart_noise_reduction=smart_noise_reduction,
            )

            if assertions:
                assertion_results = evaluate_assertions(
                    assertions,
                    replayed_body,
                    replayed_status_code,
                    diff_score,
                )

            if not error_msg and perf_threshold_ms:
                duration_ms_so_far = int((datetime.utcnow() - start).total_seconds() * 1000)
                if duration_ms_so_far > perf_threshold_ms:
                    perf_result = {
                        "type": "perf_threshold",
                        "passed": False,
                        "message": f"duration {duration_ms_so_far}ms exceeds threshold {perf_threshold_ms}ms",
                    }
                    assertion_results = (assertion_results or []) + [perf_result]

            if error_msg:
                status = "ERROR"
            elif diff_score == 0.0 and assertions_all_passed(assertion_results):
                status = "PASS"
            else:
                status = "FAIL"

        except Exception as exc:
            status = "ERROR"
            if not error_msg:
                error_msg = str(exc)

        duration_ms = int((datetime.utcnow() - start).total_seconds() * 1000)

        failure_category = None
        failure_reason = None
        if status in ("FAIL", "ERROR"):
            failure_category, failure_reason = analyze_failure(
                error_message=error_msg,
                diff_json=diff_json,
                diff_score=diff_score,
                replayed_status_code=replayed_status_code,
                assertion_results=assertion_results,
                ignore_fields=ignore_fields,
            )

        async with async_session_factory() as db:
            result = ReplayResult(
                id=str(uuid.uuid4()),
                job_id=job_id,
                recording_id=recording_id,
                status=status,
                original_response=original_response,
                replayed_response=replayed_body,
                diff_json=diff_json,
                diff_score=diff_score,
                error_message=error_msg,
                duration_ms=duration_ms,
                replayed_status_code=replayed_status_code,
                assertion_results=assertion_results,
                failure_category=failure_category,
                failure_reason=failure_reason,
            )
            db.add(result)
            await db.commit()

        return status, failure_category or "", failure_reason or ""
