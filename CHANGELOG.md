# Changelog

Notable repository-wide changes are documented here. Agent-specific behavior history may also appear in the agent's own changelog.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and releases use [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Breaking

- 默认安装从八个入口改为 manuel/mantou 两个；完整安装使用 -All。保留旧角色文件与显式安装，不自动卸载现有角色。发布为新主版本时请说明此迁移。
- manuel 从单书审计扩展为个人思考与行动伙伴，按需读取五书方法，增加记录来源、目标确认、纠错、机会试验和复盘规范；新行为待实测。
- mantou 压缩重复指令，短请求不默认扩写成复杂工作流，保留安全剪贴板交付。


### Changed

- 五位书籍顾问明确优先职责、条件式交接与联合咨询证据约定，保留点名调用和各书方法。
- 连续安装书籍顾问复用相同公共依赖；不同内容在写入前报错。新增连续安装、冲突及显式强制更新回归。

### Added

- 新增八位顾问职责重叠审查、统一选择入口、联合咨询交接约定和角色合并验收方案；保留现有角色与运行契约，未执行新增模型评估。

- 新增八位 agent 的验证状态表，汇总现有证据与尚待验证的行为。

- 将仓库首页与兼容性说明改为中文为主，扩充中文使用手册，覆盖八位 agent 的选择、调用示例、联合咨询、原书配置、更新与排错；同步修正旧的发布和评估状态说明。

- A short Chinese quick-start guide with all eight agent entry points, invocation
  examples, optional joint consultation, and installation/source setup guidance.
- `_clayton`, `_alan`, and `_jim` book-advisor pilots with 28 source-grounded
  principle summaries, explicit edition/provenance limitations, private EPUB
  setup and 27 pending semantic behavior cases. Each inherits the caller model.
- A shared source reader that supports HTML entities and exact heading locators
  scoped to the selected chapter, including single-document multi-chapter EPUBs.
- Selective installation of the three pilots with their shared reader and
  preservation of each private source configuration.
- Implementation rationale explaining the three entry points and their conceptual
  differences without claiming measured behavior gains.

- `_wayne` research-advisor pilot: nine source-checked principles, all 18 chapter
  locations, private fingerprinted EPUB access, offline regressions, and pending
  semantic behavior cases. Inherits the caller model; original book is not distributed.
- Selective installation with `-Agent`, preserving private local source configuration.
- Targeted semantic review cases for existing agents; no runtime changes or measured gains claimed.

- Five-book advisor design with explicit available/planned status, single-book
  source boundaries, learning behavior, staged collaboration, and acceptance criteria.
- Design review of `_mantou`, `_factbot`, and `_invest`, distinguishing existing
  capabilities from proposed improvements without changing their runtime contracts.
- README roadmap linking both design documents and clarifying current installer coverage.

### Fixed

- Preserve the configured Windows sandbox backend in isolated eval sessions and
  fail a model-free read preflight before spending model calls on unreadable
  packages. Verify native `_wayne` and repaired CLI reads with matching file hashes.
- Keep `_mantou`'s complete refined prompt available for manual copying when
  clipboard access is unavailable or copying fails after its single retry.
- Install only explicitly listed managed files, preserving private overlays even
  when present in both the source checkout and destination.
- Preserve mixed parent text and nested block text in both EPUB readers without
  duplication; cover nested lists, quotations, table cells, and inline formatting.
- Keep nested block recursion inside the selected heading range so a following
  chapter and its tail text cannot leak into the requested source section.
- Label `_manuel` regex evaluation as a lexical smoke check and retain private
  answers, logs, package hashes, elapsed time, and failure records for review.
- Add an opt-in paired coding evaluation runner and an initial 16-answer report
  using gpt-6.1-sol/high. Separate text self-review from unverified native routing,
  clipboard operations and support-file loading; no general quality gains claimed.

- Make the documented local model-override path usable with explicit
  `-AllowModelOverride` / `--allow-model-override` validation options. Default
  release and CI checks remain strict; all non-model checks remain enabled.
- Add offline regression coverage for accepted local model identifiers and
  preserved reasoning, read-only, agent-boundary, and privacy checks.

## [0.1.1] - 2026-09-14

### Fixed

- Let the Windows repository validator fall back to the standard `py` launcher
  when `python` is not available on `PATH`.

## [0.1.0] - 2026-08-30

### Added

- 新增八位顾问职责重叠审查、统一选择入口、联合咨询交接约定和角色合并验收方案；保留现有角色与运行契约，未执行新增模型评估。

- Windows CI for installer, agent validators, unit tests, PowerShell parsing, and TOML parsing.
- Installer and private-overlay regression tests.
- Standalone documentation and static contract tests for `_factbot` and `_mantou`.
- Repository-wide validation for local Markdown links, structured data, and common privacy leaks.
- Contribution, security, issue, pull-request, and dependency-update configuration.
- Runtime and model compatibility guidance plus a maintainer release checklist.
- Installer `-WhatIf` support for previewing forced updates without changing files.

### Changed

- Forced installation updates managed files in place and preserves unmanaged private overlays.
- Installation conflicts are checked before any package files are copied.
- Standalone invocation examples work when `CODEX_HOME` is unset.

### Fixed

- Prevent nested support directories during forced installation.
- Exclude `_invest/knowledge-map.local.md` from public-package privacy scanning.
