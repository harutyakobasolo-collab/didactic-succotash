from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class AssertionSpec:
    source: str
    operator: str
    expected: Any = None


@dataclass(frozen=True)
class StepSpec:
    name: str
    method: str
    path: str
    headers: dict[str, Any] = field(default_factory=dict)
    params: dict[str, Any] = field(default_factory=dict)
    json: Any = None
    extract: dict[str, str] = field(default_factory=dict)
    assertions: tuple[AssertionSpec, ...] = ()
    retry: int = 0
    retry_interval_ms: int = 200
    timeout_seconds: float = 10.0


@dataclass(frozen=True)
class CaseSpec:
    name: str
    description: str = ""
    tags: tuple[str, ...] = ()
    variables: dict[str, Any] = field(default_factory=dict)
    steps: tuple[StepSpec, ...] = ()


@dataclass
class StepResult:
    name: str
    status: str
    method: str
    url: str
    status_code: int | None
    elapsed_ms: float
    attempts: int
    error: str | None = None
    extracted: dict[str, Any] = field(default_factory=dict)
    assertion_count: int = 0


@dataclass
class CaseResult:
    name: str
    description: str
    status: str
    elapsed_ms: float
    steps: list[StepResult] = field(default_factory=list)


@dataclass
class RunResult:
    started_at: str
    elapsed_ms: float
    cases: list[CaseResult]

    @property
    def passed(self) -> int:
        return sum(case.status == "passed" for case in self.cases)

    @property
    def failed(self) -> int:
        return sum(case.status == "failed" for case in self.cases)

    @property
    def success_rate(self) -> float:
        return self.passed / len(self.cases) * 100 if self.cases else 0.0

