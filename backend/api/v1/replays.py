import asyncio
import uuid
import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from database import get_db
from models.replay import ReplayJob, ReplayResult
from models.test_case import TestCase, TestCaseRecording
from models.recording import Recording
from models.application import Application
from schemas.replay import ReplayJobCreate, ReplayJobOut, ReplayResultOut, ResultSummary
import httpx
from integration.arex_client import ArexClient, ArexClientError
from config import settings
from utils.diff import compute_diff
from utils.assertions import evaluate_assertions, assertions_all_passed
from utils.failure_analyzer import analyze_failure

router = APIRouter(prefix="/replays", tags=["replays"])

# Keep strong references to background tasks to prevent GC cancellation
_background_tasks: set = set()

def _fire(coro):
    task = asyncio.create_task(coro)
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)


def _extract_service_id(text: str | None) -> str | None:
    """从 XML 文本中提取 <service_id> 标签内容。"""
    if not text:
        return None
    import re as _re
    m = _re.search(r'<service_id>(.*?)</service_id>', text)
    return m.group(1).strip() if m else None



def _match_xml_template(xml_tpl: str, response_body: str | None, request_body: str | None = None) -> str | None:
    """
    Match an XML request template based on service_id.

    xml_tpl can be:
      - A JSON map: {"OPEN_ACCOUNT": "<request>...</request>", "QUERY_BALANCE": "..."}
      - A plain XML string (only returned when its service_id matches the recording)

    service_id lookup order: request body → response body (response echoes the request service_id).
    Returns the matched XML template string, or None if no match.
    """
    import re as _re
    import json as _json

    # Prefer service_id from recorded request body, fall back to response body
    # (the response always echoes the same service_id as the request for this XML API)
    service_id = (_extract_service_id(request_body)
                  or _extract_service_id(response_body))

    # Try JSON map first
    try:
        tpl_map = _json.loads(xml_tpl)
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
    except (_json.JSONDecodeError, TypeError):
        pass

    # Plain XML string: only use it when its service_id matches the recording.
    # Prevents a single-service template from being sent for every other service.
    tpl_service_id = _extract_service_id(xml_tpl)
    if tpl_service_id and service_id and tpl_service_id != service_id:
        return None
    return xml_tpl.strip()


def _apply_header_transforms(headers: dict, transforms: list[dict]) -> dict:
    """
    P1: 应用请求头转换规则。
    transforms 格式: [{"type": "replace", "key": "Host", "value": "new-host.com"}, {"type": "remove", "key": "Authorization"}]
    支持类型:
      - replace: 替换指定请求头的值
      - remove: 删除指定请求头
      - add: 添加新请求头（若不存在则添加）
    """
    if not transforms:
        return headers
    
    result = dict(headers)  # 复制一份避免修改原字典
    
    for t in transforms:
        t_type = t.get("type", "")
        key = t.get("key", "")
        
        if not key:
            continue
        
        if t_type == "replace":
            # 替换已有请求头的值
            result[key] = t.get("value", "")
        elif t_type == "remove":
            # 删除请求头
            result.pop(key, None)
        elif t_type == "add":
            # 添加请求头（仅当不存在时）
            if key not in result:
                result[key] = t.get("value", "")
    
    return result


