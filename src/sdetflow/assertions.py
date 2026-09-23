from __future__ import annotations

import operator
from collections.abc import Callable
from typing import Any

from .errors import AssertionFailure
from .extract import extract_response
from .models import AssertionSpec


def _contains(actual: Any, expected: Any) -> bool:
    return expected in actual


def _not_contains(actual: Any, expected: Any) -> bool:
    return expected not in actual


def _length_eq(actual: Any, expected: Any) -> bool:
    return len(actual) == int(expected)


OPERATORS: dict[str, Callable[[Any, Any], bool]] = {
    "eq": operator.eq,
    "ne": operator.ne,
    "gt": operator.gt,
    "gte": operator.ge,
    "lt": operator.lt,
    "lte": operator.le,
    "contains": _contains,
    "not_contains": _not_contains,
    "length_eq": _length_eq,
    "exists": lambda actual, _expected: actual is not None,
}


def check_assertion(response: Any, spec: AssertionSpec, expected: Any = None) -> None:
    actual = extract_response(response, spec.source)
    expected_value = spec.expected if expected is None else expected
    if spec.operator not in OPERATORS:
        raise AssertionFailure(f"不支持的断言操作符: {spec.operator}")
    try:
        passed = OPERATORS[spec.operator](actual, expected_value)
    except (TypeError, ValueError) as exc:
        raise AssertionFailure(
            f"断言执行失败: {spec.source} {spec.operator} {expected_value!r}; 实际值={actual!r}"
        ) from exc
    if not passed:
        raise AssertionFailure(
            f"断言失败: {spec.source} {spec.operator} {expected_value!r}; 实际值={actual!r}"
        )
