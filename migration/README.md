# Legacy fingerprints

legacy-agent-hashes.json contains SHA-256 fingerprints of the six retired TOML entrypoints found in the main-branch history through commit `644b1ba13d59b3381f26e37d418393264631ec67`. Both original and CRLF checkout representations are included. It contains no runtime role definitions or private configuration.

The migration matches exact bytes, not merely filenames or a TOML name. Unknown versions and local edits are preserved with a warning. New historical fingerprints must be derived from reviewed public Git content, never by accepting the installed user's file as trusted by default.

Tests use an isolated synthetic fingerprint registry and fixture Codex home; they never migrate the real user's configuration. See [migration instructions](../docs/migration.md).
