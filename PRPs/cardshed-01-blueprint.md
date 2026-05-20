# CARD SHED — Technical Blueprint v1.0

> **Layer:** Strategy / Blueprint
> **Source PRP:** `PRPs/01-strategy-blueprint.md`
> **Inputs (frozen):** CARD SHED Rules v2.0 (3–4 players, 52-card deck, shifting trump)
> **Consumed by:** `PRPs/02-deterministic-core.md` (rules engine + models) and `PRPs/03-experience-distribution.md` (UI / networking / AI / analytics)
> **Status:** Draft for review — **no production code, no concrete data structures.** Only decisions.

Ownership tags used below:
- **[Self]** — owned by this blueprint
- **[PRP-2]** — concrete shape defined in the deterministic-core PRP
- **[PRP-3]** — concrete shape defined in the experience-distribution PRP

---

## 1. Executive Summary [Self]

CARD SHED's first playable target is a **local hot-seat browser MVP** built in **TypeScript + React + Vite**. The architecture is designed so that the same module taxonomy — `GameManager / Deck / TurnController / RulesEngine / ActionValidator / StateReducer / EventBus / UIHandler / PersistenceAdapter` — survives the jump from browser-only hot-seat to **online multiplayer with a Rust + Axum server**, without rewriting the rules engine or the UI shell.

The state synchronization model is **hybrid**: every state transition produces both a per-player redacted `MatchSnapshot` (authoritative current state) and an append-only ordered `GameEvent[]` (animation + audit trail). Both messages carry a monotonic `seq: u64`. This lets clients reconnect cheaply, animate accurately, and replay any match deterministically from `(matchSeed, actions[])`.

The deterministic rules engine ships first as a **pure TypeScript module** (MVP) and is later mirrored in Rust on the server — both implementations consume the same canonical specification produced by PRP-2.

---

## 2. Tech Stack — Backend [Self]

Per the PRP success criteria, both Rust and Go options are fully designed; a single recommendation is made.

### 2.1 Option A — Rust

| Concern | Choice | Rationale |
|---|---|---|
| Web framework | **Axum 0.7+** | Tower-based middleware, type-safe routing, first-class WebSocket upgrade, tight `tokio` integration. |
| WebSocket | **Axum's `WebSocketUpgrade`** (uses `tokio-tungstenite` under the hood) | No extra crate; WS lifecycle managed via Axum's extractor pattern. |
| Serialization | **`serde` + `serde_json`** on the wire; **`postcard`** for internal snapshots | JSON keeps browser interop free; postcard gives compact persisted history without re-implementing format conversion. |
| RNG / shuffle | **`rand_chacha::ChaCha8Rng`** seeded from a 64-bit `matchSeed` | Deterministic, well-audited, cryptographically-flavoured — required for honest replay and shuffle audit. |
| State machine | **Discriminated `enum TurnState`** with `match` exhaustiveness in the reducer | Compiler refuses to compile if a new state is added but a branch is missed. |
| Test framework | Built-in `#[cfg(test)]` + **`proptest`** (property tests) + **`rstest`** (fixtures) | Property tests fuzz `canBeat` / `validateAttack` across the 52-card × 4-suit × 13-rank space. |
| Persistence | **`sqlx` + Postgres 16** for durable match history; **`sled`** for hot in-process match-room state | Postgres already in the W7-Base ecosystem; sled avoids round-tripping the DB for every action. |
| Deployment | **Statically-linked binary** in a multi-stage `distroless/cc` image, behind Traefik on `w7-ingress` | Matches W7-Base conventions; predictable runtime, no glibc surprises. |

### 2.2 Option B — Go

