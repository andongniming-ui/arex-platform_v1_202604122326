import asyncio
import uuid
import json as _json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File, Form, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import selectinload
from database import get_db
from models.application import Application
from models.recording import RecordingSession, Recording, RepeaterConfig
from models.test_case import TestCaseRecording
from schemas.recording import SessionCreate, SessionOut, RecordingOut, RepeaterConfigCreate, RepeaterConfigOut
from integration import ssh_executor
from integration.config_manager import build_arex_conf, get_default_conf_preview, parse_arex_storage_url
from integration.arex_client import ArexClient, ArexClientError
from config import settings
from services.session_service import (
    build_recording_uri,
    collect_recordings as _collect_recordings,
)
from utils.desensitize import desensitize_body
from utils.operation_name import extract_operation_name, get_operation_id_tags
from utils.proxy_recording import has_proxy_recording_header, with_proxy_recording_header

router = APIRouter(tags=["sessions & recordings"])


async def _get_app_with_config(app_id: str, db: AsyncSession) -> Application:
    """Fetch application with repeater_config eagerly loaded."""
    result = await db.execute(
        select(Application)
        .where(Application.id == app_id)
        .options(selectinload(Application.repeater_config))
    )
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(404, "Application not found")
    return app


# ── Config ────────────────────────────────────────────────────────────────────

@router.get("/configs/{app_id}", response_model=RepeaterConfigOut)
async def get_config(app_id: str, db: AsyncSession = Depends(get_db)):
    app = await _get_app_with_config(app_id, db)
    if not app.repeater_config:
        raise HTTPException(404, "No config found; POST to create one")
    return app.repeater_config


@router.put("/configs/{app_id}", response_model=RepeaterConfigOut)
async def upsert_config(
    app_id: str, body: RepeaterConfigCreate, db: AsyncSession = Depends(get_db)
):
    app = await _get_app_with_config(app_id, db)

    if app.repeater_config:
        cfg = app.repeater_config
        for field, value in body.model_dump().items():
            setattr(cfg, field, value)
        cfg.updated_at = datetime.utcnow()
    else:
        cfg = RepeaterConfig(id=str(uuid.uuid4()), app_id=app_id, **body.model_dump())
        db.add(cfg)
    await db.commit()
    await db.refresh(cfg)
    return cfg


@router.post("/configs/{app_id}/push", response_model=dict)
async def push_config(app_id: str, db: AsyncSession = Depends(get_db)):
    app = await _get_app_with_config(app_id, db)
    if not app.repeater_config:
        raise HTTPException(400, "No config to push; create config first")
    # Build arex.agent.conf content — use agent-facing URL if configured
    arex_storage_url = settings.arex_agent_storage_url or settings.arex_storage_url
    host, port = parse_arex_storage_url(arex_storage_url)
    conf_content = build_arex_conf(app, host, port)
    # Expand ~ to absolute home dir via SSH (SFTP does not expand ~)
    _, home_out, _ = await asyncio.to_thread(
        ssh_executor.run_command, app, "echo $HOME"
    )
    home = home_out.strip() or "/home/" + app.ssh_user
    remote_conf_path = f"{home}/arex-agent/arex.agent.conf"
    await asyncio.to_thread(
        ssh_executor.push_content, app, conf_content, remote_conf_path
    )
    app.repeater_config.pushed_at = datetime.utcnow()
    await db.commit()
    return {"pushed": True, "pushed_at": app.repeater_config.pushed_at.isoformat()}


@router.get("/configs/{app_id}/default", response_model=dict)
async def get_default_config(app_id: str, db: AsyncSession = Depends(get_db)):
    """Return a preview of the arex.agent.conf that would be generated for this app."""
    app = await db.get(Application, app_id)
    if not app:
        raise HTTPException(404, "Application not found")
    agent_url = settings.arex_agent_storage_url or settings.arex_storage_url
    host, port = parse_arex_storage_url(agent_url)
    return {"config": build_arex_conf(app, host, port)}


# ── Sessions ──────────────────────────────────────────────────────────────────

