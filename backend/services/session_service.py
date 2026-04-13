import asyncio
import base64
import json
import uuid
from datetime import datetime

from sqlalchemy import select

from config import settings
from database import async_session_factory
from integration.arex_client import ArexClient
from models.application import Application
from models.recording import Recording, RecordingSession
from utils.desensitize import desensitize_body
from utils.operation_name import extract_operation_name, get_operation_id_tags
from utils.proxy_recording import has_proxy_recording_header


def build_recording_uri(path: str, query: str | None = None) -> str:
    normalized_path = path if path.startswith("/") else f"/{path}"
    return f"{normalized_path}?{query}" if query else normalized_path


async def collect_recordings(session_id: str):
    """
    收集停止后的录制数据。

    real-time proxy 已经写入一部分数据，这里补齐 arex-storage 延迟刷盘的数据。
    """
    await asyncio.sleep(35)

    async with async_session_factory() as db:
        session = await db.get(RecordingSession, session_id)
        if not session:
            return
        app = await db.get(Application, session.app_id)
        if not app:
            return

        operation_tags = get_operation_id_tags(app)
        already_count_result = await db.execute(
            select(Recording).where(Recording.session_id == session_id)
        )
        existing_recordings = already_count_result.scalars().all()
        count = len(existing_recordings)
        existing_trace_ids = {recording.trace_id for recording in existing_recordings if recording.trace_id}

        try:
            arex_client = ArexClient(settings.arex_storage_url)
            begin_time = session.started_at
            end_time = session.stopped_at or datetime.utcnow()

            response = await asyncio.wait_for(
                arex_client.query_recordings(
                    app_id=app.name,
                    begin_time=begin_time,
                    end_time=end_time,
                    page_size=200,
                ),
                timeout=60.0,
            )

            sources = []
            if "records" in response:
                sources = response.get("records") or []
            else:
                body_value = response.get("body", {})
                if isinstance(body_value, dict):
                    sources = body_value.get("sources", []) or body_value.get("recordList", []) or []
                elif isinstance(body_value, list):
                    sources = body_value

            desensitize_rules = getattr(app, "desensitize_rules", None) or []
            full_mockers = []
            for summary in sources:
                record_id = summary.get("id") or summary.get("recordId")
                if record_id:
                    try:
                        full = await asyncio.wait_for(
                            arex_client.view_recording(record_id),
                            timeout=15.0,
                        )
                        full_mockers.append(full if full else summary)
                    except Exception:
                        full_mockers.append(summary)
                else:
                    full_mockers.append(summary)

            for mocker in full_mockers:
                category = mocker.get("categoryType", {})
                if isinstance(category, dict):
                    entry_type = category.get("name", "HTTP").upper()
                else:
                    entry_type = str(category).upper() if category else "HTTP"

                category_map = {
                    "HTTPSERVLETMOCKER": "HTTP",
                    "HTTPCLIENT": "HTTP",
                    "DUBBO_PROVIDER": "DUBBO",
                    "MYBATIS": "MYBATIS",
                }
                entry_type = category_map.get(entry_type, entry_type)

                target_req = mocker.get("targetRequest") or {}
                target_resp = mocker.get("targetResponse") or {}

                req_body_raw = ""
                req_path = "/"
                if isinstance(target_req, dict):
                    attrs = target_req.get("attributes") or {}
                    req_body_raw = target_req.get("body") or ""
                    if isinstance(req_body_raw, str) and req_body_raw:
                        try:
                            req_body_raw = base64.b64decode(req_body_raw).decode("utf-8", errors="replace")
                        except Exception:
                            pass
                    http_method = (attrs.get("HttpMethod") or "POST").upper()
                    req_path = attrs.get("RequestPath") or "/"
                    headers = attrs.get("Headers") or {}
                    if has_proxy_recording_header(headers):
                        continue
                    content_type = headers.get("content-type") or headers.get("Content-Type")
                    request_body = json.dumps(
                        {
                            "method": http_method,
                            "uri": req_path,
                            "body": req_body_raw,
                            "contentType": content_type,
                        },
                        ensure_ascii=False,
                    )
                else:
                    request_body = str(target_req)

                if isinstance(target_resp, dict):
                    response_body = str(target_resp.get("body") or "")
                else:
                    response_body = str(target_resp) if target_resp else ""

                operation_label = (
                    extract_operation_name(req_body_raw if isinstance(target_req, dict) else request_body, operation_tags)
                    or extract_operation_name(response_body, operation_tags)
                    or mocker.get("operationName")
                    or req_path
                    or "/"
                )

                if desensitize_rules:
                    request_body = desensitize_body(request_body, desensitize_rules)
                    response_body = desensitize_body(response_body, desensitize_rules)

                create_time_ms = mocker.get("creationTime") or mocker.get("createTime") or 0
                timestamp = datetime.utcfromtimestamp(create_time_ms / 1000) if create_time_ms else datetime.utcnow()
                trace_id = mocker.get("id") or mocker.get("recordId") or str(uuid.uuid4())

                if trace_id in existing_trace_ids:
                    continue

                db.add(
                    Recording(
                        id=str(uuid.uuid4()),
                        session_id=session_id,
                        app_id=session.app_id,
                        trace_id=trace_id,
                        entry_type=entry_type,
                        entry_app=app.name,
                        host=app.ssh_host,
                        path=operation_label,
                        request_body=request_body,
                        response_body=response_body,
                        timestamp=timestamp,
                        status="RAW",
                    )
                )
                count += 1
                existing_trace_ids.add(trace_id)

            session.record_count = count
            session.status = "DONE"
        except Exception as exc:
            import traceback

            print(f"[ERROR] collect_recordings failed: {exc}")
            traceback.print_exc()
            session.record_count = count
            session.status = "ERROR"
            session.error_message = str(exc)
        await db.commit()
