# Compatibility

This package contains Codex custom-agent configuration and supporting files. Local validation confirms repository structure and syntax; model availability and product features still depend on the user's Codex workspace.

## Runtime requirements

- Codex must support custom agents with `model`, `model_reasoning_effort`, and `sandbox_mode` configuration fields.
- `_factbot` and `_manuel` request `gpt-5.6-terra`; `_invest` and `_mantou` request `gpt-5.6-sol`. Installation does not grant access to either model.
- PowerShell is required for installation and the repository validation entry points.
- Python 3.11 or later is required for static validators and unit tests. The
  repository validator accepts either `python` or the Windows `py` launcher.
- `_mantou` requires a Windows interactive session with `Set-Clipboard` and `Get-Clipboard` available.
- `_invest` can optionally route approved writes to Obsidian. Its local vault path is supplied outside the public package.

## Portability

If a configured model is unavailable, choose an accessible model that supports the
agent's existing tools and reasoning setting, then change only `model` in the
relevant `agents/<name>.toml` file. Validate that local copy explicitly:

```powershell
./tests/validate_repository.ps1 -AllowModelOverride
```

Each individual agent validator also accepts `--allow-model-override`, for example:

```powershell
python agents/_factbot/tests/validate_factbot.py --allow-model-override
```

This mode relaxes only the exact default model identifier. The identifier must
still be a non-empty string without whitespace; reasoning settings, agent
boundaries, privacy checks, and all other validations remain unchanged. It does
not verify model availability, feature support, or output quality. After validation,
install the local copy, restart Codex, and run a non-sensitive smoke test before
relying on the substituted model. Standalone invocation scripts with a `-Model`
parameter need that override passed explicitly as well.

Keep local overrides out of published defaults. Running the validator without
the switch, including in CI and before a release, still rejects changed default
model identifiers. A later installation with `-Force` replaces managed TOML
files, so review and reapply intentional model overrides when upgrading.

The default CI exercises Windows with Python 3.11 and 3.13. It does not call paid model services or perform live behavioral evaluation.

## Upgrade check

Before upgrading Codex or this package:

1. run `./install.ps1 -Force -WhatIf` to preview managed targets;
2. review the changelog and agent-specific behavior changes;
3. run `./tests/validate_repository.ps1` (add `-AllowModelOverride` only for an intentional local model override);
4. install with `-Force`, then restart Codex;
5. exercise each agent with a non-sensitive smoke test before relying on it for substantive work.
