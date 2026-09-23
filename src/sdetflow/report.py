from __future__ import annotations

import html
import json
from dataclasses import asdict
from pathlib import Path

from .models import RunResult


def write_json_report(result: RunResult, path: str | Path) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(asdict(result), ensure_ascii=False, indent=2), encoding="utf-8")
    return output


def write_html_report(result: RunResult, path: str | Path) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for case in result.cases:
        for step in case.steps:
            status_class = "pass" if step.status == "passed" else "fail"
            error = html.escape(step.error or "-")
            rows.append(
                f"<tr><td>{html.escape(case.name)}</td><td>{html.escape(step.name)}</td>"
                f"<td><span class='{status_class}'>{step.status.upper()}</span></td>"
                f"<td>{step.method}</td><td>{step.status_code or '-'}</td>"
                f"<td>{step.elapsed_ms:.2f} ms</td><td>{step.attempts}</td><td>{error}</td></tr>"
            )
    document = f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>SDETFlow 测试报告</title><style>
body{{font-family:Inter,"Microsoft YaHei",sans-serif;background:#f5f7fb;color:#172033;margin:0;padding:32px}}
.container{{max-width:1180px;margin:auto}}h1{{margin-bottom:4px}}.meta{{color:#667085}}
.cards{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:24px 0}}
.card{{background:white;border-radius:12px;padding:18px;box-shadow:0 2px 10px #10182810}}
.value{{font-size:28px;font-weight:700}}table{{width:100%;border-collapse:collapse;background:white;border-radius:12px;overflow:hidden}}
th,td{{padding:13px;text-align:left;border-bottom:1px solid #eaecf0;font-size:14px}}th{{background:#101828;color:white}}
.pass{{color:#067647;font-weight:700}}.fail{{color:#b42318;font-weight:700}}@media(max-width:800px){{.cards{{grid-template-columns:1fr 1fr}}}}
</style></head><body><div class="container"><h1>SDETFlow 测试报告</h1>
<div class="meta">执行时间 {html.escape(result.started_at)}</div><div class="cards">
<div class="card"><div>用例总数</div><div class="value">{len(result.cases)}</div></div>
<div class="card"><div>通过</div><div class="value pass">{result.passed}</div></div>
<div class="card"><div>失败</div><div class="value fail">{result.failed}</div></div>
<div class="card"><div>成功率</div><div class="value">{result.success_rate:.1f}%</div></div></div>
<table><thead><tr><th>用例</th><th>步骤</th><th>结果</th><th>方法</th><th>状态码</th><th>耗时</th><th>尝试</th><th>错误</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table><p class="meta">总耗时 {result.elapsed_ms:.2f} ms</p></div></body></html>"""
    output.write_text(document, encoding="utf-8")
    return output

