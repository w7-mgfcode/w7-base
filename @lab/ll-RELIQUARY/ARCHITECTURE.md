# ARCHITECTURE — Reliquary

> Status: **SKETCH** — boilerplate phase. Refine after `BRAINSTORM.md` section 3 is locked and `STORYBOARD.md` has its first three Stitch outputs.

---

## 1. Topology (boilerplate)

```
                ┌─────────────────────┐
                │   Browser (player)  │
                └──────────┬──────────┘
                           │  HTTPS (via @ops/traefik later)
                           ▼
        ┌──────────────────────────────────┐
        │  reliquary-ui  (nginx + Vite SPA)│ :4242 → 8080
        │  React + Tailwind v4 + Radix +   │
        │  framer-motion + PixiJS          │
        └──────────────────┬───────────────┘
                           │  REST + (later) WebSocket
                           ▼
        ┌──────────────────────────────────┐
        │  reliquary-api  (FastAPI)        │ :8282
        │  - REST endpoints                │
        │  - Session signing               │
        │  - Game-loop orchestration       │
        └────┬─────────────────────┬───────┘
             │                     │
             ▼                     ▼
   ┌──────────────────┐   ┌──────────────────┐
   │ reliquary-db     │   │ reliquary-cache  │
   │ Postgres 16      │   │ Redis 7          │
   │ • users          │   │ • sessions       │
   │ • artifacts      │   │ • leaderboards   │
   │ • collections    │   │ • daily-relic    │
   │ • lineage edges  │   │ • rate limits    │
   └──────────────────┘   └──────────────────┘
```

All four containers ride on the `reliquary-net` bridge. Traefik integration is deferred to first deploy — boilerplate exposes host ports directly.

---

## 2. Service boundaries (proposed)

| Service | Owns | Does NOT own |
|---------|------|--------------|
| `reliquary-ui` | Rendering, animation, input, optimistic state | Source-of-truth game state, secrets |
| `reliquary-api` | Pulls, rewards, lineage rules, session auth | Asset CDN, analytics, payments |
| `reliquary-db` | Persistent game state, indexed lookups | Hot-path counters |
| `reliquary-cache` | Sessions, rate limits, leaderboards, pub/sub bus | Anything that must survive a flush |

---

## 3. Data shape (placeholder — finalise after Storyboard)

Draft only; refine when card mechanics solidify.

```sql
-- users — device-key first, email later
users (
  id uuid pk,
  device_key text unique not null,
  email text null unique,
  created_at timestamptz default now()
)

-- artifacts — the canonical card/relic catalog
artifacts (
  id text pk,                  -- stable slug ("ember-of-first-light")
  title text not null,
  rarity text not null,        -- 'common' | 'uncommon' | 'rare' | 'mythic'
  edition_size int null,       -- null = unlimited; e.g. 100 = finite run
  art_uri text not null,
  story_md text,
  released_at timestamptz default now()
)

-- collections — who owns what, with provenance
collections (
  id uuid pk,
  user_id uuid references users,
  artifact_id text references artifacts,
  acquired_at timestamptz default now(),
  source text not null,        -- 'first-pull' | 'daily-relic' | 'fusion' | …
  shelf_position int,          -- user-ordered
  notes text                   -- player annotation
)

-- lineage — artifact → artifact relations (story DAG)
artifact_lineage (
  parent_id text references artifacts,
  child_id  text references artifacts,
  relation text not null,      -- 'derives-from' | 'pairs-with' | 'opposes'
  primary key (parent_id, child_id, relation)
)
```

Indexes to add at first real load: `collections(user_id, shelf_position)`, `artifact_lineage(child_id)`.

---

## 4. API contract sketch (REST v0)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | liveness for w7 doctor |
| POST | `/session` | exchange device key → session cookie |
| GET | `/shelf` | current user's shelf (sorted) |
| POST | `/pull/first` | first-pull (idempotent per device) |
| POST | `/pull/daily` | daily-relic (rate-limited via Redis) |
| GET | `/artifact/:id` | single artifact detail + lineage |
| PATCH | `/shelf/:collection_id` | reorder / annotate |

WebSocket (`/ws`) is deferred. First real-time need will be daily-relic reveal countdown — handled by Redis pub/sub when it shows up.

---

## 5. Frontend architecture (Stitch-driven)

- **Routing**: file-based via Vite + react-router.
- **State**: TanStack Query for server cache; Zustand for ephemeral UI state (drag-in-progress, modal open).
- **Animation**: framer-motion for chrome (modals, page transitions); PixiJS *only* on canvas-heavy screens (pull reveal, lineage graph).
- **Design system**: `.stitch/DESIGN.md` is generated, not hand-authored. The `stitch-design` skill owns it. Tokens flow through Tailwind v4 `@theme`.
- **Component library**: Radix primitives + Tailwind-skinned wrappers under `src/components/ui/`.

**Hard rule**: see `.claude/rules/ui-design-pipeline.md`. No hand-rolled screens.

---

## 6. Deployment / GitOps (out of scope this iteration)

This stack lives in `@lab`, so when the repo wires up:
- Webhook push to `master` → `w7 up @lab/ll-RELIQUARY` (instant, HMAC-verified).
- No `@prod` migration planned for v0.
- Traefik labels added when we promote past localhost — `reliquary.w7.local`.

---

## 7. Observability (placeholder)

When the stack stabilises:
- `/metrics` endpoint on the API (Prometheus format).
- Container labels for the `w7-exporter` (`w7.zone=lab`, `w7.stack=ll-reliquary`).
- Redis is the natural place for game-event counters; periodic flush to a stats table.

---

## 8. Open architectural questions

| Q | Trigger to revisit |
|---|--------------------|
| WebSocket vs SSE vs polling for daily-relic? | First real-time UI need beyond a countdown |
| Single-player → async multi: same DB, new service, or sharded? | Decision when async PvP enters scope |
| Card-art storage: filesystem volume vs MinIO vs Gitea-LFS? | When the first 50 artifacts exist |
| Server-side rendering for share OG-images? | When Journey C ships |
| GDPR / data-export shape? | Before email login lands |

---

## 9. Decision log (architectural — append-only)

Distinct from `BRAINSTORM.md` §7 — that's product decisions, this is platform.

- `2026-05-20` — Postgres + Redis chosen over a single-DB design — Postgres for persistent identity/lineage, Redis for hot-path counters and pub/sub. Trade-off: two ops surfaces, but avoids retrofit cost later.
- `2026-05-20` — FastAPI (Python) chosen over Node/Fastify — consistency with `@lab/ll-KNOWRAG` so the operator-zone toolchain is one language.
- `2026-05-20` — React + Tailwind v4 + Radix chosen over Phaser/Godot — chrome stays React, only canvas-heavy screens reach for PixiJS. Avoids engine-creep risk.
