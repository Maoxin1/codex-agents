"""Explicitly authorized paired evals; never invoked by offline validation/CI."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
import tomllib

ROOT = Path(__file__).resolve().parents[1]


def sandbox_overrides(codex_home: Path, *, windows: bool) -> list[str]:
    """Retain only the existing Windows isolation backend, not user preferences."""
    if not windows:
        return []
    path = codex_home / "config.toml"
    config = tomllib.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    mode = config.get("windows", {}).get("sandbox")
    if mode not in {"elevated", "unelevated"}:
        raise ValueError("Configure a supported Windows sandbox backend before model calls")
    return ["-c", "windows.sandbox=" + json.dumps(mode)]


def preflight_windows_read(cli: str, output: Path, overrides: list[str]) -> None:
    """Exercise the selected sandbox without contacting a model service."""
    shell = shutil.which("pwsh")
    if shell is None:
        raise ValueError("PowerShell is required for the Windows read preflight")
    with tempfile.TemporaryDirectory(prefix="read-preflight-", dir=output) as directory:
        fixture = Path(directory) / "fixture.txt"
        fixture.write_text("PUBLIC_READ_PREFLIGHT_OK", encoding="utf-8")
        command = [cli, "sandbox", "-P", ":read-only", *overrides, "-C", directory,
                   "--", shell, "-NoProfile", "-Command", "Get-Content -LiteralPath ./fixture.txt -Raw"]
        result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8",
                                errors="replace", timeout=30)
        if result.returncode or result.stdout.strip() != "PUBLIC_READ_PREFLIGHT_OK":
            raise ValueError("Windows read-only preflight failed; no model calls started")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--authorize-model-calls", action="store_true", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--model", default="gpt-6.1-sol")
    parser.add_argument("--reasoning", default="high")
    args = parser.parse_args()
    output = args.output.resolve()
    if output == ROOT or ROOT in output.parents:
        parser.error("Evaluation output must be outside the repository")
    output.mkdir(parents=True, exist_ok=False)
    cli = shutil.which("codex.cmd") or shutil.which("codex")
    if cli is None:
        parser.error("codex CLI is not available")
    if Path(cli).suffix.lower() == ".cmd":
        binaries = list(Path(cli).parent.glob("node_modules/@openai/codex/node_modules/@openai/codex-win32-*/vendor/*/bin/codex.exe"))
        if len(binaries) != 1:
            parser.error("Resolve the native codex executable before running Windows evals")
        cli = str(binaries[0])
    codex_home = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
    overrides = sandbox_overrides(codex_home, windows=os.name == "nt")
    if os.name == "nt":
        preflight_windows_read(cli, output, overrides)
    plan = (ROOT / "docs/evaluation-plan.md").read_text(encoding="utf-8")
    cases = []
    for line in plan.splitlines():
        if line.startswith("| `_"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            cases.append({"agent": cells[0].strip("`"), "input": cells[1]})
    if len(cases) != 8:
        parser.error("Expected exactly eight approved scenarios")
    manifest = json.loads((ROOT / "managed-files.json").read_text(encoding="utf-8"))
    hashes = {entry: hashlib.sha256((ROOT / entry).read_bytes()).hexdigest() for entry in manifest}
    (output / "environment.json").write_text(json.dumps({
        "model": args.model, "reasoning": args.reasoning, "source_books": "not-configured",
        "invocation": "developer-instructions-config-override; not-native-agent-dispatch",
        "cli_version": subprocess.check_output([cli, "--version"], text=True).strip(),
        "sandbox_overrides": overrides,
        "read_preflight": "passed" if os.name == "nt" else "not-run-on-this-platform",
        "package_sha256": hashes, "cases": cases,
        "started_utc": datetime.now(timezone.utc).isoformat(),
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    def run(case: dict, arm: str) -> dict:
        folder = output / (case["agent"] + "-" + arm)
        workspace = folder / "workspace"
        workspace.mkdir(parents=True)
        # Both arms see the same public package; no private overlay or book copied.
        for entry in manifest:
            relative = entry.removeprefix("agents/")
            if relative == case["agent"] + ".toml" or relative.startswith(case["agent"] + "/") or relative.startswith("_book_sources/"):
                target = workspace / entry
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / entry, target)
        config_path = workspace / "agents" / (case["agent"] + ".toml")
        config = tomllib.loads(config_path.read_text(encoding="utf-8"))
        context = (
            "This is a bounded consultation using synthetic supplied material. Answer in Chinese. "
            "Do not spawn agents, browse the internet, read unrelated private files, or modify files. "
            "You may read the provided public package if relevant. Clipboard copying is permitted "
            "when requested by your role; do not request permission escalation. "
            "No private source book is configured for this test."
        )
        instructions = context + (("\nThe loaded configuration is at " + str(config_path) + ".\n" + config["developer_instructions"]) if arm == "advisor" else "")
        command = [cli, "exec", "--ignore-user-config", "--ephemeral", "--skip-git-repo-check",
                   *overrides,
                   "--sandbox", "read-only", "--model", args.model,
                   "-c", "approval_policy=\"never\"", "-c", "project_doc_max_bytes=0",
                   "-c", "model_reasoning_effort=" + json.dumps(args.reasoning),
                   "-c", "developer_instructions=" + json.dumps(instructions, ensure_ascii=False),
                   "-c", "web_search=\"disabled\"", "-c", "features.apps=false",
                   "-C", str(workspace), "--json", "--output-last-message", str(folder / "answer.txt"), "-"]
        (folder / "input.txt").write_text(case["input"], encoding="utf-8")
        started = time.monotonic()
        record = {"agent": case["agent"], "arm": arm, "model": args.model,
                  "reasoning": args.reasoning, "status": "incomplete", "semantic_review": "pending"}
        try:
            with (folder / "events.jsonl").open("wb") as stdout, (folder / "stderr.log").open("wb") as stderr:
                result = subprocess.run(command, input=case["input"].encode("utf-8"),
                                        stdout=stdout, stderr=stderr, timeout=360)
            record["exit_code"] = result.returncode
            record["status"] = "completed" if result.returncode == 0 and (folder / "answer.txt").is_file() else "failed"
            events = []
            for line in (folder / "events.jsonl").read_text(encoding="utf-8", errors="replace").splitlines():
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
            record["usage"] = [e["usage"] for e in events if e.get("type") == "turn.completed" and "usage" in e]
            record["tool_items"] = [e["item"] for e in events if e.get("type") == "item.completed" and e.get("item", {}).get("type") in {"command_execution", "mcp_tool_call", "web_search", "file_change"}]
        except subprocess.TimeoutExpired:
            record["status"] = "timeout"
        finally:
            record["elapsed_seconds"] = round(time.monotonic() - started, 2)
            (folder / "record.json").write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({k: record[k] for k in ("agent", "arm", "status", "elapsed_seconds")}), flush=True)
        return record

    records = []
    # One pair at a time; a failed invocation stops before any later case.
    with ThreadPoolExecutor(max_workers=2) as executor:
        for case in cases:
            futures = [executor.submit(run, case, arm) for arm in ("baseline", "advisor")]
            pair = [future.result() for future in futures]
            records.extend(pair)
            (output / "summary.json").write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
            if any(record["status"] != "completed" for record in pair):
                return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
