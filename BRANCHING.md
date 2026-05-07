# Branching & Release Strategy

> **TL;DR.** GitHub Flow on `master` + short-lived feature branches. Two SemVer trains — `platform-vX.Y.Z` and `knowrag-vX.Y.Z` — tag independently. Squash-merge only. No `develop`, no permanent `release/*`.

## 1. The trunk

`master` is the only long-lived branch. It is always green: every commit on `master` has passed CI, has an issue reference, and follows `commit-format.md`. Direct pushes are blocked by GitHub Branch Protection — work happens on feature branches.

## 2. Branch types

Branch prefixes mirror the `type` field in `commit-format.md`. The slug is kebab-case, ≤ 50 chars, no issue number (the issue lives in commit + PR).

| Prefix | Use | Example |
|--------|-----|---------|
| `feat/` | New capability | `feat/knowrag-webhook-route` |
| `fix/` | Bug fix | `fix/api-30x-redirect` |
| `chore/` | Non-functional repo work | `chore/repo-prune-stale-stacks` |
| `docs/` | Docs-only | `docs/branching-md` |
| `refactor/` | No behavior change | `refactor/state-loader` |
| `test/` | Test-only delta | `test/knowrag-verify-baseline` |
| `release/` | Ephemeral stabilization for a tag | `release/knowrag-v0.4.0` |
| `hotfix/` | Direct-to-master prod fix | `hotfix/prod-tls-renew` |
| `keep/` | Long-lived experimental branch (excluded from auto-cleanup) | `keep/qdrant-reranker-spike` |

## 3. Lifecycle

```
1. Open or pick an issue.                  gh issue create / gh issue list
2. Branch off master.                      git switch -c feat/<scope>-<slug>
3. Commit early, commit often.             commit-format.md applies to every commit
4. Open the PR.                            gh pr create — fill the template
5. CI must pass: ci, lint, test, security  required by branch protection
6. Squash-merge into master.               GitHub auto-deletes the branch
7. (Optional) Tag a release.               see § 6 Releases & Tags
```

Local rebases on the feature branch are fine and encouraged before opening the PR. After review, never force-push the PR branch — squash-merge collapses it cleanly.

## 4. Commit grammar

See `.claude/rules/commit-format.md`. The PR title is enforced to follow the same grammar (squash-merge inherits it as the merge commit).

## 5. PR rules

- 1 approving review from a CODEOWNER
- All required status checks green (`ci`, `lint`, `test`, `security`, `dependency-review`)
- Up-to-date with `master` (rebase or "Update branch" before merge)
- Linear history maintained (squash-merge only — merge commits and rebase-merge are disabled)
- Signed commits required on `master`
- Force-push blocked, branch deletion blocked

## 6. Releases & tags

Two independent SemVer trains:

| Train | Tag prefix | Bumps when |
|-------|-----------|------------|
| Platform | `platform-vX.Y.Z` | Changes to `@ops/`, `@dev/`, `@prod/`, `.shared/`, `.bin/w7` |
| KNOWRAG | `knowrag-vX.Y.Z` | Changes to `@lab/ll-KNOWRAG/**` |

Both start at `v0.Y.Z` until the train is declared stable. Bumps follow SemVer: MAJOR for breaking, MINOR for additive, PATCH for fix-only.

### Manual cut procedure (current)

1. Open `release/<train>-vX.Y.Z` from `master`.
2. Update `CHANGELOG.md` (root for platform, `@lab/ll-KNOWRAG/CHANGELOG.md` for KNOWRAG).
3. PR titled `release(<train>): vX.Y.Z (#N)`.
4. After merge, push the tag: `git tag <train>-vX.Y.Z && git push --tags`.
5. `gh release create <train>-vX.Y.Z -F CHANGELOG-section.md`.
6. Delete the `release/*` branch.

### Future: release-please

When the manual flow becomes painful (≥ 3 manual tags cut, or changelogs drift), adopt `googleapis/release-please-action@v4` in **manifest mode** with `include-component-in-tag: true`. See `RELEASE.md` for the planned configuration.

## 7. Hotfixes

Direct PR to `master` from `hotfix/<scope>-<slug>` is allowed. Same gates as a normal PR, but:
- Label the PR `hotfix`.
- Bump only PATCH on the affected train.
- Open a follow-up issue for a post-mortem within 7 days.

## 8. Stale-branch policy

- Merged branches are auto-deleted by GitHub on squash.
- Unmerged: `.github/workflows/stale-branches.yml` runs weekly.
  - **30 d** stale → comment a warning on the related PR/issue
  - **60 d** stale → archive (rename to `archived/<branch>`) and close the related PR
- Opt out by prefixing the branch `keep/` (e.g., `keep/wip-experiment`).
- Branches associated with an open PR are never auto-archived.

## 9. Zone matrix (which zone owns which branch patterns)

| Zone | Typical branch patterns |
|------|------------------------|
| Platform-wide | `chore/repo-*`, `chore/platform-*`, `docs/*`, `release/platform-*` |
| `@ops/*` | `feat/ops-*`, `fix/ops-*`, `chore/ops-*` |
| `@dev/*` | `feat/dev-*`, `fix/dev-*`, `chore/dev-*` |
| `@prod/*` | `feat/prod-*`, `fix/prod-*`, `hotfix/prod-*` |
| `@lab/ll-KNOWRAG/` | `feat/knowrag-*`, `feat/api-*`, `feat/ui-*`, `feat/mcp-*`, `feat/ingest-*`, `release/knowrag-*` |

## 10. FAQ

**Why GitHub Flow over Trunk-Based Development?**
TBD with feature flags is overkill for a single-host Compose stack — there's nothing to flag-gate. GitHub Flow gives the same benefits (short branches, always-green trunk) without the overhead.

**How do I bump KNOWRAG only?**
Tag `knowrag-vX.Y.Z`. The `release-please.yaml` workflow (when adopted) is configured to track per-component tags and will not bump `platform-*`.

**What if a PR touches both trains?**
Two scopes in the commit message (`feat(api,platform): …`) and a PR title that says so. Tag each train separately when releases are cut — the changelog entry appears under both.

**Why no `develop` branch?**
There's no QA gate. CI is the gate. A second long-lived branch would just collect drift.

## 11. References

- `.claude/rules/commit-format.md` — commit grammar (the source of truth)
- `.claude/rules/branch-naming.md` — Claude-enforced branch naming
- `.claude/rules/versioning.md` — train split + bump rules
- `RELEASE.md` — release process + future release-please plan
- `.github/CODEOWNERS` — review routing
- `.github/PULL_REQUEST_TEMPLATE.md` — PR fields
- `.github/ISSUE_TEMPLATE/` — issue forms
