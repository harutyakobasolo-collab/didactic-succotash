from sdetflow.models import CaseResult, RunResult, StepResult
from sdetflow.report import write_html_report, write_json_report


def sample_result():
    step = StepResult("login", "passed", "POST", "http://api/login", 200, 12.5, 1)
    case = CaseResult("main flow", "demo", "passed", 12.5, [step])
    return RunResult("2026-09-23T00:00:00+00:00", 12.5, [case])


def test_reports_are_written(tmp_path):
    result = sample_result()
    html_path = write_html_report(result, tmp_path / "report.html")
    json_path = write_json_report(result, tmp_path / "report.json")
    assert "成功率" in html_path.read_text(encoding="utf-8")
    assert '"status": "passed"' in json_path.read_text(encoding="utf-8")

