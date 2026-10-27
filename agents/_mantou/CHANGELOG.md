# Changelog

## [Unreleased]

### Changed

- Always return the complete refined prompt, including when clipboard access is
  unavailable or copying fails after one retry. Preserve safe clipboard handling
  and never claim a failed copy succeeded.

### Added

- Standalone usage and clipboard-boundary documentation.
- Static configuration validation and reviewable behavior cases.
