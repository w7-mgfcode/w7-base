# ll-RELIQUARY

> Browser-based collectable card / artifact game.
> A `@lab` sandbox inside W7-Base. Currently in **BRAINSTORM → PLAN → ARCHITECTURE** phase.

---

## Status

📋 **Boilerplate.** The stack boots, the planning docs exist, the UI pipeline is locked. No game logic yet.

| Layer | State |
|-------|-------|
| Stack contract (`.w7-meta`, `compose.yml`, env) | ✅ done |
| Planning docs (`BRAINSTORM`, `STORYBOARD`, `ARCHITECTURE`) | ✅ skeletons ready to fill |
| Local rules (`.claude/rules/`) | ✅ mandatory pipeline encoded |
| Container stubs (api `/health`, ui hello-shelf) | ✅ bootable |
| Stitch design system (`.stitch/DESIGN.md`) | 📋 placeholder — generate via `stitch-design` skill |
| Screen mockups (`docs/SCREENS/`) | 📋 todo (Journey A first) |
| Game logic | ⏭️ out of scope this iteration |

---

## What it is

Reliquary is a single-host, browser-rendered card-collection game. Players curate a **shelf of artifacts** — each card has identity, lineage, and (sometimes) finite scarcity. The retention pillar (`ragaszkodás`) is built around the shelf itself: it stays yours, it stays visible, and every new relic strengthens the meaning of the ones already there.

The full vision lives in `BRAINSTORM.md`. The first-session and first-month narrative is in `STORYBOARD.md`. The system shape is in `ARCHITECTURE.md`.

---

## Stack

| Service | Tech | Default host port |
|---------|------|-------------------|
| `reliquary-ui` | React 18 + Vite 5 + Tailwind v4 + Radix + framer-motion + PixiJS | `4242` |
| `reliquary-api` | FastAPI (Python 3.12) | `8282` |
| `reliquary-db` | Postgres 16 | `5454` |
| `reliquary-cache` | Redis 7 | `6464` |

All pinned (see `.claude/rules/docker-infra.md`). No `:latest`.

---

## Quick start

```bash
# From the W7 CLI (preferred)
cd ~/w7-base
cp @lab/ll-RELIQUARY/.env.example @lab/ll-RELIQUARY/.env
# (edit .env — fill POSTGRES_PASSWORD, REDIS_PASSWORD, API_SESSION_SECRET)
w7 up @lab/ll-RELIQUARY
open http://localhost:4242
```

Direct Docker:

```bash
cd @lab/ll-RELIQUARY
docker compose --env-file .env up --build -d
```

Tear down (keeps `data/`):

```bash
w7 down @lab/ll-RELIQUARY
```

---

## The mandatory UI pipeline

This stack has an **enforced** design workflow — see `.claude/rules/ui-design-pipeline.md`.

```
  IDEA (storyboard wireframe)
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

| Phase | Output | Trigger to next |
|-------|--------|-----------------|
| **0 — Boilerplate** ← *we are here* | Stack boots, docs skeletoned, pipeline locked | `BRAINSTORM.md` §3 answered |
| **1 — Design heavy** | `.stitch/DESIGN.md` generated; S01–S09 mockups under `docs/SCREENS/`; user-flow validated in agent-browser | First three screens approved |
| **2 — Vertical slice** | Journey A (cold-landing → first-pull) live end-to-end with one real artifact | Day-2 retention beat designed |
| **3 — Curator loop** | Journey B + Journey C; lineage UI; share-OG image | First external playtester |
| **4 — Hardening** | Playwright e2e suite, observability, backup story | Tag `reliquary-v0.1.0` |

---

## Repository layout

```
@lab/ll-RELIQUARY/
├── .w7-meta                  W7 contract metadata
├── compose.yml               4-service topology
├── .env.example              env schema (placeholders)
├── .gitignore                runtime + build outputs
│
├── README.md                 you are here
├── CLAUDE.md                 Claude Code project rules
├── AGENTS.md                 agent guide
├── BRAINSTORM.md             vision & open questions
├── STORYBOARD.md             user journeys + screen inventory
├── ARCHITECTURE.md           system sketch
│
├── .claude/
│   └── rules/
│       ├── ui-design-pipeline.md    MANDATORY Stitch + agent-browser + Playwright
│       └── docker-infra.md          container infra rules
│
├── .stitch/
│   └── DESIGN.md             generated design system (placeholder)
│
├── apps/
│   ├── api/                  FastAPI backend
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── src/server/main.py
│   └── ui/                   React + Vite + Tailwind v4
│       ├── Dockerfile
│       ├── package.json
│       ├── vite.config.ts
│       ├── tsconfig.json
│       ├── index.html
│       ├── nginx.conf
│       └── src/{App.tsx,main.tsx,index.css}
│
├── docs/
│   ├── SCREENS/              Stitch-generated mockups (one per S0x)
│   └── DECISIONS/            ADRs as they accumulate
│
├── data/                     persistent volumes (gitignored)
└── dogfood-output/           agent-browser + playwright artifacts (gitignored)
```

---

## Next moves

1. **Open Section 3 in `BRAINSTORM.md`** and lock the four open-question blocks (game loop / card economics / retention / theme).
2. **Fill `STORYBOARD.md` §5** wireframes for S01, S02, S03 (Journey A).
3. **Run `Skill: stitch-design`** with the wireframes + premise + aesthetic decision. Save outputs to `docs/SCREENS/`.
4. **Run agent-browser** against the running UI to capture the boilerplate baseline screenshot.
5. **Re-evaluate `ARCHITECTURE.md`** §3 (data shape) once card mechanics are clearer.

---

## License

Inherits W7-Base MIT.
