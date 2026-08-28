## Summary

Describe the user-visible change and the agent or package affected.

## Validation

- [ ] `./tests/validate_install.ps1`
- [ ] `_invest` static validator and unit tests
- [ ] `_manuel` static validator
- [ ] Relevant behavior cases were reviewed, or this change does not affect behavior

## Safety and compatibility

- [ ] No secrets, personal vault paths, holdings, or private note content are included
- [ ] Agent TOML and supporting files remain consistent
- [ ] Documentation and changelog are updated when behavior or installation changes
