# AGENTS.md — ll-RELIQUARY

> Agent-side overview for this stack. For full project rules read `CLAUDE.md`; for the platform rules see the repo root `AGENTS.md` and `.claude/rules/`.

## What this stack is

ll-RELIQUARY is a browser-based collectable card / artifact game in `@lab`. **Phase: Boilerplate** — no game logic yet, planning trio (`BRAINSTORM.md` / `STORYBOARD.md` / `ARCHITECTURE.md`) is the active artifact.

## The non-negotiable

**Every UI change** goes through Stitch → agent-browser → (Playwright if needed). See `.claude/rules/ui-design-pipeline.md`. Hand-rolled screens are a bug.

## Specialist tools for this stack

| Surface | First-choice tool |
|---------|-------------------|
| New / edited screen | `Skill: stitch-design` |
| Vague UI prompt | `Skill: enhance-prompt` → `stitch-design` |
| Multi-screen iteration | `Skill: stitch-loop` |
| Design system synthesis | `Skill: design-md` |
| Visual verification | `Skill: agent-browser` |
| Complex e2e / network mocks | `mcp__plugin_playwright_playwright__*` + `Skill: webapp-testing` |
| Stitch direct calls | `mcp__stitch__*` |

## Useful root agents

| Agent | When |
|-------|------|
| `policy-gatekeeper` | Before risky bash; before cross-zone changes |
| `repo-visibility-manager` | If you touch this stack's README / planning trio at release time |
| `Plan` | When breaking down a new phase (Phase 1, 2, …) before execution |
| `Explore` | Fast lookups within `@lab/ll-RELIQUARY/` |

## Daily commands

```bash
w7 up @lab/ll-RELIQUARY      # boot stack
w7 logs @lab/ll-RELIQUARY    # tail logs
w7 down @lab/ll-RELIQUARY    # graceful stop
w7 prune @lab/ll-RELIQUARY   # destroy (allowed only in @lab)
```

## Conventions

- **Commits**: `type(scope): description (#issue)`. Add `reliquary` to the commit-format scope allow-list before first commit, or fall back to `stacks`.
- **Branches**: `feat/reliquary-*`, `fix/reliquary-*`, kebab-case ≤ 50 chars.
- **Issue first**: every commit references `#N` on the `stack:reliquary` issue tracker.
- **No `:latest`**: image pins always.
- **No invented tokens**: `.stitch/DESIGN.md` is the source of truth.

## Phase-0 acceptance checklist

- [x] `.w7-meta`, `compose.yml`, `.env.example`, `.gitignore` written
- [x] Planning trio committed: `BRAINSTORM.md`, `STORYBOARD.md`, `ARCHITECTURE.md`
- [x] Local rules: `.claude/rules/ui-design-pipeline.md`, `.claude/rules/docker-infra.md`
- [x] `.stitch/DESIGN.md` placeholder (generation deferred to Phase 1)
- [x] Container stubs build and boot (`/health` returns 200)
- [ ] `w7 up @lab/ll-RELIQUARY` verified locally
- [ ] First agent-browser baseline run saved under `dogfood-output/baseline-<UTC>/`
- [ ] `BRAINSTORM.md` §3 open questions answered → Phase 1 unlocked

When all boxes are ticked, the stack is ready for Phase 1 (Design heavy).
