# PyPI Trusted Release Runbook

Use this runbook for Python CLI/tooling projects where the public install path
is `uvx --from <package> <command>`.

## Clean Public Scope

Before publishing or updating public docs, scan the intended public tree:

```bash
rg --pcre2 -n '(/Users/|\\.local|\\.codex|HANDOFF|CONTINUITY|internal|gho_|ghp_|github_pat_|BEGIN [A-Z ]*PRIVATE KEY|AKIA|SECRET|PASSWORD|api[_-]?key)' \
  README* docs .github pyproject.toml package.json
```

Review matches manually. Some words such as `token` may be legitimate when they
describe OIDC or usage accounting, but local paths, private repo names, and
handoff files should not appear in public-facing docs.

Also inspect the tracked file set and largest files:

```bash
git ls-files | rg -n '(^dist/|^\\.build/|\\.mov$|\\.mp4$|\\.xcuserstate$|\\.DS_Store$|\\.log$)'
git ls-files -z | xargs -0 ls -l | awk '{print $5 "\t" $9}' | sort -nr | head -30
```

For README media, prefer a small inline GIF for the first-screen demo. GitHub
README rendering is more reliable for images/GIFs than repo-local MP4 links or
`<video>` embeds. If an MP4 is useful, put it in GitHub Release assets and
include it only if it is part of the intended public release.

## Trusted Publisher Setup

Create pending publishers on both TestPyPI and PyPI with matching fields:

```text
Project name: <package>
Owner: <github-owner>
Repository name: <public-repo-name>
Workflow filename: <workflow-file>.yml
Environment name: testpypi
```

Repeat for PyPI with environment `pypi`.

Rules:

- Do not create or store PyPI API tokens in GitHub secrets.
- GitHub workflow jobs that publish need `id-token: write`.
- `pypi` should require maintainer approval via a GitHub environment.
- Restrict environments to release tags when practical.

## Release Order

1. Confirm clean git state and current remotes.
2. Run repo checks, for example:

```bash
git diff --check
bash scripts/check.sh
python3 -m build --sdist --wheel
python3 scripts/verify-python-wheel dist/*.whl
```

3. Create or confirm the release tag only after release guards are present.
4. Run build-only workflow for the tag.
5. Create or verify GitHub Release archive, `SHA256SUMS`, and attestations.
6. Run readiness for TestPyPI.
7. Publish to TestPyPI.
8. Verify TestPyPI JSON and install smoke:

```bash
curl -fsS https://test.pypi.org/pypi/<package>/json
uvx --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ \
  --from <package> <command> --help
```

9. Run readiness for PyPI.
10. Publish to PyPI through the approved `pypi` environment.
11. Verify PyPI JSON and install smoke:

```bash
curl -fsS https://pypi.org/pypi/<package>/json
uvx --from <package> <command> --help
```

12. Update README/docs so the live PyPI command is primary and GitHub archive is
    the high-assurance fallback.

## Workflow Ref Lesson

GitHub uses the workflow file from the ref passed to `gh workflow run --ref`.
If a tag predates a new input such as `trusted_publishers_configured`, GitHub
will reject that input for runs dispatched from the old tag.

Preferred fix for future releases:

1. Add guards on `main`.
2. Validate them.
3. Create the tag after the guards exist.
4. Dispatch from the tag with the guarded inputs.

Historical exception handling:

- If an already published/approved tag predates the guard, stop and document
  the mismatch.
- Run local readiness checks.
- Publish TestPyPI first.
- Verify TestPyPI install and artifact attestations.
- Only then publish PyPI through environment approval.
- Record the exception in handoff/release docs.

## Public Docs Audit

Docs should say:

- Current primary install path.
- Persistent install path, if applicable.
- High-assurance GitHub Release verification path.
- Trusted Publishing and no long-lived PyPI token.
- Homebrew archived or secondary, if true.
- Next-release flow using `TAG=vX.Y.Z`.
- Public-facing product information, install steps, privacy constraints, and
  screenshots/media that render on GitHub.

Docs should not say:

- "After the first PyPI release" once PyPI is already live.
- "not published yet" after package publication.
- Private repository names.
- Local absolute paths from a maintainer machine.
- `HANDOFF.md` or `CONTINUITY.md` as public prerequisites.
- Personal approval wording; use "maintainer approval".
- Temporary demo filenames, local desktop filenames, repo-local MP4 preview
  links that fail on GitHub, or deleted Release assets.

## GitHub Visibility Flip Gate

For a clean snapshot that is private only while being polished:

1. Confirm clean worktree, default branch, latest CI, and intended Release
   assets.
2. Re-run the public-surface scrub and tracked-file/large-file checks.
3. Verify README referenced images through GitHub's contents API.
4. Verify Release archives by downloading `SHA256SUMS` and checking hashes.
5. State the planned visibility mutation and target repo.
6. Run `gh repo edit <owner>/<repo> --visibility public --accept-visibility-change-consequences`.
7. Re-fetch `visibility`, README, Release assets, latest CI, and local
   `git status -sb`.
