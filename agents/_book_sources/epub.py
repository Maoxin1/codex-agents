"""Bounded, fingerprint-checked private EPUB access for book-advisor packages."""
from __future__ import annotations

import argparse
import hashlib
from html.entities import html5
import json
import os
from pathlib import Path
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET
import zipfile

MAX_BOOK_BYTES = 64 * 1024 * 1024
MAX_MEMBER_BYTES = 4 * 1024 * 1024
HEADINGS = {"h1", "h2", "h3", "h4", "h5", "h6"}
BLOCKS = HEADINGS | {"p", "li", "td", "th", "blockquote", "figcaption"}


def normalize(value: str) -> str:
    return " ".join(unicodedata.normalize("NFC", value).replace("\u00ad", "").split())


def tag(node: ET.Element) -> str:
    return node.tag.rsplit("}", 1)[-1]


def block_text(node: ET.Element, block_tags: set[str]) -> list[str]:
    """Keep mixed text in document order, separating nested block boundaries."""
    def render(element: ET.Element) -> str:
        parts = [element.text or ""]
        for child in element:
            boundary = "\n\n" if tag(child) in block_tags else ""
            parts.extend((boundary, render(child), boundary, child.tail or ""))
        return "".join(parts)
    return [value for part in render(node).split("\n\n") if (value := normalize(part))]


def section(xml: bytes, anchor: str, within: str = "@document") -> str:
    if len(xml) > MAX_MEMBER_BYTES:
        raise ValueError("Source document exceeds size limit")
    # Accept only the declaration present in these HTML5 EPUBs; no entities/DTDs.
    xml = re.sub(br"<!DOCTYPE\s+html\s*>", b"", xml, flags=re.IGNORECASE)
    if b"<!DOCTYPE" in xml.upper() or b"<!ENTITY" in xml.upper():
        raise ValueError("Entity-bearing or unsupported document declaration")
    def entity(match: re.Match[str]) -> str:
        value = html5.get(match[1] + ";")
        return "".join(f"&#{ord(c)};" for c in value) if value is not None else match[0]
    xml = re.sub(r"&([A-Za-z][A-Za-z0-9]+);", entity, xml.decode("utf-8")).encode("utf-8")
    root = ET.fromstring(xml)
    body = next((e for e in root.iter() if tag(e) == "body"), root)
    nodes = list(body.iter())

    def select(candidates: list[ET.Element], locator: str) -> list[ET.Element]:
        if locator == "@document":
            return candidates
        if locator.startswith("text:"):
            expected = normalize(locator[5:])
            matches = [i for i, e in enumerate(candidates)
                       if tag(e) in HEADINGS and normalize("".join(e.itertext())) == expected]
        else:
            matches = [i for i, e in enumerate(candidates) if e.get("id") == locator]
        if len(matches) != 1:
            raise ValueError(f"Source anchor missing or ambiguous: {locator}")
        start = matches[0]
        node = candidates[start]
        if tag(node) in HEADINGS:
            level = int(tag(node)[1])
            end = next((i for i in range(start + 1, len(candidates))
                        if tag(candidates[i]) in HEADINGS and int(tag(candidates[i])[1]) <= level), len(candidates))
            return candidates[start:end]
        elif tag(node) in {"section", "div"}:
            return list(node.iter())
        raise ValueError("Anchor must identify a heading or content container")

    selected = select(select(nodes, within), anchor)
    blocks = []
    consumed = set()
    for node in selected:
        kind = tag(node)
        if kind in BLOCKS and node not in consumed:
            blocks.extend(block_text(node, BLOCKS))
            consumed.update(node.iter())
    value = "\n\n".join(blocks)
    if not value:
        raise ValueError("Source section has no readable text")
    return value


def open_book(path: Path, manifest: dict) -> zipfile.ZipFile:
    if not path.is_file():
        raise ValueError("Local source file is missing")
    if path.stat().st_size > MAX_BOOK_BYTES:
        raise ValueError("Source exceeds size limit")
    if hashlib.sha256(path.read_bytes()).hexdigest() != manifest["sha256"]:
        raise ValueError("Source fingerprint mismatch; verify and re-anchor this file first")
    return zipfile.ZipFile(path)


def read_section(book: zipfile.ZipFile, chapter: dict, anchor: str) -> str:
    member = book.getinfo(chapter["href"])
    if member.file_size > MAX_MEMBER_BYTES:
        raise ValueError("Source chapter exceeds size limit")
    return section(book.read(member), anchor, within=chapter["anchor"])


def check_source(path: Path, manifest: dict) -> int:
    count = 0
    with open_book(path, manifest) as book:
        chapters = {c["number"]: c for c in manifest["chapters"]}
        for chapter in chapters.values():
            read_section(book, chapter, chapter["anchor"])
        for principle in manifest["principles"]:
            for anchor in principle["anchors"]:
                value = read_section(book, chapters[principle["chapter"]], anchor["id"])
                if normalize(value.split("\n\n", 1)[0]) != normalize(anchor["heading"]):
                    raise ValueError(f"Heading mismatch: {principle['id']} / {anchor['id']}")
                count += 1
    return count


def source_path(package: Path, explicit: str | None) -> Path:
    value = explicit or os.environ.get(package.name.lstrip("_").upper() + "_SOURCE_EPUB")
    if not value and (package / "source.local.json").is_file():
        config = json.loads((package / "source.local.json").read_text(encoding="utf-8"))
        if not isinstance(config, dict):
            raise ValueError("Local source configuration must be an object")
        value = config.get("epub")
    if not isinstance(value, str) or not value.strip():
        raise ValueError("No valid local source configured; use verified principles only")
    path = Path(value).expanduser()
    if not path.is_absolute():
        raise ValueError("Source path must be absolute")
    return path


def main(package: Path, argv: list[str] | None = None) -> int:
    # Stable JSON output even when Windows launches Python with a legacy encoding.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["check", "read", "configure"])
    parser.add_argument("--epub", help="Absolute path to a lawfully held matching EPUB")
    parser.add_argument("--chapter", type=int)
    parser.add_argument("--anchor", help="EPUB ID or exact heading prefixed with text:")
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--limit", type=int, default=6000)
    args = parser.parse_args(argv)
    try:
        manifest = json.loads((package / "sources.json").read_text(encoding="utf-8"))
        path = source_path(package, args.epub)
        if args.command in {"check", "configure"}:
            count = check_source(path, manifest)
            if args.command == "configure":
                (package / "source.local.json").write_text(
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
            print(json.dumps({"chapter": args.chapter, "member": chapter["href"], "anchor": anchor,
                              "offset": args.offset, "total_characters": len(value),
                              "has_more": args.offset + args.limit < len(value),
                              "text": value[args.offset:args.offset + args.limit]}, ensure_ascii=False))
        return 0
    except (OSError, ValueError, KeyError, TypeError, ET.ParseError, zipfile.BadZipFile) as exc:
        print(f"SOURCE UNAVAILABLE: {exc}", file=sys.stderr)
        return 2
