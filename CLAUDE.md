# CLAUDE.md

> Project instructions for Claude Code. Terse on purpose — `README.md` is the human-facing overview, `AGENTS.md` is the agent overview, and `.claude/rules/*.md` are the always-loaded policy files.

## Repo identity

W7-Base is a single-host, Compose-shaped, GitOps-driven monorepo with four zones:

- `@ops/` — platform & infrastructure (Gitea, Traefik, Prometheus, Grafana, …)
- `@dev/` — active development stacks
- `@prod/` — production-grade local stacks (gated, interactive `--yes` required)
- `@lab/` — sandboxes / experiments (only zone where `w7 prune` is allowed)

The active sub-project is `@lab/ll-KNOWRAG/` — see its own `CLAUDE.md` and `BLUEPRINT.md`.

## Hard rules (always apply)

These are loaded automatically from `.claude/rules/`:

- `commit-format.md` — `type(scope): description (#issue)`; no AI co-author trailers
- `product-vision.md` — single-host, Compose-only, zone-first, SOPS secrets
- `security-patterns.md` — three-file secret model, no privileged @prod, validate webhook HMAC
- `test-requirements.md` — `w7 verify` is the platform test contract; KNOWRAG keeps unit-test floor
- `output-formatting.md` — emoji status indicators, box-drawing separators, scannable reports
- `ui-design.md` — UI work goes through Stitch + frontend-design + agent-browser
- `branch-naming.md` — branch names mirror commit grammar
- `versioning.md` — two SemVer trains: `platform-vX.Y.Z` + `knowrag-vX.Y.Z`

## How to work in this repo

1. **Read first.** Before touching a stack, read `<stack>/AGENTS.md` (if present) and `<stack>/.w7-meta`.
2. **Stay in your zone.** A change in `@dev/x` should not touch `@ops/y` without a clear cross-zone reason.
3. **Use the CLI, don't reach around it.** `w7 up`, `w7 doctor`, `w7 verify`, `w7 secret edit`. Direct `docker compose` is acceptable for debugging only.
4. **Issue before commit.** Every commit references `#N`. Open an issue first if needed.
5. **Branch off master, PR back, squash.** GitHub Flow. Branch names follow `<type>/<scope-slug>` — see `BRANCHING.md`.
6. **Two version trains.** Platform and KNOWRAG tag independently — never bump them together.

## What lives where

| Path | What it is |
|------|-----------|
| `.bin/w7` | The CLI entry-point (Bash) |
| `.shared/w7.sh` | Shell integration (sourced from `~/.bashrc`) |
| `.shared/policy/*.sh` | Static policy checks run by `w7 doctor` and CI |
| `.shared/W7-CONTRACT.md` | The stack contract (`.w7-meta` schema) |
| `.shared/SECRETS.md` | SOPS+AGE operator guide |
| `.shared/GITOPS_DESIGN.md` | Webhook + Actions deploy design |
| `.github/workflows/` | GitHub-side CI (gating + releases + security) |
| `.gitea/workflows/` | Local Gitea-side CI (deploy via act-runner) |
| `.claude/rules/*.md` | Always-loaded project rules (this file references them) |
| `.claude/agents/*.md` | Specialist subagents (`repo-visibility-manager`, …) |
| `.claude/skills/*` | Project-installed skills |
| `.claude/hooks/*.sh` | PreToolUse / SessionStart hook scripts |
| `.memo/` | Active memory-compiler runtime (hooks + daily/) |
| `docs/` | Platform documentation (operator-facing) |
| `docs/_session-patterns/` | Reusable session patterns extracted from past work |

## Before you do destructive things

The user MUST confirm before:
- `git push --force` (forbidden against `master`)
- `git reset --hard`
- `docker compose down -v` (destroys volumes)
- `w7 prune` outside `@lab/`
- `gh issue close` (system-level rule — close manually with verification claim)
- Mass file deletes, branch deletes, tag deletes

Reading and searching is always allowed. Acting on shared state is not.

## Useful agents and skills

| Agent | When |
|-------|------|
| `repo-visibility-manager` | Audit README / docs / llms.txt clarity before a release |
| `policy-gatekeeper` | Wrap `.shared/policy/*` checks before risky ops |
| `knowrag-investigator` | Specialist for `@lab/ll-KNOWRAG/` failures |

| Skill | When |
|-------|------|
| `repo-visibility-audit` | Run a full visibility audit (read-only report) |
| `commit-format-check` | Validate a staged commit message |
| `audit-rules-drift` | Detect drift between `.claude/rules/` and the codebase |

## Reference

- `README.md` — platform overview for humans
- `AGENTS.md` — agent overview (kept short; lives at root)
- `BRANCHING.md` — branching + release strategy
- `RELEASE.md` — release cadence + tag-cut procedure
- `docs/README-LLM.md` — LLM-optimized concise platform guide
- `docs/_session-patterns/` — reusable session patterns
