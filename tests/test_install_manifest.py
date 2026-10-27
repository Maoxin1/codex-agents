"""Ensure newly packaged agent files cannot silently miss installation."""
import json
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


class InstallManifestTests(unittest.TestCase):
    def test_manifest_matches_versioned_agent_files(self):
        files = json.loads((ROOT / "managed-files.json").read_text(encoding="utf-8"))
        self.assertEqual(len(files), len(set(files)))
        for name in files:
            self.assertTrue(name.startswith("agents/"))
            self.assertNotIn("..", Path(name).parts)
            self.assertNotIn(Path(name).name, {"source.local.json", "knowledge-map.local.md"})
            self.assertTrue((ROOT / name).is_file(), name)
        result = subprocess.run(["git", "ls-files", "agents"], cwd=ROOT,
                                capture_output=True, text=True)
        if result.returncode == 0:
            self.assertEqual(set(files), set(result.stdout.splitlines()))
