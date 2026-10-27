# Contributing

Contributions should keep each agent portable, reviewable, and safe to publish.

## Before opening a pull request

1. Create a branch from `main` and keep the change focused on one concern.
2. Update an agent's TOML, supporting files, tests, documentation, and changelog together when their contract changes.
3. Use synthetic examples. Never commit API keys, private vault paths, holdings, case indexes, or note content.
4. Run the local validation commands below from PowerShell at the repository root.

```powershell
./tests/validate_repository.ps1
```

The repository validator runs the installer regression, all four established agent validators, book-advisor offline source-reader and package tests,
local-model-override regressions, `_invest` unit tests, PowerShell parsing, and TOML
parsing. Individual validators may be run while developing a focused change.
Keep the default strict mode for contributions and releases. The explicit local
override mode described in [COMPATIBILITY.md](COMPATIBILITY.md) does not qualify
changed model defaults for publication.

Behavior evaluation can require a configured Codex environment and is not part of the default CI. Follow the relevant agent's test README and state what was run in the pull request.

Installation copies only paths in `managed-files.json`. When adding or removing a
versioned file under `agents/`, update this list in the same change. Source-checkout
private overlays and other unlisted files are never installed. Updates preserve
unmanaged destination files; automatic removal of obsolete files is not implemented.

The [coding evaluation draft](docs/evaluation-plan.md) defines paired comparisons
and pending edge cases. Offline checks use a fake CLI to test evaluation recording;
they do not run a model or establish semantic quality.

`tests/run_coding_eval.py` is a separate, opt-in runner for the eight paired
scenarios. It requires `--authorize-model-calls` and an output directory outside
the repository. It uses the selected model and reasoning setting for both arms,
retains private JSONL events and usage, and stops before later scenarios if a
call fails. Running it is not part of CI; obtain explicit authorization first.
On Windows it preserves only the existing `windows.sandbox` backend and performs
a model-free read-only preflight before any inference. A missing backend or failed
read stops the run. It does not change global configuration or enable broad access.

## Change and release policy

- Record repository-wide changes under `Unreleased` in `CHANGELOG.md`.
- Record agent-specific behavior changes in that agent's changelog when one exists.
- Use semantic version tags for releases. Breaking agent contracts require a major version; backward-compatible behavior additions require a minor version; fixes and documentation-only releases use a patch version.
- Release notes should copy the relevant changelog entries and identify any migration steps.

By contributing, you agree that your contribution is licensed under the repository's MIT License.
