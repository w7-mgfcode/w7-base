# Sources — 2026-05-07 Repo Strategy Session

> Every external source cited in this session, grouped by research agent. Each entry has an accessed-on date and a one-line "how to refresh" note so future-you knows when to re-fetch.

## Refresh policy (read this first)

| Topic area | Shelf life | Refresh trigger |
|------------|-----------|-----------------|
| Branching models (GitHub Flow / TBD / etc.) | ~12 months | Yearly review; the consensus has been stable since 2023 |
| GitHub branch protection / Rulesets | ~3 months | Re-fetch whenever you author/edit `.github/rulesets/*.json` — the surface evolves quarterly |
| release-please / changesets | ~6 months | Re-check on a major-version bump of either tool, or before a release-tooling decision |
| GitHub Actions security (SHA pinning, CVEs) | ~3 months | Re-check on every Dependabot bump that bumps an Action major version |
| CodeQL / trivy / gitleaks coverage | ~6 months | Re-check yearly or on tool-major-version events |
| Claude Code subagent / skill / hook schema | ~3 months | Re-fetch on any Claude Code minor release (CHANGELOG) |
| Documentation freshness / docs-as-code | ~12 months | Stable; refresh on team-grow or repo-merge events |

## Agent A — Branching + Repo Hygiene

| Title | URL | Accessed | Refresh hint |
|-------|-----|---------|--------------|
| Branching strategies for monorepo development (Graphite) | https://graphite.com/guides/branching-strategies-monorepo | 2026-05-07 | Yearly; trunk-vs-flow consensus drifts slowly |
| Agile Git Branching Strategies in 2026 (JavaCodeGeeks) | https://www.javacodegeeks.com/2025/11/agile-git-branching-strategies-in-2026.html | 2026-05-07 | Replace if a 2027 follow-up appears |
| Trunk Based Development — Monorepos | https://trunkbaseddevelopment.com/monorepos/ | 2026-05-07 | Stable; re-check on TBD spec bumps |
| Monorepos: Version, Tag, and Release Strategy (Streamdal/Medium) | https://medium.com/streamdal/monorepos-version-tag-and-release-strategy-ce26a3fd5a03 | 2026-05-07 | Re-read when picking release-please vs changesets |
| release-please automated SemVer (DevOpsil, 2026-03) | https://devopsil.com/articles/2026-03-21-semantic-versioning-automated-releases | 2026-05-07 | Refresh when adopting release-please |
| About rulesets — GitHub Docs | https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets | 2026-05-07 | Refresh before authoring `.github/rulesets/master.json` |
| Available rules for rulesets — GitHub Docs | https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets | 2026-05-07 | Same trigger as above |
| GitHub Branch Protection Rules complete guide 2026 | https://copyprogramming.com/howto/can-i-add-a-new-branch-protection-rule-via-github-api | 2026-05-07 | Re-fetch if migrating to org-level rulesets |
| Every big monorepo needs CODEOWNERS (Satellytes) | https://www.satellytes.com/blog/post/monorepo-codeowner-github-enterprise/ | 2026-05-07 | Stable; re-check only on team-grow event |
| 10 Code Owners Strategies for Monorepos (Modexa) | https://medium.com/@Modexa/10-code-owners-strategies-for-monorepos-2ab01e848182 | 2026-05-07 | Optional follow-up read |
| GitHub Docs — Auto-delete head branches | https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-the-automatic-deletion-of-branches | 2026-05-07 | Stable |
| Remove Stale Branches Action (Marketplace) | https://github.com/marketplace/actions/remove-stale-branches | 2026-05-07 | Re-pin SHA when wiring the cleanup workflow |

## Agent B — CI/CD + Release + GitHub Actions

