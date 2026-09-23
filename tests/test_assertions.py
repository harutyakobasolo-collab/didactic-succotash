import httpx
import pytest

from sdetflow.assertions import check_assertion
from sdetflow.errors import AssertionFailure
from sdetflow.models import AssertionSpec


@pytest.mark.parametrize(
    ("spec", "body"),
    [
        (AssertionSpec("status_code", "eq", 200), {"ok": True}),
        (AssertionSpec("$.message", "contains", "success"), {"message": "create success"}),
        (AssertionSpec("$.items", "length_eq", 2), {"items": [1, 2]}),
        (AssertionSpec("$.value", "gte", 10), {"value": 12}),
        (AssertionSpec("$.value", "exists"), {"value": 0}),
    ],
)
def test_supported_assertions(spec, body):
    check_assertion(httpx.Response(200, json=body), spec)


def test_failed_assertion_contains_actual_value():
    with pytest.raises(AssertionFailure, match="实际值=500"):
        check_assertion(httpx.Response(500, json={}), AssertionSpec("status_code", "eq", 200))


def test_unknown_operator_is_rejected():
    with pytest.raises(AssertionFailure, match="不支持"):
        check_assertion(httpx.Response(200, json={"a": 1}), AssertionSpec("$.a", "magic", 1))

