from __future__ import annotations

import argparse
from pathlib import Path

from .loader import load_cases, load_environment
from .report import write_html_report, write_json_report
from .runner import TestRunner


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SDETFlow YAML 接口自动化测试框架")
    parser.add_argument("cases", help="YAML 用例文件")
    parser.add_argument("--env", help="环境配置 YAML")
    parser.add_argument("--base-url", help="覆盖环境配置中的 base_url")
    parser.add_argument("--tag", action="append", default=[], help="仅运行指定标签，可重复传入")
    parser.add_argument("--report-dir", default="reports", help="报告输出目录")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    variables = load_environment(args.env)
    base_url = args.base_url or variables.get("base_url")
    if not base_url:
        raise SystemExit("缺少 base_url，请通过 --base-url 或环境 YAML 配置")

    result = TestRunner(base_url, variables).run(load_cases(args.cases), set(args.tag))
    report_dir = Path(args.report_dir)
    html_path = write_html_report(result, report_dir / "report.html")
    write_json_report(result, report_dir / "report.json")
    print(
        f"执行完成: {len(result.cases)} 个用例, 通过 {result.passed}, "
        f"失败 {result.failed}, 成功率 {result.success_rate:.1f}%"
    )
    print(f"HTML 报告: {html_path.resolve()}")
    return 1 if result.failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

