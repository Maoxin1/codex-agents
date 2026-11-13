# Changelog

记录当前待发布变更与已发布版本。整理前的开发过程记录保存在[历史快照](docs/history/changelog-before-organization.md)，其中已撤销的方案不再作为发布说明。

## [Unreleased]

后续变更待记录。

## [0.2.0-rc.1] - 2026-11-13（候选，尚未发布）

### Breaking

- 仅发布 `_manuel` 和 `_mantou`，移除六个旧角色及 `-All` 参数。旧安装使用[迁移流程](docs/migration.md)预览、备份和退役入口；用户修改过的配置与私人资料保留。下一次正式版本应体现这一破坏性变更。
- 四本书资料及公共读取器迁入 `_manuel/books/`；新旧原书环境变量均可读取，独立书籍顾问不再分发。

### Changed

- `_manuel` 按解释、草稿、判断、行动和学习分流，按需读取个人记录与方法；建议依赖实际证据和约束，学习流程包含反馈与迁移练习。行为变更详见[agent 日志](agents/_manuel/CHANGELOG.md)。
- `_mantou` 保持短请求规模，始终交付完整提示词，并如实报告剪贴板状态。
- 首页按具体任务引导使用；网页与通用包方案已撤回。当前说明、安装、评估与 GitHub 模板统一到两个 agent。
- 整理文档导航、测试说明与历史索引；合并重复 Unreleased 段落，将旧验证报告移出当前说明。

### Added

- 版本与下载入口说明，区分当前 main 的两入口结构与历史 v0.1.1 发行版，并记录发布前提及恢复方式。
- `_manuel` 的创业验证、事实核验与投资研究资料，以及合成用例、对照方案和多轮人工验收协议。
- 旧入口迁移脚本，支持预览、历史指纹识别、备份、原书私有配置复制及冲突保留。
- 精确角色集合、安装参数、迁移和来源读取回归；公开清单隔离私人覆盖文件，原文读取保留章节边界和输出限额。

### Validation

- 离线检查验证配置、安装、迁移、来源读取器与评估记录，不证明回答质量。付费评估需明确授权；旧版探索性结果不转移为新版效果证明。详见[验证状态](docs/verification-status.md)。

## 已发布版本

以下保留各版本当时的说明，其中旧角色和旧路径仅描述历史行为。

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