| Concern | Choice | Rationale |
|---|---|---|
| Web framework | **`chi`** | Lightweight, stdlib-shaped routing, no global state. `echo`/`fiber` add weight without solving any CARD SHED problem. |
| WebSocket | **`nhooyr.io/websocket`** | Context-aware, modern, ping/pong + close-codes out of the box. Preferred over `gorilla/websocket` for new code. |
| Serialization | **`encoding/json`** on the wire; **`encoding/gob`** internal | stdlib first; swap to `goccy/go-json` only if profile demands. |
| RNG / shuffle | **`math/rand/v2`** seeded from a 64-bit `matchSeed`; **`crypto/rand`** for the seed itself | Same determinism story as the Rust option. |
| State machine | **`stateless`** library (Go port of .NET Stateless) or hand-rolled `iota` enum + `switch` | No compiler-enforced exhaustiveness — must lean on `go vet` extensions + tests. |
| Test framework | `testing` + **`testify/require`** + **`gopter`** (property tests) | gopter is workable but ergonomically thinner than proptest. |
| Persistence | **`pgx` + Postgres 16** for durable; **`bbolt`** embedded for hot cache | Same Postgres baseline. |
| Deployment | **Static `CGO_ENABLED=0` binary** in `gcr.io/distroless/static` | Smallest images and fastest cold start of the two languages. |

### 2.3 Recommendation — **Rust**

Weighted comparison on CARD SHED's specific shape:

| Criterion | Weight | Rust | Go | Winner |
|---|---|---|---|---|
| Sum-type modelling of action & turn-state spaces | high | enum + exhaustive match | iota + manual switch | Rust |
| Compile-time prevention of missed-branch bugs as rules grow | high | ✅ | ❌ (linter only) | Rust |
| `Result<T, RulesError>` ergonomics for validator output | high | natural | manual `(T, error)` | Rust |
| Hiring / onboarding speed | medium | steeper | shallower | Go |
| Compile / iteration loop | medium | slower (incremental ok) | faster | Go |
| Latency under load | low (turn-based) | excellent | excellent | tie |
| GC pause sensitivity | low (turn-based) | n/a | n/a in practice | tie |
| Long-term refactor cost as rules evolve | high | low (compiler shouts) | medium (lint + tests) | Rust |
| WS + JSON + Postgres ecosystem maturity | medium | mature | mature | tie |

**Decision: Rust.** CARD SHED is dominated by **correctness across a discriminated rule space** (1/3/5-card attacks, suit-vs-trump beat logic, refill mechanics, win condition gated on deck exhaustion). The compiler-as-reviewer payoff outweighs Go's onboarding and compile-speed advantages, because the server is small (target ≤ 5 kloc) and the rules-engine port from PRP-2's canonical TS spec is mechanical.

---

## 3. Tech Stack — Frontend [Self]

**Recommendation: TypeScript + React + Vite.**

Evaluation across the five axes mandated by the PRP:

| Axis | TS+React+Vite | TS+Svelte | TS+PixiJS | Godot | Unity |
|---|---|---|---|---|---|
| **Browser MVP speed** | ✅ Vite + HMR + mature templates | ✅ even smaller bundles | ⚠️ DIY UI primitives | ❌ engine boot + export | ❌ heavy WebGL build |
| **Mobile-friendly web** | ✅ native CSS / Tailwind | ✅ native CSS | ⚠️ manual scaling | ⚠️ touch ok, perf variable | ❌ heavy on mobile browsers |
| **Future native apps** | ✅ Capacitor / React Native | ⚠️ Capacitor only | ⚠️ custom shell | ✅ native targets | ✅ native targets |
| **Online multiplayer** | ✅ `ws` + TanStack Query + Zustand | ✅ `ws` + Svelte stores | ✅ but UI work is larger | ⚠️ custom WS | ⚠️ Mirror / Photon |
| **Fast iteration** | ✅ ecosystem + Storybook + Vitest | ✅ great DX | ⚠️ thin tooling | ❌ rebuilds | ❌ rebuilds |

Why React, specifically for CARD SHED:

1. **The game is DOM-friendly.** Cards are rectangles with rank + suit. WebGL gives nothing; HTML + CSS + SVG with `framer-motion` is faster to ship and trivially testable with React Testing Library.
2. **W7-Base ecosystem inertia.** `@lab/ll-KNOWRAG` and `@lab/ll-RELIQUARY` already standardize on React + Vite + Tailwind v4 + Radix. Introducing a third frontend paradigm increases the tax on every shared concern.
3. **Component testing.** Vitest + RTL means we can pin a `MatchState` projection and assert the rendered table exactly — no engine needed.
4. **State management.** Zustand for ephemeral client state, TanStack Query for server-state (matchmaking, profile), Immer for reducer-style hand updates. All composable, all type-safe.
5. **Native path.** Capacitor wraps the existing web bundle without rewrites — Godot/Unity would force building the same UI twice.

