import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func, update as sql_update
from database import get_db
from models.test_case import TestCase, TestCaseRecording
from models.recording import Recording
from schemas.test_case import TestCaseCreate, TestCaseUpdate, TestCaseOut, AddRecordingsRequest

router = APIRouter(prefix="/test-cases", tags=["test-cases"])


@router.post("", response_model=TestCaseOut, status_code=201)
async def create_test_case(body: TestCaseCreate, db: AsyncSession = Depends(get_db)):
    tc = TestCase(id=str(uuid.uuid4()), **body.model_dump())
    db.add(tc)
    await db.commit()
    await db.refresh(tc)
    return tc


@router.get("", response_model=dict)
async def list_test_cases(
    app_id: str | None = None,
    tag: str | None = None,
    created_after: datetime | None = None,
    created_before: datetime | None = None,
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import cast, String
    base = select(TestCase).where(TestCase.status == "ACTIVE")
    if app_id:
        base = base.where(TestCase.app_id == app_id)
    if tag:
        base = base.where(cast(TestCase.tags, String).ilike(f'%"{tag}"%'))
    if created_after:
        base = base.where(TestCase.created_at >= created_after)
    if created_before:
        base = base.where(TestCase.created_at <= created_before)
    total = (await db.execute(select(func.count()).select_from(base.subquery()))).scalar() or 0
    result = await db.execute(base.order_by(TestCase.created_at.desc()).offset(offset).limit(limit))
    cases = result.scalars().all()
    # Sync recording_count in one batch query instead of N+1
    if cases:
        ids = [tc.id for tc in cases]
        cnt_result = await db.execute(
            select(TestCaseRecording.case_id, func.count().label("cnt"))
            .where(TestCaseRecording.case_id.in_(ids))
            .group_by(TestCaseRecording.case_id)
        )
        counts = {row.case_id: row.cnt for row in cnt_result}
        changed = False
        for tc in cases:
            actual = counts.get(tc.id, 0)
            if tc.recording_count != actual:
                tc.recording_count = actual
                changed = True
        if changed:
            await db.commit()
    return {"items": [TestCaseOut.model_validate(tc) for tc in cases], "total": total}


@router.get("/{case_id}", response_model=TestCaseOut)
async def get_test_case(case_id: str, db: AsyncSession = Depends(get_db)):
    tc = await db.get(TestCase, case_id)
    if not tc or tc.status == "DELETED":
        raise HTTPException(404, "Test case not found")
    # Sync recording_count with actual rows
    result = await db.execute(
        select(func.count()).where(TestCaseRecording.case_id == case_id)
    )
    actual = result.scalar() or 0
    if tc.recording_count != actual:
        tc.recording_count = actual
        await db.commit()
    return tc


@router.put("/{case_id}", response_model=TestCaseOut)
async def update_test_case(
    case_id: str, body: TestCaseUpdate, db: AsyncSession = Depends(get_db)
):
    tc = await db.get(TestCase, case_id)
    if not tc:
        raise HTTPException(404, "Test case not found")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(tc, field, value)
    tc.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(tc)
    return tc


@router.delete("/batch", status_code=204)
async def batch_delete_test_cases(body: dict, db: AsyncSession = Depends(get_db)):
    """Soft-delete multiple test cases by ID. Body: {"ids": [...]}"""
    ids = body.get("ids") or []
    if not ids:
        return
    await db.execute(
        sql_update(TestCase).where(TestCase.id.in_(ids)).values(status="DELETED")
    )
    await db.commit()


@router.delete("/{case_id}", status_code=204)
async def delete_test_case(case_id: str, db: AsyncSession = Depends(get_db)):
    tc = await db.get(TestCase, case_id)
    if not tc:
        raise HTTPException(404, "Test case not found")
    tc.status = "DELETED"
    await db.commit()


@router.post("/{case_id}/clone", response_model=TestCaseOut, status_code=201)
async def clone_test_case(case_id: str, db: AsyncSession = Depends(get_db)):
    """Clone a test case (metadata + all recording links)."""
    src = await db.get(TestCase, case_id)
    if not src:
        raise HTTPException(404, "Test case not found")

    new_id = str(uuid.uuid4())
    clone = TestCase(
        id=new_id,
        name=f"{src.name} (副本)",
        description=src.description,
        app_id=src.app_id,
        tags=list(src.tags) if src.tags else None,
        recording_count=0,
    )
    db.add(clone)

    # Copy recording links
    result = await db.execute(
        select(TestCaseRecording).where(TestCaseRecording.case_id == case_id)
        .order_by(TestCaseRecording.sort_order)
    )
    links = result.scalars().all()
    for lnk in links:
        db.add(TestCaseRecording(
            id=str(uuid.uuid4()),
            case_id=new_id,
            recording_id=lnk.recording_id,
            sort_order=lnk.sort_order,
        ))
    clone.recording_count = len(links)
    await db.commit()
    await db.refresh(clone)
    return clone


@router.post("/{case_id}/recordings", response_model=dict)
async def add_recordings(
    case_id: str, body: AddRecordingsRequest, db: AsyncSession = Depends(get_db)
):
    tc = await db.get(TestCase, case_id)
    if not tc:
        raise HTTPException(404, "Test case not found")

    # 查询已有最大 sort_order，新条目从此后追加
    max_order_result = await db.execute(
        select(func.max(TestCaseRecording.sort_order)).where(TestCaseRecording.case_id == case_id)
    )
    max_order = max_order_result.scalar() or -1

    added = 0
    for i, rec_id in enumerate(body.recording_ids):
        rec = await db.get(Recording, rec_id)
        if not rec:
            continue
        # Check duplicate
        existing = await db.execute(
            select(TestCaseRecording).where(
                TestCaseRecording.case_id == case_id,
                TestCaseRecording.recording_id == rec_id,
            )
        )
        if existing.scalar_one_or_none():
            continue
        link = TestCaseRecording(
            id=str(uuid.uuid4()),
            case_id=case_id,
            recording_id=rec_id,
            sort_order=max_order + 1 + added,
        )
        db.add(link)
        rec.status = "ADDED_TO_CASE"
        added += 1

    if added:
        await db.execute(
            sql_update(TestCase)
            .where(TestCase.id == case_id)
            .values(recording_count=TestCase.recording_count + added, updated_at=datetime.utcnow())
        )
    await db.commit()
    return {"added": added}


@router.get("/{case_id}/recordings", response_model=list)
async def get_case_recordings(case_id: str, db: AsyncSession = Depends(get_db)):
    """Return recordings associated with this test case, ordered by sort_order."""
    tc = await db.get(TestCase, case_id)
    if not tc:
        raise HTTPException(404, "Test case not found")
    result = await db.execute(
        select(Recording, TestCaseRecording.sort_order)
        .join(TestCaseRecording, TestCaseRecording.recording_id == Recording.id)
        .where(TestCaseRecording.case_id == case_id)
        .order_by(TestCaseRecording.sort_order)
    )
    rows = result.all()
    out = []
    for rec, sort_order in rows:
        d = {c.name: getattr(rec, c.name) for c in rec.__table__.columns}
        d["sort_order"] = sort_order
        out.append(d)
    return out


@router.get("/{case_id}/suggest-ignore", response_model=dict)
async def suggest_ignore_fields(case_id: str, db: AsyncSession = Depends(get_db)):
    """
    Analyze recordings in this test case and suggest fields to ignore during diff.
    Groups recordings by path, then diffs response pairs to find fields that vary
    across recordings of the same endpoint (i.e., dynamic/non-deterministic fields).
    """
    import json
    from deepdiff import DeepDiff

    tc = await db.get(TestCase, case_id)
    if not tc:
        raise HTTPException(404, "Test case not found")

    result = await db.execute(
        select(Recording)
        .join(TestCaseRecording, TestCaseRecording.recording_id == Recording.id)
        .where(TestCaseRecording.case_id == case_id)
    )
    recordings = result.scalars().all()

    # Group by path
    by_path: dict[str, list] = {}
    for rec in recordings:
        key = rec.path or "unknown"
        by_path.setdefault(key, []).append(rec)

    def _parse(text):
        if not text:
            return text
        try:
            return json.loads(text)
        except Exception:
            return text

    def _extract_field_names(diff: DeepDiff) -> set[str]:
        """Extract clean field names from DeepDiff result paths."""
        import re
        names: set[str] = set()
        for change_type in ("values_changed", "type_changes", "dictionary_item_added",
                            "dictionary_item_removed", "iterable_item_added", "iterable_item_removed"):
            for path_str in (diff.get(change_type) or {}):
                # path_str looks like: root['data']['timestamp'] or root[0]['id']
                # Extract the last meaningful key name
                parts = re.findall(r"\['([^']+)'\]", str(path_str))
                if parts:
                    names.add(parts[-1])
        return names

    # Heuristic: field name patterns that are typically dynamic
    _DYNAMIC_SUFFIXES = ("time", "at", "date", "timestamp", "ts", "id", "version", "no", "num", "seq")
    _DYNAMIC_EXACT = {"id", "timestamp", "ts", "date", "time", "created", "updated",
                      "createTime", "updateTime", "createAt", "updateAt", "version",
                      "traceId", "requestId", "sessionId", "token", "expire", "expireAt"}

    def _is_dynamic_field(name: str) -> bool:
        lower = name.lower()
        if lower in {s.lower() for s in _DYNAMIC_EXACT}:
            return True
        for suffix in _DYNAMIC_SUFFIXES:
            if lower.endswith(suffix) and len(lower) > len(suffix):
                return True
        return False

    def _collect_field_names(obj, names: set[str]):
        """Recursively collect all dict keys from a parsed JSON object."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(k, str):
                    names.add(k)
                _collect_field_names(v, names)
        elif isinstance(obj, list):
            for item in obj:
                _collect_field_names(item, names)

    suggested: dict[str, int] = {}  # field_name → how many paths it appears in
    heuristic_fields: set[str] = set()  # detected via field-name heuristics

    for path, recs in by_path.items():
        # Collect all field names appearing in responses for heuristic detection
        for rec in recs:
            parsed = _parse(rec.response_body)
            if isinstance(parsed, (dict, list)):
                _collect_field_names(parsed, heuristic_fields)

        if len(recs) < 2:
            continue
        path_fields: set[str] = set()
        # Compare each pair
        for i in range(len(recs) - 1):
            a = _parse(recs[i].response_body)
            b = _parse(recs[i + 1].response_body)
            if a is None or b is None:
                continue
            try:
                diff = DeepDiff(a, b, ignore_order=True, verbose_level=0)
                path_fields |= _extract_field_names(diff)
            except Exception:
                pass
        for f in path_fields:
            suggested[f] = suggested.get(f, 0) + 1

    # Add heuristic-detected dynamic fields that weren't caught by diff
    # (marked with count=0 so they sort below diff-detected ones)
    for f in heuristic_fields:
        if f not in suggested and _is_dynamic_field(f):
            suggested[f] = 0

    # Sort: diff-detected (count>0) first by frequency, then heuristic (count=0) alphabetically
    diff_fields = sorted([(f, c) for f, c in suggested.items() if c > 0], key=lambda x: -x[1])
    heur_fields = sorted([(f, c) for f, c in suggested.items() if c == 0], key=lambda x: x[0])
    sorted_fields = diff_fields + heur_fields

    return {
        "suggested_fields": [f for f, _ in sorted_fields],
        "details": [
            {"field": f, "paths_affected": cnt, "source": "diff" if cnt > 0 else "heuristic"}
            for f, cnt in sorted_fields
        ],
        "analyzed_paths": len([p for p, r in by_path.items() if len(r) >= 2]),
        "total_paths": len(by_path),
    }


@router.delete("/{case_id}/recordings/{recording_id}", status_code=204)
async def remove_recording(
    case_id: str, recording_id: str, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(TestCaseRecording).where(
            TestCaseRecording.case_id == case_id,
            TestCaseRecording.recording_id == recording_id,
        )
    )
    link = result.scalar_one_or_none()
    if not link:
        raise HTTPException(404, "Recording not in this test case")
    await db.delete(link)
    await db.execute(
        sql_update(TestCase)
        .where(TestCase.id == case_id, TestCase.recording_count > 0)
        .values(recording_count=TestCase.recording_count - 1)
    )
    await db.commit()
