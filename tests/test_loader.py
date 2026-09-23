from pathlib import Path

import pytest

from sdetflow.errors import CaseValidationError
from sdetflow.loader import load_cases, load_environment


def test_load_example_cases():
    cases = load_cases(Path("examples/ecommerce/cases.yaml"))
    assert len(cases) == 2
    assert cases[0].steps[0].method == "POST"
    assert cases[0].steps[-1].retry == 2


def test_environment_can_be_overridden(monkeypatch, tmp_path):
    env_file = tmp_path / "env.yaml"
    env_file.write_text("base_url: http://old\nregion: cn\n", encoding="utf-8")
    monkeypatch.setenv("SDETFLOW_BASE_URL", "http://new")
    assert load_environment(env_file) == {"base_url": "http://new", "region": "cn"}


def test_empty_case_list_is_rejected(tmp_path):
    case_file = tmp_path / "cases.yaml"
    case_file.write_text("cases: []\n", encoding="utf-8")
    with pytest.raises(CaseValidationError, match="至少需要一个"):
        load_cases(case_file)