@router.post("", response_model=ReplayJobOut, status_code=201)
async def create_replay_job(
    body: ReplayJobCreate,
    db: AsyncSession = Depends(get_db),
):
    tc = await db.get(TestCase, body.case_id)
    if not tc:
        raise HTTPException(404, "Test case not found")
    target_app = await db.get(Application, body.target_app_id)
    if not target_app:
        raise HTTPException(404, "Target application not found")

    # 校验用例是否有录制数据
    count_result = await db.execute(
        select(TestCaseRecording).where(TestCaseRecording.case_id == body.case_id)
    )
    if not count_result.scalars().first():
        raise HTTPException(400, "该测试用例还没有添加任何录制接口，请先在测试用例库中添加录制后再回放")

    job = ReplayJob(
        id=str(uuid.uuid4()),
        total_count=tc.recording_count,
        **body.model_dump(),
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    _fire(_run_replay_job(job.id))
    return job


@router.get("", response_model=dict)
async def list_replay_jobs(
    case_id: str | None = None,
    app_id: str | None = None,
    status: str | None = None,
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    base = select(ReplayJob)
    if case_id:
        base = base.where(ReplayJob.case_id == case_id)
    if app_id:
        base = base.where(ReplayJob.target_app_id == app_id)
    if status:
        base = base.where(ReplayJob.status == status)
    total = (await db.execute(select(func.count()).select_from(base.subquery()))).scalar() or 0
    items = (await db.execute(base.order_by(ReplayJob.created_at.desc()).offset(offset).limit(limit))).scalars().all()
    return {"items": [ReplayJobOut.model_validate(i) for i in items], "total": total}


@router.get("/{job_id}", response_model=ReplayJobOut)
async def get_replay_job(job_id: str, db: AsyncSession = Depends(get_db)):
    job = await db.get(ReplayJob, job_id)
    if not job:
        raise HTTPException(404, "Replay job not found")
    return job


@router.put("/{job_id}/cancel", response_model=dict)
async def cancel_replay_job(job_id: str, db: AsyncSession = Depends(get_db)):
    job = await db.get(ReplayJob, job_id)
    if not job:
        raise HTTPException(404, "Replay job not found")
    if job.status not in ("PENDING", "RUNNING"):
        raise HTTPException(400, f"Cannot cancel job in status {job.status}")
    job.status = "CANCELLED"
    job.finished_at = datetime.utcnow()
    await db.commit()
    return {"status": "CANCELLED"}


# ── Results ───────────────────────────────────────────────────────────────────

@router.get("/{job_id}/summary", response_model=ResultSummary)
async def get_result_summary(job_id: str, db: AsyncSession = Depends(get_db)):
    job = await db.get(ReplayJob, job_id)
    if not job:
        raise HTTPException(404, "Replay job not found")
    sent = job.sent_count or 0
    success = job.success_count or 0
    fail = job.fail_count or 0
    error_count = max(sent - success - fail, 0)
    pass_rate = success / sent if sent else 0.0
    return ResultSummary(
        job_id=job_id,
        status=job.status,
        total_count=job.total_count,
        success_count=success,
        fail_count=fail,
        error_count=error_count,
        pass_rate=pass_rate,
    )


@router.get("/{job_id}/analysis", response_model=dict)
async def get_failure_analysis(job_id: str, db: AsyncSession = Depends(get_db)):
    """
    Get failure analysis aggregated by category.
    
    Returns:
        {
            "job_id": str,
            "total_failures": int,
            "categories": {
                "ENVIRONMENT": {"count": int, "percentage": float, "results": [...]},
                "DATA_ISSUE": {"count": int, "percentage": float, "results": [...]},
                "BUG": {"count": int, "percentage": float, "results": [...]},
                "PERFORMANCE": {"count": int, "percentage": float, "results": [...]},
                "UNKNOWN": {"count": int, "percentage": float, "results": [...]},
            }
        }
    """
    job = await db.get(ReplayJob, job_id)
    if not job:
        raise HTTPException(404, "Replay job not found")
    
    # Get all FAIL and ERROR results with their failure analysis
    q = (
        select(ReplayResult, Recording.path, Recording.entry_type)
        .join(Recording, Recording.id == ReplayResult.recording_id, isouter=True)
        .where(ReplayResult.job_id == job_id)
        .where(ReplayResult.status.in_(["FAIL", "ERROR"]))
        .order_by(ReplayResult.replayed_at)
    )
    rows = (await db.execute(q)).all()
    
    # Initialize category stats
    categories = {
        "ENVIRONMENT": {"count": 0, "percentage": 0.0, "results": []},
        "DATA_ISSUE": {"count": 0, "percentage": 0.0, "results": []},
        "BUG": {"count": 0, "percentage": 0.0, "results": []},
        "PERFORMANCE": {"count": 0, "percentage": 0.0, "results": []},
        "UNKNOWN": {"count": 0, "percentage": 0.0, "results": []},
    }
    
    total_failures = len(rows)
    
    for rr, path, entry_type in rows:
        category = rr.failure_category or "UNKNOWN"
        if category not in categories:
            category = "UNKNOWN"
        
        categories[category]["count"] += 1
        # Add to results list (limit to essential fields for bandwidth)
        categories[category]["results"].append({
            "id": rr.id,
            "recording_id": rr.recording_id,
            "recording_path": path,
            "recording_entry_type": entry_type,
            "status": rr.status,
            "failure_reason": rr.failure_reason,
            "replayed_status_code": rr.replayed_status_code,
            "diff_score": rr.diff_score,
            "error_message": rr.error_message,
            "duration_ms": rr.duration_ms,
            "replayed_at": rr.replayed_at.isoformat() if rr.replayed_at else None,
        })
    
    # Calculate percentages
    if total_failures > 0:
        for cat in categories:
            categories[cat]["percentage"] = round(categories[cat]["count"] / total_failures * 100, 1)
    
    return {
        "job_id": job_id,
        "total_failures": total_failures,
        "categories": categories,
    }


@router.get("/{job_id}/results", response_model=dict)
async def list_results(
    job_id: str,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    base = select(ReplayResult).where(ReplayResult.job_id == job_id)
    if status:
        base = base.where(ReplayResult.status == status.upper())
    total = (await db.execute(select(func.count()).select_from(base.subquery()))).scalar() or 0
    q = (
        select(ReplayResult, Recording.path, Recording.entry_type,
               Recording.request_body, Recording.response_body)
        .join(Recording, Recording.id == ReplayResult.recording_id, isouter=True)
        .where(ReplayResult.job_id == job_id)
        .order_by(ReplayResult.replayed_at)
        .offset(offset)
        .limit(limit)
    )
    if status:
        q = q.where(ReplayResult.status == status.upper())
    rows = (await db.execute(q)).all()
    out = []
    for rr, path, entry_type, req_body, resp_body in rows:
        d = ReplayResultOut.model_validate(rr)
        d.recording_path = path
        d.recording_entry_type = entry_type
        raw_xml = None
        if req_body:
            try:
                raw_xml = json.loads(req_body).get("body")
            except Exception:
                pass
        d.recording_service_id = _extract_service_id(raw_xml) or _extract_service_id(resp_body)
        out.append(d)
    return {"items": out, "total": total}


@router.delete("/batch", status_code=204)
async def batch_delete_replay_jobs(body: dict, db: AsyncSession = Depends(get_db)):
    """Delete multiple replay jobs by ID. Body: {"ids": [...]}"""
    ids = body.get("ids") or []
    if not ids:
        return
    await db.execute(delete(ReplayResult).where(ReplayResult.job_id.in_(ids)))
    await db.execute(delete(ReplayJob).where(ReplayJob.id.in_(ids)))
    await db.commit()


@router.delete("/{job_id}", status_code=204)
async def delete_replay_job(job_id: str, db: AsyncSession = Depends(get_db)):
    job = await db.get(ReplayJob, job_id)
    if not job:
        raise HTTPException(404, "Replay job not found")
    await db.delete(job)
    await db.commit()


@router.get("/{job_id}/report", response_class=HTMLResponse)
async def get_report(job_id: str, db: AsyncSession = Depends(get_db)):
    """Generate a self-contained HTML test report for the replay job."""
    from html import escape as he
    job = await db.get(ReplayJob, job_id)
    if not job:
        raise HTTPException(404, "Replay job not found")

    # Load test case and application names for report header
    from models.test_case import TestCase
    from models.application import Application
    tc = await db.get(TestCase, job.case_id) if job.case_id else None
    app = await db.get(Application, job.target_app_id) if job.target_app_id else None
    case_name = tc.name if tc else job.case_id or "-"
    app_name = app.name if app else job.target_app_id or "-"

    result = await db.execute(
        select(ReplayResult, Recording.path, Recording.entry_type, Recording.request_body)
        .join(Recording, Recording.id == ReplayResult.recording_id, isouter=True)
        .where(ReplayResult.job_id == job_id)
        .order_by(ReplayResult.replayed_at)
    )
    rows = result.all()

    sent = job.sent_count or 0
    success = job.success_count or 0
    fail = job.fail_count or 0
    error = max(sent - success - fail, 0)
    pass_rate = success / sent if sent else 0.0

    def fmt_dt(dt):
        return dt.strftime("%Y-%m-%d %H:%M:%S") if dt else "-"

    def fmt_json(text):
        if not text:
            return ""
        try:
            return json.dumps(json.loads(text), indent=2, ensure_ascii=False)
        except Exception:
            return text

    def diff_summary(diff_json_str, score):
        if not diff_json_str:
            return "-"
        try:
            d = json.loads(diff_json_str)
            score_str = f"{score:.3f}" if score is not None else "?"
            return f"score={score_str}，{len(d)} 处差异"
        except Exception:
            return "有差异"

    tbody = ""
    for idx, (r, path, entry_type, req_body) in enumerate(rows):
        rid = f"row_{idx}"
        status = r.status or "ERROR"
        status_colors = {"PASS": "#18a058", "FAIL": "#d03050", "ERROR": "#f0a020"}
        sc = status_colors.get(status, "#999")
        safe_path = he(path or "-")
        safe_type = he(entry_type or "HTTP")
        diff_txt = diff_summary(r.diff_json, r.diff_score)
        orig_fmt = he(fmt_json(r.original_response))
        replay_fmt = he(fmt_json(r.replayed_response))
        req_fmt = he(fmt_json(req_body))
        err_txt = he(r.error_message or "")
        sc_txt = str(r.replayed_status_code) if r.replayed_status_code else "-"

        # Build diff detail lines
        diff_detail_html = ""
        if r.diff_json:
            try:
                d = json.loads(r.diff_json)
                lines = []
                for change_type, changes in d.items():
                    if isinstance(changes, dict):
                        for field_path, detail in changes.items():
                            lines.append(
                                f'<div class="diff-line"><span class="diff-key">{he(str(field_path))}</span>'
                                f'<span class="diff-val">{he(json.dumps(detail, ensure_ascii=False)[:200])}</span></div>'
                            )
                diff_detail_html = "\n".join(lines)
            except Exception:
                diff_detail_html = f'<pre>{he(r.diff_json[:500])}</pre>'

        # Build assertion results
        assertion_html = ""
        if r.assertion_results:
            alines = []
            for ar in r.assertion_results:
                ico = "✅" if ar.get("passed") else "❌"
                msg = he(ar.get("message", ar.get("type", "")))
                alines.append(f'<div class="assert-line">{ico} {msg}</div>')
            assertion_html = "\n".join(alines)

        tbody += f"""
  <tr class="data-row row-{status.lower()}" data-status="{status}" onclick="toggle('{rid}')">
    <td><span class="type-badge">{safe_type}</span><span class="path-text">{safe_path}</span></td>
    <td><span class="status-badge" style="color:{sc}">{status}</span></td>
    <td class="mono">{diff_txt}</td>
    <td class="mono">{sc_txt}</td>
    <td class="mono">{r.duration_ms or '-'}</td>
    <td>{fmt_dt(r.replayed_at)}</td>
    <td class="toggle-hint">▶ 展开</td>
  </tr>
  <tr id="{rid}" class="detail-row" style="display:none">
    <td colspan="7">
      <div class="detail-wrap">
        {"<div class='detail-section err-section'><div class='detail-title'>❌ 错误信息</div><pre>" + err_txt + "</pre></div>" if err_txt else ""}
        {"<div class='detail-section assert-result-section'><div class='detail-title'>🔍 断言结果</div>" + assertion_html + "</div>" if assertion_html else ""}
        {"<div class='detail-section'><div class='detail-title'>📤 请求体（录制时）</div><pre>" + req_fmt + "</pre></div>" if req_fmt else ""}
        <div class="detail-cols">
          <div class="detail-section">
            <div class="detail-title">📥 原始响应（录制时）</div>
            <pre>{orig_fmt or '<span style="color:#999">（无数据）</span>'}</pre>
          </div>
          <div class="detail-section">
            <div class="detail-title">🔄 回放响应</div>
            <pre>{replay_fmt or '<span style="color:#999">（无数据）</span>'}</pre>
          </div>
        </div>
        {"<div class='detail-section diff-section'><div class='detail-title'>📋 差异明细</div>" + diff_detail_html + "</div>" if diff_detail_html else ""}
      </div>
    </td>
  </tr>"""

    bar_pass = f"{pass_rate*100:.1f}%"
    bar_fail = f"{(fail/sent*100) if sent else 0:.1f}%"
    bar_error = f"{(error/sent*100) if sent else 0:.1f}%"
    ignore_str = he(', '.join(job.ignore_fields) if job.ignore_fields else '无')
    diff_rules_str = he(f"{len(job.diff_rules)} 条规则" if job.diff_rules else '无')
    assertions_str = he(f"{len(job.assertions)} 条断言" if job.assertions else '无')

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>回放报告 · {he(app_name)} · {he(case_name)}</title>
<style>
  *{{box-sizing:border-box}}
  body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;margin:0;padding:24px;background:#f0f2f5;color:#333;}}
  .report-header{{background:#fff;border-radius:10px;padding:16px 24px;margin-bottom:20px;box-shadow:0 1px 4px rgba(0,0,0,.08);border-left:4px solid #1677ff;}}
  .report-title{{font-size:20px;font-weight:700;margin:0 0 6px;color:#1a1a1a;}}
  .report-breadcrumb{{font-size:13px;color:#888;display:flex;align-items:center;gap:6px;flex-wrap:wrap;}}
  .breadcrumb-app{{color:#1677ff;font-weight:600;}}
  .breadcrumb-sep{{color:#ccc;}}
  .breadcrumb-case{{color:#333;font-weight:600;}}
  h1{{font-size:22px;margin:0 0 4px;font-weight:700;}}
  .meta{{color:#666;font-size:13px;margin-bottom:20px;line-height:1.8;}}
  .meta b{{color:#333;}}
  .stats{{display:flex;flex-wrap:wrap;gap:16px;margin-bottom:20px;}}
  .stat-box{{background:#fff;border-radius:10px;padding:16px 24px;min-width:110px;box-shadow:0 1px 4px rgba(0,0,0,.08);text-align:center;}}
  .stat-num{{font-size:30px;font-weight:700;line-height:1.2;}}
  .stat-label{{font-size:12px;color:#888;margin-top:4px;}}
  .pass{{color:#18a058}}.fail{{color:#d03050}}.error{{color:#f0a020}}
  .progress-bar{{display:flex;height:10px;border-radius:5px;overflow:hidden;margin-bottom:20px;background:#e8e8e8;}}
  .bar-pass{{background:#18a058}}.bar-fail{{background:#d03050}}.bar-error{{background:#f0a020}}
  .toolbar{{display:flex;align-items:center;gap:10px;margin-bottom:12px;flex-wrap:wrap;}}
  .filter-btn{{padding:5px 14px;border:1px solid #ddd;border-radius:20px;cursor:pointer;font-size:13px;background:#fff;transition:all .15s;}}
  .filter-btn:hover,.filter-btn.active{{background:#1677ff;color:#fff;border-color:#1677ff;}}
  .search-box{{padding:5px 12px;border:1px solid #ddd;border-radius:20px;font-size:13px;outline:none;width:220px;}}
  .search-box:focus{{border-color:#1677ff;}}
  .result-count{{font-size:12px;color:#888;margin-left:auto;}}
  table{{width:100%;border-collapse:collapse;background:#fff;border-radius:10px;overflow:hidden;box-shadow:0 1px 4px rgba(0,0,0,.08);font-size:13px;}}
  th{{background:#fafafa;padding:10px 14px;text-align:left;font-weight:600;border-bottom:2px solid #f0f0f0;color:#555;}}
  .data-row td{{padding:10px 14px;border-bottom:1px solid #f5f5f5;vertical-align:middle;cursor:pointer;}}
  .data-row:hover td{{background:#fafbff!important;}}
  .data-row.row-pass{{background:#fafffe;}}
  .data-row.row-fail{{background:#fff8f8;}}
  .data-row.row-error{{background:#fffdf0;}}
  .detail-row td{{padding:0;border-bottom:1px solid #e8e8e8;}}
  .detail-wrap{{padding:16px 20px;background:#fafafa;border-top:2px solid #e8e8e8;}}
  .detail-cols{{display:grid;grid-template-columns:1fr 1fr;gap:16px;}}
  .detail-section{{margin-bottom:12px;}}
  .detail-title{{font-size:12px;font-weight:600;color:#555;margin-bottom:6px;padding-bottom:4px;border-bottom:1px solid #e8e8e8;}}
  .err-section pre{{color:#d03050;background:#fff6f6;border:1px solid #ffd0d0;}}
  .diff-section{{background:#fff;border:1px solid #ffe7ba;border-radius:6px;padding:10px;}}
  .diff-line{{padding:3px 0;border-bottom:1px solid #f5f5f5;font-size:12px;display:flex;gap:8px;}}
  .diff-key{{color:#d03050;font-weight:600;font-family:monospace;min-width:160px;}}
  .diff-val{{color:#333;font-family:monospace;word-break:break-all;}}
  .assert-result-section{{background:#fff;border:1px solid #d6e4ff;border-radius:6px;padding:10px;}}
  .assert-line{{padding:3px 0;font-size:13px;}}
  pre{{margin:0;background:#f8f8f8;border:1px solid #eee;border-radius:6px;padding:10px;font-size:12px;font-family:"SFMono-Regular",Consolas,monospace;white-space:pre-wrap;word-break:break-all;max-height:300px;overflow-y:auto;}}
  .type-badge{{display:inline-block;padding:1px 6px;border-radius:4px;font-size:11px;font-weight:700;background:#e8f4ff;color:#1677ff;margin-right:8px;vertical-align:middle;}}
  .path-text{{font-family:monospace;font-size:13px;}}
  .status-badge{{font-weight:700;font-size:13px;}}
  .mono{{font-family:monospace;font-size:12px;}}
  .toggle-hint{{color:#aaa;font-size:12px;user-select:none;text-align:right;}}
  .footer{{margin-top:20px;font-size:12px;color:#aaa;text-align:center;}}
  @media(max-width:700px){{.detail-cols{{grid-template-columns:1fr;}}}}
</style>
</head>
<body>
<div class="report-header">
  <div class="report-title">录制回放测试报告</div>
  <div class="report-breadcrumb">
    <span class="breadcrumb-app">🖥 {he(app_name)}</span>
    <span class="breadcrumb-sep">›</span>
    <span class="breadcrumb-case">📋 {he(case_name)}</span>
    <span class="breadcrumb-sep">|</span>
    <span>任务 ID: {he(job_id[:8])}</span>
    <span class="breadcrumb-sep">|</span>
    <span>环境: {he(job.environment or '-')}</span>
    <span class="breadcrumb-sep">|</span>
    <span>开始: {fmt_dt(job.started_at)}</span>
    <span class="breadcrumb-sep">|</span>
    <span>结束: {fmt_dt(job.finished_at)}</span>
    <span class="breadcrumb-sep">|</span>
    <span>并发: {job.concurrency}</span>
    <span class="breadcrumb-sep">|</span>
    <span>忽略字段: {ignore_str}</span>
    <span class="breadcrumb-sep">|</span>
    <span>差异规则: {diff_rules_str}</span>
    <span class="breadcrumb-sep">|</span>
    <span>断言规则: {assertions_str}</span>
  </div>
</div>

<div class="stats">
  <div class="stat-box"><div class="stat-num">{sent}</div><div class="stat-label">已执行</div></div>
  <div class="stat-box"><div class="stat-num pass">{success}</div><div class="stat-label">通过 PASS</div></div>
  <div class="stat-box"><div class="stat-num fail">{fail}</div><div class="stat-label">失败 FAIL</div></div>
  <div class="stat-box"><div class="stat-num error">{error}</div><div class="stat-label">错误 ERROR</div></div>
  <div class="stat-box"><div class="stat-num {'pass' if pass_rate >= 0.9 else 'fail'}">{pass_rate*100:.1f}%</div><div class="stat-label">通过率</div></div>
</div>

<div class="progress-bar">
  <div class="bar-pass" style="width:{bar_pass}"></div>
  <div class="bar-fail" style="width:{bar_fail}"></div>
  <div class="bar-error" style="width:{bar_error}"></div>
</div>

<div class="toolbar">
  <button class="filter-btn active" onclick="filterStatus('ALL',this)">全部 ({sent})</button>
  <button class="filter-btn" onclick="filterStatus('PASS',this)">✅ PASS ({success})</button>
  <button class="filter-btn" onclick="filterStatus('FAIL',this)">❌ FAIL ({fail})</button>
  <button class="filter-btn" onclick="filterStatus('ERROR',this)">⚠️ ERROR ({error})</button>
  <input class="search-box" type="text" placeholder="搜索接口路径…" oninput="filterSearch(this.value)">
  <span class="result-count" id="result-count">共 {sent} 条</span>
</div>

<table>
<thead>
  <tr>
    <th style="width:38%">接口</th>
    <th style="width:70px">状态</th>
    <th style="width:150px">差异</th>
    <th style="width:60px">状态码</th>
    <th style="width:70px">耗时(ms)</th>
    <th style="width:140px">回放时间</th>
    <th style="width:55px"></th>
  </tr>
</thead>
<tbody id="tbody">
{tbody}
</tbody>
</table>

<div class="footer">生成时间: {fmt_dt(datetime.utcnow())} UTC &nbsp;|&nbsp; 录制回放平台</div>

<script>
var currentStatus = 'ALL';
var currentSearch = '';

function toggle(id) {{
  var el = document.getElementById(id);
  var row = el.previousElementSibling;
  var hint = row.querySelector('.toggle-hint');
  if (el.style.display === 'none') {{
    el.style.display = '';
    hint.textContent = '▼ 收起';
  }} else {{
    el.style.display = 'none';
    hint.textContent = '▶ 展开';
  }}
}}

function filterStatus(status, btn) {{
  currentStatus = status;
  document.querySelectorAll('.filter-btn').forEach(function(b) {{ b.classList.remove('active'); }});
  btn.classList.add('active');
  applyFilter();
}}

function filterSearch(val) {{
  currentSearch = val.toLowerCase();
  applyFilter();
}}

function applyFilter() {{
  var rows = document.querySelectorAll('.data-row');
  var visible = 0;
  rows.forEach(function(row) {{
    var status = row.getAttribute('data-status');
    var path = row.querySelector('.path-text') ? row.querySelector('.path-text').textContent.toLowerCase() : '';
    var statusOk = currentStatus === 'ALL' || status === currentStatus;
    var searchOk = !currentSearch || path.indexOf(currentSearch) >= 0;
    var show = statusOk && searchOk;
    row.style.display = show ? '' : 'none';
    var detailId = row.getAttribute('onclick').replace("toggle('","").replace("')","");
    var detailRow = document.getElementById(detailId);
    if (detailRow) detailRow.style.display = 'none';
    if (show) visible++;
  }});
  document.getElementById('result-count').textContent = '显示 ' + visible + ' / ' + {sent} + ' 条';
}}
</script>
</body>
</html>"""

    from datetime import timezone, timedelta
    _CST = timezone(timedelta(hours=8))
    ts = (job.finished_at or job.created_at or datetime.utcnow()).replace(tzinfo=timezone.utc).astimezone(_CST).strftime("%Y%m%d-%H%M%S")
    import re as _re
    from urllib.parse import quote as _quote
    def _safe(s): return _re.sub(r'[\\/:*?"<>|\s]', '_', s)[:30]
    filename = f"replay-{_safe(app_name)}-{_safe(case_name)}-{ts}.html"
    # RFC 5987: encode UTF-8 filename for Content-Disposition header
    filename_encoded = _quote(filename, safe="-_.~")
    ascii_fallback = f"replay-report-{ts}.html"
    return HTMLResponse(
        content=html,
        headers={"Content-Disposition": f"attachment; filename=\"{ascii_fallback}\"; filename*=UTF-8''{filename_encoded}"},
    )


@router.get("/{job_id}/results/{result_id}", response_model=ReplayResultOut)
async def get_result(job_id: str, result_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.get(ReplayResult, result_id)
    if not r or r.job_id != job_id:
        raise HTTPException(404, "Result not found")
    return r


# ── Background replay worker ──────────────────────────────────────────────────

async def _run_replay_job(job_id: str):
    from database import async_session_factory

    # Phase 1: mark as RUNNING and load job data
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
            await db.commit()
            return

        result = await db.execute(
            select(TestCaseRecording)
            .where(TestCaseRecording.case_id == job.case_id)
            .order_by(TestCaseRecording.sort_order)
        )
        links = result.scalars().all()

        # Snapshot job fields needed by subtasks (avoid sharing session)
        job_id_snap = job.id
        job_delay = job.delay_ms
        job_ignore = job.ignore_fields or []
        job_diff_rules = job.diff_rules or []
        job_assertions = job.assertions or []
        job_override_host = job.override_host
        job_perf_threshold = job.perf_threshold_ms
        job_use_mocks = job.use_sub_invocation_mocks
        job_concurrency = job.concurrency or 1
        # P0-P1 新参数
        job_smart_noise = job.smart_noise_reduction
        job_header_transforms = job.header_transforms or []
        job_retry_count = job.retry_count or 0
        job_repeat_count = job.repeat_count or 1  # P0: 流量放大
        recording_ids = [lnk.recording_id for lnk in links]

    # P0: 流量放大 - 扩展录制列表
    expanded_recording_ids = []
    for rid in recording_ids:
        expanded_recording_ids.extend([rid] * job_repeat_count)
    
    # Phase 2: replay each recording with its own independent session
    sem = asyncio.Semaphore(job_concurrency)
    tasks = [
        _replay_one(job_id_snap, rid, target_app, sem, job_delay, job_ignore,
                    job_override_host, job_diff_rules, job_assertions, job_perf_threshold,
                    job_use_mocks, job_smart_noise, job_header_transforms, job_retry_count)
        for rid in expanded_recording_ids
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Phase 3: tally and finalize
    async with async_session_factory() as db:
        job = await db.get(ReplayJob, job_id)
        if job:
            # Handle both old string results and new tuple results for backward compatibility
            success = sum(1 for r in results if (isinstance(r, tuple) and r[0] == "PASS") or r == "PASS")
            # Only FAIL counted as fail; ERROR (network/infra) kept separate so
            # error_count = sent - success - fail is non-zero when errors occur.
            fail = sum(1 for r in results if (isinstance(r, tuple) and r[0] == "FAIL") or r == "FAIL")
            job.sent_count = len(expanded_recording_ids)
            job.success_count = success
            job.fail_count = fail
            job.status = "DONE"
            job.finished_at = datetime.utcnow()
            await db.commit()

            # Fire webhook / notification if configured
            if job.webhook_url:
                sent_n = len(recording_ids)
                _pass_rate = round(success / sent_n, 4) if sent_n else 0.0
                _error_count = max(sent_n - success - fail, 0)
                generic_payload = {
                    "job_id": job_id,
                    "status": "DONE",
                    "total_count": job.total_count,
                    "sent_count": sent_n,
                    "success_count": success,
                    "fail_count": fail,
                    "error_count": _error_count,
                    "pass_rate": _pass_rate,
                    "finished_at": job.finished_at.isoformat(),
                }
                notify_type = job.notify_type or "generic"
                emoji = "✅" if _pass_rate >= 0.9 else "❌"
                pct = f"{_pass_rate * 100:.1f}%"
                if notify_type == "dingtalk":
                    text = (
                        f"## {emoji} 回放任务完成\n\n"
                        f"- **通过率**: {pct}\n"
                        f"- **通过**: {success} &nbsp; **失败**: {fail} &nbsp; **错误**: {_error_count}\n"
                        f"- **总计**: {sent_n} 条 &nbsp; 任务ID: `{job_id[:8]}`"
                    )
                    send_payload = {
                        "msgtype": "markdown",
                        "markdown": {"title": f"回放完成 — 通过率 {pct}", "text": text},
                    }
                elif notify_type == "wecom":
                    text = (
                        f"## 回放任务完成 {emoji}\n"
                        f"> 通过率：**{pct}**\n"
                        f"> 通过：{success} | 失败：{fail} | 错误：{_error_count}\n"
                        f"> 总计：{sent_n} 条 | 任务ID：`{job_id[:8]}`"
                    )
                    send_payload = {
                        "msgtype": "markdown",
                        "markdown": {"content": text},
                    }
                else:
                    send_payload = generic_payload
                try:
                    import httpx
                    async with httpx.AsyncClient(timeout=10) as hx:
                        await hx.post(job.webhook_url, json=send_payload)
                except Exception as e:
                    print(f"[replay] webhook POST failed: {e}")


async def _replay_one(
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
    # P0-P1 新增参数
    smart_noise_reduction: bool = False,
    header_transforms: list | None = None,
    retry_count: int = 0,
) -> tuple[str, str, str]:
    from database import async_session_factory

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

            # Auto-fill XML request body when replay target app has xml_request_template.
            # Template can be a JSON map {"SERVICE_ID": "<xml>..."} or a plain XML string.
            if not send_body and method in ("POST", "PUT", "PATCH"):
                xml_tpl = getattr(target_app, 'xml_request_template', None)
                if xml_tpl and xml_tpl.strip():
                    matched_body = _match_xml_template(xml_tpl, recording.response_body, send_body)
                    if matched_body:
                        send_body = matched_body
                        if "Content-Type" not in headers:
                            headers["Content-Type"] = "application/xml"

            # P1: 应用请求头转换规则
            if header_transforms:
                headers = _apply_header_transforms(headers, header_transforms)

            # Resolve replay path: prefer full URI from request_body (preserves query params)
            from urllib.parse import urlparse
            uri = req_info.get("uri") or ""
            if uri.startswith("http"):
                parsed = urlparse(uri)
                replay_path = parsed.path + ("?" + parsed.query if parsed.query else "")
            elif uri and not uri.upper() in {"GET","POST","PUT","DELETE","PATCH","HEAD","OPTIONS"}:
                replay_path = uri
            else:
                replay_path = recording.path or "/"

            # P1: 失败重试逻辑
            final_status = None
            last_error = None
            for attempt in range(max(1, retry_count + 1)):  # 至少执行1次
                if attempt > 0:
                    # 重试前等待一小段时间
                    await asyncio.sleep(0.5 * attempt)
                
                try:
                    # When mock mode is on AND the recording has a trace_id + sub_invocations,
                    # route through the Repeater agent so downstream calls (DB/RPC/Redis)
                    # are intercepted and served from the recorded responses.
                    # Fall back to direct HTTP if the agent call fails.
                    if use_sub_invocation_mocks and recording.trace_id and recording.sub_invocations:
                        # AREX mock replay: preload sub-invocation mocks into Redis, then HTTP with arex-record-id header
                        arex = ArexClient(settings.arex_storage_url)
                        try:
                            await arex.cache_load_mock(recording.trace_id)
                        except ArexClientError as e:
                            print(f"[replay] cache_load_mock failed (non-fatal): {e}")

                        # Inject arex-record-id header so arex-agent mocks sub-calls
                        mock_headers = dict(headers)
                        mock_headers["arex-record-id"] = recording.trace_id

                        # Determine target host
                        host = override_host or f"http://{target_app.ssh_host}:{target_app.sandbox_port}"
                        url = host.rstrip("/") + replay_path
                        try:
                            async with httpx.AsyncClient(timeout=30.0) as client:
                                resp = await client.request(method, url, content=send_body, headers=mock_headers)
                            replay_resp = {
                                "body": resp.text,
                                "status_code": resp.status_code,
                                "error": None,
                            }
                        except httpx.RequestError as e:
                            replay_resp = {"body": None, "status_code": None, "error": str(e)}

                        # Clean up Redis cache
                        try:
                            await arex.cache_remove_mock(recording.trace_id)
                        except ArexClientError:
                            pass  # Non-fatal cleanup failure
                    else:
                        # Direct HTTP replay (no mocking)
                        host = override_host or f"http://{target_app.ssh_host}:{target_app.sandbox_port}"
                        url = host.rstrip("/") + replay_path
                        try:
                            async with httpx.AsyncClient(timeout=30.0) as client:
                                resp = await client.request(method, url, content=send_body, headers=headers)
                            replay_resp = {
                                "body": resp.text,
                                "status_code": resp.status_code,
                                "error": None,
                            }
                        except httpx.RequestError as e:
                            replay_resp = {"body": None, "status_code": None, "error": str(e)}

                    replayed_body = replay_resp.get("body")
                    replayed_status_code = replay_resp.get("status_code")
                    error_msg = replay_resp.get("error")
                    
                    # 检查是否成功（无错误且有响应）
                    if not error_msg:
                        final_status = "SUCCESS"
                        break  # 成功则退出重试循环
                    
                    # 如果还有重试次数，继续
                    last_error = error_msg
                    
                except Exception as e:
                    last_error = str(e)
                    if attempt < retry_count:
                        continue
                    error_msg = last_error
            
            # 如果所有重试都失败
            if final_status != "SUCCESS" and last_error:
                error_msg = last_error

            ignore_patterns = [rf".*\['{f}'\].*" for f in ignore_fields]
            # P0: 传递 smart_noise_reduction 参数
            diff_json, diff_score = compute_diff(
                recording.response_body, replayed_body,
                ignore_patterns, diff_rules or [],
                smart_noise_reduction=smart_noise_reduction
            )

            # Evaluate assertions
            if assertions:
                assertion_results = evaluate_assertions(
                    assertions, replayed_body, replayed_status_code, diff_score
                )

            # Performance threshold check — only fires on successful HTTP calls (not errors)
            # Fix Bug 4: skip perf check when request itself failed
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

        except Exception as e:
            status = "ERROR"
            if not error_msg:
                error_msg = str(e)

        duration_ms = int((datetime.utcnow() - start).total_seconds() * 1000)

        # Analyze failure reason
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


# ── P2-2: 保存回放结果为测试用例 ───────────────────────────────────────────────

class SaveToTestCaseRequest(BaseModel):
    case_name: str
    case_description: str | None = None
    recording_ids: list[str]  # 要保存的录制ID列表


@router.post("/{job_id}/save-to-testcase", response_model=dict)
async def save_replay_results_to_testcase(
    job_id: str,
    body: SaveToTestCaseRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    P2-2: 将回放失败的录制保存为测试用例。
    创建一个新测试用例，并将选中的录制添加到用例中。
    """
    job = await db.get(ReplayJob, job_id)
    if not job:
        raise HTTPException(404, "Replay job not found")

    # 创建新测试用例
    test_case = TestCase(
        id=str(uuid.uuid4()),
        name=body.case_name,
        description=body.case_description or f"从回放任务 {job_id[:8]} 导入",
        app_id=job.target_app_id,
        created_by=job.created_by,
    )
    db.add(test_case)

    # 添加选中的录制
    added_count = 0
    for idx, recording_id in enumerate(body.recording_ids):
        # 检查录制是否存在
        recording = await db.get(Recording, recording_id)
        if not recording:
            continue

        link = TestCaseRecording(
            id=str(uuid.uuid4()),
            case_id=test_case.id,
            recording_id=recording_id,
            sort_order=idx,
        )
        db.add(link)
        added_count += 1

    if added_count == 0:
        raise HTTPException(400, "没有有效的录制可添加")

    # 更新用例的录制数量
    test_case.recording_count = added_count

    await db.commit()
    await db.refresh(test_case)

    return {
        "test_case_id": test_case.id,
        "test_case_name": test_case.name,
        "added_count": added_count,
    }
