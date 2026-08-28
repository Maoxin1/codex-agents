# Repository maintenance instructions

- Treat `agents/<name>.toml` and any sibling `agents/<name>/` directory as one versioned agent package.
- When changing an agent contract, update its configuration, supporting documentation, validation assets, and changelog together where applicable.
- Keep installers idempotent. `-Force` may update package-managed files but must preserve unmanaged local files, especially `agents/_invest/knowledge-map.local.md`.
- Never commit credentials, personal vault paths, holdings, case indexes, private notes, generated caches, or internal machine paths. Use synthetic fixtures in tests and examples.
- Do not run behavior evaluations that can consume paid services unless the user explicitly authorizes them. Static and local regression checks are safe defaults.
- Before handoff, run the commands in `CONTRIBUTING.md` and report any skipped checks.
