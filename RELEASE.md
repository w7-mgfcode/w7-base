# Release Process

> Two SemVer trains, manual cuts today, `release-please` later.
> Companion docs: `BRANCHING.md` (lifecycle), `.claude/rules/versioning.md` (bump rules).

## 1. Cadence

| Train | Cadence | Reason |
|-------|---------|--------|
| `platform-vX.Y.Z` | Slow — when changes accumulate or a stack contract evolves | Platform is stable infrastructure; no calendar-driven cadence |
| `knowrag-vX.Y.Z` | Fast — per-feature when a `feat/*` PR lands cleanly and `w7 verify` is green | Sub-project is mid-pivot; users want signal per change |

Neither train uses calendar-versioned releases. Both are SemVer; both stay in `v0.x` until declared stable.

## 2. Tag prefixes

- Platform → `platform-vX.Y.Z`
- KNOWRAG → `knowrag-vX.Y.Z`

There is no shared `vX.Y.Z` tag. Cross-train PRs cut **two** tags, one per train.

## 3. Manual cut procedure (current)

1. Pick the train and bump level (per `versioning.md`).
2. Branch: `git switch -c release/<train>-vX.Y.Z`.
3. Update the changelog:
   - Platform → `CHANGELOG.md` (root)
   - KNOWRAG → `@lab/ll-KNOWRAG/CHANGELOG.md`
   Use sections: `### Added`, `### Changed`, `### Fixed`, `### Breaking`, `### Deprecated`, `### Security`.
4. Open a PR titled `release(<train>): vX.Y.Z (#N)` where `#N` is the tracking issue.
5. CI must pass. CODEOWNER review required.
6. Squash-merge.
7. From master: `git tag <train>-vX.Y.Z && git push --tags`
8. `gh release create <train>-vX.Y.Z --notes-file <path-to-changelog-section>.md --title "<train> vX.Y.Z"`
9. Delete the `release/*` branch (auto on squash if "auto-delete head branches" is on).

## 4. Hotfix policy

- Branch from master: `hotfix/<scope>-<slug>`.
- Direct PR to master, label `hotfix`, single-commit when feasible.
- Bump only PATCH on the affected train.
- Open a follow-up issue for a post-mortem within 7 days.

## 5. Train coordination

- **Platform breakage that affects KNOWRAG** → bump platform PATCH first, then KNOWRAG PATCH if a contract change leaked through.
- **KNOWRAG-internal breakage** → never bumps platform.
- **Cross-train PR** → two scopes in commit (`feat(api,platform): …`), two tags cut, two changelog entries.

## 6. Version skew (KNOWRAG-internal)

KNOWRAG ships three services that share contracts: `apps/api`, `apps/ui`, `apps/mcp`. When a release breaks compatibility between any two:
1. Document the matrix in the KNOWRAG changelog under `### Skew`.
2. Mention the matrix in the GitHub release notes.
3. If the skew is large, ship the components on a single tag and pin them together (don't independently bump for one cycle).

## 7. Future automation: release-please

Adopt `googleapis/release-please-action@v4` in **manifest mode** when:
- ≥ 3 manual tags have been cut on each train, AND
- The changelogs have started to drift from commits.

### Planned configuration

`release-please-config.json`:
```json
{
  "release-type": "simple",
  "include-component-in-tag": true,
  "tag-separator": "-",
  "packages": {
    ".": {
      "release-type": "simple",
      "package-name": "platform",
      "changelog-path": "CHANGELOG.md"
    },
    "@lab/ll-KNOWRAG": {
      "release-type": "simple",
      "package-name": "knowrag",
      "changelog-path": "CHANGELOG.md"
    }
  }
}
```

`.release-please-manifest.json`:
```json
{
  ".": "0.0.0",
  "@lab/ll-KNOWRAG": "0.0.0"
}
```

Workflow file (`.github/workflows/release-please.yaml`) will run on push-to-master and `workflow_dispatch`. PR-driven — never auto-tags from a push.

## 8. Rollback

If a release tag points at a broken master:
1. **Don't delete the tag** (signed history). Cut a new PATCH that reverts the offender.
2. Tag the new PATCH; mark the broken release as a pre-release in `gh release edit`.
3. Open a post-mortem issue.

For a stack-level deploy rollback (separate from tags), use Gitea Actions `deploy.yaml` against a previous SHA.

## 9. Where artifacts live

| Artifact | Path |
|----------|------|
| Platform changelog | `CHANGELOG.md` |
| KNOWRAG changelog | `@lab/ll-KNOWRAG/CHANGELOG.md` |
| Tags | `git tag` (signed, never deleted) |
| Release notes | GitHub Releases page |
| Release branch (ephemeral) | `release/<train>-vX.Y.Z` |

## 10. Pre-1.0 stability

While in `v0.x`, MINOR releases MAY include breaking changes — call them out under `### Breaking` in the changelog. Once a train hits `v1.0.0`, full SemVer applies and breaking changes require a MAJOR bump.

## 11. Who pushes the merge button

- Solo operator today: any CODEOWNER (`@w7-mgfcode`).
- When the release-please flow is adopted, a release-PR is opened automatically; merging that PR is the entire release ceremony.
