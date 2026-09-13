---
name: release-checklist
description: Use this skill before every release; drive the release through a dedicated
  release/v* branch, verification, changelog review, PR publish, and CI tagging without
  skipping checks.
metadata:
  loadout.managed: 'true'
  loadout.source: skills/release-checklist/SKILL.md
  loadout.sha: 9180c3a
---

# Release checklist

1. Confirm the intended semver, release scope, and that work starts from `main` or `master`.
2. Create dedicated branch `release/vX.Y.Z` from the default branch tip — never land release commits directly on the default branch.
3. Commit version bumps and CHANGELOG updates on that branch only (`## X.Y.Z` section; bump `pyproject.toml`, `src/loadout/__init__.py`, and lockfile as needed).
4. Review the full diff and user-facing CHANGELOG for that version.
5. Run the full required lint, test, build, and packaging checks from a clean state (or via `just release`).
6. Verify version consistency across branch name (`release/vX.Y.Z`), `CHANGELOG.md` (`## X.Y.Z`), `pyproject.toml`, and `src/loadout/__init__.py`.
7. Publish with `just release X.Y.Z` (push + open PR) and merge after review — **do not** create or push git tags locally; CI owns tagging on the merge commit.
8. After merge, confirm annotated tag `vX.Y.Z` exists; record rollback as consumers pinning the previous tag.