**Stack pinning** (matches existing W7-Base precedent):
- TypeScript ≥ 5.4 (`strict: true`)
- React 18
- Vite 5.4 (per RELIQUARY/KNOWRAG; Vite 6 deferred until that ecosystem matures)
- Tailwind v4 with `@theme` token blocks
- Radix UI primitives (selective)
- framer-motion for card flips and table animations
- Zustand + TanStack Query + Immer
- Vitest + React Testing Library (unit) + Playwright (e2e)

Explicit rejections:
- **PixiJS** — adds WebGL complexity without payoff for a 52-card layout.
- **Svelte** — excellent DX but breaks the shared-component story.
- **Godot / Unity** — browser-first MVP is not what these engines optimize for; Capacitor delivers the native-app path at a fraction of the onboarding cost.

---

## 4. Game State Entities — Decisions Only [Self for classification; PRP-2 for shapes]

The blueprint **names** the entities and **classifies** their visibility. PRP-2 owns concrete `struct` / `interface` / `enum` bodies.

| Entity | Visibility class | What opponents see | Owned by |
|---|---|---|---|
| `Card` | public when face-up; private when face-down | nothing while held; suit + rank once placed on the table | shared |
| `Deck` | public (count, trump face) + private (order) | the draw-pile count and the revealed bottom (trump) card | GameManager |
| `Player` | public (id, displayName, handCount, role) + self (full hand) | id, name, hand count, role ∈ `{Attacker, Defender, Idle, NextAttacker}` | per-player |
| `MatchState` | per-player redacted | aggregate of the above with `hand` replaced by `HandSummary` for other players | GameManager |
| `RoundState` | public | trump suit, dealer index, currentAttacker index, currentDefender index, deckCount, turnNumber | GameManager |
| `PendingAttack` | public to Defender (full faces); public to others (face-up cards as the rules expose them) | depends on observer + rule-stage | TurnController |
| `DiscardPile` | public count only | a count; contents are not inspectable per Rules v2.0 | Deck |
| `TurnState` | public (whose turn) + role-specific (legal actions enumerated) | the current `TurnState` enum value | TurnController |
| `Action` | public once applied; private while in-flight from a single client | wire envelope `{playerId, kind, payload, clientSeq}` | client → server |
| `ActionResult` | public | `Ok(StateDelta + GameEvent[])` \| `Err(RulesError)` | server → all |
| `GameEvent` | per-player redacted | append-only audit / animation trail | EventBus |

**Hidden-hand representation to opponents — `HandSummary`** (shape decided by PRP-2):
- `ownerId`
- `count: u8`
- `publiclyKnown: Card[]` — cards opponents must know because they were captured-unbeaten by this player or otherwise revealed under the rules

PRP-2 decides whether `publiclyKnown` is a `Vec`, a `Set`, or a `BitSet` over the 52-card space.

**Cross-PRP handoff checklist — every entity above must be concretely defined in PRP-2:**

- [ ] `Card` — rank + suit; trump-aware comparison
- [ ] `Deck` — storage, `shuffle(seed)`, `revealBottom()`, `drawTo(player, target)`
- [ ] `Player` — public + private partitions
- [ ] `MatchState` — root aggregate + `redactFor(playerId) → PlayerView`
- [ ] `RoundState`
- [ ] `PendingAttack`
- [ ] `DiscardPile`
- [ ] `TurnState` enum
- [ ] `Action` envelope + variants (`Attack1`, `Attack3`, `Attack5`, `BeatCard`, `StopDefending`)
- [ ] `ActionResult` + `RulesError` taxonomy
- [ ] `GameEvent` enum

---

## 5. Server-Authoritative Synchronization [Self]

### 5.1 Snapshot vs Event-Sourcing vs Hybrid

