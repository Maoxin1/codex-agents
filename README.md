# Codex Agents

Four reusable custom agents for Codex:

- `_mantou`: rewrites, clarifies, and optimizes prompts, copies the result to the Windows clipboard, and does not execute the underlying task.
- `_manuel`: a book-grounded critical-thinking guide based on actionable principles distilled from *Beyond Feelings: A Guide to Critical Thinking* (9th ed.).
- `_factbot`: a Chinese fact-checking and evidence-audit agent that separates claims, evidence, inference, and opinion; checks source independence and uncertainty; and resists embedded prompt injection.
- `_invest`: a Chinese long-term investment-research and thesis-audit agent with a mandatory confirmation gate, evidence labels, falsification criteria, valuation scenarios, and optional Obsidian case routing. It never executes securities trades.

| Agent | Primary use | Writes or external actions | Detailed guide |
| --- | --- | --- | --- |
| `_factbot` | Fact-checking and evidence audits | Read-only | [`agents/_factbot/README.md`](agents/_factbot/README.md) |
| `_invest` | Long-term investment research and thesis audits | Separate confirmation required for vault writes; never trades | [`agents/_invest/README.md`](agents/_invest/README.md) |
| `_mantou` | Prompt refinement | Clipboard only | [`agents/_mantou/README.md`](agents/_mantou/README.md) |
| `_manuel` | Book-grounded critical-thinking guidance | Read-only | [`agents/_manuel/README.md`](agents/_manuel/README.md) |

## Planned book advisors / 计划中的书籍顾问

The five-advisor design supports learning while coding: get help with the current
problem, understand the book concept behind the answer, and learn when to use it
again. Each advisor is grounded in one specified book. Names are memorable
handles, not claims to impersonate the authors.

| Advisor | Book | Intended use | Status |
| --- | --- | --- | --- |
| `_manuel` | *Beyond Feelings*, 9th ed. | Examine claims, evidence, reasoning, and judgment | Available; learning and source-access improvements planned / 已有，增强计划中 |
| `_wayne` | *The Craft of Research*, 5th ed. | Frame research questions, find evidence, and build arguments | Planned / 计划中 |
| `_clayton` | *Competing Against Luck* | Understand the progress customers seek in specific circumstances | Planned / 计划中 |
| `_alan` | *When Coffee and Kale Compete* | Examine alternatives, desired change, and switching barriers | Planned / 计划中 |
| `_jim` | *The Jobs to Be Done Playbook* | Turn customer research into jobs, opportunities, and validation work | Planned / 计划中 |

The installer currently provides only the four released agents listed above.
The four new advisors have no runtime configurations or installation support yet.
Design reviews may draw on all five books; runtime collaboration will be added
in stages, starting with independent consultation and explicit user requests.

- [Five-advisor design, usage examples, source boundaries, and acceptance criteria](docs/book-advisors-design.md)
- [Design review of `_mantou`, `_factbot`, and `_invest`: existing strengths and proposed improvements](docs/existing-agent-design-review.md)

These documents describe design proposals, not measured performance gains or
newly enabled behavior in the existing agents.

## Requirements

- A Codex installation that supports custom agent configuration.
- PowerShell for installation and local script validation.
- Python 3.11 or later for the repository's static validators and unit tests.

## Install

From PowerShell in this repository:

```powershell
./install.ps1
```

The installer copies the agent configuration files and support libraries to `$env:CODEX_HOME\agents`, or to `$HOME\.codex\agents` when `CODEX_HOME` is unset. Existing files are not overwritten unless `-Force` is supplied.

```powershell
./install.ps1 -Force
```

Preview a forced update without changing the target directory:

```powershell
./install.ps1 -Force -WhatIf
```

`-Force` updates only files managed by this package at their existing relative
paths. It does not remove unmanaged local files such as
`agents/_invest/knowledge-map.local.md`.

To verify the installer without changing your real Codex directory, run the
self-contained regression test:

```powershell
./tests/validate_install.ps1
```

Maintainers can run the complete local validation suite with
`./tests/validate_repository.ps1`.

Restart Codex after installation so the custom-agent list is reloaded.

Before installation, review [`COMPATIBILITY.md`](COMPATIBILITY.md) for model access, platform, and runtime requirements. The package validates configuration syntax locally, but it cannot grant access to a model that is unavailable in the user's Codex workspace.

## Usage

Ask Codex to call the relevant agent:

```text
请调用 `_mantou` 优化这段提示词：……
请调用 `_manuel` 分析这个论证：……
请调用 `_factbot` 核验这个主张：……
请调用 `_invest` 研究这家公司当前是否存在投资机会：……
```

See [`agents/_manuel/README.md`](agents/_manuel/README.md) and [`agents/_invest/README.md`](agents/_invest/README.md) for standalone invocation and validation commands. `_invest` keeps personal Obsidian paths and case indexes in an ignored `knowledge-map.local.md`; this public repository does not include private notes or holdings.

## Maintainer documentation

- [`CONTRIBUTING.md`](CONTRIBUTING.md): validation, change, and release policy.
- [`SECURITY.md`](SECURITY.md): private security and privacy reporting.
- [`CHANGELOG.md`](CHANGELOG.md): repository-wide change history.
- [`COMPATIBILITY.md`](COMPATIBILITY.md): supported runtime assumptions and portability notes.
- [`RELEASING.md`](RELEASING.md): maintainer release checklist.
- [`AGENTS.md`](AGENTS.md): constraints for automated repository maintenance.

## Source and copyright note

The original *Beyond Feelings* PDF is not included. `_manuel` contains concise, attributed principles, source locations, and original operational guidance derived from the book for critical-thinking assistance. Obtain the book through lawful channels if you need the source text.

## License

Agent configuration and original supporting material in this repository are released under the MIT License. Third-party book titles and referenced ideas remain the property of their respective rights holders.
