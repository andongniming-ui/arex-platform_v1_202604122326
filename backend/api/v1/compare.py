"""
A/B environment comparison — replay the same test case against two applications
and compare their responses against each other and against the original recording.
"""
import asyncio
import uuid
import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete, or_
from sqlalchemy.orm import aliased
from database import get_db
from models.compare import CompareRun, CompareResult
from models.test_case import TestCase, TestCaseRecording
from models.recording import Recording
from models.application import Application
from schemas.compare import CompareRequest, CompareRunOut, CompareResultOut
from services.compare_service import run_compare as _run_compare
from utils.diff import compute_diff

router = APIRouter(prefix="/compare", tags=["compare"])

_background_tasks: set = set()

def _fire(coro):
    task = asyncio.create_task(coro)
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)


# ── CRUD / list ───────────────────────────────────────────────────────────────

@router.post("", response_model=CompareRunOut, status_code=201)
async def create_compare_run(body: CompareRequest, db: AsyncSession = Depends(get_db)):
    tc = await db.get(TestCase, body.case_id)
    if not tc:
        raise HTTPException(404, "Test case not found")
    app_a = await db.get(Application, body.app_a_id)
    if not app_a:
        raise HTTPException(404, "Application A not found")
    app_b = await db.get(Application, body.app_b_id)
    if not app_b:
        raise HTTPException(404, "Application B not found")

    # Validate recordings exist
    has_recs = await db.execute(
        select(TestCaseRecording).where(TestCaseRecording.case_id == body.case_id).limit(1)
    )
    if not has_recs.scalars().first():
        raise HTTPException(400, "Test case has no recordings")

    run = CompareRun(
        id=str(uuid.uuid4()),
        name=body.name,
        case_id=body.case_id,
        app_a_id=body.app_a_id,
        app_b_id=body.app_b_id,
        ignore_fields=body.ignore_fields,
        diff_rules=body.diff_rules,
        status="RUNNING",
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)

    _fire(_run_compare(run.id, body))
    return run


