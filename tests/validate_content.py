from __future__ import annotations

import json
import re
import sys
import tomllib
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
IGNORED_PARTS = {".git", "__pycache__"}
TEXT_SUFFIXES = {".md", ".toml", ".ps1", ".py", ".json", ".yml", ".yaml"}


def repository_files() -> list[Path]:
    return [
        path
        for path in ROOT.rglob("*")
        if path.is_file() and not IGNORED_PARTS.intersection(path.parts)
    ]


def main() -> int:
    errors: list[str] = []
    files = repository_files()

    toml_files = [path for path in files if path.suffix == ".toml"]
    for path in toml_files:
        with path.open("rb") as handle:
            tomllib.load(handle)

    json_files = [path for path in files if path.suffix == ".json"]
    for path in json_files:
        json.loads(path.read_text(encoding="utf-8"))

    markdown_files = [path for path in files if path.suffix == ".md"]
    link_pattern = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
    for path in markdown_files:
        text = path.read_text(encoding="utf-8")
        for raw_target in link_pattern.findall(text):
            target = raw_target.strip().strip("<>").split("#", 1)[0]
            if not target or re.match(r"^[a-z][a-z0-9+.-]*:", target, re.IGNORECASE):
                continue
            resolved = (path.parent / unquote(target)).resolve()
            if not resolved.exists():
                errors.append(f"失效的相对链接：{path.relative_to(ROOT)} -> {raw_target}")

    private_patterns = {
        "用户绝对路径": re.compile(r"[A-Za-z]:[/\\]Users[/\\][^\s`'\"]+"),
        "疑似明文密钥": re.compile(
            r"(?i)(?:api[_-]?key|secret|token)\s*[:=]\s*['\"]?[A-Za-z0-9_-]{20,}"
        ),
    }
    for path in files:
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8")
        for label, pattern in private_patterns.items():
            if pattern.search(text):
                errors.append(f"公开文件包含{label}：{path.relative_to(ROOT)}")

    if errors:
        print("CONTENT VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print("CONTENT VALIDATION PASSED")
    print(f"- Markdown 相对链接：{len(markdown_files)} 个文件")
    print(f"- TOML/JSON 解析：{len(toml_files)}/{len(json_files)} 个文件")
    print(f"- 公开文本隐私模式：{len(files)} 个文件")
    return 0


if __name__ == "__main__":
    sys.exit(main())
