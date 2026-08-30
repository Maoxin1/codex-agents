# Compatibility

This package contains Codex custom-agent configuration and supporting files. Local validation confirms repository structure and syntax; model availability and product features still depend on the user's Codex workspace.

## Runtime requirements

- Codex must support custom agents with `model`, `model_reasoning_effort`, and `sandbox_mode` configuration fields.
- `_factbot` and `_manuel` request `gpt-5.6-terra`; `_invest` and `_mantou` request `gpt-5.6-sol`. Installation does not grant access to either model.
- PowerShell is required for installation and the repository validation entry points.
- Python 3.11 or later is required for static validators and unit tests.
- `_mantou` requires a Windows interactive session with `Set-Clipboard` and `Get-Clipboard` available.
- `_invest` can optionally route approved writes to Obsidian. Its local vault path is supplied outside the public package.

## Portability

If a configured model is unavailable, choose an accessible model with equivalent tool and reasoning support, update the relevant TOML file, and run `./tests/validate_repository.ps1` before installation. Treat that change as a local compatibility override unless the repository's supported defaults are intentionally being changed.

The default CI exercises Windows with Python 3.11 and 3.13. It does not call paid model services or perform live behavioral evaluation.

## Upgrade check

Before upgrading Codex or this package:

1. run `./install.ps1 -Force -WhatIf` to preview managed targets;
2. review the changelog and agent-specific behavior changes;
3. run `./tests/validate_repository.ps1`;
4. install with `-Force`, then restart Codex;
5. exercise each agent with a non-sensitive smoke test before relying on it for substantive work.
