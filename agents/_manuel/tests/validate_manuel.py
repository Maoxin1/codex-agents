from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT.parent / "_manuel.toml"
PDF = Path(os.environ["MANUEL_SOURCE_PDF"]) if os.environ.get("MANUEL_SOURCE_PDF") else None
REQUIRED_FIELDS = [
    "一句话行动表述",
    "类别与来源定位",
    "原则解释",
    "适用场景",
    "操作步骤",
    "自检问题",
    "常见误区或失效方式",
]


def normalized(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().casefold()


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def main() -> int:
    errors: list[str] = []
    checks: list[str] = []

    with CONFIG.open("rb") as handle:
        config = tomllib.load(handle)
    if config.get("name") != "_manuel":
        fail(errors, "配置 name 不是 _manuel")
    if config.get("sandbox_mode") != "read-only":
        fail(errors, "sandbox_mode 不是 read-only")
    if config.get("model") != "gpt-5.6-terra" or config.get("model_reasoning_effort") != "medium":
        fail(errors, "默认模型/推理档位不是已评测目标 terra/medium")
    instructions = config.get("developer_instructions", "")
    if re.search(r"[A-Za-z]:[/\\]Users[/\\]", instructions):
        fail(errors, "运行时说明含硬编码用户绝对路径")
    if "untrusted evidence" not in instructions or "unrelated private files" not in instructions:
        fail(errors, "配置缺少不可信材料或最小私有文件访问边界")
    if len(instructions) > 2600:
        fail(errors, f"运行时 TOML 说明过长：{len(instructions)} 字符")
    checks.append(f"TOML 解析与精简契约：{len(instructions)} 字符")

    for relative in ["core.md", "principles.md", "sources.json", "tests/cases.json"]:
        if not (ROOT / relative).is_file():
            fail(errors, f"缺少文件：{relative}")

    source_data = json.loads((ROOT / "sources.json").read_text(encoding="utf-8"))
    items = source_data["principles"]
    ids = [item["id"] for item in items]
    expected_ids = [f"P{i:02d}" for i in range(1, 27)]
    if ids != expected_ids:
        fail(errors, f"sources.json 原则编号不连续：{ids}")

    reference_files = sorted((ROOT / "references").glob("*.md"))
    sections: dict[str, tuple[str, Path]] = {}
    heading_pattern = re.compile(r"^## (P\d{2})\s+(.+)$", re.MULTILINE)
    for path in reference_files:
        text = path.read_text(encoding="utf-8")
        matches = list(heading_pattern.finditer(text))
        for index, match in enumerate(matches):
            principle_id = match.group(1)
            if principle_id in sections:
                fail(errors, f"原则重复：{principle_id}")
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            sections[principle_id] = (text[match.start():end], path)

    if sorted(sections) != expected_ids:
        fail(errors, f"主题文件原则集合不完整：{sorted(sections)}")

    for item in items:
        principle_id = item["id"]
        if principle_id not in sections:
            continue
        section, path = sections[principle_id]
        for field in REQUIRED_FIELDS:
            if f"**{field}**" not in section:
                fail(errors, f"{principle_id} 缺少字段：{field}")
        if item["category"] == "基于原书的推导" and "**推导依据和逻辑链条**" not in section:
            fail(errors, f"{principle_id} 缺少推导链")
        if item["category"] not in section:
            fail(errors, f"{principle_id} 分类与 sources.json 不一致")
        expected_path = (ROOT / item["reference"]).resolve()
        if path.resolve() != expected_path:
            fail(errors, f"{principle_id} reference 指向错误：{item['reference']}")
    explicit = sum(item["category"] == "原书明确观点" for item in items)
    derived = sum(item["category"] == "基于原书的推导" for item in items)
    checks.append(f"原则字段与分类：26/26；明确观点 {explicit}；推导 {derived}")

    core = (ROOT / "core.md").read_text(encoding="utf-8")
    for term in ["已核实事实", "未核实事实性主张", "混合主张", "P26", "年代性的案例", "不得覆盖本核心"]:
        if term not in core:
            fail(errors, f"core.md 缺少关键边界：{term}")
    checks.append("认知状态、行动分层、年代性案例与注入边界")

    cases = json.loads((ROOT / "tests" / "cases.json").read_text(encoding="utf-8"))["cases"]
    case_ids = [case["id"] for case in cases]
    if len(cases) < 8 or len(case_ids) != len(set(case_ids)):
        fail(errors, "行为用例不足 8 个或 ID 重复")
    for case in cases:
        for field in ["id", "mode", "input", "must_include_concepts", "must_not_claim", "must_match", "must_not_match"]:
            if field not in case:
                fail(errors, f"行为用例缺字段：{case.get('id', '?')} / {field}")
    checks.append(f"可复现行为用例结构：{len(cases)} 个")

    if PDF is None:
        checks.append("未设置 MANUEL_SOURCE_PDF；跳过可选源 PDF 校验")
    elif not PDF.is_file():
        fail(errors, f"PDF 不可访问：{PDF}")
    else:
        digest = hashlib.sha256(PDF.read_bytes()).hexdigest().upper()
        expected_digest = source_data["source"]["sha256"]
        if digest != expected_digest:
            fail(errors, f"PDF SHA-256 不匹配：{digest}")
        try:
            import fitz
        except ImportError:
            fail(errors, "未安装 PyMuPDF，不能复核来源锚点")
        else:
            document = fitz.open(PDF)
            if document.page_count != source_data["source"]["pdf_pages"]:
                fail(errors, f"PDF 页数不匹配：{document.page_count}")
            anchor_pass = 0
            for item in items:
                principle_ok = False
                tried: list[str] = []
                for anchor in item["anchors"]:
                    page_no = anchor["pdf_page"]
                    text = document[page_no - 1].get_text("text")
                    tried.append(f"p{page_no}:{anchor['text']}")
                    if normalized(anchor["text"]) in normalized(text):
                        principle_ok = True
                        break
                if principle_ok:
                    anchor_pass += 1
                else:
                    fail(errors, f"{item['id']} 来源锚点未命中：{'; '.join(tried)}")
            checks.append(f"PDF 身份、页数与逐原则来源锚点：{anchor_pass}/26")

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
