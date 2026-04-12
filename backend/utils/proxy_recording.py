from __future__ import annotations


PROXY_RECORDING_HEADER = "X-AREX-Proxy-Recorded"
PROXY_RECORDING_VALUE = "transparent-proxy"


def with_proxy_recording_header(headers: dict[str, str] | None) -> dict[str, str]:
    result = dict(headers or {})
    result[PROXY_RECORDING_HEADER] = PROXY_RECORDING_VALUE
    return result


def has_proxy_recording_header(headers: dict | None) -> bool:
    if not isinstance(headers, dict):
        return False
    for key, value in headers.items():
        if str(key).lower() == PROXY_RECORDING_HEADER.lower():
            return str(value).strip().lower() == PROXY_RECORDING_VALUE
    return False
