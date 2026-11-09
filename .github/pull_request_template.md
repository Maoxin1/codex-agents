## Summary

Describe the user-visible change and the agent or package affected.

## Validation

- [ ] `./tests/validate_repository.ps1`
- [ ] Exactly `_manuel` and `_mantou` remain published and installable
- [ ] Migration preserves modified configurations and private files
- [ ] Relevant behavior cases were reviewed, or this change does not affect behavior

## Safety and compatibility

- [ ] No secrets, personal vault paths, holdings, or private note content are included
- [ ] Agent TOML and supporting files remain consistent
- [ ] Documentation and changelog are updated when behavior or installation changes
