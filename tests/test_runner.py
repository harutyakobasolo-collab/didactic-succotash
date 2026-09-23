import json

import httpx

from sdetflow.models import AssertionSpec, CaseSpec, StepSpec
from sdetflow.runner import TestRunner as FlowRunner


def test_runner_passes_context_between_steps():
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/login":
            return httpx.Response(200, json={"token": "abc"})
        assert request.headers["authorization"] == "Bearer abc"
        return httpx.Response(201, json={"id": "order-1", "status": "created"})

    case = CaseSpec(
        name="order flow",
        steps=(
            StepSpec(name="login", method="POST", path="/login", extract={"token": "$.token"}),
            StepSpec(
                name="create",
                method="POST",
                path="/orders",
                headers={"Authorization": "Bearer ${token}"},
                assertions=(AssertionSpec("status_code", "eq", 201),),
            ),
        ),
    )
    result = FlowRunner("https://example.test", transport=httpx.MockTransport(handler)).run([case])
    assert result.passed == 1
    assert result.cases[0].steps[0].extracted == {"token": "abc"}


def test_runner_retries_then_passes():
    calls = 0

    def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(200, json={"ready": calls >= 2})

    case = CaseSpec(
        name="eventual consistency",
        steps=(
            StepSpec(
                name="poll",
                method="GET",
                path="/status",
                retry=2,
                retry_interval_ms=0,
                assertions=(AssertionSpec("$.ready", "eq", True),),
            ),
        ),
    )
    result = FlowRunner("https://example.test", transport=httpx.MockTransport(handler)).run([case])
    assert result.passed == 1
    assert result.cases[0].steps[0].attempts == 2


def test_runner_stops_case_after_failure():
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"error": "boom"})

    case = CaseSpec(
        name="failed flow",
        steps=(
            StepSpec(
                name="first",
                method="GET",
                path="/first",
                assertions=(AssertionSpec("status_code", "eq", 200),),
            ),
            StepSpec(name="never", method="GET", path="/never"),
        ),
    )
    result = FlowRunner("https://example.test", transport=httpx.MockTransport(handler)).run([case])
    assert result.failed == 1
    assert len(result.cases[0].steps) == 1
    assert "实际值=500" in result.cases[0].steps[0].error


def test_runner_renders_json_with_native_types():
    def handler(request: httpx.Request) -> httpx.Response:
        assert json.loads(request.content) == {"quantity": 2}
        return httpx.Response(200, json={"ok": True})

    case = CaseSpec(
        name="native json type",
        variables={"quantity": 2},
        steps=(
            StepSpec(name="post", method="POST", path="/items", json={"quantity": "${quantity}"}),
        ),
    )
    result = FlowRunner("https://example.test", transport=httpx.MockTransport(handler)).run([case])
    assert result.success_rate == 100
