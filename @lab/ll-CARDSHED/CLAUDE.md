# CLAUDE.md — ll-CARDSHED

> Project instructions for Claude Code inside this stack. Root rules at `~/w7-base/.claude/rules/` still apply; this file layers stack-specific rules on top.

## Stack identity

ll-CARDSHED is a browser implementation of the **CARD SHED** card game (3–4 player, shifting-trump, single-deck). It's a `@lab` sandbox — disposable, instant-deploy via webhook, no production gates.

**Current phase: CORE SEALED.** The pure-logic rules engine (`apps/core/`) is shipped and tested. The active artifact is `PRPs/cardshed-03-experience-prp.md` — the 17-milestone plan covering MVP + UI/UX + WebSocket + analytics + AI bots.

## Hard rules (stack-local)

Always loaded from `.claude/rules/` inside this directory:

- **`ui-design-pipeline.md`** — MANDATORY Stitch + agent-browser + Playwright workflow once `apps/ui/` exists. **No hand-rolled UI.** No invented design tokens. Every screen has a Stitch origin under `docs/SCREENS/` and an agent-browser validation under `dogfood-output/<timestamp>/`.
- **`core-determinism.md`** — Purity guarantees for `apps/core/`. No `Math.random`, `Date.now`, `new Date()`, `performance.now`, `crypto.getRandomValues` outside `prng.ts`. Every reducer returns a fresh `MatchState`. ESLint enforces this.

These layer on top of root rules (`commit-format.md`, `branch-naming.md`, `security-patterns.md`, etc.).

## How to work in this stack

1. **Read the PRP bundle.** Before touching anything, read `PRPs/cardshed-01-blueprint.md` (locked tech-stack + module taxonomy), `PRPs/cardshed-02-core-prp.md` (delivered core + flagged contradictions), and `PRPs/cardshed-03-experience-prp.md` (the active execution plan).
2. **Core is sealed.** Do not modify `apps/core/` rule logic without an explicit issue + the same level of property-test coverage. `npm test` and `npm run sim-smoke` must both stay green at every commit.
3. **UI work goes through the pipeline.** Period. See `.claude/rules/ui-design-pipeline.md`. Does not apply yet — there's no UI — but applies the moment `apps/ui/` lands.
4. **Use the W7 CLI.** `w7 up @lab/ll-CARDSHED`, `w7 logs`, `w7 down`. Direct `docker compose` is acceptable for debugging only.
5. **Commit grammar.** Per root `commit-format.md` — `feat|fix|chore|docs(cardshed): description (#issue)`. The `cardshed` scope is already in the allow-list (added in #139).
6. **Branches.** `feat/cardshed-*`, `fix/cardshed-*`, `chore/cardshed-*`, kebab-case ≤50 chars.
7. **Issue first.** Every commit references `#N`. Open an issue before committing.
8. **One PR per PRP 3 milestone.** PRP 3's 17 milestones are intentionally atomic. Bundling them = bad PRs.
9. **Don't invent rule variants.** CARD SHED v2.0 is frozen in PRP 2. Variant exploration belongs to PRP 3's simulation harness behind an explicit `RuleVariant` flag — never silently in the engine.

## Common commands

```bash
# Core (pure-logic library — no container)
cd @lab/ll-CARDSHED/apps/core
npm install
npm test              # 82/82 green
npm run typecheck     # 0 errors
npm run lint          # 0 errors, 0 warnings
npm run sim-smoke     # 1000 random-legal-bot games, <30s

# Stack (bootstrap stub — boots a placeholder until PRP 3 M1)
w7 up @lab/ll-CARDSHED
w7 logs @lab/ll-CARDSHED
w7 down @lab/ll-CARDSHED
w7 prune @lab/ll-CARDSHED   # destroy (allowed only in @lab)

# Compose syntax + envvar coverage
docker compose --env-file .env.example -f @lab/ll-CARDSHED/compose.yml config -q
```

## Service map (target — most services do not exist yet)

| Service | Tech | Container port | Host port | Status |
|---------|------|----------------|-----------|--------|
| `cardshed-placeholder` | alpine 3.20 | — | — | ✅ bootstrap stub |
| `cardshed-ui` | React + Vite + Tailwind v4 + Radix, served by nginx | 8080 | 4343 | ⏭️ PRP 3 M1 |
| `cardshed-server` | Rust + Axum, uvicorn-equivalent | 8383 | 8383 | ⏭️ PRP 3 M3 |
| `cardshed-db` | Postgres 16 | 5432 | 5555 | ⏭️ PRP 3 M3 |

Start order will be healthcheck-gated once the real services exist: `db` → `server` → `ui`.

## Design pipeline (active once `apps/ui/` exists)

```
   Screen spec (PRP 3 §B)
        ↓
   Skill: stitch-design  (or stitch-loop for multi-screen)
        ↓
   docs/SCREENS/<screen-slug>.md   ← committed
        ↓
   Implement UI (consume .stitch/DESIGN.md tokens)
        ↓
   Skill: agent-browser → dogfood-output/<utc>/ → screenshots + report.md
        ↓
   (if complex eval) playwright MCP + webapp-testing skill
        ↓
   PR with all evidence linked
```

**Hard prohibition**: claiming a UI change works without agent-browser evidence. Type-check + unit-tests passing ≠ UI works.

## PRP execution map

| PRP | What | Where | Status |
|-----|------|-------|--------|
| 1 — Blueprint | Tech-stack + sync model + module taxonomy + roadmap | `PRPs/cardshed-01-blueprint.md` | ✅ locked |
| 2 — Deterministic Core | TS rules engine + types + Vitest + sim-smoke | `apps/core/` + `PRPs/cardshed-02-core-prp.md` | ✅ shipped (#139, #140) |
| 3 — Experience & Distribution | MVP + UI/UX + WebSocket + analytics + AI bots (17 milestones) | `PRPs/cardshed-03-experience-prp.md` | ⏭️ next slice |

## Out of scope (this iteration of the stack root)

- Real UI / game screens (PRP 3 M1)
- Real server / WebSocket protocol (PRP 3 M3)
- Real bots (PRP 3 §E)
- Multi-round match semantics (PRP 3 NEW #9 — deferred post-MVP)
- `@prod` promotion
- Card art / asset pipeline

## Reference

- `PRPs/cardshed-01-blueprint.md` — locked decisions
- `PRPs/cardshed-02-core-prp.md` — delivered core + flagged contradictions
- `PRPs/cardshed-03-experience-prp.md` — next slice (17 milestones)
- `apps/core/src/core/types.ts` — frozen Shared Contract
- `apps/core/src/core/rules.ts` — Rules Engine API surface
- `.claude/rules/ui-design-pipeline.md` — mandatory UI pipeline (active from M1)
- `.claude/rules/core-determinism.md` — apps/core/ purity guarantees
