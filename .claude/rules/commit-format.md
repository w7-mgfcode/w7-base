# Commit Message Format

Every commit in this repository MUST follow this format:

```
type(scope): description (#issue)
```

## Rules

- **type** — one of: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `release`
- **scope** — one of the W7-Base scope allow-list (below). Comma-pairs are allowed when a change cuts across two scopes (e.g., `ui,api`).
- **description** — lowercase, imperative mood, no trailing period
- **#issue** — a valid GitHub issue number. Every commit MUST reference one.

### Scope allow-list

| Scope | Use for |
|-------|---------|
| `knowrag` | Anything under `@lab/ll-KNOWRAG/` that doesn't fit a narrower scope below |
| `api` | KNOWRAG `apps/api/` |
| `ui` | KNOWRAG `apps/ui/` |
| `mcp` | KNOWRAG `apps/mcp/` |
| `ingest` | KNOWRAG ingestion pipeline (crawling/embedding/chunking) |
| `reliquary` | Anything under `@lab/ll-RELIQUARY/` (browser-based collectable artifact game) |
| `cardshed` | Anything under `@lab/ll-CARDSHED/` (CARD SHED card game — pure-logic core + UI + bots) |
| `repo` | Repo-wide hygiene (gitignore, scaffolding, untracked-path triage) |
| `platform` | `.bin/`, `.shared/`, top-level CLI |
| `stacks` | Anything under `@ops/`, `@dev/`, `@prod/` (any single zone-stack) |
| `state` | `.omg/state/` artifacts (taskboard, checkpoint, ROADMAP, …) |
| `ops` | `@ops/*` operational stacks (gitea, traefik, prometheus, grafana, …) |
| `ci` | `.github/workflows/`, `.gitea/workflows/`, `.shared/workflows/` |
| `docs` | Anything under `docs/`, root `README.md`, `AGENTS.md`, `CLAUDE.md`, `llms.txt` |
| `release` | Tag-cut commits and changelog updates |

### No AI co-author trailer — ever

Do NOT include any of the following in commit messages — past, present, or future model versions:

- `Co-Authored-By: Claude <noreply@anthropic.com>`
- `Co-Authored-By: Claude <any-version> <noreply@anthropic.com>`
- `Generated with [Claude Code]` lines
- `🤖 Generated with …` lines
- Any other AI-attribution line

The session is already attributed via `git config user.name` (e.g., `Gemini CLI`). That is the only attribution we keep.

## Examples

Good:
- `feat(ui): wire SourceDetail to /related (#42)`
- `fix(api): preserve POST body across 30x redirects (#17)`
- `chore(repo): triage 9 untracked tooling paths (#11)`
- `docs(knowrag): document w7 verify across runbook + READMEs (#17)`
- `release(platform): cut platform-v0.1.0 (#100)`
- `feat(ui,api): add /related to artifact detail (#42)`

Bad:
- `fixed bug` — no type, scope, or issue
- `feat: add new feature` — missing issue reference
- `feat(api): Add Endpoint (#17)` — capitalized description
- `feat(misc): X (#17)` — `misc` is not in the allow-list

## Scope exception

`docs` and `release` types may omit scope when the change is project-wide (e.g., root README, CHANGELOG bump for both trains).

## Before committing

Verify, in this order:
1. Message matches `type(scope): description (#issue)`
2. The issue exists and is open: `gh issue view <N> --json state`
3. The scope matches the primary path being changed
4. The type accurately reflects the change (`feat`=new, `fix`=bug, `chore`=non-functional, `release`=tag-cut)
5. There is NO AI co-author or "Generated with" trailer

If a user-supplied message doesn't match, reformat it. If no issue number is provided, ask — never commit without one.

A `commit-format-check` skill and a `PreToolUse` hook (`.claude/hooks/check-commit-format.sh`) enforce this rule deterministically.