@router.post("/sessions", response_model=SessionOut, status_code=201)
async def create_session(body: SessionCreate, db: AsyncSession = Depends(get_db)):
    app = await _get_app_with_config(body.app_id, db)

    # Snapshot current config
    config_snapshot = app.repeater_config.config_json if app.repeater_config else None

    session = RecordingSession(
        id=str(uuid.uuid4()),
        config_snapshot=config_snapshot,
        **body.model_dump(),
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


@router.get("/sessions", response_model=dict)
async def list_sessions(
    app_id: str | None = None,
    name: str | None = None,
    status: str | None = None,
    started_after: str | None = None,
    started_before: str | None = None,
    limit: int = 20,
    offset: int = 0,
    sort_by: str = "started_at",
    sort_order: str = "desc",
    db: AsyncSession = Depends(get_db),
):
    base = select(RecordingSession)
    if app_id:
        base = base.where(RecordingSession.app_id == app_id)
    if name:
        base = base.where(RecordingSession.name.ilike(f"%{name}%"))
    if status:
        base = base.where(RecordingSession.status == status)
    if started_after:
        from datetime import datetime as _dt
        base = base.where(RecordingSession.started_at >= _dt.fromisoformat(started_after.replace("Z", "+00:00")))
    if started_before:
        from datetime import datetime as _dt
        base = base.where(RecordingSession.started_at <= _dt.fromisoformat(started_before.replace("Z", "+00:00")))
    _SESSION_SORT_COLS = {"started_at"}
    if sort_by not in _SESSION_SORT_COLS:
        raise HTTPException(400, f"Invalid sort_by '{sort_by}'. Allowed: {_SESSION_SORT_COLS}")
    _sort_col = getattr(RecordingSession, sort_by)
    _order_expr = _sort_col.desc() if sort_order == "desc" else _sort_col.asc()
    total = (await db.execute(select(func.count()).select_from(base.subquery()))).scalar() or 0
    items = (await db.execute(base.order_by(_order_expr).offset(offset).limit(limit))).scalars().all()
    return {"items": [SessionOut.model_validate(i) for i in items], "total": total}


@router.get("/sessions/{session_id}", response_model=SessionOut)
async def get_session(session_id: str, db: AsyncSession = Depends(get_db)):
    s = await db.get(RecordingSession, session_id)
    if not s:
        raise HTTPException(404, "Session not found")
    return s


@router.delete("/sessions/batch", status_code=204)
async def batch_delete_sessions(body: dict, db: AsyncSession = Depends(get_db)):
    """Delete multiple sessions by ID. Body: {"ids": [...]}"""
    ids = body.get("ids") or []
    if not ids:
        return
    from models.replay import ReplayResult
    result = await db.execute(
        select(Recording.id).where(Recording.session_id.in_(ids))
    )
    recording_ids = result.scalars().all()
    if recording_ids:
        await db.execute(
            delete(TestCaseRecording).where(TestCaseRecording.recording_id.in_(recording_ids))
        )
        await db.execute(
            delete(ReplayResult).where(ReplayResult.recording_id.in_(recording_ids))
        )
        await db.execute(
            delete(Recording).where(Recording.session_id.in_(ids))
        )
    await db.execute(
        delete(RecordingSession).where(RecordingSession.id.in_(ids))
    )
    await db.commit()


@router.delete("/sessions/{session_id}", status_code=204)
async def delete_session(session_id: str, db: AsyncSession = Depends(get_db)):
    s = await db.get(RecordingSession, session_id)
    if not s:
        raise HTTPException(404, "Session not found")
    # Get recording IDs under this session
    result = await db.execute(
        select(Recording.id).where(Recording.session_id == session_id)
    )
    recording_ids = result.scalars().all()
    if recording_ids:
        # Delete test_case_recording links
        await db.execute(
            delete(TestCaseRecording).where(TestCaseRecording.recording_id.in_(recording_ids))
        )
        # Delete replay_results
        from models.replay import ReplayResult
        await db.execute(
            delete(ReplayResult).where(ReplayResult.recording_id.in_(recording_ids))
        )
        # Delete recordings
        await db.execute(
            delete(Recording).where(Recording.session_id == session_id)
        )
    await db.delete(s)
    await db.commit()


@router.put("/sessions/{session_id}/stop", response_model=dict)
async def stop_session(
    session_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    # Atomic conditional update: only transition ACTIVE → COLLECTING once
    result = await db.execute(
        update(RecordingSession)
        .where(RecordingSession.id == session_id, RecordingSession.status == "ACTIVE")
        .values(status="COLLECTING", stopped_at=datetime.utcnow())
    )
    await db.commit()
    if result.rowcount == 0:
        s = await db.get(RecordingSession, session_id)
        if not s:
            raise HTTPException(404, "Session not found")
        raise HTTPException(400, f"Session is {s.status}, not ACTIVE")

    background_tasks.add_task(_collect_recordings, session_id)
    return {"session_id": session_id, "status": "COLLECTING"}
# ── Direct-record proxy ───────────────────────────────────────────────────────

@router.post("/sessions/{session_id}/direct-record", response_model=dict)
async def direct_record(
    session_id: str,
    request: dict,
    db: AsyncSession = Depends(get_db),
):
    """
    Bypass-agent recording: forward a request to the target service and capture
    the request/response pair as a Recording in this session.

    This is the correct approach for services that use a single HTTP endpoint
    (e.g. /api/bank/service) with different operations encoded in the request body,
    because the arex-agent uses URL path as the dedup key and would only keep one
    recording per batch window regardless of body content.

    Body:
      method       - HTTP method (default POST)
      url          - Full target URL, e.g. http://172.25.109.28:8081/api/bank/service
      headers      - dict of request headers (optional)
      body         - request body string (optional)
      operation    - logical operation name to label the recording (optional, auto-detected)
    """
    import httpx as _httpx

    s = await db.get(RecordingSession, session_id)
    if not s:
        raise HTTPException(404, "Session not found")
    if s.status != "ACTIVE":
        raise HTTPException(400, f"Session is {s.status}, not ACTIVE")

    app = await db.get(Application, s.app_id)
    if not app:
        raise HTTPException(404, "Application not found")

    method = (request.get("method") or "POST").upper()
    url = request.get("url") or ""
    if not url:
        raise HTTPException(400, "url is required")
    req_headers = request.get("headers") or {}
    req_body = request.get("body") or ""
    operation = request.get("operation") or ""

    if not operation and req_body:
        operation = extract_operation_name(req_body, get_operation_id_tags(app)) or ""

    from urllib.parse import urlparse as _urlparse
    _parsed = _urlparse(url)
    req_path = _parsed.path + ("?" + _parsed.query if _parsed.query else "")
    operation_label = operation or req_path

    content_type = req_headers.get("Content-Type") or req_headers.get("content-type") or ""

    request_body_obj = _json.dumps({
        "method": method,
        "uri": url,
        "body": req_body or None,
        "contentType": content_type or None,
    }, ensure_ascii=False)

    # Forward the request to the target service
    response_text = ""
    status_code = 0
    duration_ms = 0
    try:
        import time as _time
        _t0 = _time.monotonic()
        async with _httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.request(
                method=method,
                url=url,
                headers={k: v for k, v in req_headers.items()},
                content=req_body.encode() if req_body else None,
            )
        duration_ms = int((_time.monotonic() - _t0) * 1000)
        response_text = resp.text
        status_code = resp.status_code
    except Exception as e:
        raise HTTPException(502, f"Failed to reach target service: {e}")

    # Persist as a Recording
    rec = Recording(
        id=str(uuid.uuid4()),
        session_id=session_id,
        app_id=s.app_id,
        entry_type="HTTP",
        entry_app=app.name,
        host=_parsed.netloc,
        path=operation_label,
        request_body=request_body_obj,
        response_body=response_text,
        duration_ms=duration_ms,
        timestamp=datetime.utcnow(),
        status="RAW",
    )
    db.add(rec)
    s.record_count = (s.record_count or 0) + 1
    await db.commit()
    await db.refresh(rec)

    return {
        "recording_id": rec.id,
        "status_code": status_code,
        "duration_ms": duration_ms,
        "response": response_text,
    }


# ── Transparent recording proxy ──────────────────────────────────────────────
# Usage: point your test tool at
#   http://<platform>:8001/api/v1/proxy/<app_name>/<original_path>
# The platform finds the ACTIVE session for that app, forwards the request to
# the real service, and captures each call as a separate Recording.
# Operation name is auto-extracted from <service_id> (or any configured tag).

@router.api_route(
    "/proxy/{app_name}/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    response_model=None,
    include_in_schema=True,
)
async def transparent_proxy(
    app_name: str,
    path: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    透明录制代理：将测试工具的目标地址从
        http://host:port/<path>
    改为
        http://platform:8001/api/v1/proxy/<app_name>/<path>
    即可自动录制，无需修改其他任何配置。

    同一 URL 不同请求体的接口（如通过 <service_id> 区分的 XML 服务）
    均会被单独记录，彻底绕过 arex-agent 的 URL 级去重限制。
    """
    import re as _re
    import time as _time
    import httpx as _httpx
    from fastapi.responses import Response as _FResponse

    # Find application by name
    app_result = await db.execute(
        select(Application).where(Application.name == app_name)
    )
    app = app_result.scalar_one_or_none()
    if not app:
        return _FResponse(
            content=f"app '{app_name}' not found".encode(),
            status_code=404,
        )

    # Find the active session
    sess_result = await db.execute(
        select(RecordingSession)
        .where(
            RecordingSession.app_id == app.id,
            RecordingSession.status == "ACTIVE",
        )
        .order_by(RecordingSession.started_at.desc())
        .limit(1)
    )
    session = sess_result.scalar_one_or_none()
    if not session:
        return _FResponse(
            content=f"no ACTIVE session for app '{app_name}'".encode(),
            status_code=409,
        )

    # Build target URL using app's repeater_port
    target_base = f"http://{app.ssh_host}:{app.repeater_port}"
    target_url = f"{target_base}/{path}"
    query = request.url.query
    if query:
        target_url += f"?{query}"

    # Read request body
    body_bytes = await request.body()
    body_str = body_bytes.decode("utf-8", errors="replace") if body_bytes else ""

    # Forward headers (strip hop-by-hop)
    skip = {"host", "content-length", "transfer-encoding", "connection"}
    fwd_headers = {k: v for k, v in request.headers.items() if k.lower() not in skip}
    fwd_headers = with_proxy_recording_header(fwd_headers)

    # Forward request to real service
    response_text = ""
    resp_status = 502
    resp_headers: dict = {}
    resp_content = b""
    duration_ms = 0
    try:
        _t0 = _time.monotonic()
        async with _httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.request(
                method=request.method,
                url=target_url,
                headers=fwd_headers,
                content=body_bytes or None,
            )
        duration_ms = int((_time.monotonic() - _t0) * 1000)
        resp_status = resp.status_code
        resp_content = resp.content
        response_text = resp.text
        resp_headers = dict(resp.headers)
    except Exception as e:
        resp_content = f"proxy error: {e}".encode()
        resp_status = 502

    operation = extract_operation_name(body_str, get_operation_id_tags(app)) or ""

    req_path = build_recording_uri(path, query)
    operation_label = operation or req_path
    content_type = fwd_headers.get("content-type") or fwd_headers.get("Content-Type") or ""

    request_body_obj = _json.dumps({
        "method": request.method,
        "uri": req_path,
        "body": body_str or None,
        "contentType": content_type or None,
    }, ensure_ascii=False)

    rec = Recording(
        id=str(uuid.uuid4()),
        session_id=session.id,
        app_id=app.id,
        entry_type="HTTP",
        entry_app=app.name,
        host=f"{app.ssh_host}:{app.repeater_port}",
        path=operation_label,
        request_body=request_body_obj,
        response_body=response_text,
        duration_ms=duration_ms,
        timestamp=datetime.utcnow(),
        status="RAW",
    )
    db.add(rec)
    session.record_count = (session.record_count or 0) + 1
    await db.commit()

    # Strip hop-by-hop response headers before returning
    skip_resp = {"transfer-encoding", "content-encoding", "content-length", "connection"}
    clean_headers = {k: v for k, v in resp_headers.items() if k.lower() not in skip_resp}

    return _FResponse(
        content=resp_content,
        status_code=resp_status,
        headers=clean_headers,
        media_type=resp_headers.get("content-type"),
    )


# ── Recordings ────────────────────────────────────────────────────────────────

@router.get("/recordings", response_model=dict)
async def list_recordings(
    session_id: str | None = None,
    app_id: str | None = None,
    entry_type: str | None = None,
    status: str | None = None,
    path_contains: str | None = None,
    created_after: str | None = None,
    created_before: str | None = None,
    limit: int = 50,
    offset: int = 0,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    db: AsyncSession = Depends(get_db),
):
    base = select(Recording)
    if session_id:
        base = base.where(Recording.session_id == session_id)
    if app_id:
        base = base.where(Recording.app_id == app_id)
    if entry_type:
        base = base.where(Recording.entry_type == entry_type.upper())
    if status:
        base = base.where(Recording.status == status)
    if path_contains:
        base = base.where(Recording.path.ilike(f"%{path_contains}%"))
    if created_after:
        from datetime import datetime as _dt
        base = base.where(Recording.created_at >= _dt.fromisoformat(created_after.replace("Z", "+00:00")))
    if created_before:
        from datetime import datetime as _dt
        base = base.where(Recording.created_at <= _dt.fromisoformat(created_before.replace("Z", "+00:00")))
    _RECORDING_SORT_COLS = {"created_at", "duration_ms"}
    if sort_by not in _RECORDING_SORT_COLS:
        raise HTTPException(400, f"Invalid sort_by '{sort_by}'. Allowed: {_RECORDING_SORT_COLS}")
    _sort_col = getattr(Recording, sort_by)
    _order_expr = _sort_col.desc() if sort_order == "desc" else _sort_col.asc()
    total = (await db.execute(select(func.count()).select_from(base.subquery()))).scalar() or 0
    items = (await db.execute(base.order_by(_order_expr).offset(offset).limit(limit))).scalars().all()
    return {"items": [RecordingOut.model_validate(i) for i in items], "total": total}


@router.get("/recordings/{recording_id}", response_model=RecordingOut)
async def get_recording(recording_id: str, db: AsyncSession = Depends(get_db)):
    rec = await db.get(Recording, recording_id)
    if not rec:
        raise HTTPException(404, "Recording not found")
    return rec


@router.post("/recordings/import-har", response_model=dict)
async def import_har(
    file: UploadFile = File(...),
    app_id: str = Form(...),
    session_name: str = Form(default="HAR 导入"),
    db: AsyncSession = Depends(get_db),
):
    """
    Import recordings from a Chrome DevTools HAR file.
    Creates a new RecordingSession + one Recording per HAR entry.
    """
    from urllib.parse import urlparse, urlencode

    app = await db.get(Application, app_id)
    if not app:
        raise HTTPException(404, "Application not found")

    raw = await file.read()
    try:
        har = _json.loads(raw)
    except Exception:
        raise HTTPException(400, "Invalid JSON / not a valid HAR file")

    entries = har.get("log", {}).get("entries", [])
    if not entries:
        raise HTTPException(400, "HAR file contains no entries")

    # Create a completed session
    session = RecordingSession(
        id=str(uuid.uuid4()),
        app_id=app_id,
        name=session_name,
        status="DONE",
        started_at=datetime.utcnow(),
        stopped_at=datetime.utcnow(),
    )
    db.add(session)

    count = 0
    for entry in entries:
        req = entry.get("request", {})
        resp = entry.get("response", {})

        method = (req.get("method") or "GET").upper()
        url = req.get("url") or ""
        parsed = urlparse(url)
        host = parsed.netloc
        path = parsed.path

        # Append query params from queryString array if not already in URL
        qs_pairs = req.get("queryString") or []
        if qs_pairs and not parsed.query:
            path += "?" + urlencode([(q["name"], q["value"]) for q in qs_pairs])
        elif parsed.query:
            path += "?" + parsed.query

        # Request body
        post_data = req.get("postData") or {}
        body_text = post_data.get("text") or ""
        content_type = post_data.get("mimeType") or ""
        operation_label = extract_operation_name(body_text, get_operation_id_tags(app)) or path

        request_body_obj = {
            "method": method,
            "uri": url,
            "body": body_text if body_text else None,
            "contentType": content_type if content_type else None,
        }

        # Response body
        resp_content = resp.get("content") or {}
        resp_text = resp_content.get("text") or ""

        # Timestamp
        started_str = entry.get("startedDateTime") or ""
        timestamp = None
        if started_str:
            try:
                parsed_ts = datetime.fromisoformat(started_str.replace("Z", "+00:00"))
                if parsed_ts.tzinfo is not None:
                    timestamp = parsed_ts.astimezone().replace(tzinfo=None)
                else:
                    timestamp = parsed_ts
            except Exception:
                pass

        duration_ms = int(entry.get("time") or 0)

        rec = Recording(
            id=str(uuid.uuid4()),
            session_id=session.id,
            app_id=app_id,
            entry_type="HTTP",
            host=host,
            path=operation_label,
            request_body=_json.dumps(request_body_obj, ensure_ascii=False),
            response_body=resp_text or None,
            duration_ms=duration_ms,
            timestamp=timestamp,
            status="PARSED",
        )
        db.add(rec)
        count += 1

    session.record_count = count
    await db.commit()
    return {"session_id": session.id, "imported": count, "session_name": session_name}


@router.patch("/recordings/{recording_id}/request", response_model=RecordingOut)
async def update_request_body(
    recording_id: str,
    body: dict,
    db: AsyncSession = Depends(get_db),
):
    """Edit the request body of a recording (for parameter mutation testing).
    Body: {"request_body": "{...json string...}"}
    """
    rec = await db.get(Recording, recording_id)
    if not rec:
        raise HTTPException(404, "Recording not found")
    new_rb = body.get("request_body")
    if new_rb is None:
        raise HTTPException(400, "request_body field is required")
    # Validate it's parseable JSON
    try:
        _json.loads(new_rb)
    except Exception:
        raise HTTPException(400, "request_body must be a valid JSON string")
    rec.request_body = new_rb
    await db.commit()
    await db.refresh(rec)
    return rec


@router.patch("/recordings/{recording_id}/tags", response_model=RecordingOut)
async def update_tags(
    recording_id: str,
    body: dict,
    db: AsyncSession = Depends(get_db),
):
    """Update the tags list of a recording. Body: {"tags": ["smoke", "P0"]}"""
    rec = await db.get(Recording, recording_id)
    if not rec:
        raise HTTPException(404, "Recording not found")
    rec.tags = body.get("tags") or []
    await db.commit()
    await db.refresh(rec)
    return rec


@router.delete("/recordings/batch", status_code=204)
async def batch_delete_recordings(body: dict, db: AsyncSession = Depends(get_db)):
    """Delete multiple recordings by ID. Body: {"ids": [...]}"""
    ids = body.get("ids") or []
    if not ids:
        return
    from models.replay import ReplayResult
    await db.execute(
        delete(TestCaseRecording).where(TestCaseRecording.recording_id.in_(ids))
    )
    await db.execute(
        delete(ReplayResult).where(ReplayResult.recording_id.in_(ids))
    )
    await db.execute(
        delete(Recording).where(Recording.id.in_(ids))
    )
    await db.commit()


@router.post("/recordings/{recording_id}/recapture", response_model=RecordingOut)
async def recapture_response(recording_id: str, db: AsyncSession = Depends(get_db)):
    """Re-send the recorded request to the app and update response_body as baseline."""
    import httpx
    rec = await db.get(Recording, recording_id)
    if not rec:
        raise HTTPException(404, "Recording not found")
    app = await db.get(Application, rec.app_id)
    if not app:
        raise HTTPException(404, "Application not found")

    req_info: dict = {}
    if rec.request_body:
        try:
            req_info = _json.loads(rec.request_body)
        except Exception:
            pass

    method = (req_info.get("method") or "GET").upper()
    uri = req_info.get("uri") or rec.path or "/"
    from urllib.parse import urlparse
    if uri.startswith("http"):
        parsed = urlparse(uri)
        path = parsed.path + ("?" + parsed.query if parsed.query else "")
    else:
        path = uri

    send_body = req_info.get("body") if method not in ("GET", "DELETE", "HEAD") else None
    headers = {}
    ct = req_info.get("contentType")
    if ct and send_body:
        headers["Content-Type"] = ct

    try:
        url = f"http://{app.ssh_host}:{app.repeater_port}{path}"
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.request(method=method, url=url, headers=headers,
                                     content=send_body.encode() if send_body else None)
        rec.response_body = r.text
        await db.commit()
        await db.refresh(rec)
        return rec
    except Exception as e:
        raise HTTPException(500, f"Recapture failed: {e}")


@router.delete("/recordings/{recording_id}", status_code=204)
async def delete_recording(recording_id: str, db: AsyncSession = Depends(get_db)):
    rec = await db.get(Recording, recording_id)
    if not rec:
        raise HTTPException(404, "Recording not found")
    from models.replay import ReplayResult
    await db.execute(
        delete(TestCaseRecording).where(TestCaseRecording.recording_id == recording_id)
    )
    await db.execute(
        delete(ReplayResult).where(ReplayResult.recording_id == recording_id)
    )
    await db.delete(rec)
    await db.commit()
