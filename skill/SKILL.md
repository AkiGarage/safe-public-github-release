---
name: safe-public-github-release
description: Safe public GitHub release workflow for clean public snapshots, release branches, PR/CI gates, GitHub Release archives, assets, checksums, visibility changes, and private-to-public repository publishing. Also use when auditing release docs for private paths, secrets, maintainer-only notes, stale distribution instructions, or GitHub visibility changes. Includes an optional PyPI/TestPyPI subsection for Python packages.
---

# Safe Public GitHub Release

## Core Rule

Protect public trust before speed. Prefer a clean public snapshot, a
release-branch PR/CI gate, verified GitHub Release artifacts, checksums, and
explicit maintainer approval for irreversible operations.

Never publish from private history in place. A repo that was created as a
clean public snapshot and kept private only for final polishing may be flipped
public after the final scrub gate. Use PyPI/TestPyPI only when Python package
distribution is actually in scope.

## Workflow

1. Inspect first:
   - `git status -sb`, remotes, current branch, tags, and relevant workflows.
   - Public repo visibility, default branch, release/tag state, and GitHub
     environments with `gh`.
   - Existing docs that mention install paths, publishing, Homebrew, TestPyPI,
     PyPI, private repos, local paths, or handoff files.
2. Scope the public surface:
   - Public docs and package metadata may mention the public owner/repo,
     package name, public tags, and official install commands.
   - Public docs must not mention private repo names, local home paths,
     `HANDOFF.md`, `CONTINUITY.md`, `.local`, `.codex`, tokens, keys, raw
     internal transcripts, or maintainer-only instructions unless rewritten as
     public-facing guidance.
   - Prefer relative README links for repo-local docs and media. Absolute
     GitHub owner/repo URLs are fine in release notes, but in README they can
     create avoidable owner-coupling and false positives in public-surface
     scrub checks.
3. Prepare GitHub release gates:
   - Build/test locally before remote mutation.
   - Use `release/vX.Y.Z` -> PR -> CI -> merge by default before tagging.
   - Require Aki's GitHub-rendered README visual approval before merge when
     README or localized README files change.
   - Verify Release assets before upload: expected filenames, version metadata,
     checksum, archive contents, and platform-specific signature/notarization
     checks when applicable.
   - For macOS `.app` zip assets, build the archive without AppleDouble or
     Finder metadata. Prefer `COPYFILE_DISABLE=1 zip` or an equivalent archive
     command, and reject archives containing `__MACOSX`, `.DS_Store`, or
     `._*` files. Those extra files can make a signed app fail verification
     after unzip.
   - Always verify the exact archive that will be uploaded by extracting it to
     a temporary directory, checking app/package version metadata, and running
     the relevant signature/notarization verification on the extracted payload.
4. Publish the GitHub release in this order:
   - Re-fetch `main`, verify latest CI is green, and confirm local worktree is
     clean.
   - Confirm the target tag and GitHub Release do not already exist.
   - Create the tag on the verified `main` commit.
   - Push the tag.
   - Create checksum files from the final upload files using release-facing
     basenames, not local paths such as `dist/...`.
   - Create the GitHub Release with intentional notes and only intentional
     assets.
   - Upload checksum files when useful for the asset type, and include the
     checksum in the Release notes when it helps users verify the download.
5. Verify after GitHub publishing:
   - The tag points to the expected commit.
   - The GitHub Release is visible at the expected URL.
   - Release assets and checksums match local verified files.
   - Download the published Release assets into a temporary directory and verify
     them from the downloaded copies. For checksum-backed archives, run
     `shasum -a 256 -c <asset>.sha256`; for macOS `.app` zips, unzip the
     downloaded asset and run the app version and `codesign --verify --strict
     --deep` checks on the extracted app.
   - Public README/docs match the live release version and asset names.

## Optional PyPI / TestPyPI Subsection

Use this subsection only when the GitHub release also publishes a Python
package, CLI, or `uvx` install path.

1. Ensure GitHub environments exist for `testpypi` and `pypi`.
2. Keep `pypi` behind maintainer approval.
3. Use `id-token: write` and PyPI Trusted Publishers instead of stored PyPI
   tokens.
4. Publish in this order:
   - Build-only workflow from the intended tag.
   - GitHub Release archive with `SHA256SUMS` and artifact attestations.
   - TestPyPI publish, then install smoke.
   - PyPI publish only after TestPyPI shows the version and install smoke
     passes.
   - Docs update to make the live install path primary.
5. Verify after publishing:
   - PyPI/TestPyPI JSON contains the expected version.
   - `uvx --from <package> <command> --help` works.
   - Re-uploading the same version is blocked by readiness checks.
   - Public README/docs match the live install path.

## GitHub-Only Public Snapshot Checklist

Use this when the target is a GitHub repository or app release without PyPI.

1. Keep the repo private until the final gate passes. If the public target is a
   separate already-public repository, never copy private history into it; move
   only the scrubbed snapshot content.
