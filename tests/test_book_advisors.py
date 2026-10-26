"""Offline shared-source and package checks; no private books or paid model calls."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest
import zipfile

AGENTS = Path(__file__).resolve().parents[1] / "agents"
SPEC = importlib.util.spec_from_file_location("book_epub", AGENTS / "_book_sources" / "epub.py")
epub = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(epub)

XML = b'''<!DOCTYPE html><html><head><title>Not content</title></head><body>
<h1 id="one">Chapter One</h1><h2>Repeated title</h2>
<p>A &ldquo;quoted&rdquo; syn<span>thetic</span> &amp; example.</p>
<ul><li>First</li><li><p>Second</p></li></ul>
<h3>Subsection</h3><p>Nested text.</p>
<h1 id="two">Chapter Two</h1><h2>Repeated title</h2><p>Other content.</p>
<h2>Unique title</h2><p>Other details.</p></body></html>'''


class SharedSourceTests(unittest.TestCase):
    def test_html_entities_inline_text_and_nested_lists(self):
        value = epub.section(XML, "text:Repeated title", within="one")
        self.assertIn('A “quoted” synthetic & example.', value)
        self.assertEqual(value.count("Second"), 1)
        self.assertIn("Nested text", value)
        self.assertNotIn("Other content", value)
        self.assertNotIn("Not content", epub.section(XML, "@document"))

    def test_repeated_headings_are_scoped_to_selected_chapter(self):
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            epub.section(XML, "text:Repeated title")
        value = epub.section(XML, "text:Repeated title", within="two")
        self.assertIn("Other content", value)
        self.assertNotIn("First", value)
        with self.assertRaisesRegex(ValueError, "missing"):
            epub.section(XML, "text:Unique title", within="one")
        self.assertNotIn("Chapter Two", epub.section(XML, "one"))

    def test_unreadable_sources_are_explicit(self):
        for xml in [b"<broken", b'<html><p>&unknownEntity;</p></html>',
                    b'<!DOCTYPE html SYSTEM "remote.dtd"><html/>',
                    b'<!DOCTYPE html [<!ENTITY x "value">]><html/>']:
            with self.subTest(xml=xml):
                with self.assertRaises((ValueError, epub.ET.ParseError)):
                    epub.section(xml, "@document")

    def test_limits_apply_before_decompression_and_xml_parsing(self):
        with self.assertRaisesRegex(ValueError, "size limit"):
            epub.section(b"x" * (epub.MAX_MEMBER_BYTES + 1), "@document")
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "fixture.epub"
            with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as book:
                book.writestr("large.xhtml", b"x" * (epub.MAX_MEMBER_BYTES + 1))
            with zipfile.ZipFile(path) as book:
                with self.assertRaisesRegex(ValueError, "size limit"):
                    epub.read_section(book, {"href": "large.xhtml", "anchor": "@document"}, "@document")

    def test_fingerprint_and_heading_mismatch(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "fixture.epub"
            with zipfile.ZipFile(path, "w") as book:
                book.writestr("chapter.xhtml", XML)
            manifest = {"sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                        "chapters": [{"number": 1, "href": "chapter.xhtml", "anchor": "one"}],
                        "principles": [{"id": "X01", "chapter": 1,
                                        "anchors": [{"id": "text:Repeated title", "heading": "Repeated title"}]}]}
            self.assertEqual(epub.check_source(path, manifest), 1)
            manifest["principles"][0]["anchors"][0]["heading"] = "Wrong"
            with self.assertRaisesRegex(ValueError, "Heading mismatch"):
                epub.check_source(path, manifest)
            manifest["sha256"] = "0" * 64
            with self.assertRaisesRegex(ValueError, "fingerprint mismatch"):
                epub.open_book(path, manifest)

    def test_installed_layout_cli_and_private_configuration(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            package = root / "_clayton"
            package.mkdir()
            shutil.copytree(AGENTS / "_book_sources", root / "_book_sources",
                            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            script = package / "source.py"
            script.write_bytes((AGENTS / "_clayton" / "source.py").read_bytes())
            path = root / "fixture.epub"
            with zipfile.ZipFile(path, "w") as book:
                book.writestr("chapter.xhtml", XML)
            manifest = {"sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                        "chapters": [{"number": 1, "href": "chapter.xhtml", "anchor": "one"}],
                        "principles": []}
            (package / "sources.json").write_text(json.dumps(manifest), encoding="utf-8")
            environment = dict(os.environ)
            environment.pop("CLAYTON_SOURCE_EPUB", None)
            environment.pop("PYTHONDONTWRITEBYTECODE", None)
            environment["PYTHONIOENCODING"] = "utf-8"
            def run(*args):
                return subprocess.run([sys.executable, str(script), *args], env=environment,
                                      capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(run("check").returncode, 2)
            local = package / "source.local.json"
            local.write_text('[]', encoding="utf-8")
            result = run("check")
            self.assertEqual(result.returncode, 2)
            self.assertIn("SOURCE UNAVAILABLE", result.stderr)
            result = run("configure", "--epub", str(root / "absent.epub"))
            self.assertEqual(result.returncode, 2)
            self.assertEqual(local.read_text(encoding="utf-8"), '[]')
            self.assertEqual(run("configure", "--epub", str(path)).returncode, 0)
            before = local.read_bytes()
            result = run("read", "--chapter", "1", "--limit", "12", "--offset", "2")
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(len(payload["text"]), 12)
            self.assertTrue(payload["has_more"])
            self.assertEqual(local.read_bytes(), before)
            environment["PYTHONIOENCODING"] = "ascii"
            result = run("read", "--chapter", "1", "--limit", "1000")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("“quoted”", json.loads(result.stdout)["text"])
            self.assertEqual(run("read", "--chapter", "1", "--limit", "12001").returncode, 2)
            self.assertEqual(run("read", "--chapter", "1", "--anchor", "text:Unique title").returncode, 2)
            environment["CLAYTON_SOURCE_EPUB"] = str(root / "absent.epub")
            self.assertEqual(run("check").returncode, 2)
            self.assertEqual(run("check", "--epub", str(path)).returncode, 0)
            self.assertFalse(list(root.rglob("__pycache__")), "Read commands wrote bytecode caches")


class AdvisorPackageTests(unittest.TestCase):
    def test_manifests_routes_and_pending_behavior_assets(self):
        for name, count, units in [("_clayton", 9, 10), ("_alan", 9, 19), ("_jim", 10, 8)]:
            with self.subTest(agent=name):
                package = AGENTS / name
                config = tomllib.loads((AGENTS / (name + ".toml")).read_text(encoding="utf-8"))
                self.assertEqual(config["name"], name)
                self.assertNotIn("model", config)
                for required in ["core.md", "principles.md", "source.py", "README.md", "validation.md"]:
                    self.assertTrue((package / required).is_file(), required)
                manifest = json.loads((package / "sources.json").read_text(encoding="utf-8"))
                self.assertEqual([c["number"] for c in manifest["chapters"]], list(range(1, units + 1)))
                self.assertEqual(len({p["id"] for p in manifest["principles"]}), count)
                for principle in manifest["principles"]:
                    reference = (package / principle["reference"]).read_text(encoding="utf-8")
                    self.assertIn(principle["id"], reference)
                    for anchor in principle["anchors"]:
                        self.assertIn(anchor["id"], reference)
                cases = json.loads((package / "tests" / "cases.json").read_text(encoding="utf-8"))
                self.assertEqual(cases["status"], "not-run")
                self.assertEqual(len({c["id"] for c in cases["cases"]}), len(cases["cases"]))
                self.assertTrue(all(c.get("acceptance") and c.get("failure") for c in cases["cases"]))


if __name__ == "__main__":
    unittest.main()
