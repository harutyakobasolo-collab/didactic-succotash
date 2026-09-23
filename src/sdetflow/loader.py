from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

from .errors import CaseValidationError
from .models import AssertionSpec, CaseSpec, StepSpec


def load_environment(path: str | Path | None) -> dict[str, Any]:
    values: dict[str, Any] = {}
    if path:
        values.update(_read_yaml(path) or {})
    for key, value in os.environ.items():
        if key.startswith("SDETFLOW_"):
            values[key.removeprefix("SDETFLOW_").lower()] = value
    return values


def load_cases(path: str | Path) -> list[CaseSpec]:
    raw = _read_yaml(path)
    if not isinstance(raw, dict) or not isinstance(raw.get("cases"), list):
        raise CaseValidationError("用例文件必须包含 cases 列表")
    cases = [_parse_case(item, index) for index, item in enumerate(raw["cases"], 1)]
    if not cases:
        raise CaseValidationError("用例文件至少需要一个测试用例")
    return cases


def _read_yaml(path: str | Path) -> Any:
    file_path = Path(path)
    if not file_path.exists():
        raise CaseValidationError(f"文件不存在: {file_path}")
    try:
        return yaml.safe_load(file_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise CaseValidationError(f"YAML 解析失败: {file_path}") from exc


def _parse_case(raw: Any, index: int) -> CaseSpec:
    if not isinstance(raw, dict) or not raw.get("name"):
        raise CaseValidationError(f"第 {index} 个用例缺少 name")
    raw_steps = raw.get("steps")
    if not isinstance(raw_steps, list) or not raw_steps:
        raise CaseValidationError(f"用例 {raw['name']} 至少需要一个 step")
    return CaseSpec(
        name=str(raw["name"]),
        description=str(raw.get("description", "")),
        tags=tuple(str(tag) for tag in raw.get("tags", [])),
        variables=dict(raw.get("variables", {})),
        steps=tuple(_parse_step(step, raw["name"], i) for i, step in enumerate(raw_steps, 1)),
    )


def _parse_step(raw: Any, case_name: str, index: int) -> StepSpec:
    if not isinstance(raw, dict):
        raise CaseValidationError(f"用例 {case_name} 的第 {index} 个 step 格式错误")
    request = raw.get("request", {})
    if not raw.get("name") or not request.get("path"):
        raise CaseValidationError(
            f"用例 {case_name} 的第 {index} 个 step 缺少 name 或 request.path"
        )
    assertions = []
    for item in raw.get("assert", []):
        if not isinstance(item, dict) or not item.get("source") or not item.get("operator"):
            raise CaseValidationError(f"用例 {case_name} 存在无效断言")
        assertions.append(
            AssertionSpec(item["source"], item["operator"], item.get("expected"))
        )
    return StepSpec(
        name=str(raw["name"]),
        method=str(request.get("method", "GET")).upper(),
        path=str(request["path"]),
        headers=dict(request.get("headers", {})),
        params=dict(request.get("params", {})),
        json=request.get("json"),
        extract=dict(raw.get("extract", {})),
        assertions=tuple(assertions),
        retry=max(0, int(raw.get("retry", 0))),
        retry_interval_ms=max(0, int(raw.get("retry_interval_ms", 200))),
        timeout_seconds=float(raw.get("timeout_seconds", 10.0)),
    )
