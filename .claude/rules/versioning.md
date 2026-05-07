---
paths:
  - "@lab/ll-KNOWRAG/**"
  - "@ops/**"
  - "@dev/**"
  - "@prod/**"
  - ".shared/**"
  - ".bin/**"
  - "CHANGELOG*.md"
  - "RELEASE.md"
  - "BRANCHING.md"
---

# Versioning

W7-Base ships **two independent SemVer trains** in one repo. They tag independently, never lockstep.

## Trains

| Train | Tag prefix | Source paths | Changelog |
|-------|-----------|--------------|-----------|
| Platform | `platform-vX.Y.Z` | `@ops/`, `@dev/`, `@prod/`, `.shared/`, `.bin/w7`, root configs | `CHANGELOG.md` (root) |
| KNOWRAG | `knowrag-vX.Y.Z` | `@lab/ll-KNOWRAG/**` | `@lab/ll-KNOWRAG/CHANGELOG.md` |

Both start in `v0.Y.Z` until declared stable.

## SemVer mapping

| Bump | Trigger |
|------|---------|
| MAJOR (1.0.0 → 2.0.0) | Breaking change to `w7` CLI flags, `.w7-meta` schema, KNOWRAG API/MCP contract, `compose.yml` env-var contract removal |
| MINOR (0.1.0 → 0.2.0) | New CLI subcommand, new stack, new KNOWRAG endpoint/tool, new policy script, new SOPS rule |
| PATCH (0.1.0 → 0.1.1) | Bug fix, doc-only change, dependency bump, internal refactor |

## What does NOT bump a version

- `docs/` changes only
- `.claude/rules/` adjustments
- CI / workflow internals (`.github/workflows/`, `.gitea/workflows/`)
- Memory-compiler tweaks (`.memo/`, `.shared/claude-memory-compiler/`)
- Dev-loop ergonomics that ship no runtime behavior

## Cross-train PRs

If a PR touches both trains:
1. Use a multi-scope commit (`feat(api,platform): …`).
2. PR title says so.
3. When tagging, cut **two separate tags** (one per train).
4. Each train's CHANGELOG gets its own entry.

## Pre-1.0 stability

While in `v0.x`, MINOR may include breaking changes — call them out in the changelog under a `### Breaking` heading. Once a train hits `v1.0.0`, full SemVer applies and breaking changes require a MAJOR bump.

## Future automation

When manual cuts get painful, switch to `googleapis/release-please-action@v4` in manifest mode. See `RELEASE.md` for the planned config (two components, per-component changelogs, `include-component-in-tag: true`). Until then, follow the manual procedure in `BRANCHING.md` § 6.

## Skew policy (KNOWRAG-internal)

The KNOWRAG api ↔ ui ↔ mcp services have an internal compatibility matrix. When a KNOWRAG release breaks compatibility between any two of these, document the matrix in `@lab/ll-KNOWRAG/CHANGELOG.md` and call it out in the GitHub release notes.
