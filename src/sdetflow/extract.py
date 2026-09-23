from __future__ import annotations

import re
from typing import Any

from .errors import ExtractionError

TOKEN_PATTERN = re.compile(r"([^.[\]]+)|\[(\d+)]")


def resolve_path(data: Any, path: str) -> Any:
    """Resolve a lightweight JSONPath expression such as $.data.items[0].id."""
    if path in {"$", "body"}:
        return data
    normalized = path[2:] if path.startswith("$.") else path
    current = data
    for key, index in TOKEN_PATTERN.findall(normalized):
        try:
            current = current[int(index)] if index else current[key]
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise ExtractionError(f"无法从路径 {path!r} 提取数据") from exc
    return current


def extract_response(response: Any, source: str) -> Any:
    if source == "status_code":
        return response.status_code
    if source.startswith("headers."):
        header_name = source.split(".", 1)[1]
        if header_name not in response.headers:
            raise ExtractionError(f"响应头不存在: {header_name}")
        return response.headers[header_name]
    if source == "text":
        return response.text
    try:
        body = response.json()
    except ValueError as exc:
        raise ExtractionError("响应体不是合法 JSON") from exc
    return resolve_path(body, source)