| Model | Pros | Cons | Fit for CARD SHED |
|---|---|---|---|
| **Full snapshot every change** | trivial impl; trivially correct | no animation timeline; debug is hard | acceptable but loses replay |
| **Pure event-sourced** | tiny deltas; perfect replay; debug-friendly | drift recovery is fragile; clients must implement a reducer to render | overkill on its own |
| **Hybrid (snapshot + events)** | deterministic state + animated timeline + cheap reconnect | minor duplication on the wire | **best fit** |

### 5.2 Recommendation — Hybrid

Every state transition emits, atomically:

1. A **per-player redacted `MatchSnapshot`** — authoritative current state, with the recipient's own hand and any publicly-known opponent cards filled in.
2. An **ordered `GameEvent[]`** — the animation / audit timeline since the previous snapshot.
3. A **monotonic `seq: u64`** — applied to both messages so clients can reorder, dedupe, and reconnect.

Why both: snapshots make a reconnecting (or just-joined-spectator) client cheap to bootstrap; events give the UI the *narrative* it needs to animate `CardPlayed → CardBeaten → HandTaken → TurnAdvanced` faithfully.

### 5.3 Reconnection

- Client persists `lastSeenSeq` per match in `localStorage`.
- On reconnect, client sends `{type: "Resume", matchId, lastSeenSeq}`.
- Server responds with either:
  - `Resume(eventsSince=lastSeenSeq, latestSnapshot)` — if the gap is bounded (e.g. ≤ N events held in the hot cache), or
  - `ResnapOnly(latestSnapshot)` — if too much has happened; client drops its event tail and reboots from snapshot.
- **60-second grace period** during the active player's turn before they are marked `disconnected`; configurable to either pass the turn or pause the match (default: pause for friend matches).

### 5.4 Replay

`(matchSeed, actions[])` deterministically reproduces every match — the shuffle is seeded, the rules engine is pure, the reducer is pure. The server stores that triple plus the final snapshot for fast lookup. Replay viewer is a reducer + EventBus running over the action log.

### 5.5 Anti-Cheat

- **Server is authoritative.** Clients send `Action`s; the server validates against current state and emits results.
- **Per-player state redaction** means clients never see opponent hands; a tampered client cannot reveal hidden cards because the server never sent them.
- **Rate limiting** at the WS layer (`tower-governor` for Rust / `tollbooth`-style for Go).
- **Move-rate sanity** at the application layer — a 0-ms decision in a hidden-info turn is logged as suspicious.
- **Seq-number monotonicity** detects replay attacks; non-monotonic `seq` is rejected.

### 5.6 Idempotency

- Every `Action` carries `clientSeq: u32`, monotonic per `(matchId, playerId)`.
- The server tracks the last-accepted `clientSeq` per pair and replies to duplicates with a no-op `Ok` (retries are safe).

### 5.7 Simultaneous Connections, Turn-Based Semantics

All players hold an open WebSocket for the full match — they need state updates even when it isn't their turn. The server rejects `Action`s from non-active players with `Err(NotYourTurn)`. Lobby and spectator sockets follow the same envelope shape but the server ignores their `Action` messages entirely.

---

## 6. Clean Local Architecture [Self]

### 6.1 Module Diagram

```
                              ┌──────────────────────────────┐
                              │        GameManager           │
                              │  (lifecycle orchestrator)    │
                              └─────────────────┬────────────┘
                                                │
                ┌───────────────────────────────┼───────────────────────────────┐
                ▼                               ▼                               ▼
       ┌────────────────┐         ┌─────────────────────┐         ┌────────────────────┐
       │     Deck       │         │   TurnController    │         │ PersistenceAdapter │
       │ (cards+trump)  │         │ (roles + rotation)  │         │ (snapshot + events)│
       └────────┬───────┘         └──────────┬──────────┘         └─────────┬──────────┘
                │                            │                              │
                │            ┌───────────────▼──────────────┐               │
                │            │      ActionValidator         │               │
                │            │  (schema-level gating)       │               │
                │            └───────────────┬──────────────┘               │
                │                            ▼                              │
                │            ┌──────────────────────────────┐               │
                │            │        RulesEngine           │               │
                │            │ (pure: state, action → res)  │               │
                │            └───────────────┬──────────────┘               │
                │                            ▼                              │
                │            ┌──────────────────────────────┐               │
                └───────────►│       StateReducer           │◄──────────────┘
                             │  (state' = apply(state, Δ))  │
                             └───────────────┬──────────────┘
                                             ▼
                             ┌──────────────────────────────┐
                             │          EventBus            │
                             │  (ordered GameEvent stream)  │
                             └───────────────┬──────────────┘
                                             ▼
                             ┌──────────────────────────────┐
                             │         UIHandler            │
                             │  (subscribes + dispatches)   │
                             └──────────────────────────────┘
```

