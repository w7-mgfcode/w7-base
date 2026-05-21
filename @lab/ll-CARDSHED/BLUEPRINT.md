# BLUEPRINT — ll-CARDSHED

> Index. The real blueprint is the PRP bundle under `PRPs/cardshed-*.md` at the repo root. This file exists so future contributors landing on the stack can navigate the PRPs without grep.

---

## The PRP bundle

CARD SHED is decomposed into three layered concerns (per `PRPs/INDEX.md`):

| # | Layer | Brief | Generated PRP | Status |
|---|-------|-------|---------------|--------|
| 1 | **Strategy & Blueprint** | `PRPs/01-strategy-blueprint.md` | `PRPs/cardshed-01-blueprint.md` | ✅ locked |
| 2 | **Deterministic Core** | `PRPs/02-deterministic-core.md` | `PRPs/cardshed-02-core-prp.md` | ✅ shipped (#139, #140) |
| 3 | **Experience & Distribution** | `PRPs/03-experience-distribution.md` | `PRPs/cardshed-03-experience-prp.md` | ⏭️ next — 17 milestones |

The bundle was designed for parallel PRP generation: each brief embeds the complete CARD SHED v2.0 rule set as its source of truth, and PRP 2's brief pre-commits the `Card`/`Suit`/`Rank` enum encoding so PRP 3 can be written against the same vocabulary without consuming PRP 2's output.

---

## What's locked (from PRP 1)

- **Backend**: Rust + Axum (over Go) — sum-type modelling + compile-time exhaustiveness for a rules-dominated codebase.
- **Frontend**: TypeScript + React + Vite + Tailwind v4 + Radix + framer-motion + Zustand + TanStack Query + Immer + Vitest + Playwright.
- **Sync model**: Hybrid snapshot + events with monotonic `seq: u64`. Reconnection via `lastSeenSeq`; replay from `(matchSeed, actions[])`.
- **Module taxonomy**: `GameManager / Deck / TurnController / RulesEngine / ActionValidator / StateReducer / EventBus / UIHandler / PersistenceAdapter`.
- **Persistence**: `sqlx + Postgres 16` durable; `sled` hot match-room cache.
- **Deployment**: Statically-linked Rust binary in `distroless/cc`; static React bundle in nginx; both behind Traefik on `w7-ingress`.

---

## What's shipped (PRP 2 — `apps/core/`)

- `types.ts` — full Shared Contract: `Card`, `Suit`, `Rank`, `MatchState`, `RoundState`, `PendingAttack`, `BeatenPair`, `Player`, `Action`, `GameEvent`, `PublicGameView`, `PrivatePlayerView`, `ValidationError`, `ActionResult`.
- `rules.ts` — every function on the Rules Engine API: `createDeck`, `shuffleDeck`, `dealInitialHands`, `determineTrumpFromBottomCard`, `startNewRound`, `validateAttack`, `submitAttack`, `canBeat`, `submitBeat`, `stopDefending`, `drawToMinimum`, `checkWin`, `advanceTurnAfter{Full,Partial}Defense`, `rotateDealer`, `getLegalActions`, `createPublicView`, `createPrivateView`, `pendingAttackCardCount`.
- `prng.ts` — `mulberry32(seed)` + seeded Fisher-Yates. The ONLY randomness source in `apps/core/`.
- `__tests__/*.test.ts` — 14 test files, 82 tests. Conservation property holds across ≥200 iterations.
- `scripts/sim-smoke.ts` — 1000 random-legal-bot games complete in <30s with 0 conservation violations.

**Cross-PRP contradictions resolved** (see `PRPs/cardshed-02-core-prp.md` §"Cross-PRP Contradictions Flagged"):

1. `beatenPairs` live inside `pendingAttack` until `stopDefending` flushes them — in BOTH full-defence and partial-defence branches.
2. Conservation operand uses `pendingAttackCardCount(pa) = unbeatenCards.length + 2 * beatenPairs.length`.
3. `checkWin(defenderId)` runs after refill in BOTH `stopDefending` branches — a defender CAN win on the trailing edge of a round.
4. `deck[0]` = bottom (trump face); `deck[deck.length-1]` = top (drawn next).
5. `Card.id` is `"{C|D|H|S}-{rank}-{slotHex}[-{saltB36}]"` — opaque; consumers MUST NOT parse the id.

---

## What's next (PRP 3 — 17 milestones)

Sub-deliverables A/B/C/D/E (per `PRPs/cardshed-03-experience-prp.md` §Implementation Blueprint):

| Group | Scope |
|-------|-------|
| **A** — MVP Implementation | 17 milestones M1–M17 covering `apps/ui/` scaffold → hot-seat playable → bots → replay → online → polish |
| **B** — UI/UX Spec | Screen inventory + Stitch-driven design system + agent-browser dogfood gates |
| **C** — WebSocket Protocol | Wire envelope, JSON schemas, reconnection semantics, idempotency keys (PRP-1 vocab: `seq`/`clientSeq`/`idempotencyKey`) |
| **D** — Analytics & Simulation | Event taxonomy + balance metrics + bot-vs-bot simulation harness |
| **E** — AI Bot Ladder | Level 0 (random-legal) / Level 1 (heuristic) / Level 2 (MCTS information-set) |

**Cross-PRP contradictions surfaced by PRP 3** (see PRP 3 §"Newly found"):

- **NEW #6** — `shuffleDeck(deck, seed)` seed is REQUIRED everywhere; brief is being updated.
- **NEW #7** — wire envelope normalized to PRP-1 vocab: server→client = `seq`; client→server = `clientSeq + idempotencyKey`; ack = `ackClientSeq + seq`.
- **NEW #8** — emission order locked: `RoundStarted → TrumpSelected → CardsDealt`.
- **NEW #9** — MVP treats single round as a match; `RoundEnded` is followed by `MatchEnded`. Multi-round semantics deferred (no wire-format change required).
- **NEW #10** — `Resolving` phase is rendered as `AwaitingDefense` UX-wise with an "auto-suggest Stop" affordance.

---

## How to read this stack

1. **Start here** (`BLUEPRINT.md`) for the 60-second map.
2. **PRP 1** (`PRPs/cardshed-01-blueprint.md`) — the decision document.
3. **PRP 2** (`PRPs/cardshed-02-core-prp.md`) — the shipped truth machine.
4. **PRP 3** (`PRPs/cardshed-03-experience-prp.md`) — the active execution plan.
5. **`apps/core/src/core/`** — the actual code.
6. **`CLAUDE.md`** — stack-local Claude rules.
7. **`AGENTS.md`** — agent overview.
