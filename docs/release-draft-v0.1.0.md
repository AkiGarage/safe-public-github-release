# Release Draft: v0.1.0

## Summary

Initial release of the `safe-public-github-release` Codex skill.

## Changes

- Adds the main release-safety workflow for clean public snapshots.
- Adds GitHub-only public snapshot and no-public-repository-yet flows.
- Adds optional Python package release guidance for TestPyPI/PyPI Trusted
  Publishing.
- Adds local validation and CI validation.

## Validation Before Publishing

- `python3 scripts/validate_skill.py`
- `git diff --check`
- public-surface scrub for private paths, handoff files, tokens, generated
  archives, and accidental binary files
- GitHub-rendered README visual approval

## Publishing Status

Not published. Do not create `v0.1.0`, create a GitHub Release, or make the
repository public until Aki explicitly approves the final gate.