2. Use a release branch and PR by default for public snapshots:
   - Create or update `release/vX.Y.Z` in the public repository.
   - Commit the prepared snapshot and public docs on that branch.
   - Open a PR into `main` and let CI run there.
   - When README or release-facing docs change, also use
     `readme-release-sync` so public copy stays readable, bilingual, and
     aligned with the shipped behavior.
   - Give Aki GitHub-rendered README links for the PR/branch and wait for
     explicit visual approval before merge. Local Markdown previews, raw file
     views, screenshots, or automated link checks do not replace this gate.
   - Merge only after CI is green and the public-surface scrub has passed.
   - Push directly to `main` only when Aki explicitly asks to skip the PR gate.
3. Scrub tracked files, not just the working tree:
   - secrets, local paths, maintainer names, old private repo names, handoff
     files, generated archives, and stale product names.
   - `git ls-files` for accidental `.mov`, `.mp4`, build outputs, caches, and
     large binary files.
4. Treat README media as part of the public surface:
   - Inline GIFs are the most reliable GitHub README demo format; keep them
     under GitHub's practical image/GIF limit.
   - Local README `<video>` embeds and repo-local MP4 preview links may fail or
     open unstable GitHub file-preview pages.
   - Put optional MP4 demos in GitHub Release assets only when they are truly
     needed, and remove them plus release-note references if the product does
     not need them.
5. Before creating the tag or GitHub Release, re-fetch:
   - PR merge state and latest CI status on `main` after merge
   - `git status -sb`, `git log --oneline -1`, `git tag --list`, and current
     release assets
   - README and referenced image paths through the GitHub contents API when the
     repository is already public
   - archive contents and extracted-asset verification results for every
     binary upload
6. Before flipping visibility, re-fetch:
   - `gh repo view ... --json visibility,isPrivate,url,defaultBranchRef`
   - latest Actions status for the default branch
   - Release assets and release notes
   - README and referenced image paths through the GitHub contents API
7. Flip visibility only after Aki explicitly says to publish, then verify
   `visibility=PUBLIC`, public README URL availability, Release assets, and a
   clean local worktree.

## Clean Snapshot To Public Repo Flow

Use this flow when a private/internal repository feeds a separate public
repository.

1. Finish and validate the feature in the private repository.
2. Create a temporary snapshot folder from an allowlist of public files.
3. Apply public naming and remove private-only surfaces in the snapshot.
4. Scrub the snapshot for secrets, private paths, handoff files, old product
   names, generated archives, and large accidental files.
5. Copy the scrubbed snapshot into the public repository working tree.
6. Create or switch to `release/vX.Y.Z`.
7. Update public README, localized README, changelog, version metadata, release
   draft notes, and README media references on that branch.
8. Inspect `git diff`, README media links, bilingual parity, stale wording, and
   public-surface scan results.
9. Run the relevant local build/test/package checks.
10. Commit the release-prep changes on `release/vX.Y.Z` and push the branch.
11. Open a PR into `main`; do not tag or create a GitHub Release yet.
12. Wait for CI, fix failures on the release branch, and re-run checks.
13. Send Aki the GitHub-rendered README URLs for `README.md` and any localized
    README files on the PR/branch. Wait for explicit visual approval that the
    README looks correct on GitHub.
14. Merge the PR only after CI, scrub gates, and Aki's GitHub-rendered README
    visual approval all pass.
15. Re-fetch `main` and verify the merged commit is clean and green.
16. Stop for Aki approval before creating `vX.Y.Z`, uploading assets, or
    creating/publishing the GitHub Release.

## No Public Repository Yet Flow

Use this route when the project has never had a public repository.

1. Do not flip the private/internal working repository public.
2. Create a new clean publishing repository and keep it private at first.
3. Initialize it from the scrubbed public snapshot only, not from private
   history.
4. Use public-facing product names, package metadata, README files, license,
   changelog, release draft notes, screenshots/GIFs, and workflows from the
   start.
5. Run the same secret/private-path/large-file/public-surface scrub on tracked
   files.
6. Use `release/vX.Y.Z` -> PR -> CI -> Aki GitHub-rendered README visual
   approval -> merge, even though the repository is still private.
7. Create the intended tag and GitHub Release draft while the repo is still
   private when possible, and verify assets/checks there.
8. Stop for Aki approval before changing visibility.
9. Flip visibility to public only after final scrub, green CI, intentional
   release assets, and explicit Aki approval.
10. After the visibility flip, re-fetch and verify public README availability,
    Release assets, tags, latest Actions status, and local clean worktree.

## Important Lessons

- GitHub Actions workflow definitions are taken from the ref used to dispatch
  the workflow. If a tag was created before a new workflow input or guard was
  added, dispatching from that old tag will not know about the new input.
- Future releases should land release guards before creating the tag. Then
  dispatch from that tag with the guarded inputs.
- If a one-time historical tag predates the guard, do not guess. Run local
  readiness checks, prove TestPyPI first, verify artifacts/attestations, and
  document the exception.
- Release asset hygiene matters: after exploratory uploads, the final public
  Release should contain only intentional artifacts. Delete unwanted assets and
  remove their SHA lines or release-note mentions before publishing.

## Detailed Runbook

Read `references/pypi-trusted-release-runbook.md` for the step-by-step
checklist, command patterns, and public-doc audit patterns.
