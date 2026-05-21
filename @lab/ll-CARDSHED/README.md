# ll-CARDSHED

> Local-first browser implementation of the **CARD SHED** card game.
> A `@lab` sandbox inside W7-Base. Pure-logic core sealed; browser hot-seat MVP next.

---

## Status

📋 **Core sealed. UI/network/AI pending.** The deterministic rules engine is shipped and tested. The next slice is a hot-seat browser MVP per PRP 3 M1.

| Layer | State |
|-------|-------|
| Stack contract (`.w7-meta`, `compose.yml`, env) | ✅ bootstrap stub |
| Pure-logic core (`apps/core/`) | ✅ sealed — 82/82 tests green, conservation property holds ≥200 iters |
| Strategy + Blueprint (`PRPs/cardshed-01-blueprint.md`) | ✅ locked |
| Experience & Distribution PRP (`PRPs/cardshed-03-experience-prp.md`) | ✅ generated — 17 milestones |
| Stitch design system (`.stitch/DESIGN.md`) | 📋 placeholder — generate via `stitch-design` skill at PRP 3 M1 |
| `apps/ui/` (React + Vite + Tailwind v4) | ⏭️ PRP 3 M1 |
| `apps/server/` (Rust + Axum) | ⏭️ PRP 3 M3 (online multiplayer) |
| Bot ladder (Levels 0/1/2) | ⏭️ PRP 3 M9/M11/M13 |

---

## What it is

CARD SHED is a 3–4 player, single-deck, shifting-trump card game (Russian-style "fool" variant — *durak*-shaped, not *durak*-identical). The W7 implementation targets:

1. **A pure TypeScript rules engine** — the *truth machine*. UI, network, and AI are transformations over its state and event stream. Already shipped at `apps/core/`.
2. **A hot-seat browser MVP** — 3–4 humans share one device, pass-and-play. PRP 3 M1.
3. **A bot ladder** — Levels 0 (random-legal), 1 (heuristic), 2 (basic-search). PRP 3.
4. **An online server** — Rust + Axum, hybrid snapshot+event sync, replay from `(seed, actions[])`. PRP 3 M3+.

The rule set is **CARD SHED v2.0**, frozen in `PRPs/cardshed-02-core-prp.md`. The engine is deterministic given `(matchSeed, actions[])`; replay reproduces every match byte-identically.

---

## Stack

| Layer | Tech | Status |
|-------|------|--------|
| `@cardshed/core` | TypeScript 5.7 + Vitest 4 + fast-check 3 | ✅ shipped |
| `cardshed-ui` (future) | React 18 + Vite 5 + Tailwind v4 + Radix + framer-motion + Zustand + TanStack Query | ⏭️ PRP 3 M1 |
| `cardshed-server` (future) | Rust + Axum + tokio-tungstenite + sqlx + Postgres 16 | ⏭️ PRP 3 M3+ |

All eventual containers pin image tags (see `.claude/rules/docker-infra.md`). No `:latest`.

---

## Quick start

The core is a pure-logic library — no containers needed today:

```bash
cd @lab/ll-CARDSHED/apps/core
npm install
npm test          # 82/82 green; conservation property holds ≥200 iters
npm run sim-smoke # 1000 random-legal-bot games
```

Once PRP 3 M1 lands, the browser MVP will boot via:

```bash
# (forward-looking — apps/ui/ does not exist yet)
cd ~/w7-base
cp @lab/ll-CARDSHED/.env.example @lab/ll-CARDSHED/.env
w7 up @lab/ll-CARDSHED
open http://localhost:4343
```

Tear down (keeps `data/`):

```bash
w7 down @lab/ll-CARDSHED
```

---

## The mandatory UI pipeline (applies once `apps/ui/` exists)

This stack adopts the same **enforced** design workflow as `ll-RELIQUARY` — see `.claude/rules/ui-design-pipeline.md`.

```
  IDEA (PRP 3 §B screen inventory)
        ↓
  STITCH (stitch-design skill + Stitch MCP)
        ↓
  AGENT-BROWSER (visual validation, Vercel-sandboxed)
        ↓
  PLAYWRIGHT MCP (only for complex eval: multi-tab, network mocks, traces)
```

No hand-rolled screens. No invented design tokens. Every UI change has Stitch provenance and `dogfood-output/<timestamp>/` validation evidence.

---

## Phase plan (high level)

| Milestone | Output | Trigger to next | Source |
|-----------|--------|-----------------|--------|
| **M0 — Core sealed** ← *we are here* | Pure rules engine + tests + sim-smoke + this stack-root scaffold | PRP 3 M1 issue opens | PRP 2 (#139) + #143 |
| **M1 — Hot-seat MVP** | `apps/ui/` scaffolded; 3-player hot-seat playable on one device | 4 humans complete a full round | PRP 3 §A M1–M5 |
| **M2 — Bot ladder + replay** | Levels 0/1/2 bots + `(seed, actions[])` replay viewer | Level 1 beats Level 0 ≥60%/100 matches | PRP 3 §E + §A M9–M13 |
| **M3 — Online multiplayer** | Rust + Axum server; lobby; reconnect + replay; anti-cheat | 2 remote + 1 bot finish with mid-match reconnect | PRP 3 §C + §A M14–M17 |
| **M4 — Polish & scale** | Ranked matchmaking; tournaments; Capacitor native shell; Prometheus | First external playtester onboarded | `cardshed-v0.1.0` tag cut |

---

## Repository layout

```
@lab/ll-CARDSHED/
├── .w7-meta                  W7 contract metadata
├── compose.yml               stub (alpine sleep) — replaced at PRP 3 M1
├── .env.example              env schema (placeholders)
├── .gitignore                runtime + build outputs
│
├── README.md                 you are here
├── CLAUDE.md                 Claude Code project rules
├── AGENTS.md                 agent guide
├── BLUEPRINT.md              index → PRPs/cardshed-{01,02,03}-*.md
│
├── .claude/
│   └── rules/
│       ├── ui-design-pipeline.md    MANDATORY Stitch + agent-browser + Playwright (PRP 3 M1+)
│       └── core-determinism.md      apps/core/ purity guarantees from PRP 2
│
├── .stitch/
│   └── DESIGN.md             generated design system (placeholder)
│
├── apps/
│   └── core/                 @cardshed/core — pure-logic rules engine (PRP 2)
│       ├── package.json
│       ├── src/core/{types,rules,prng,index}.ts
│       ├── src/core/__tests__/*.test.ts
│       └── scripts/sim-smoke.ts
│   └── ui/                   PRP 3 M1 (does not exist yet)
│   └── server/               PRP 3 M3+ (does not exist yet)
│
├── docs/
│   ├── SCREENS/              Stitch-generated mockups (one per screen)
│   └── DECISIONS/            ADRs as they accumulate
│
├── data/                     persistent volumes (gitignored)
└── dogfood-output/           agent-browser + playwright artifacts (gitignored)
```

---

## Next moves

1. **Land this stack-root bootstrap** (#143) — current PR.
2. **Open the PRP 3 M1 umbrella issue** with sub-issues for: `apps/ui/` scaffold, Stitch design-system run, hot-seat shell, attack/defend interactions, dogfood baseline.
3. **Run `Skill: stitch-design`** with PRP 3 §B screen inventory + the locked engine API. Save outputs to `docs/SCREENS/`.
4. **Wire `@cardshed/core` into `apps/ui/`** as a workspace dep — the UI must not re-implement any rule.
5. **Run agent-browser** against the running stack to capture the first hot-seat baseline.

---

## License

Inherits W7-Base MIT.
