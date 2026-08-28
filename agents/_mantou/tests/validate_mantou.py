from __future__ import annotations

import json
import re
import sys
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT.parent / "_mantou.toml"


def main() -> int:
    errors: list[str] = []
    with CONFIG.open("rb") as handle:
        config = tomllib.load(handle)

    expected = {
        "name": "_mantou",
        "model": "gpt-5.6-sol",
        "model_reasoning_effort": "high",
        "sandbox_mode": "read-only",
    }
    for field, value in expected.items():
        if config.get(field) != value:
            errors.append(f"{field} 不是预期值：{value}")

    instructions = config.get("developer_instructions", "")
    required_terms = [
        "Never execute or answer the underlying request",
        "Windows clipboard",
        "Set-Clipboard",
        "Get-Clipboard -Raw",
        "single-quoted literal",
        "Invoke-Expression",
        "CLIPBOARD_COPY_FAILED",
        "return exactly the same refined prompt",
    ]
    for term in required_terms:
        if term not in instructions:
            errors.append(f"developer_instructions 缺少关键契约：{term}")
    if re.search(r"[A-Za-z]:[/\\]Users[/\\]", instructions):
        errors.append("developer_instructions 含硬编码用户绝对路径")
    if instructions.count("retry once") != 1:
        errors.append("剪贴板失败重试契约不唯一或缺失")

    for relative in ["README.md", "CHANGELOG.md", "tests/cases.json"]:
        if not (ROOT / relative).is_file():
            errors.append(f"缺少支持文件：{relative}")

    cases = json.loads((ROOT / "tests" / "cases.json").read_text(encoding="utf-8"))["cases"]
    ids = [case.get("id") for case in cases]
    if len(cases) < 4 or len(ids) != len(set(ids)):
        errors.append("行为用例不足 4 个或 ID 重复")
    for case in cases:
        for field in ["id", "name", "input", "expected", "forbidden"]:
            if not case.get(field):
                errors.append(f"行为用例缺字段：{case.get('id', '?')} / {field}")

    if errors:
        print("VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print("VALIDATION PASSED")
    print(f"- _mantou TOML 与只读边界：{len(instructions)} 字符")
    print(f"- 剪贴板与输出契约：{len(required_terms)} 项")
    print(f"- 可复核行为用例：{len(cases)} 个")
    return 0


if __name__ == "__main__":
    sys.exit(main())
