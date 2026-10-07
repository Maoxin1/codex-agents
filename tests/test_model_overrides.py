from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AGENTS = {
    "_factbot": ("gpt-5.6-terra", "不得修改文件"),
    "_invest": ("gpt-5.6-sol", "不执行证券交易"),
    "_mantou": ("gpt-5.6-sol", "Get-Clipboard -Raw"),
    "_manuel": ("gpt-5.6-terra", "unrelated private files"),
}
# Synthetic identifier: these tests never call a model service.
ALTERNATIVE_MODEL = "local-test-model"


class ModelOverrideTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        shutil.copytree(
            ROOT / "agents",
            self.root / "agents",
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )
        # Tests must also work in a checkout with intentional local model overrides.
        for agent, (default_model, _) in AGENTS.items():
            self.set_model(agent, default_model)

    def config_path(self, agent: str) -> Path:
        return self.root / "agents" / f"{agent}.toml"

    def replace(self, agent: str, old: str, new: str) -> None:
        path = self.config_path(agent)
        content = path.read_text(encoding="utf-8")
        self.assertIn(old, content)
        path.write_text(content.replace(old, new), encoding="utf-8")

    def set_model(self, agent: str, model: object) -> None:
        path = self.config_path(agent)
        content = path.read_text(encoding="utf-8")
        content = re.sub(
            r"^model = .*?$",
            lambda _: "model = " + json.dumps(model),
            content,
            count=1,
            flags=re.MULTILINE,
        )
        path.write_text(content, encoding="utf-8")

    def run_validator(self, agent: str, *, override: bool = False) -> subprocess.CompletedProcess[str]:
        validator = self.root / "agents" / agent / "tests" / f"validate{agent}.py"
        command = [sys.executable, str(validator)]
        if override:
            command.append("--allow-model-override")
        environment = os.environ.copy()
        environment.pop("INVEST_VAULT_PATH", None)
        environment.pop("MANUEL_SOURCE_PDF", None)
        environment["PYTHONIOENCODING"] = "utf-8"
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        return subprocess.run(
            command,
            cwd=self.root,
            env=environment,
            text=True,
            encoding="utf-8",
            capture_output=True,
            timeout=30,
            check=False,
        )

    def assert_result(self, agent: str, *, override: bool, succeeds: bool) -> None:
        result = self.run_validator(agent, override=override)
        output = result.stdout + result.stderr
        if succeeds:
            self.assertEqual(result.returncode, 0, output)
        else:
            self.assertEqual(result.returncode, 1, output)
            self.assertIn("VALIDATION FAILED", output)

    def test_release_defaults_pass(self) -> None:
        for agent in AGENTS:
            with self.subTest(agent=agent):
                self.assert_result(agent, override=False, succeeds=True)

    def test_release_validation_rejects_alternative_models(self) -> None:
        for agent in AGENTS:
            with self.subTest(agent=agent):
                self.set_model(agent, ALTERNATIVE_MODEL)
                self.assert_result(agent, override=False, succeeds=False)

    def test_explicit_local_override_accepts_alternative_models(self) -> None:
        for agent in AGENTS:
            with self.subTest(agent=agent):
                self.set_model(agent, ALTERNATIVE_MODEL)
                self.assert_result(agent, override=True, succeeds=True)

    def test_local_mode_also_accepts_release_defaults(self) -> None:
        for agent in AGENTS:
            with self.subTest(agent=agent):
                self.assert_result(agent, override=True, succeeds=True)

    def test_override_rejects_invalid_model_identifiers(self) -> None:
        for agent in AGENTS:
            for model in ("", "  ", "model with spaces", 42):
                with self.subTest(agent=agent, model=model):
                    self.set_model(agent, model)
                    self.assert_result(agent, override=True, succeeds=False)

    def test_override_rejects_missing_model(self) -> None:
        for agent, (default_model, _) in AGENTS.items():
            with self.subTest(agent=agent):
                self.replace(agent, f'model = "{default_model}"\n', "")
                self.assert_result(agent, override=True, succeeds=False)

    def test_override_preserves_reasoning_checks(self) -> None:
        for agent in AGENTS:
            with self.subTest(agent=agent):
                self.set_model(agent, ALTERNATIVE_MODEL)
                reasoning = "medium" if agent == "_manuel" else "high"
                self.replace(agent, f'model_reasoning_effort = "{reasoning}"', 'model_reasoning_effort = "low"')
                self.assert_result(agent, override=True, succeeds=False)

    def test_override_preserves_read_only_sandboxes(self) -> None:
        for agent in ("_factbot", "_mantou", "_manuel"):
            with self.subTest(agent=agent):
                self.set_model(agent, ALTERNATIVE_MODEL)
                self.replace(agent, 'sandbox_mode = "read-only"', 'sandbox_mode = "workspace-write"')
                self.assert_result(agent, override=True, succeeds=False)

    def test_override_preserves_agent_boundary_checks(self) -> None:
        for agent, (_, boundary) in AGENTS.items():
            with self.subTest(agent=agent):
                self.set_model(agent, ALTERNATIVE_MODEL)
                self.replace(agent, boundary, "removed-boundary-fixture")
                self.assert_result(agent, override=True, succeeds=False)

    def test_override_preserves_private_path_checks(self) -> None:
        for agent in AGENTS:
            with self.subTest(agent=agent):
                self.set_model(agent, ALTERNATIVE_MODEL)
                private_path = "\\".join(("C:", "Users", "Synthetic", "fixture"))
                escaped_path = private_path.replace("\\", "\\\\")
                opening = 'developer_instructions = """\n'
                self.replace(agent, opening, opening + escaped_path + "\n")
                self.assert_result(agent, override=True, succeeds=False)


if __name__ == "__main__":
    unittest.main()
