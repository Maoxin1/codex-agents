# Codex Agents

Four reusable custom agents for Codex:

- `_mantou`: rewrites, clarifies, and optimizes prompts, copies the result to the Windows clipboard, and does not execute the underlying task.
- `_manuel`: a book-grounded critical-thinking guide based on actionable principles distilled from *Beyond Feelings: A Guide to Critical Thinking* (9th ed.).
- `_factbot`: a Chinese fact-checking and evidence-audit agent that separates claims, evidence, inference, and opinion; checks source independence and uncertainty; and resists embedded prompt injection.
- `_invest`: a Chinese long-term investment-research and thesis-audit agent with a mandatory confirmation gate, evidence labels, falsification criteria, valuation scenarios, and optional Obsidian case routing. It never executes securities trades.

## Install

From PowerShell in this repository:

```powershell
./install.ps1
```

The installer copies the agent configuration files and support libraries to `$env:CODEX_HOME\agents`, or to `$HOME\.codex\agents` when `CODEX_HOME` is unset. Existing files are not overwritten unless `-Force` is supplied.

```powershell
./install.ps1 -Force
```

Restart Codex after installation so the custom-agent list is reloaded.

## Usage

Ask Codex to call the relevant agent:

```text
请调用 `_mantou` 优化这段提示词：……
请调用 `_manuel` 分析这个论证：……
请调用 `_factbot` 核验这个主张：……
请调用 `_invest` 研究这家公司当前是否存在投资机会：……
```

See [`agents/_manuel/README.md`](agents/_manuel/README.md) and [`agents/_invest/README.md`](agents/_invest/README.md) for standalone invocation and validation commands. `_invest` keeps personal Obsidian paths and case indexes in an ignored `knowledge-map.local.md`; this public repository does not include private notes or holdings.

## Source and copyright note

The original *Beyond Feelings* PDF is not included. `_manuel` contains concise, attributed principles, source locations, and original operational guidance derived from the book for critical-thinking assistance. Obtain the book through lawful channels if you need the source text.

## License

Agent configuration and original supporting material in this repository are released under the MIT License. Third-party book titles and referenced ideas remain the property of their respective rights holders.
