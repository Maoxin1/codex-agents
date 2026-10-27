"""Offline source-reader regressions; synthetic text only, no model calls."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import tomllib
import unittest
import zipfile

PACKAGE = Path(__file__).resolve().parents[1] / "agents" / "_wayne"
SPEC = importlib.util.spec_from_file_location("wayne_source", PACKAGE / "source.py")
source = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(source)

XML = b'''<html><body><section id="ch01"><h1>Chapter</h1>
<h2 id="a">Question</h2><p>A syn<span>thetic</span> example.</p>
<ul><li>First item</li><li><p>Second item</p></li></ul>
<h3 id="child">Details</h3><p>Nested text.</p>
<h2 id="b">Boundary</h2><p>Other section.</p></section></body></html>'''


class WayneSourceTests(unittest.TestCase):

    def test_nested_container_cannot_cross_heading_boundary(self):
        xml = b'<html><body><h1 id="one">One</h1><blockquote><p>IN_SCOPE</p><h1 id="two">Two</h1>OUTSIDE_TAIL<p>OUT_OF_SCOPE</p></blockquote></body></html>'
        self.assertEqual(source.section(xml, "one").split("\n\n"), ["One", "IN_SCOPE"])
        self.assertIn("OUT_OF_SCOPE", source.section(xml, "two"))
    def test_mixed_nested_blocks_preserve_text_once_in_order(self):
        xml = b'<html><body><section id="chapter"><ul><li>BEFORE<ul><li>INNER</li></ul>AFTER</li></ul><blockquote>QUOTE<p>BODY <em>inline</em></p>TAIL</blockquote><table><tr><td>CELL<p>DETAIL</p>END</td></tr></table></section></body></html>'
        value = source.section(xml, "chapter")
        expected = ["BEFORE", "INNER", "AFTER", "QUOTE", "BODY inline", "TAIL", "CELL", "DETAIL", "END"]
        self.assertEqual(value.split("\n\n"), expected)

    def test_section_boundaries_and_nested_list_text(self):
        value = source.section(XML, "a")
        self.assertIn("A synthetic example.", value)
        self.assertEqual(value.count("Second item"), 1)
        self.assertIn("First item", value)
        self.assertIn("Nested text.", value)
        self.assertNotIn("Other section", value)
        self.assertIn("Other section", source.section(XML, "ch01"))

    def test_bad_xml_missing_anchor_and_entity_rejected(self):
        for xml, anchor in [(b"<broken", "a"), (XML, "missing"),
                            (b'<!DOCTYPE x [<!ENTITY e "text">]><x/>', "a")]:
            with self.subTest(xml=xml):
                with self.assertRaises((ValueError, source.ET.ParseError)):
                    source.section(xml, anchor)

    def test_normalization_preserves_words(self):
        self.assertEqual(source.normalize("re\u00adsearch\u00a0  notes"), "research notes")

    def test_fingerprint_and_all_anchors(self):
        with tempfile.TemporaryDirectory() as folder:
            book = Path(folder) / "synthetic.epub"
            with zipfile.ZipFile(book, "w") as archive:
                archive.writestr("chapter.xhtml", XML)
            manifest = {"sha256": hashlib.sha256(book.read_bytes()).hexdigest(),
                        "chapters": [{"number": 1, "href": "chapter.xhtml", "anchor": "ch01"}],
                        "principles": [{"id": "W01", "chapter": 1,
                                        "anchors": [{"id": "a", "heading": "Question"}]}]}
            self.assertEqual(source.check_source(book, manifest), 1)
            manifest["principles"][0]["anchors"][0]["heading"] = "Wrong heading"
            with self.assertRaisesRegex(ValueError, "Heading mismatch"):
                source.check_source(book, manifest)
            manifest["sha256"] = "0" * 64
            with self.assertRaisesRegex(ValueError, "fingerprint mismatch"):
                source.open_book(book, manifest)

    def test_cli_read_is_bounded_and_configure_checks_before_write(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            script = root / "source.py"
            script.write_bytes((PACKAGE / "source.py").read_bytes())
            book = root / "fixture.epub"
            with zipfile.ZipFile(book, "w") as archive:
                archive.writestr("chapter.xhtml", XML)
            manifest = {"sha256": hashlib.sha256(book.read_bytes()).hexdigest(),
                        "chapters": [{"number": 1, "href": "chapter.xhtml", "anchor": "ch01"}],
                        "principles": []}
            (root / "sources.json").write_text(json.dumps(manifest), encoding="utf-8")
            def run(*args):
                environment = dict(os.environ)
                environment.pop("WAYNE_SOURCE_EPUB", None)
                return subprocess.run([sys.executable, str(script), *args], capture_output=True,
                                      text=True, env=environment)
            result = run("read", "--epub", str(book), "--chapter", "1", "--anchor", "a", "--limit", "9")
            self.assertEqual(result.returncode, 0, result.stderr)
            output = json.loads(result.stdout)
            self.assertEqual(len(output["text"]), 9)
            self.assertTrue(output["has_more"])
            self.assertFalse((root / "source.local.json").exists())
            self.assertEqual(run("read", "--epub", str(book), "--chapter", "1", "--limit", "12001").returncode, 2)
            self.assertEqual(run("configure", "--epub", str(root / "missing.epub")).returncode, 2)
            self.assertFalse((root / "source.local.json").exists())
            self.assertEqual(run("configure", "--epub", str(book)).returncode, 0)
            self.assertEqual(run("check").returncode, 0)

    def test_published_routes_and_source_locations_resolve(self):
        manifest = json.loads((PACKAGE / "sources.json").read_text(encoding="utf-8"))
        self.assertEqual([c["number"] for c in manifest["chapters"]], list(range(1, 19)))
        self.assertEqual(len({p["id"] for p in manifest["principles"]}), 9)
        for principle in manifest["principles"]:
            text = (PACKAGE / principle["reference"]).read_text(encoding="utf-8")
            self.assertIn(principle["id"], text)
            for anchor in principle["anchors"]:
                self.assertIn(anchor["id"], text)
        config = tomllib.loads((PACKAGE.parent / "_wayne.toml").read_text(encoding="utf-8"))
        self.assertEqual(config["name"], "_wayne")
        self.assertNotIn("model", config)  # Intentionally inherits the caller's model.


if __name__ == "__main__":
    unittest.main()
