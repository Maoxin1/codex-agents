from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate_invest  # noqa: E402


class PublicFilesTests(unittest.TestCase):
    def test_private_runtime_overlay_is_excluded(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "_invest"
            root.mkdir()
            config = Path(directory) / "_invest.toml"
            config.write_text('name = "_invest"', encoding="utf-8")
            public = root / "knowledge-map.md"
            public.write_text("public", encoding="utf-8")
            private = root / "knowledge-map.local.md"
            private.write_text("D:" + r"\private\vault", encoding="utf-8")

            files = validate_invest.public_files(root=root, config=config)

            self.assertIn(config, files)
            self.assertIn(public, files)
            self.assertNotIn(private, files)


if __name__ == "__main__":
    unittest.main()
