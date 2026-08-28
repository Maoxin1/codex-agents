from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT.parent / "_invest.toml"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate the portable _invest package.")
    parser.add_argument(
        "--vault",
        type=Path,
        help="Optional Obsidian vault to validate. Defaults to INVEST_VAULT_PATH when set.",
    )
    return parser.parse_args()


def public_files() -> list[Path]:
    files = [CONFIG]
    files.extend(path for path in ROOT.rglob("*") if path.is_file())
    return files


def main() -> int:
    args = parse_args()
    errors: list[str] = []
    checks: list[str] = []

    if not CONFIG.is_file():
        errors.append(f"缺少配置：{CONFIG}")
    else:
        with CONFIG.open("rb") as handle:
            config = tomllib.load(handle)
        for field in ["name", "description", "developer_instructions"]:
            if not config.get(field):
                errors.append(f"TOML 缺少必填字段：{field}")
        if config.get("name") != "_invest":
            errors.append("配置 name 不是 _invest")
        if config.get("model") != "gpt-5.6-sol":
            errors.append("默认模型不是 gpt-5.6-sol")
        if config.get("model_reasoning_effort") != "high":
            errors.append("默认推理档位不是 high")
        instructions = config.get("developer_instructions", "")
        for term in [
            "确认门",
            "Obsidian",
            "[F-已核实]",
            "不执行证券交易",
            "INVEST_VAULT_PATH",
            "knowledge-map.local.md",
        ]:
            if term not in instructions:
                errors.append(f"developer_instructions 缺少关键边界：{term}")
        if len(instructions) > 4600:
            errors.append(f"developer_instructions 过长：{len(instructions)} 字符")
        checks.append(f"TOML 可解析；运行时说明 {len(instructions)} 字符")

    required_files = [
        ".gitignore",
        "README.md",
        "core.md",
        "evidence.md",
        "workflow.md",
        "archive-rules.md",
        "knowledge-map.md",
        "CHANGELOG.md",
        "invoke_invest.ps1",
        "tests/cases.json",
        "tests/README.md",
    ]
    for relative in required_files:
        if not (ROOT / relative).is_file():
            errors.append(f"缺少支持文件：{relative}")
    checks.append(f"支持文件检查：{len(required_files)} 项")

    private_patterns = {
        "Windows 绝对路径": re.compile(r"(?<![\w>])[A-Za-z]:\\[^\r\n`'\"]+"),
        "具体 Case ID": re.compile(r"\bCASE-[A-Z0-9]+-[A-Z0-9-]+\b"),
    }
    for path in public_files():
        if path.suffix.lower() not in {".md", ".toml", ".ps1", ".py", ".json", ""}:
            continue
        file_text = path.read_text(encoding="utf-8")
        for label, pattern in private_patterns.items():
            if pattern.search(file_text):
                errors.append(f"公开文件包含个人标记：{path.relative_to(ROOT.parent)} / {label}")
    checks.append("公开包隐私扫描")

    gitignore_path = ROOT / ".gitignore"
    if gitignore_path.is_file():
        ignored = gitignore_path.read_text(encoding="utf-8").splitlines()
        if "knowledge-map.local.md" not in ignored:
            errors.append(".gitignore 未忽略 knowledge-map.local.md")
        checks.append("私有案例覆盖文件忽略规则")

    invoke_path = ROOT / "invoke_invest.ps1"
    if invoke_path.is_file():
        invoke_text = invoke_path.read_text(encoding="utf-8")
        for term in ["VaultPath", "INVEST_VAULT_PATH"]:
            if term not in invoke_text:
                errors.append(f"独立调用脚本缺少便携配置：{term}")
        checks.append("独立调用脚本可配置 vault")

    vault = args.vault
    if vault is None and os.environ.get("INVEST_VAULT_PATH"):
        vault = Path(os.environ["INVEST_VAULT_PATH"])
    if vault is None:
        checks.append("未指定 vault；跳过私有知识入口检查")
    elif not vault.is_dir():
        errors.append(f"指定的 Obsidian vault 不可访问：{vault}")
    else:
        checks.append(f"Obsidian vault 可访问：{vault.resolve()}")

    cases_path = ROOT / "tests" / "cases.json"
    if cases_path.is_file():
        data = json.loads(cases_path.read_text(encoding="utf-8"))
        cases = data.get("cases", [])
        case_ids = [case.get("id") for case in cases]
        expected_ids = ["CONFIRM-001", "EVIDENCE-001", "WRITE-001"]
        if case_ids != expected_ids:
            errors.append(f"冒烟测试 ID 或顺序不符：{case_ids}")
        for case in cases:
            for field in ["id", "name", "phase", "input", "expected", "forbidden"]:
                if not case.get(field):
                    errors.append(f"测试用例缺字段：{case.get('id', '?')} / {field}")
        checks.append(f"轻量行为用例：{len(cases)} 个")

    knowledge_map = ROOT / "knowledge-map.md"
    if knowledge_map.is_file():
        map_text = knowledge_map.read_text(encoding="utf-8")
        for term in ["knowledge-map.local.md", "相对路径", "Case ID", "使用边界"]:
            if term not in map_text:
                errors.append(f"案例地图缺少便携模板字段：{term}")
        checks.append("可移植案例地图与私有覆盖路由")

    evidence_path = ROOT / "evidence.md"
    if evidence_path.is_file():
        evidence_text = evidence_path.read_text(encoding="utf-8")
        if "必须列出至少一个可观察的后续验证信号" not in evidence_text:
            errors.append("evidence.md 缺少公司指引的后续验证信号规则")
        checks.append("公司指引与前瞻预测的验证路径契约")

    if errors:
        print("VALIDATION FAILED")
        for message in errors:
            print(f"- {message}")
        return 1

    print("VALIDATION PASSED")
    for message in checks:
        print(f"- {message}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