@router.get("", response_model=dict)
async def list_compare_runs(
    keyword: str | None = None,
    case_id: str | None = None,
    app_id: str | None = None,
    status: str | None = None,
    created_after: datetime | None = None,
    created_before: datetime | None = None,
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    app_a = aliased(Application)
    app_b = aliased(Application)
    base = (
        select(CompareRun)
        .join(TestCase, TestCase.id == CompareRun.case_id, isouter=True)
        .join(app_a, app_a.id == CompareRun.app_a_id, isouter=True)
        .join(app_b, app_b.id == CompareRun.app_b_id, isouter=True)
    )
    if keyword:
        like = f"%{keyword}%"
        base = base.where(
            or_(
                CompareRun.name.ilike(like),
                TestCase.name.ilike(like),
                app_a.name.ilike(like),
                app_b.name.ilike(like),
            )
        )
    if case_id:
        base = base.where(CompareRun.case_id == case_id)
    if app_id:
        base = base.where((CompareRun.app_a_id == app_id) | (CompareRun.app_b_id == app_id))
    if status:
        base = base.where(CompareRun.status == status)
    if created_after:
        base = base.where(CompareRun.created_at >= created_after)
    if created_before:
        base = base.where(CompareRun.created_at <= created_before)
    total = (await db.execute(select(func.count()).select_from(base.subquery()))).scalar() or 0
    items = (await db.execute(base.order_by(CompareRun.created_at.desc()).offset(offset).limit(limit))).scalars().all()
    return {"items": [CompareRunOut.model_validate(i) for i in items], "total": total}


@router.get("/{run_id}", response_model=CompareRunOut)
async def get_compare_run(run_id: str, db: AsyncSession = Depends(get_db)):
    run = await db.get(CompareRun, run_id)
    if not run:
        raise HTTPException(404, "Compare run not found")
    return run


@router.delete("/batch", status_code=204)
async def batch_delete_compare_runs(body: dict, db: AsyncSession = Depends(get_db)):
    """Delete multiple compare runs by ID. Body: {"ids": [...]}"""
    ids = body.get("ids") or []
    if not ids:
        return
    await db.execute(delete(CompareResult).where(CompareResult.run_id.in_(ids)))
    await db.execute(delete(CompareRun).where(CompareRun.id.in_(ids)))
    await db.commit()


@router.delete("/{run_id}", status_code=204)
async def delete_compare_run(run_id: str, db: AsyncSession = Depends(get_db)):
    run = await db.get(CompareRun, run_id)
    if not run:
        raise HTTPException(404, "Compare run not found")
    await db.delete(run)
    await db.commit()


@router.get("/{run_id}/results", response_model=dict)
async def list_compare_results(
    run_id: str,
    path_contains: str | None = None,
    agreement: str | None = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    base = select(CompareResult).where(CompareResult.run_id == run_id)
    if path_contains:
        base = base.where(CompareResult.path.ilike(f"%{path_contains}%"))
    if agreement == "agreed":
        base = base.where(CompareResult.status_a == CompareResult.status_b)
    elif agreement == "diverged":
        base = base.where(CompareResult.status_a != CompareResult.status_b)
    total = (await db.execute(select(func.count()).select_from(base.subquery()))).scalar() or 0
    q = (
        select(CompareResult, Recording.request_body, Recording.response_body)
        .join(Recording, Recording.id == CompareResult.recording_id, isouter=True)
        .where(CompareResult.run_id == run_id)
        .order_by(CompareResult.created_at)
        .offset(offset)
        .limit(limit)
    )
    if path_contains:
        q = q.where(CompareResult.path.ilike(f"%{path_contains}%"))
    if agreement == "agreed":
        q = q.where(CompareResult.status_a == CompareResult.status_b)
    elif agreement == "diverged":
        q = q.where(CompareResult.status_a != CompareResult.status_b)
    rows = (await db.execute(q)).all()
    from api.v1.replays import _extract_service_id
    out = []
    for cr, req_body, resp_body in rows:
        d = CompareResultOut.model_validate(cr)
        raw_xml = None
        if req_body:
            try:
                raw_xml = json.loads(req_body).get("body")
            except Exception:
                pass
        d.service_id = _extract_service_id(raw_xml) or _extract_service_id(resp_body)
        out.append(d)
    return {"items": out, "total": total}
# ── HTML Report ────────────────────────────────────────────────────────────────

@router.get("/{run_id}/report", response_class=HTMLResponse)
async def get_compare_report(run_id: str, db: AsyncSession = Depends(get_db)):
    """Generate a self-contained HTML report for a double-environment compare run."""
    from html import escape as he

    run = await db.get(CompareRun, run_id)
    if not run:
        raise HTTPException(404, "Compare run not found")

    tc = await db.get(TestCase, run.case_id) if run.case_id else None
    app_a = await db.get(Application, run.app_a_id) if run.app_a_id else None
    app_b = await db.get(Application, run.app_b_id) if run.app_b_id else None
    case_name = tc.name if tc else (run.case_id or "-")
    app_a_name = app_a.name if app_a else (run.app_a_id or "-")
    app_b_name = app_b.name if app_b else (run.app_b_id or "-")

    q = (
        select(CompareResult, Recording.path, Recording.entry_type, Recording.request_body)
        .join(Recording, Recording.id == CompareResult.recording_id, isouter=True)
        .where(CompareResult.run_id == run_id)
        .order_by(CompareResult.created_at)
    )
    rows = (await db.execute(q)).all()

    total = run.total_count or 0
    agreed = run.agreed_count or 0
    diverged = run.diverged_count or 0
    agree_rate = agreed / total if total else 0.0

    def fmt_dt(dt):
        return dt.strftime("%Y-%m-%d %H:%M:%S") if dt else "-"

    def fmt_json(text):
        if not text:
            return ""
        try:
            return json.dumps(json.loads(text), indent=2, ensure_ascii=False)
        except Exception:
            return text

    def extract_service_id(xml_str):
        if not xml_str:
            return None
        try:
            import re
            m = re.search(r'<service_id>\s*([^<]+)\s*</service_id>', xml_str)
            return m.group(1).strip() if m else None
        except Exception:
            return None

    ignore_str = he(', '.join(run.ignore_fields) if run.ignore_fields else '无')
    diff_rules_str = he(f"{len(run.diff_rules)} 条规则" if run.diff_rules else '无')
    run_name_str = he(run.name or run_id[:8])
    status_label = {'DONE': '已完成', 'FAILED': '失败', 'RUNNING': '运行中'}.get(run.status, run.status)
    status_color = {'DONE': '#18a058', 'FAILED': '#d03050', 'RUNNING': '#1677ff'}.get(run.status, '#999')

    tbody = ""
    for idx, (cr, path, entry_type, req_body) in enumerate(rows):
        rid = f"row_{idx}"
        is_agreed = cr.status_a == cr.status_b
        consist_label = "一致" if is_agreed else "差异"
        consist_color = "#18a058" if is_agreed else "#d03050"
        consist_data = "agreed" if is_agreed else "diverged"

        sa = cr.status_a or "ERROR"
        sb = cr.status_b or "ERROR"
        sa_color = {"PASS": "#18a058", "FAIL": "#d03050", "ERROR": "#f0a020"}.get(sa, "#999")
        sb_color = {"PASS": "#18a058", "FAIL": "#d03050", "ERROR": "#f0a020"}.get(sb, "#999")

        safe_path = he(path or "-")
        safe_type = he(entry_type or "HTTP")

        raw_xml = None
        if req_body:
            try:
                raw_xml = json.loads(req_body).get("body")
            except Exception:
                pass
        svc_id = extract_service_id(raw_xml)
        svc_html = f'<div class="svc-id">{he(svc_id)}</div>' if svc_id else ""

        score_a = f"{cr.diff_score_a:.3f}" if cr.diff_score_a is not None else "-"
        score_b = f"{cr.diff_score_b:.3f}" if cr.diff_score_b is not None else "-"
        score_ab = f"{cr.diff_score_a_vs_b:.3f}" if cr.diff_score_a_vs_b is not None else "-"
        dur_a = f"{cr.duration_a_ms} ms" if cr.duration_a_ms is not None else "-"
        dur_b = f"{cr.duration_b_ms} ms" if cr.duration_b_ms is not None else "-"

        resp_a_fmt = he(fmt_json(cr.resp_a))
        resp_b_fmt = he(fmt_json(cr.resp_b))
        req_fmt = he(fmt_json(raw_xml) if raw_xml else (fmt_json(req_body) if req_body else ""))

        # A vs B diff detail
        diff_ab_html = ""
        if cr.diff_a_vs_b:
            try:
                d = json.loads(cr.diff_a_vs_b)
                lines = []
                for change_type, changes in d.items():
                    if isinstance(changes, dict):
                        for field_path, detail in changes.items():
                            lines.append(
                                f'<div class="diff-line">'
                                f'<span class="diff-key">{he(str(field_path))}</span>'
                                f'<span class="diff-val">{he(json.dumps(detail, ensure_ascii=False)[:300])}</span>'
                                f'</div>'
                            )
                diff_ab_html = "\n".join(lines) if lines else '<span style="color:#999">无结构差异</span>'
            except Exception:
                diff_ab_html = f'<pre>{he(str(cr.diff_a_vs_b)[:500])}</pre>'

        tbody += f"""
  <tr class="data-row" data-consist="{consist_data}" onclick="toggle('{rid}')">
    <td>
      <span class="type-badge">{safe_type}</span><span class="path-text">{safe_path}</span>
      {svc_html}
    </td>
    <td><span class="status-badge" style="color:{sa_color}">{sa}</span><br><span class="mono small">{score_a}</span></td>
    <td><span class="status-badge" style="color:{sb_color}">{sb}</span><br><span class="mono small">{score_b}</span></td>
    <td class="mono">{score_ab}</td>
    <td><span class="consist-badge" style="color:{consist_color}">{consist_label}</span></td>
    <td class="mono small">{dur_a} / {dur_b}</td>
    <td class="toggle-hint">▶ 展开</td>
  </tr>
  <tr id="{rid}" class="detail-row" style="display:none">
    <td colspan="7">
      <div class="detail-wrap">
        {"<div class='detail-section'><div class='detail-title'>📤 请求体（录制时）</div><pre>" + req_fmt + "</pre></div>" if req_fmt else ""}
        <div class="detail-cols">
          <div class="detail-section">
            <div class="detail-title">📱 应用 A 响应 <span class="app-tag app-tag-a">{he(app_a_name)}</span><span class="detail-meta">{sa} · {dur_a} · diff {score_a}</span></div>
            <pre>{resp_a_fmt or '<span style="color:#999">（无数据）</span>'}</pre>
          </div>
          <div class="detail-section">
            <div class="detail-title">📱 应用 B 响应 <span class="app-tag app-tag-b">{he(app_b_name)}</span><span class="detail-meta">{sb} · {dur_b} · diff {score_b}</span></div>
            <pre>{resp_b_fmt or '<span style="color:#999">（无数据）</span>'}</pre>
          </div>
        </div>
        {"<div class='detail-section diff-section'><div class='detail-title'>🔍 A vs B 差异明细 <span class='detail-meta'>diff score: " + score_ab + "</span></div>" + diff_ab_html + "</div>" if diff_ab_html else ""}
      </div>
    </td>
  </tr>"""

    bar_agree = f"{agree_rate * 100:.1f}%"
    bar_diverge = f"{((diverged / total) * 100) if total else 0:.1f}%"

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>双环境对比报告 · {he(app_a_name)} vs {he(app_b_name)} · {he(case_name)}</title>
<style>
  *{{box-sizing:border-box}}
  body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;margin:0;padding:24px;background:#f0f2f5;color:#333;}}
  .report-header{{background:#fff;border-radius:10px;padding:16px 24px;margin-bottom:20px;box-shadow:0 1px 4px rgba(0,0,0,.08);border-left:4px solid #722ed1;}}
  .report-title{{font-size:20px;font-weight:700;margin:0 0 10px;color:#1a1a1a;}}
  .report-breadcrumb{{font-size:13px;color:#888;display:flex;align-items:center;gap:6px;flex-wrap:wrap;line-height:2;}}
  .breadcrumb-app{{font-weight:600;}}
  .app-a-label{{color:#1677ff;}}
  .app-b-label{{color:#722ed1;}}
  .breadcrumb-sep{{color:#ccc;}}
  .breadcrumb-case{{color:#333;font-weight:600;}}
  .ignore-fields-block{{margin-top:8px;padding:7px 12px;background:#fdf6ff;border:1px solid #e9d8fd;border-radius:6px;font-size:13px;display:flex;align-items:baseline;gap:8px;flex-wrap:wrap;}}
  .ignore-label{{font-weight:600;color:#722ed1;white-space:nowrap;}}
  .ignore-tag{{display:inline-block;background:#f0e6ff;color:#531dab;border-radius:4px;padding:1px 8px;font-size:12px;font-family:monospace;margin:2px 2px;}}
  .ignore-none{{color:#999;font-style:italic;}}
  .stats{{display:flex;flex-wrap:wrap;gap:16px;margin-bottom:20px;}}
  .stat-box{{background:#fff;border-radius:10px;padding:16px 24px;min-width:110px;box-shadow:0 1px 4px rgba(0,0,0,.08);text-align:center;}}
  .stat-num{{font-size:30px;font-weight:700;line-height:1.2;}}
  .stat-label{{font-size:12px;color:#888;margin-top:4px;}}
  .agreed{{color:#18a058}}.diverged{{color:#d03050}}.info-color{{color:#1677ff}}
  .progress-bar{{display:flex;height:10px;border-radius:5px;overflow:hidden;margin-bottom:20px;background:#e8e8e8;}}
  .bar-agreed{{background:#18a058}}.bar-diverged{{background:#d03050}}
  .toolbar{{display:flex;align-items:center;gap:10px;margin-bottom:12px;flex-wrap:wrap;}}
  .filter-btn{{padding:5px 14px;border:1px solid #ddd;border-radius:20px;cursor:pointer;font-size:13px;background:#fff;transition:all .15s;}}
  .filter-btn:hover,.filter-btn.active{{background:#722ed1;color:#fff;border-color:#722ed1;}}
  .search-box{{padding:5px 12px;border:1px solid #ddd;border-radius:20px;font-size:13px;outline:none;width:240px;}}
  .search-box:focus{{border-color:#722ed1;}}
  .result-count{{font-size:12px;color:#888;margin-left:auto;}}
  table{{width:100%;border-collapse:collapse;background:#fff;border-radius:10px;overflow:hidden;box-shadow:0 1px 4px rgba(0,0,0,.08);font-size:13px;}}
  th{{background:#fafafa;padding:10px 14px;text-align:left;font-weight:600;border-bottom:2px solid #f0f0f0;color:#555;}}
  .data-row td{{padding:9px 14px;border-bottom:1px solid #f5f5f5;vertical-align:middle;cursor:pointer;}}
  .data-row:hover td{{background:#faf5ff!important;}}
  .detail-row td{{padding:0;border-bottom:1px solid #e8e8e8;}}
  .detail-wrap{{padding:16px 20px;background:#fafafa;border-top:2px solid #e8e8e8;}}
  .detail-cols{{display:grid;grid-template-columns:1fr 1fr;gap:16px;}}
  .detail-section{{margin-bottom:12px;}}
  .detail-title{{font-size:12px;font-weight:600;color:#555;margin-bottom:6px;padding-bottom:4px;border-bottom:1px solid #e8e8e8;display:flex;align-items:center;gap:6px;flex-wrap:wrap;}}
  .detail-meta{{color:#999;font-weight:400;font-size:11px;}}
  .diff-section{{background:#fff;border:1px solid #ffe7ba;border-radius:6px;padding:10px;}}
  .diff-line{{padding:3px 0;border-bottom:1px solid #f5f5f5;font-size:12px;display:flex;gap:8px;}}
  .diff-key{{color:#d03050;font-weight:600;font-family:monospace;min-width:180px;flex-shrink:0;}}
  .diff-val{{color:#333;font-family:monospace;word-break:break-all;}}
  pre{{margin:0;background:#f8f8f8;border:1px solid #eee;border-radius:6px;padding:10px;font-size:12px;font-family:"SFMono-Regular",Consolas,monospace;white-space:pre-wrap;word-break:break-all;max-height:320px;overflow-y:auto;}}
  .type-badge{{display:inline-block;padding:1px 6px;border-radius:4px;font-size:11px;font-weight:700;background:#f0e6ff;color:#722ed1;margin-right:8px;vertical-align:middle;}}
  .path-text{{font-family:monospace;font-size:13px;}}
  .svc-id{{font-size:11px;color:#888;margin-top:3px;font-family:monospace;letter-spacing:0.5px;padding-left:2px;}}
  .status-badge{{font-weight:700;font-size:13px;}}
  .consist-badge{{font-weight:700;font-size:13px;}}
  .app-tag{{display:inline-block;padding:1px 7px;border-radius:4px;font-size:11px;font-weight:600;}}
  .app-tag-a{{background:#e8f4ff;color:#1677ff;}}
  .app-tag-b{{background:#f0e6ff;color:#722ed1;}}
  .mono{{font-family:monospace;font-size:12px;}}
  .small{{font-size:11px;color:#888;}}
  .toggle-hint{{color:#aaa;font-size:12px;user-select:none;text-align:right;}}
  .footer{{margin-top:20px;font-size:12px;color:#aaa;text-align:center;}}
  @media(max-width:700px){{.detail-cols{{grid-template-columns:1fr;}}}}
</style>
</head>
<body>

<div class="report-header">
  <div class="report-title">双环境对比测试报告</div>
  <div class="report-breadcrumb">
    <span class="breadcrumb-app app-a-label">🅰 {he(app_a_name)}</span>
    <span class="breadcrumb-sep">vs</span>
    <span class="breadcrumb-app app-b-label">🅱 {he(app_b_name)}</span>
    <span class="breadcrumb-sep">|</span>
    <span class="breadcrumb-case">📋 {he(case_name)}</span>
    <span class="breadcrumb-sep">|</span>
    <span>对比名称: <b>{run_name_str}</b></span>
    <span class="breadcrumb-sep">|</span>
    <span>状态: <b style="color:{status_color}">{status_label}</b></span>
    <span class="breadcrumb-sep">|</span>
    <span>开始: {fmt_dt(run.created_at)}</span>
    <span class="breadcrumb-sep">|</span>
    <span>结束: {fmt_dt(run.finished_at)}</span>
    <span class="breadcrumb-sep">|</span>
    <span>差异规则: {diff_rules_str}</span>
  </div>
  <div class="ignore-fields-block">
    <span class="ignore-label">🚫 忽略字段</span>
    {''.join(f'<span class="ignore-tag">{he(f)}</span>' for f in run.ignore_fields) if run.ignore_fields else '<span class="ignore-none">无（未配置忽略字段）</span>'}
  </div>
</div>

<div class="stats">
  <div class="stat-box"><div class="stat-num info-color">{total}</div><div class="stat-label">总接口数</div></div>
  <div class="stat-box"><div class="stat-num agreed">{agreed}</div><div class="stat-label">一致 AGREED</div></div>
  <div class="stat-box"><div class="stat-num diverged">{diverged}</div><div class="stat-label">差异 DIVERGED</div></div>
  <div class="stat-box"><div class="stat-num {'agreed' if agree_rate >= 0.9 else 'diverged'}">{agree_rate * 100:.1f}%</div><div class="stat-label">一致率</div></div>
</div>

<div class="progress-bar">
  <div class="bar-agreed" style="width:{bar_agree}"></div>
  <div class="bar-diverged" style="width:{bar_diverge}"></div>
</div>

<div class="toolbar">
  <button class="filter-btn active" onclick="filterConsist('ALL',this)">全部 ({total})</button>
  <button class="filter-btn" onclick="filterConsist('agreed',this)">✅ 一致 ({agreed})</button>
  <button class="filter-btn" onclick="filterConsist('diverged',this)">❌ 差异 ({diverged})</button>
  <input class="search-box" type="text" placeholder="搜索接口路径 / service_id…" oninput="filterSearch(this.value)">
  <span class="result-count" id="result-count">共 {total} 条</span>
</div>

<table>
<thead>
  <tr>
    <th style="width:32%">接口</th>
    <th style="width:110px">应用 A 状态<br><span style="font-weight:400;font-size:11px;color:#999">/ 差异分</span></th>
    <th style="width:110px">应用 B 状态<br><span style="font-weight:400;font-size:11px;color:#999">/ 差异分</span></th>
    <th style="width:80px">A vs B</th>
    <th style="width:80px">一致性</th>
    <th style="width:130px">耗时 A / B</th>
    <th style="width:55px"></th>
  </tr>
</thead>
<tbody id="tbody">
{tbody}
</tbody>
</table>

<div class="footer">生成时间: {fmt_dt(datetime.utcnow())} UTC &nbsp;|&nbsp; 录制回放平台 · 双环境对比报告</div>

<script>
var currentConsist = 'ALL';
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

function filterConsist(consist, btn) {{
  currentConsist = consist;
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
    var consist = row.getAttribute('data-consist');
    var pathEl = row.querySelector('.path-text');
    var svcEl = row.querySelector('.svc-id');
    var pathText = (pathEl ? pathEl.textContent : '').toLowerCase();
    var svcText = (svcEl ? svcEl.textContent : '').toLowerCase();
    var consistOk = currentConsist === 'ALL' || consist === currentConsist;
    var searchOk = !currentSearch || pathText.indexOf(currentSearch) >= 0 || svcText.indexOf(currentSearch) >= 0;
    var show = consistOk && searchOk;
    row.style.display = show ? '' : 'none';
    var detailId = row.getAttribute('onclick').replace("toggle('","").replace("')","");
    var detailRow = document.getElementById(detailId);
    if (detailRow) detailRow.style.display = 'none';
    if (show) visible++;
  }});
  document.getElementById('result-count').textContent = '显示 ' + visible + ' / {total} 条';
}}
</script>
</body>
</html>"""

    from datetime import timezone, timedelta
    import re as _re
    from urllib.parse import quote as _quote
    _CST = timezone(timedelta(hours=8))
    ts = (run.finished_at or run.created_at or datetime.utcnow()).replace(tzinfo=timezone.utc).astimezone(_CST).strftime("%Y%m%d-%H%M%S")
    def _safe(s): return _re.sub(r'[\\/:*?"<>|\s]', '_', s)[:24]
    filename = f"compare-{_safe(app_a_name)}-vs-{_safe(app_b_name)}-{_safe(case_name)}-{ts}.html"
    filename_encoded = _quote(filename, safe="-_.~")
    ascii_fallback = f"compare-report-{ts}.html"
    return HTMLResponse(
        content=html,
        headers={"Content-Disposition": f"attachment; filename=\"{ascii_fallback}\"; filename*=UTF-8''{filename_encoded}"},
    )
