from __future__ import annotations

import re
from typing import Any

from .errors import RenderError

VARIABLE_PATTERN = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_.-]*)}")


def _lookup(name: str, variables: dict[str, Any]) -> Any:
    current: Any = variables
    for part in name.split("."):
        if not isinstance(current, dict) or part not in current:
            raise RenderError(f"变量未定义: {name}")
        current = current[part]
    return current


def render(value: Any, variables: dict[str, Any]) -> Any:
    """Recursively replace ${variable} placeholders while preserving native types."""
    if isinstance(value, dict):
        return {key: render(item, variables) for key, item in value.items()}
    if isinstance(value, list):
        return [render(item, variables) for item in value]
    if not isinstance(value, str):
        return value

    full_match = VARIABLE_PATTERN.fullmatch(value)
    if full_match:
        return _lookup(full_match.group(1), variables)

    def replace(match: re.Match[str]) -> str:
        return str(_lookup(match.group(1), variables))

    return VARIABLE_PATTERN.sub(replace, value)

