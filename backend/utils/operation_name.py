import json
import re
from typing import Any


DEFAULT_OPERATION_ID_TAGS = [
    "service_id",
    "serviceId",
    "service_code",
    "msgType",
    "transCode",
    "txCode",
    "trand_id",
    "trandId",
    "trans_id",
    "tranId",
]


def get_operation_id_tags(app: Any | None = None) -> list[str]:
    configured = getattr(app, "operation_id_tags", None) if app is not None else None
    raw_tags = configured or []

    if isinstance(raw_tags, str):
        try:
            parsed = json.loads(raw_tags)
        except Exception:
            parsed = [part.strip() for part in raw_tags.split(",")]
        raw_tags = parsed

    if not isinstance(raw_tags, list):
        raw_tags = []

    raw_tags = [*raw_tags, *DEFAULT_OPERATION_ID_TAGS]

    tags: list[str] = []
    seen: set[str] = set()
    for item in raw_tags:
        tag = str(item).strip()
        if not tag:
            continue
        lowered = tag.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        tags.append(tag)
    return tags


def extract_operation_name(text: str | None, tags: list[str] | None = None) -> str | None:
    if not text:
        return None

    tag_list = tags or DEFAULT_OPERATION_ID_TAGS
    lowered_tags = {tag.lower(): tag for tag in tag_list}

    for tag in tag_list:
        match = re.search(
            rf"<{re.escape(tag)}[^>]*>\s*([^<]+)\s*</{re.escape(tag)}>",
            text,
            re.IGNORECASE,
        )
        if match and match.group(1).strip():
            return match.group(1).strip()

    try:
        parsed = json.loads(text)
    except Exception:
        parsed = None

    if parsed is not None:
        found = _search_json(parsed, lowered_tags)
        if found:
            return found

    key_pattern = "|".join(re.escape(tag) for tag in tag_list)
    if key_pattern:
        match = re.search(
            rf'"(?:{key_pattern})"\s*:\s*"([^"]+)"',
            text,
            re.IGNORECASE,
        )
        if match and match.group(1).strip():
            return match.group(1).strip()

    return None


def _search_json(value: Any, lowered_tags: dict[str, str]) -> str | None:
    if isinstance(value, dict):
        for key, child in value.items():
            if str(key).lower() in lowered_tags and child is not None:
                text = str(child).strip()
                if text:
                    return text
        for child in value.values():
            found = _search_json(child, lowered_tags)
            if found:
                return found
    elif isinstance(value, list):
        for child in value:
            found = _search_json(child, lowered_tags)
            if found:
                return found
    return None
