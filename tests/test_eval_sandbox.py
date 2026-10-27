"""Prevent paid evals from silently losing the configured Windows backend."""
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("coding_eval", Path(__file__).with_name("run_coding_eval.py"))
evaluation = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(evaluation)


class SandboxPreflightTests(unittest.TestCase):
    def test_preserves_only_the_explicit_backend(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            (home / "config.toml").write_text(
                'model = "different-model"\nsandbox_mode = "danger-full-access"\n'
                '[windows]\nsandbox = "elevated"\n', encoding="utf-8")
            self.assertEqual(evaluation.sandbox_overrides(home, windows=True),
                             ["-c", 'windows.sandbox="elevated"'])
            self.assertEqual(evaluation.sandbox_overrides(home, windows=False), [])

    def test_missing_backend_stops_before_inference(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "before model calls"):
                evaluation.sandbox_overrides(Path(directory), windows=True)

    def test_failed_or_wrong_read_is_rejected(self):
        for code, output in [(1, ""), (0, "wrong value")]:
            with self.subTest(code=code), tempfile.TemporaryDirectory() as directory:
                with patch.object(evaluation.shutil, "which", return_value="pwsh"), \
                     patch.object(evaluation.subprocess, "run", return_value=subprocess.CompletedProcess([], code, output, "")):
                    with self.assertRaisesRegex(ValueError, "no model calls started"):
                        evaluation.preflight_windows_read("codex", Path(directory), ["-c", 'windows.sandbox="elevated"'])

    def test_read_preflight_retains_readonly_profile(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(evaluation.shutil, "which", return_value="pwsh"), \
                 patch.object(evaluation.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, "PUBLIC_READ_PREFLIGHT_OK\n", "")) as run:
                evaluation.preflight_windows_read("codex", Path(directory), ["-c", 'windows.sandbox="elevated"'])
                command = run.call_args.args[0]
                self.assertIn(":read-only", command)
                self.assertIn('windows.sandbox="elevated"', command)
                self.assertNotIn("danger-full-access", " ".join(command))
