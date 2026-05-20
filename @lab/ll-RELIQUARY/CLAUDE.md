# CLAUDE.md — ll-RELIQUARY

> Project instructions for Claude Code inside this stack. Root rules at `~/w7-base/.claude/rules/` still apply; this file layers stack-specific rules on top.

## Stack identity

ll-RELIQUARY is a browser-based collectable card / artifact game. It's a `@lab` sandbox — disposable, instant-deploy via webhook, no production gates.

**Current phase: BOILERPLATE.** The stack boots, the pipeline is locked, no game logic yet. The active artifact is the *planning trio*: `BRAINSTORM.md` → `STORYBOARD.md` → `ARCHITECTURE.md`.

## Hard rules (stack-local)

Always loaded from `.claude/rules/` inside this directory:

- **`ui-design-pipeline.md`** — MANDATORY Stitch + agent-browser + Playwright workflow. **No hand-rolled UI.** No invented design tokens. Every screen has a Stitch origin under `docs/SCREENS/` and an agent-browser validation under `dogfood-output/<timestamp>/`.
- **`docker-infra.md`** — image pinning, healthcheck-gated start order, three-file secret model, no `:latest`.

These layer on top of root rules (`commit-format.md`, `branch-naming.md`, `security-patterns.md`, etc.).

## How to work in this stack

1. **Read the trio.** Before touching anything, read `BRAINSTORM.md`, `STORYBOARD.md`, `ARCHITECTURE.md`. They are the source of truth for product direction.
2. **UI work goes through the pipeline.** Period. See `.claude/rules/ui-design-pipeline.md`.
3. **Use the W7 CLI.** `w7 up @lab/ll-RELIQUARY`, `w7 logs`, `w7 down`. Direct `docker compose` is acceptable for debugging only.
4. **Commit grammar.** Per root `commit-format.md` — `feat|fix|chore|docs(scope): description (#issue)`. Use scope `knowrag`'s sibling for game work: open issues with label `stack:reliquary` and use the *new* scope `reliquary` once it's added to the allow-list. **Today the allow-list doesn't include `reliquary` — add it before the first commit, or use `stacks` as a fallback.**
5. **Branches.** `feat/reliquary-*`, `fix/reliquary-*`, etc. — kebab-case, ≤50 chars.
6. **Issue first.** Every commit references `#N`. Open an issue with the `stack:reliquary` label before committing.
7. **Don't add features beyond what the boilerplate requires.** This stack has a real risk of scope-creep into "platform with cards" instead of "card game". Defer-or-document any expansion in `BRAINSTORM.md` §7.

## Common commands

```bash
# Boot
w7 up @lab/ll-RELIQUARY

# Tail logs
w7 logs @lab/ll-RELIQUARY

# Compose syntax + envvar coverage
docker compose --env-file .env.example config -q

# Tear down (keeps data/)
w7 down @lab/ll-RELIQUARY

# Destroy everything (sandbox only — @lab allows prune)
w7 prune @lab/ll-RELIQUARY

# UI dev (hot-reload outside Docker — for fast loop with Stitch outputs)
cd apps/ui && npm install && npm run dev

# API dev (hot-reload outside Docker)
cd apps/api && pip install -r requirements.txt
PYTHONPATH=src uvicorn server.main:app --host 0.0.0.0 --port 8282 --reload
```

## Service map

| Service | Tech | Container port | Host port |
|---------|------|----------------|-----------|
| `reliquary-ui` | React + Vite + Tailwind v4 + Radix + framer-motion + PixiJS, served by nginx | 8080 | 4242 |
| `reliquary-api` | FastAPI (Python 3.12), uvicorn | 8282 | 8282 |
| `reliquary-db` | Postgres 16 (alpine) | 5432 | 5454 |
| `reliquary-cache` | Redis 7 (alpine) | 6379 | 6464 |

Start order is healthcheck-gated: `db + cache` → `api` → `ui`.

## Design pipeline summary

```
   Wireframe (STORYBOARD.md §5)
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

## Phase plan

| Phase | What ships | Done when |
|-------|-----------|-----------|
| 0 — Boilerplate (now) | Stack contract + planning trio + pipeline lock | This README's checklist is ✅ |
| 1 — Design heavy | `.stitch/DESIGN.md` generated; S01–S09 mockups; visual validation | First three screens approved by user |
| 2 — Vertical slice | Journey A (cold-landing → first-pull) end-to-end | Real artifact persists across restart |
| 3 — Curator loop | Journey B + C; lineage UI; share OG-image | First external playtester onboarded |
| 4 — Hardening | Playwright e2e; observability; backup story | `reliquary-v0.1.0` tag cut |

## Out of scope (boilerplate)

- Real game logic
- Real artifacts / card art
- Database schema migrations (Alembic, etc.) — defer until ARCHITECTURE §3 is locked
- Auth flow beyond device-key sketch
- Multiplayer / trade
- Mobile-specific gestures
- `@prod` promotion

## Reference

- `BRAINSTORM.md` — vision, open questions, anti-goals, risks
- `STORYBOARD.md` — user journeys, screen inventory, flows
- `ARCHITECTURE.md` — system shape, data sketch, decision log
- `.stitch/DESIGN.md` — generated design system (placeholder until first stitch-design run)
- `.claude/rules/ui-design-pipeline.md` — mandatory UI pipeline
- `.claude/rules/docker-infra.md` — container infra rules