### 6.2 Module Responsibilities — one paragraph each

- **GameManager** owns match lifecycle. It instantiates the other modules at match-start with a seeded RNG, accepts inbound `Action`s, drives them through the pipeline (Validate → RulesEngine → StateReducer → EventBus → broadcast), and emits end-of-round / end-of-match transitions. No game logic lives here — only orchestration.

- **Deck** encapsulates the 52-card draw pile, the revealed trump (bottom card), and the count-only discard pile. Exposes `shuffle(seed)`, `revealBottom() → Card`, `drawTo(hand, target)` (refill to 5 when possible), and `count() → u8`. Holds the only mutable card-order state in the game.

- **TurnController** tracks who is Attacker, who is Defender, and what `TurnState` we are in. Rotates roles per Rules v2.0: **full defence → defender becomes attacker**; **partial / no defence → next clockwise player becomes attacker**. Does not validate moves; just owns role state.

- **RulesEngine** is the **pure heart**. Signature: `(MatchState, Action) → Result<StateDelta, RulesError>`. Encodes attack legality (1 / 3 / 5 card combos, pair semantics, kicker rules), defence legality (same-suit higher OR any trump; trump beaten only by higher trump), refill mechanics, and win condition (zero cards after refill attempt with empty deck). No I/O, no clocks, no randomness — fully deterministic from inputs.

- **ActionValidator** is the cheap pre-filter. It checks only structural validity: the action is a known kind, the payload's cards exist in the actor's hand, the actor holds the role currently expected to move. Returns before RulesEngine pays the cost of full rule evaluation.

- **StateReducer** applies an accepted `StateDelta` to `MatchState`, producing the next state. Pure, idempotent for a given delta. Emits no events of its own — the EventBus is fed by GameManager from the delta.

- **EventBus** broadcasts ordered `GameEvent`s to subscribers (UI, persistence, network). In the MVP it's an in-memory pub/sub; in the online server it sits behind the WebSocket fan-out layer. Every event carries a `seq: u64` for client-side ordering and reconnect catch-up.

