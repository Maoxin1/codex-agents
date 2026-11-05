# Changelog

## [Unreleased]

### Changed

- 压缩重复指令，默认保持短请求的规模，只为执行必需的缺口加占位符；保留下游动作与安全剪贴板交付。

- Always return the complete refined prompt, including when clipboard access is
  unavailable or copying fails after one retry. Preserve safe clipboard handling
  and never claim a failed copy succeeded.

### Added

- Standalone usage and clipboard-boundary documentation.
- Static configuration validation and reviewable behavior cases.
