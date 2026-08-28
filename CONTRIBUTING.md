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

The repository validator runs the installer regression, all four agent validators, `_invest` unit tests, PowerShell parsing, and TOML parsing. Individual validators may be run while developing a focused change.

Behavior evaluation can require a configured Codex environment and is not part of the default CI. Follow the relevant agent's test README and state what was run in the pull request.

## Change and release policy

- Record repository-wide changes under `Unreleased` in `CHANGELOG.md`.
- Record agent-specific behavior changes in that agent's changelog when one exists.
- Use semantic version tags for releases. Breaking agent contracts require a major version; backward-compatible behavior additions require a minor version; fixes and documentation-only releases use a patch version.
- Release notes should copy the relevant changelog entries and identify any migration steps.

By contributing, you agree that your contribution is licensed under the repository's MIT License.