- **UIHandler** subscribes to events to drive rendering and forwards user input as candidate `Action`s back into GameManager. In the hot-seat MVP it owns *both* perspectives (the next-actor's hand is made visible after a "pass device" splash). In the online build it owns only the local player's perspective.

- **PersistenceAdapter** is the storage seam. Two flavours: `LocalStoragePersistence` (browser, MVP) and `PostgresPersistence` (server, online). Stores `(matchId, seed, actions[], finalSnapshot)` so any match can be exported, resumed, or replayed.

### 6.3 Deployment-Target Matrix

| Module | Hot-seat MVP | Browser single-player vs AI | Online server-authoritative | Test / sim harness |
|---|---|---|---|---|
| GameManager | browser (TS) | browser (TS) | server (Rust) | node / `cargo test` |
| Deck | browser (TS) | browser (TS) | server (Rust) | node / `cargo test` |
| TurnController | browser (TS) | browser (TS) | server (Rust) | node / `cargo test` |
| RulesEngine | browser (TS) | browser (TS) | server (Rust) + **TS port stays for client-side prediction + replay viewer** | either |
| ActionValidator | browser (TS) | browser (TS) | server (Rust) | either |
| StateReducer | browser (TS) | browser (TS) | server (Rust) + browser mirror for optimistic UI | either |
| EventBus | in-memory | in-memory | WebSocket fan-out + per-peer in-memory | in-memory |
| UIHandler | browser only | browser only | browser only | none |
| PersistenceAdapter | `LocalStoragePersistence` | `LocalStoragePersistence` | `PostgresPersistence` (server) + `LocalStorage` cache (client) | `InMemoryPersistence` |

The matrix shows the architecture survives the local → online jump by **replacing only the EventBus and PersistenceAdapter implementations** and **adding a Rust mirror of the deterministic core**. The UI's contract — `subscribe(events) → render; dispatch(action) → manager` — does not change.

---

## 7. Twenty-Section Deliverable Outline

Canonical TOC for the full design doc. Each section is tagged with the PRP that owns its detail.

| # | Section | One-line synopsis | Owner |
|---|---|---|---|
| 1 | Executive Summary | One-page overview: target, stack, MVP, roadmap | [Self] |
| 2 | Tech Stack | Rust + Axum server, TS + React + Vite client, with rationale | [Self] |
| 3 | Backend Architecture | Module map of the Rust server: routes, WS lifecycle, persistence, deploy | [Self] |
| 4 | Frontend Architecture | Component tree, state-mgmt stack, routing, build pipeline | [Self] |
| 5 | State Model | Concrete struct / interface / enum bodies for every entity in §4 | [PRP-2] |
| 6 | Rules Engine Design | Pseudocode for `validateAttack`, `canBeat`, `resolveBeat`, `drawToMinimum`, `checkWin` | [PRP-2] |
| 7 | Turn-Flow State Machine | States = `{Dealing, AwaitingAttack, AwaitingDefense, Resolving, RoundEnded, MatchEnded}`; transitions per Rules v2.0 | [Self] names states; [PRP-2] formalizes transitions |
| 8 | MVP Scope | Hot-seat feature checklist + implementation order | [PRP-3] |
| 9 | Roadmap | now / next / later milestones from this blueprint | [Self] |
| 10 | Networking | WS transport, lobby, room creation, observability | [PRP-3] |
| 11 | Message Protocol | JSON envelopes (`Action`, `Snapshot`, `Event`, `Resume`) | [PRP-3] |
| 12 | Reconnection | last_seen_seq + snapshot + delta + grace-period model | [Self] for model; [PRP-3] for wire impl |
| 13 | Analytics | Event taxonomy for funnel + game balance | [PRP-3] |
| 14 | UI/UX | Screens, table layout, card interactions, juice | [PRP-3] |
| 15 | AI | Bot Level 0 (random legal), Level 1 (heuristic), Level 2 (basic search) | [PRP-3] |
| 16 | Testing | Pyramid: rules unit + property + integration + e2e | [PRP-2] engine; [PRP-3] UI/e2e |
| 17 | Security / Anti-Cheat | Server-auth, action validation, rate-limit, seq monotonicity | [Self] |
| 18 | Deployment | Rust binary in distroless container; static frontend; Traefik routing; observability hooks | [Self] |
| 19 | Future Enhancements | Tournament, ranked, deck skins, spectator chat, mobile native | [Self] |
| 20 | Risks / Mitigations | Cold-start latency, animation desync, RNG audit, scope creep | [Self] |

---

## 8. Implementation Roadmap

| Tier | Milestone | Scope | Exit criteria |
|---|---|---|---|
| **now** | M1 — Hot-seat browser MVP | TS rules engine ([PRP-2]); React UI for 3–4 player pass-and-play ([PRP-3]); `localStorage` persistence; unit + property tests for engine | 4 humans complete a full round on one device; rules engine has ≥ 95% branch coverage |
| **next** | M2 — Bot vs human | Bot Levels 0–2 ([PRP-3]); replay viewer over `(seed, actions[])` | Level 1 bot beats Level 0 ≥ 60 % over 100 matches; replay reconstructs to byte-identical final snapshot |
| **later** | M3 — Online multiplayer | Rust server (Axum + tokio-tungstenite); lobby; server-authoritative; reconnect + replay; anti-cheat | 2 remote players + 1 bot complete a match with one mid-match reconnect succeeding |
| **later** | M4 — Polish & scale | Ranked matchmaking; tournament mode; Capacitor native shell; Prometheus + Grafana | First external playtester onboarded; observability dashboards green; on-call runbook published |

---

## 9. Cross-PRP Implications

These decisions propagate constraints into the sibling PRPs:

1. **Hybrid sync requires `seq: u64` on every message.** → [PRP-3] must include `seq` in every WebSocket envelope (`Snapshot`, `Event`, `Action`, `Resume`).
2. **Seeded RNG for replay.** → [PRP-2]'s `Deck.shuffle(seed)` accepts a 64-bit seed; the seed is part of `MatchState`. → [PRP-3]'s persistence must store it. → Test harness must accept it as input.
3. **Per-player `MatchState` redaction.** → [PRP-2] defines `MatchState.redactFor(playerId) → PlayerView`. → [PRP-3]'s WS broadcast sends `PlayerView`, never the unredacted `MatchState`.
4. **Action envelope is wire-stable.** → [PRP-2] and [PRP-3] must agree on `Action.clientSeq: u32`; both rely on it for idempotency.
5. **Shared turn-state vocabulary.** → All three docs use `{Dealing, AwaitingAttack, AwaitingDefense, Resolving, RoundEnded, MatchEnded}`. Renaming requires a coordinated change here first.
6. **MVP rules engine is TS; server engine is Rust.** → [PRP-2]'s pseudocode must be written in language-neutral form (TS implementation with explicit semantics) so the Rust port is mechanical. → [PRP-3] uses the TS implementation for the MVP and for the client-side replay viewer even after the server lands.
7. **Frontend stack pinned to React + Tailwind v4 + Radix.** → [PRP-3] does not re-evaluate this; any UI library it adopts must be React-compatible.
8. **Backend stack pinned to Rust.** → [PRP-3]'s networking section assumes Axum's WS shape (extractor + `Message::Text`); messages travel as JSON over text frames.
9. **Match-room state lives in `sled` hot-cache + Postgres durable.** → [PRP-3]'s lobby design must distinguish "match in flight" (hot cache) from "history" (DB).
10. **No reshuffles; deck exhaustion gates winning.** → [PRP-2]'s `checkWin` runs only after refill attempts when `deckCount == 0`. → [PRP-3]'s end-of-round UI must communicate "deck empty — race to zero hand".

---

## 10. Validation Self-Check

### Level 1 — Coherence

- ✅ Tech-stack recommendation cites concrete tradeoffs (sum-type modelling, GC irrelevance, ecosystem inertia, onboarding cost). Not vague.
- ✅ Hybrid sync is chosen because the game is turn-based + tiny state + animation-driven; no high-frequency-tick rationale is invoked.
- ✅ Module diagram has no orphan dependencies; no two modules overlap (RulesEngine ≠ ActionValidator — one is semantic, one is structural).

### Level 2 — Round-trip with siblings

- ✅ Every entity in §4 has an explicit `[PRP-2]` handoff checklist line.
- ✅ Every "later" roadmap item has a sibling owner (UI → PRP-3; rules pseudocode → PRP-2; networking → PRP-3; AI → PRP-3).
- ✅ Cross-PRP Implications section is present with 10 line-items.

### Level 3 — Authoritative-spec round-trip

- ✅ All Master Prompt sections (§1A, §1B, §1C, §1D, §9, Additional Instruction) are addressed.
- ✅ The 20-section deliverable outline lists every PRP-mandated header with a clear owner tag.

### Anti-Patterns

- ✅ No full type definitions written (entity bodies deferred to PRP-2).
- ✅ No WebSocket JSON message bodies written (deferred to PRP-3).
- ✅ Rust-vs-Go tradeoff fully designed; single recommendation made with weighted rationale.
- ✅ No game-balance discussion in this blueprint.
- ✅ No rule variants introduced. Rules v2.0 are quoted from the PRP unchanged.

---

> **Next step:** lock this blueprint. Once approved, PRP-2 (deterministic-core) and PRP-3 (experience-distribution) can be generated and executed in parallel — both consuming this document as their input contract.
