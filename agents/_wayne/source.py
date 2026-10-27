"""Read bounded sections of a privately supplied, fingerprinted EPUB. Stdlib only."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import unicodedata
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parent
MAX_BOOK_BYTES = 64 * 1024 * 1024
MAX_MEMBER_BYTES = 4 * 1024 * 1024


def normalize(value: str) -> str:
    return " ".join(unicodedata.normalize("NFC", value).replace("\u00ad", "").split())


def tag(element: ET.Element) -> str:
    return element.tag.rsplit("}", 1)[-1]


def block_text(node: ET.Element, block_tags: set[str]) -> list[str]:
    """Keep mixed text in document order, separating nested block boundaries."""
    def render(element: ET.Element) -> str:
        parts = [element.text or ""]
        for child in element:
            boundary = "\n\n" if tag(child) in block_tags else ""
            parts.extend((boundary, render(child), boundary, child.tail or ""))
        return "".join(parts)
    return [value for part in render(node).split("\n\n") if (value := normalize(part))]


def section(xml: bytes, anchor: str) -> str:
    if len(xml) > MAX_MEMBER_BYTES or b"<!DOCTYPE" in xml.upper() or b"<!ENTITY" in xml.upper():
        raise ValueError("Oversized or entity-bearing source document")
    nodes = list(ET.fromstring(xml).iter())
    start = next((i for i, node in enumerate(nodes) if node.get("id") == anchor), None)
    if start is None:
        raise ValueError(f"Source anchor not found: {anchor}")
    heading = tag(nodes[start])
    headings = {"h1", "h2", "h3", "h4", "h5", "h6"}
    if heading in headings:
        level = int(heading[1])
        selected = nodes[start:]
    elif heading == "section":
        level = 0
        selected = list(nodes[start].iter())
    else:
        raise ValueError("Requested anchor must identify a heading or section")
    blocks = []
    consumed = set()
    for i, node in enumerate(selected):
        kind = tag(node)
        if i and level and kind in headings and int(kind[1]) <= level:
            break
        block_tags = headings | {"p", "li", "td", "th", "blockquote", "figcaption"}
        if kind in block_tags and node not in consumed:
            blocks.extend(block_text(node, block_tags))
            consumed.update(node.iter())
    return "\n\n".join(blocks)


def open_book(path: Path, manifest: dict) -> zipfile.ZipFile:
    if not path.is_file():
        raise ValueError("Local source file is missing")
    if path.stat().st_size > MAX_BOOK_BYTES:
        raise ValueError("Source exceeds size limit")
    if hashlib.sha256(path.read_bytes()).hexdigest() != manifest["sha256"]:
        raise ValueError("Source fingerprint mismatch; this edition/file needs re-anchoring")
    return zipfile.ZipFile(path)


def read_section(book: zipfile.ZipFile, chapter: dict, anchor: str) -> str:
    member = book.getinfo(chapter["href"])
    if member.file_size > MAX_MEMBER_BYTES:
        raise ValueError("Source chapter exceeds size limit")
    return section(book.read(member), anchor)


def check_source(path: Path, manifest: dict) -> int:
    count = 0
    with open_book(path, manifest) as book:
        for chapter in manifest["chapters"]:
            read_section(book, chapter, chapter["anchor"])
        by_number = {c["number"]: c for c in manifest["chapters"]}
        for principle in manifest["principles"]:
            for anchor in principle["anchors"]:
                value = read_section(book, by_number[principle["chapter"]], anchor["id"])
                if normalize(anchor["heading"]) not in normalize(value.split("\n\n", 1)[0]):
                    raise ValueError(f"Heading mismatch: {principle['id']} / {anchor['id']}")
                count += 1
    return count


def source_path(explicit: str | None) -> Path:
    value = explicit or os.environ.get("WAYNE_SOURCE_EPUB")
    if not value:
        config = ROOT / "source.local.json"
        if config.is_file():
            value = json.loads(config.read_text(encoding="utf-8"))["epub"]
    if not value:
        raise ValueError("No local source configured; use verified principles only")
    path = Path(value).expanduser()
    if not path.is_absolute():
        raise ValueError("Source path must be absolute")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["check", "read", "configure"])
    parser.add_argument("--epub", help="Absolute path to a lawfully held local EPUB")
    parser.add_argument("--chapter", type=int)
    parser.add_argument("--anchor", help="Heading ID; defaults to chapter heading")
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--limit", type=int, default=6000)
    args = parser.parse_args(argv)
    try:
        manifest = json.loads((ROOT / "sources.json").read_text(encoding="utf-8"))
        path = source_path(args.epub)
        if args.command in {"check", "configure"}:
            count = check_source(path, manifest)
            if args.command == "configure":
                (ROOT / "source.local.json").write_text(
                    json.dumps({"epub": str(path)}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(json.dumps({"status": "verified", "chapters": len(manifest["chapters"]),
                              "principle_anchors": count, "configured": args.command == "configure"}))
        else:
            if not 1 <= args.limit <= 12000 or args.offset < 0:
                raise ValueError("limit must be 1..12000 and offset must be nonnegative")
            chapter = next((c for c in manifest["chapters"] if c["number"] == args.chapter), None)
            if chapter is None:
                raise ValueError("Choose a chapter number listed in sources.json")
            anchor = args.anchor or chapter["anchor"]
            with open_book(path, manifest) as book:
                value = read_section(book, chapter, anchor)
            print(json.dumps({"chapter": args.chapter, "location": chapter["href"] + "#" + anchor,
                              "offset": args.offset, "total_characters": len(value),
                              "has_more": args.offset + args.limit < len(value),
                              "text": value[args.offset:args.offset + args.limit]}, ensure_ascii=False))
        return 0
    except (OSError, ValueError, KeyError, ET.ParseError, zipfile.BadZipFile) as exc:
        print(f"SOURCE UNAVAILABLE: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
