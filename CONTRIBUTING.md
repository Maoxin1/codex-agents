# Contributing

Publish exactly two agents: `_manuel` and `_mantou`. Books and task-specific methods belong to Manuel's support package; they must not create additional registered roles or install options.

## Before opening a pull request

1. Branch from main. Update configuration, support materials, tests, documentation and changelogs together when their contract changes.
2. Use synthetic fixtures. Never commit credentials, personal vault paths, source books, private notes or holdings.
3. Update managed-files.json for every packaged file change. Installation only copies explicitly managed files; preserve unmanaged files and private overlays.
4. Run from PowerShell:

```powershell
./tests/validate_repository.ps1
```

The suite checks the exact published agent set, default and selective installation, rejected retired names, migration preview/backup/idempotence, private and modified file preservation, source readers, the two configuration contracts, model overrides, evaluation bookkeeping, links, privacy patterns and PowerShell syntax. No model calls occur. Optional private-source validation must be reported separately.

Use -AllowModelOverride only for intentional local preferences; release validation is strict. Install updates replace managed TOML; migration of retired entries is a separate previewable script, never recursive deletion of user data.

## Behavioral evaluation

The [current plan](docs/evaluation-plan.md) covers only the two published agents. tests/run_coding_eval.py requires --authorize-model-calls and an output directory outside the repository. It runs two paired synthetic scenarios, preserves records, and stops on failure. On Windows it retains the configured sandbox backend and performs a model-free read preflight. A config-override run does not prove native agent dispatch.

Obtain explicit authorization for paid model calls; prior versions' authorization does not cover a new run. Multi-turn scenarios in docs/evaluation/task-routing.md require actual sequential inputs, not a flattened prompt. Offline tests use fake CLI fixtures only.

Historical designs and evaluations are under docs/history, labelled obsolete and linked to their original revision. Do not rewrite historical results as new evidence or use them as current installation guidance.

## Release policy

Record changes under Unreleased in CHANGELOG.md and affected agent changelogs. Removing legacy agent contracts is a breaking change; the next semantic version release must reflect it. Confirm exact-commit CI before release. Contributions are licensed under MIT.
