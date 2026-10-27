"""Exercise evaluation bookkeeping with a fake CLI; no model calls."""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("pwsh"), "PowerShell required")
class EvaluationRecordTests(unittest.TestCase):
    def test_pass_failure_and_cli_error_preserve_records(self):
        script = ROOT / "agents/_manuel/tests/run_behavior_eval.ps1"
        for answer, code, expected in [
            ("未核实事实性主张，需要比较因果，证据不足，可能。", 0, "smoke-passed"),
            ("unrelated answer", 0, "smoke-failed"),
            ("", 7, "cli-failed"),
        ]:
            with self.subTest(expected=expected), tempfile.TemporaryDirectory() as folder:
                # PowerShell single-quoted data literals; never invoke a real codex.
                quote = lambda value: "'" + str(value).replace("'", "''") + "'"
                wrapper = Path(folder) / "fake.ps1"
                wrapper.write_text(
                    "function global:codex {\n"
                    " $idx = [Array]::IndexOf($args, '--output-last-message')\n"
                    f" Set-Content -LiteralPath $args[$idx + 1] -Value {quote(answer)} -Encoding utf8\n"
                    f" $global:LASTEXITCODE = {code}\n"
                    " Write-Output 'synthetic CLI log'\n}\n"
                    f"& {quote(script)} -OutputDirectory {quote(folder)}\nexit $LASTEXITCODE\n",
                    encoding="utf-8")
                result = subprocess.run(["pwsh", "-NoProfile", "-File", str(wrapper)],
                                        capture_output=True, text=True, encoding="utf-8")
                self.assertEqual(result.returncode, 0 if expected == "smoke-passed" else code or 1,
                                 result.stdout + result.stderr)
                records = list(Path(folder).glob("*/record.json"))
                self.assertEqual(len(records), 1, result.stdout + result.stderr)
                record = json.loads(records[0].read_text(encoding="utf-8-sig"))
                self.assertEqual(record["status"], expected)
                self.assertEqual(record["semantic_review"], "pending")
                self.assertEqual(record["invocation"], "standalone-config-loading")
                self.assertTrue((records[0].parent / "answer.txt").is_file())
                self.assertIn("synthetic CLI log", (records[0].parent / "cli.log").read_text(encoding="utf-8-sig"))
