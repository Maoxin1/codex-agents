# Releasing

Releases use Semantic Versioning and copy their user-visible notes from `CHANGELOG.md`.

## Checklist

1. Confirm the intended version and move relevant entries from `Unreleased` to a dated version section.
2. Review model identifiers and the assumptions in `COMPATIBILITY.md` against current official Codex documentation.
3. Run `./tests/validate_repository.ps1` from a clean checkout.
4. Confirm the `Validate` workflow succeeds on the exact release commit.
5. Create a signed or annotated `vMAJOR.MINOR.PATCH` tag.
6. Create the GitHub Release from that tag, copy the changelog notes, and include any migration steps.
7. Test a clean installation from the released archive without using private overlays or credentials.

Do not publish a release while required validation is skipped, a model identifier is known to be unavailable to the intended audience, or private material appears in the diff or archive.
