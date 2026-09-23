from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

import httpx

from .assertions import check_assertion
from .extract import extract_response
from .models import CaseResult, CaseSpec, RunResult, StepResult, StepSpec
from .template import render


class TestRunner:
    def __init__(
        self,
        base_url: str,
        variables: dict[str, Any] | None = None,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.variables = dict(variables or {})
        self.transport = transport

    def run(self, cases: list[CaseSpec], tags: set[str] | None = None) -> RunResult:
        selected = [case for case in cases if not tags or tags.intersection(case.tags)]
        run_started = time.perf_counter()
        started_at = datetime.now(timezone.utc).isoformat()
        results: list[CaseResult] = []
        with httpx.Client(transport=self.transport, follow_redirects=True) as client:
            for case in selected:
                results.append(self._run_case(client, case))
        return RunResult(
            started_at=started_at,
            elapsed_ms=round((time.perf_counter() - run_started) * 1000, 2),
            cases=results,
        )

    def _run_case(self, client: httpx.Client, case: CaseSpec) -> CaseResult:
        started = time.perf_counter()
        context = {**self.variables, **case.variables}
        steps: list[StepResult] = []
        status = "passed"
        for step in case.steps:
            result = self._run_step(client, step, context)
            steps.append(result)
            if result.status == "failed":
                status = "failed"
                break
            context.update(result.extracted)
        return CaseResult(
            name=case.name,
            description=case.description,
            status=status,
            elapsed_ms=round((time.perf_counter() - started) * 1000, 2),
            steps=steps,
        )

    def _run_step(
        self, client: httpx.Client, step: StepSpec, context: dict[str, Any]
    ) -> StepResult:
        url = f"{self.base_url}/{render(step.path, context).lstrip('/')}"
        started = time.perf_counter()
        attempts = 0
        last_error: Exception | None = None
        status_code: int | None = None
        extracted: dict[str, Any] = {}

        for attempt in range(step.retry + 1):
            attempts = attempt + 1
            try:
                response = client.request(
                    method=step.method,
                    url=url,
                    headers=render(step.headers, context),
                    params=render(step.params, context),
                    json=render(step.json, context),
                    timeout=step.timeout_seconds,
                )
                status_code = response.status_code
                for assertion in step.assertions:
                    check_assertion(response, assertion, render(assertion.expected, context))
                extracted = {
                    name: extract_response(response, source)
                    for name, source in step.extract.items()
                }
                return StepResult(
                    name=step.name,
                    status="passed",
                    method=step.method,
                    url=url,
                    status_code=status_code,
                    elapsed_ms=round((time.perf_counter() - started) * 1000, 2),
                    attempts=attempts,
                    extracted=extracted,
                    assertion_count=len(step.assertions),
                )
            # Retry intentionally covers HTTP, extraction and assertion errors.
            except Exception as exc:
                last_error = exc
                if attempt < step.retry:
                    time.sleep(step.retry_interval_ms / 1000)

        return StepResult(
            name=step.name,
            status="failed",
            method=step.method,
            url=url,
            status_code=status_code,
            elapsed_ms=round((time.perf_counter() - started) * 1000, 2),
            attempts=attempts,
            error=str(last_error),
            extracted=extracted,
            assertion_count=len(step.assertions),
        )