| Title | URL | Accessed | Refresh hint |
|-------|-----|---------|--------------|
| release-please manifest-releaser docs | https://github.com/googleapis/release-please/blob/main/docs/manifest-releaser.md | 2026-05-07 | Re-check on release-please v5 |
| release-please-action repo | https://github.com/googleapis/release-please-action | 2026-05-07 | Watch for v5 breaking changes |
| Beware release-please v4 (Wakeem) | https://danwakeem.medium.com/beware-the-release-please-v4-github-action-ee71ff9de151 | 2026-05-07 | Stable post-mortem |
| Changesets monorepo guide (jsdev) | https://jsdev.space/complete-monorepo-guide/ | 2026-05-07 | Refresh if pnpm workspaces adopted |
| CodeQL supported languages | https://codeql.github.com/docs/codeql-overview/supported-languages-and-frameworks/ | 2026-05-07 | Yearly; check shell support |
| CodeQL 2.24.0 changelog | https://codeql.github.com/docs/codeql-overview/codeql-changelog/codeql-cli-2.24.0/ | 2026-05-07 | Quarterly |
| Gitleaks vs TruffleHog 2026 (AppSec Santa) | https://appsecsanta.com/sast-tools/gitleaks-vs-trufflehog | 2026-05-07 | Yearly |
| Rafter — secret scanner comparison | https://rafter.so/blog/secrets/secret-scanning-tools-comparison | 2026-05-07 | Stable |
| GitHub Actions SHA pinning policy (Aug 2025) | https://github.blog/changelog/2025-08-15-github-actions-policy-now-supports-blocking-and-sha-pinning-actions/ | 2026-05-07 | Stable changelog entry |
| StepSecurity SHA pinning guide | https://www.stepsecurity.io/blog/pinning-github-actions-for-enhanced-security-a-complete-guide | 2026-05-07 | Refresh on policy changes |
| CISA: tj-actions CVE-2025-30066 | https://www.cisa.gov/news-events/alerts/2025/03/18/supply-chain-compromise-third-party-tj-actionschanged-files-cve-2025-30066-and-reviewdogaction | 2026-05-07 | Stable advisory |
| Wiz tj-actions analysis | https://www.wiz.io/blog/github-action-tj-actions-changed-files-supply-chain-attack-cve-2025-30066 | 2026-05-07 | Stable post-mortem |
| OpenSSF maintainers guide post-tj-actions | https://openssf.org/blog/2025/06/11/maintainers-guide-securing-ci-cd-pipelines-after-the-tj-actions-and-reviewdog-supply-chain-attacks/ | 2026-05-07 | Yearly |
| dorny/paths-filter v3 | https://github.com/dorny/paths-filter/tree/v3 | 2026-05-07 | Watch for v4; consider step-security fork |
| step-security/paths-filter (secure fork) | https://github.com/step-security/paths-filter | 2026-05-07 | If dorny goes unmaintained |
| Selective CI for monorepos | https://stn-dts.github.io/2025/10/21/monorepo-github-actions.html | 2026-05-07 | Stable |
| GitHub Actions cache reference | https://docs.github.com/en/actions/reference/workflows-and-actions/dependency-caching | 2026-05-07 | Refresh on actions/cache v5 |
| Reusable workflows vs composite actions (jfagerberg, Oct 2025) | https://jfagerberg.me/blog/2025-10-17-reusable-workflows-custom-actions/ | 2026-05-07 | Stable |
| Gitea Actions design docs | https://docs.gitea.com/usage/actions/design | 2026-05-07 | Refresh on Gitea 1.24+ |
| Hoop.dev — GitHub Actions on Gitea | https://hoop.dev/blog/the-simplest-way-to-make-github-actions-gitea-work-like-it-should | 2026-05-07 | Stable |
| ISE devblog — independent release cycles in monorepo | https://devblogs.microsoft.com/ise/streamlining-development-through-monorepo-with-independent-release-cycles/ | 2026-05-07 | Stable design pattern |

## Agent C — Agents / Skills / Hooks / Visibility

| Title | URL | Accessed | Refresh hint |
|-------|-----|---------|--------------|
| Create custom subagents (frontmatter spec, `tools:` format) | https://code.claude.com/docs/en/sub-agents | 2026-05-07 | Re-fetch on Claude Code minor releases |
| Extend Claude with skills (SKILL.md frontmatter, lifecycle) | https://code.claude.com/docs/en/skills | 2026-05-07 | Quarterly or on `disable-model-invocation` field changes |
| Hooks reference (PreToolUse `permissionDecision: deny`) | https://code.claude.com/docs/en/hooks | 2026-05-07 | Re-fetch on any `settings.json` schema change |
| Subagents Italian mirror (cross-check) | https://docs.anthropic.com/it/docs/claude-code/sdk/subagents | 2026-05-07 | Cross-reference only |
| Anthropic Skills repo (skill-creator example) | https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md | 2026-05-07 | On version bumps |
| Hooks complete guide (community) | https://claudefa.st/blog/tools/hooks/hooks-guide | 2026-05-07 | Verify against official docs |
| Disler hooks-mastery repo (settings.json examples) | https://github.com/disler/claude-code-hooks-mastery | 2026-05-07 | Verify before adoption |
| DataCamp Claude Code Hooks tutorial | https://www.datacamp.com/tutorial/claude-code-hooks | 2026-05-07 | Tutorial; secondary source |

## In-repo references (not external)

These are W7-Base-internal references the session leaned on. Not "sources" in the cite sense, but the session would not have produced its specific shape without them. List for traceability.

| Path | Why it mattered |
|------|-----------------|
| `~/.claude/projects/-home-w7-hector-w7-localbase/memory/MEMORY.md` | The auto-memory index — KNOWRAG Phase 8 traps, workflow preferences, agent-browser as the only working UI verifier |
| `.shared/W7-CONTRACT.md` | Stack-contract semantics that informed `BRANCHING.md` zone matrix |
| `.shared/SECRETS.md` | SOPS+AGE three-file model used to rewrite `security-patterns.md` |
| `.shared/policy/*.sh` | Existing static policy scripts; informed Agent C's `policy-gatekeeper` shape |
| `.claude/skills/skill-creator/SKILL.md` | Skill anatomy + `init_skill.py` / `package_skill.py` scripts the reusable stub points at |
| `@lab/ll-KNOWRAG/.claude/rules/*.md` | Path-scoped frontmatter pattern (`paths:`) reused for `versioning.md` |
| `.memo/hooks/*.py` | Active SessionStart/PreCompact/SessionEnd implementations; informed the no-duplicate-hook decision |

## How to refresh this entire bibliography

```bash
# In a fresh session, run the same three agent search queries
# (see PATTERN.md § "How to re-run") and replace the rows in this table
# with new accessed-on dates.

# Quick rot-check (run this monthly):
xargs -I{} -P 8 sh -c 'curl -sI -o /dev/null -w "%{http_code} {}\n" --max-time 5 "{}"' \
  < <(grep -oE 'https?://[^ )]+' SOURCES.md | sort -u) \
  | grep -vE '^(2|3)' | sed 's/^/STALE: /'
```

Anything not returning 2xx/3xx is a candidate for refresh.
