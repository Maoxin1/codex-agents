# Changelog

Notable repository-wide changes are documented here. Agent-specific behavior history may also appear in the agent's own changelog.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and releases use [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Windows CI for installer, agent validators, unit tests, PowerShell parsing, and TOML parsing.
- Installer and private-overlay regression tests.
- Standalone documentation and static contract tests for `_factbot` and `_mantou`.
- Repository-wide validation for local Markdown links, structured data, and common privacy leaks.
- Contribution, security, issue, pull-request, and dependency-update configuration.

### Changed

- Forced installation updates managed files in place and preserves unmanaged private overlays.
- Installation conflicts are checked before any package files are copied.
- Standalone invocation examples work when `CODEX_HOME` is unset.

### Fixed

- Prevent nested support directories during forced installation.
- Exclude `_invest/knowledge-map.local.md` from public-package privacy scanning.
