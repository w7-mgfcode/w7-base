name: "CARD SHED — Deterministic Core PRP (v2.0 rules)"
description: |
  Implementation-grade PRP for the pure-logic CARD SHED rules engine.
  Encodes the v2.0 rules as a side-effect-free TypeScript module with a
  Vitest suite that proves correctness, invariants, and hidden-info hygiene.
  Inputs: PRPs/01-strategy-blueprint.md (locked decisions), PRPs/02-deterministic-core.md (frozen brief), PRPs/03-experience-distribution.md (consumer contract).

---

## Cross-PRP Contradictions Flagged

These conflicts were surfaced while reconciling the brief (PRP 2), the blueprint (PRP 1), and the consumer brief (PRP 3). All five were resolved by the operator during PRP execution (see `Resolved:` lines below). PRP 3 MUST consume these resolutions verbatim.

1. **Beaten-pair custody (PRP 2 vs PRP 2).** The brief's `PendingAttack` type carries `beatenPairs: {attack, counter}[]` as live pending state, but the `stopDefending` pseudocode under FULL DEFENCE comments "move all beatenPairs flat → discard (already there, no-op)". Either beatens live inside `pendingAttack` until `stopDefending`, or `submitBeat` moves each beaten pair into `discard` eagerly. Both are defensible; they differ in where the card-conservation accountant looks. **Resolved:** `beatenPairs` live inside `pendingAttack` for the duration of the turn (better debuggability, simpler `createPublicView`), and `stopDefending` flushes them into `discard` in **both** branches — on FULL DEFENCE *and* on partial defence (already-beaten cards leave play with the rest of the table pile). The conservation invariant counts beaten pairs under `pendingAttack`, not `discard`, while a turn is in flight. Implementation: `rules.ts:submitBeat` pushes into `npa.beatenPairs`; `rules.ts:stopDefending` flushes to `next.discard` in both the full-defence and partial-defence branches.

2. **Conservation invariant operand (PRP 2 success-criteria vs PRP 2 property-test text).** Success Criteria says `sum(hands) + deck + discard + pendingAttack === 52`. The property-test bullet then writes `sum(pendingAttack)`. These reconcile only if `pendingAttack` is interpreted as "all cards currently held by the pending-attack object" = `unbeatenCards.length + 2 * beatenPairs.length`. **Resolved:** the helper `pendingAttackCardCount(pa)` is exported from `rules.ts` and used by every invariant assertion (test helper `totalCards(state)` and the property-test conservation check).

3. **Win-check on partial-defence path (PRP 2 pseudocode silent).** `submitAttack` calls `checkWin(state, attackerId)` after attacker refill. `stopDefending` does not call `checkWin` on the defender after partial-defence refill — but if the deck is empty and the defender ended partial defence holding 0 cards (e.g. they had to take 0 unbeaten cards because they beat none but had 0 hand before… edge of edges), the rules say end-of-turn hand size 0 + deck empty = win. **Resolved:** `checkWin(state, defenderId)` runs after refill in **both** `stopDefending` branches (full and partial). Because `checkWin` requires `deck.length === 0 && hand.length === 0`, this only fires when the round has genuinely exhausted the deck — a fully-defending defender with cards left in the deck refills and becomes the next attacker as normal. PRP 3 consumers MUST NOT assume "winner = current attacker"; a defender can win on the trailing-end of a round.

4. **Bottom-card / top-of-deck convention (PRP 2 implicit).** The brief uses `peekBottom`, `drawTop`, and `deck.pop()` interchangeably. Standard conventions vary: index 0 = top vs index 0 = bottom. The trump card sits at the *bottom* and must be drawn *last*. **Resolved:** `deck[0]` = bottom (trump face), `deck[deck.length - 1]` = top (drawn next). `drawTop` returns `deck.pop()`; `peekBottom` returns `deck[0]`. Documented inline in `types.ts` on the `MatchState.deck` field.

5. **Card-id format (PRP 2 vs PRP 3 examples).** Brief example: `"S-14-uuid"`. PRP 3 message examples use `"S-14-abc"`, `"H-14-def"`, `"C-9-ghi"`. Suit prefix letter encoding (`S/H/D/C`) is not formally specified relative to the numeric `Suit = 0|1|2|3` mapping in the Shared Contract. **Resolved:** the canonical `Card.id` is `"${suitLetter}-${rank}-${slotHex}[-${saltB36}]"` where `suitLetter` is `C|D|H|S` for `Suit 0|1|2|3`, `slotHex` is the 2-digit hex of the card's canonical slot index (`suit*13 + rank-2`), and the optional `saltB36` is `(salt >>> 0).toString(36)` derived from the round seed. `createDeck()` (no argument) produces unsalted ids like `S-14-33`; `createDeck(salt)` produces salted ids like `S-14-33-1c`; `startNewRound` passes the round seed as the salt so each round's 52 cards have **deterministic but uniquely-tagged** ids — disjoint across rounds and matches. The letter and slot-hex are presentational only; equality is by full `id` string. Bots, the engine, and PRP 3 wire code MUST NEVER parse the id to extract suit/rank — always use `card.suit` / `card.rank`.

---

## Purpose

Build the **deterministic core** of CARD SHED: a pure, side-effect-free TypeScript module that encodes Rules v2.0. Given a `MatchState` and a player `Action`, the core returns the next `MatchState` plus a list of emitted `GameEvent`s, or a structured `ValidationError`. A Vitest suite proves it.

## Core Principles

1. **Purity is non-negotiable.** No `Math.random`, no `Date.now`, no `console.*` in `src/core/`, no module-level mutable state. Every reducer returns a *new* `MatchState`.
2. **Errors are values.** Validation failures return `{ ok: false, error }`. Throws are reserved for invariant violations (programmer bugs).
3. **Hidden information is law.** Opponent hands and deck order never leak through any exported function except `createPrivateView(state, viewerId)` for the viewer's own hand.
4. **Determinism through seeded RNG.** `shuffleDeck(deck, seed)` is the *only* place randomness happens, and only when given a numeric seed. Same seed in → same permutation out, on every JS runtime.
5. **Conservation is invariant.** Across every legal state transition, the 52 cards are accounted for exactly once.

---

## Goal

Deliver three files (and only these three, plus a `package.json` + `tsconfig.json` + `vitest.config.ts` if the project does not already have them):

1. `src/core/types.ts` — declares every data structure in the Shared Contract + the entities listed in §"Data models".
2. `src/core/rules.ts` — implements every function on the **Rules Engine API** surface.
3. `src/core/__tests__/*.test.ts` — Vitest suite covering deck, attack validation, beat legality, turn flow, conservation, and hidden-info redaction.

The output is a black box that PRP 3's UI, networking, AI, and simulation harness import without ever reaching into core internals.

## Why

The rules engine is the **truth machine** of CARD SHED. UI, networking, AI, and analytics are all transformations over its state or its event stream. If the core is wrong, the whole game is wrong. If the core is impure, replay, anti-cheat, and bot simulation all break.

Building this layer first (and independently of UI/networking) lets PRP 3 wrap a stable interface, and lets bot simulators in PRP 3 generate millions of games for balance analytics from a known-good engine.

## What

A TypeScript module that exposes the Rules Engine API surface defined below. The module is consumed by:
- The hot-seat MVP (PRP 3, browser, direct import).
- The bot ladder (PRP 3, browser + node, direct import).
- The simulation harness (PRP 3, node, direct import).
- The eventual Rust server (PRP 1, mechanical port — the TS implementation is the canonical spec).

### Success Criteria

- [ ] All types defined in `src/core/types.ts` are referenced from `rules.ts` and exported.
- [ ] Every rule function listed in the **Rules Engine API** section is implemented and unit-tested.
- [ ] **Card conservation invariant**: `sum(player.hand.length) + deck.length + discard.length + pendingAttackCardCount(round.pendingAttack) === 52` at every state transition.
- [ ] **No hidden-info leak**: `createPublicView(state, viewerId?)` strips opponents' hand contents and the deck order. `createPrivateView(state, viewerId)` reveals only the viewer's own hand.
- [ ] **Deterministic shuffling**: `shuffleDeck(deck, 42)` returns byte-identical output on every run; cross-checked against a recorded fixture.
- [ ] **No mutation of input state**: every reducer returns a new `MatchState`. A `freezeDeep` test catches accidental mutation.
- [ ] **Every action returns `{ ok: true, state, events }` or `{ ok: false, error: { code, message } }`.** No throws on validation errors.
- [ ] **Determinism guards**: ESLint configured to forbid `Math.random`, `Date.now`, `new Date()`, `performance.now`, `crypto.getRandomValues` inside `src/core/**` (allowed only inside the seeded shuffle helper, where it never appears anyway).
- [ ] **All Vitest tests below pass** (§"Test cases" in this PRP).
- [ ] **Property-based tests run ≥ 200 iterations** each and report zero invariant violations.
- [ ] **Simulation smoke**: 1000 random-legal-bot games complete in < 30s with 0 conservation violations and 100% reaching `RoundEnded` or `MatchEnded`.

---

## All Needed Context

### CARD SHED — Rules v2.0 summary (canonical, frozen)

- **Players & deck.** 3 or 4 players, single 52-card deck. Suits `Clubs(0), Diamonds(1), Hearts(2), Spades(3)`. Ranks `2..10, J(11), Q(12), K(13), A(14)`.
- **Trump.** Bottom card of shuffled deck declared trump. The card itself **stays in the deck** and is drawn normally when its turn comes.
- **Attack.** Attacker sends exactly one of:
  - 1 card (any), or
  - 3 cards = a pair (same rank) + 1 kicker, or
  - 5 cards = two pairs of *different* ranks + 1 kicker.
  After sending, attacker refills to 5 from deck if hand < 5 and deck > 0.
- **Defence.** Defender beats received cards in any order:
  - Non-trump attack → same-suit higher rank, OR any trump.
  - Trump attack → higher trump only.
  - Defender may stop at any time.
- **Resolution.**
  - **Full defence** (every attack card beaten): all (attack, counter) pairs go to discard, defender refills to 5, **defender immediately becomes attacker** and must send a new attack.
  - **Partial / no defence**: unbeaten cards go into defender's hand, defender refills to ≥ 5, **next clockwise player becomes attacker**.
- **No reshuffles.** Once the deck is empty, hands may shrink below 5.
- **Win.** End-of-turn hand size 0 *after* the refill attempt, which is only possible when `deck.length === 0`.
- **New round.** Winner recorded, dealer rotates clockwise, gather + reshuffle (new seed), new bottom-card trump, deal 5 to each.

### Shared Contract (frozen — byte-identical to PRP 3)

```ts
// src/core/types.ts — Shared Contract block (do not diverge from PRP 3)
export type Suit = 0 | 1 | 2 | 3;   // Clubs, Diamonds, Hearts, Spades
export type Rank = 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14;

export interface Card {
  id: string;          // immutable per card instance, e.g. "S-14-7f3a"
  suit: Suit;
  rank: Rank;
}

export type TurnState =
  | "Dealing"
  | "AwaitingAttack"
  | "AwaitingDefense"
  | "Resolving"
  | "RoundEnded"
  | "MatchEnded";

export type ValidationError = {
  code: string;        // machine-readable, e.g. "ATTACK_INVALID_COMBO"
  message: string;     // human-readable
  details?: unknown;
};

export type ActionResult<T = unknown> =
  | { ok: true; state: MatchState; events: GameEvent[]; value?: T }
  | { ok: false; error: ValidationError };
```

### Rules Engine API (the surface PRP 3 will call)

```ts
// Pure, deterministic. No I/O, no Math.random outside the seeded shuffle.
createDeck(): Card[]
shuffleDeck(deck: Card[], seed: number): Card[]   // seed REQUIRED for determinism
dealInitialHands(deck: Card[], playerCount: 3 | 4): { hands: Card[][]; deck: Card[] }
determineTrumpFromBottomCard(deck: Card[]): Suit
startNewRound(prev: MatchState | null, seed: number): MatchState

validateAttack(cards: Card[], playerHand: Card[]): { ok: true } | { ok: false; error: ValidationError }
submitAttack(state: MatchState, playerId: string, cardIds: string[]): ActionResult
canBeat(attackCard: Card, counterCard: Card, trump: Suit): boolean
submitBeat(state: MatchState, defenderId: string, attackCardId: string, counterCardId: string): ActionResult
stopDefending(state: MatchState, defenderId: string): ActionResult

drawToMinimum(hand: Card[], deck: Card[], target: number): { hand: Card[]; deck: Card[] }
checkWin(state: MatchState, playerId: string): boolean

advanceTurnAfterFullDefense(state: MatchState): MatchState
advanceTurnAfterPartialDefense(state: MatchState): MatchState
rotateDealer(state: MatchState): MatchState

getLegalActions(state: MatchState, playerId: string): Action[]
createPublicView(state: MatchState, viewerId?: string): PublicGameView
createPrivateView(state: MatchState, viewerId: string): PrivatePlayerView
```

### Documentation & References

```yaml
# MUST READ — frozen design inputs
- file: PRPs/02-deterministic-core.md
  why: source of truth for rules, success criteria, test taxonomy, anti-patterns

- file: PRPs/cardshed-01-blueprint.md
  why: locked tech-stack + TurnState vocab + module taxonomy
  sections: §1 Executive Summary, §2 Tech Stack, §6 Clean Local Architecture, §9 Cross-PRP Implications

- file: PRPs/03-experience-distribution.md
  why: confirms Shared Contract block and engine API surface
  sections: "Shared Contract", "Rules-engine surface", §C "Networking Protocol" (for Card.id wire shape)

# External — pinned tooling and patterns
- url: https://vitest.dev/guide/
  why: Vitest v2 config + run modes; suite uses `vitest run` (one-shot, CI-friendly)
  critical: with type `module` package.json, default config works; no jest globals needed

- url: https://github.com/dubzzz/fast-check
  why: property-based tests for invariants; fast-check ≥ 3.x is the standard JS library
  critical: use `fc.assert(fc.property(...), { numRuns: 200 })` for invariant tests

- url: https://en.wikipedia.org/wiki/Xorshift#xorshift+
  why: background for the chosen PRNG family (mulberry32) — small, deterministic, public-domain

- url: https://gist.github.com/tommyettinger/46a3c64a2ecfe7c4ce5c
  why: canonical mulberry32 reference; passes for our use (shuffle, not crypto)
  critical: NOT a CSPRNG; do NOT use for security; perfect for game shuffle

- url: https://bost.ocks.org/mike/shuffle/
  why: Fisher-Yates shuffle reference; the only correct uniform shuffle for a finite deck
  critical: iterate i from length-1 down to 1; swap with random index in [0..i]

- url: https://github.com/davidbau/seedrandom
  why: optional alternative PRNG if mulberry32 fails portability tests; included as fallback note only

# Codebase references (existing TS conventions — for tsconfig + tooling shape only)
- file: @lab/ll-RELIQUARY/apps/ui/tsconfig.json
  why: TS strict-mode baseline used elsewhere in the repo (ES2022, bundler resolution, strict)
  critical: mirror these compiler options for the core package; no JSX needed in core/

- file: @lab/ll-RELIQUARY/apps/ui/package.json
  why: precedent for vitest ^2.1.x + typescript ^5.7.x + "type": "module"
  critical: do NOT introduce a NEW major version of vitest or typescript without justification
```

### Current codebase tree

```bash
PRPs/
├── 01-strategy-blueprint.md          # locked
├── 02-deterministic-core.md          # THIS PRP'S BRIEF
├── 03-experience-distribution.md     # sibling, parallel
├── INDEX.md
├── cardshed-01-blueprint.md          # locked output of PRP 1
└── templates/
    └── prp_base.md

@lab/
├── ll-RELIQUARY/                     # TS+Vite+Tailwind reference
└── ll-KNOWRAG/                       # TS+Vite reference
```

There is **no existing `src/core/` directory** in the repo. CARD SHED has not landed any code yet — this PRP creates the first slice. The destination is intentionally left ambiguous in the brief; **proposed location is `@lab/ll-CARDSHED/apps/core/`** (mirroring the `@lab/<game>/apps/<thing>/` convention from RELIQUARY and KNOWRAG). Confirm with operator before the first commit.

### Desired codebase tree (additions)

```bash
@lab/ll-CARDSHED/apps/core/
├── package.json
├── tsconfig.json
├── vitest.config.ts
├── .eslintrc.cjs                    # forbids Math.random/Date.now in src/core/**
├── src/
│   └── core/
│       ├── index.ts                 # public re-exports
│       ├── types.ts                 # all data shapes
│       ├── rules.ts                 # all engine functions
│       ├── prng.ts                  # mulberry32 + seeded Fisher-Yates
│       └── __tests__/
│           ├── deck.test.ts
│           ├── shuffle.test.ts
│           ├── attack-validation.test.ts
│           ├── can-beat.test.ts
│           ├── submit-attack.test.ts
│           ├── submit-beat.test.ts
│           ├── stop-defending.test.ts
│           ├── draw-to-minimum.test.ts
│           ├── check-win.test.ts
│           ├── turn-flow.test.ts
│           ├── views.test.ts
│           ├── legal-actions.test.ts
│           ├── conservation.property.test.ts
│           └── integration.test.ts
└── scripts/
    └── sim-smoke.ts                 # 1000-game random-legal smoke
```

### Known Gotchas & Library Quirks

```ts
// CRITICAL: Vitest v2 with "type": "module" needs vitest.config.ts (ESM), not .js.
// CRITICAL: TypeScript's `readonly` does NOT prevent runtime mutation; use Object.freeze
//           or a deep-freeze helper inside tests to catch mutation regressions.
// CRITICAL: Array.prototype.sort is NOT stable across all engines historically; for
//           determinism, always use an explicit comparator and stable inputs.
// CRITICAL: JSON.stringify property order is NOT guaranteed across engines for
//           non-string keys; do not use stringified state as an equality proxy without sort.
// CRITICAL: Math.random() is BANNED in src/core/**. Use prng.mulberry32(seed) only.
// CRITICAL: Date.now() / new Date() are BANNED in src/core/** — the engine has no
//           concept of time. Timestamps belong to PRP 3's event emitter, not the core.
// CRITICAL: structuredClone is available in Node 17+ and all modern browsers; use it
//           freely for the immutable-reducer pattern. Falls back to JSON clone in tests
//           if needed (but plain Card/MatchState are JSON-safe).
// CRITICAL: fast-check shrinks failing inputs to a minimal counterexample — let it.
//           Do NOT add `try { ... } catch {}` around fc.assert; the failure IS the signal.
// CRITICAL: When refilling the deck with drawToMinimum, the brief is explicit:
//           NEVER reshuffle the discard pile. Once deck.length === 0, draws stop.
// CRITICAL: checkWin MUST run AFTER refill, not before. A player at 0 cards with deck
//           non-empty will be refilled to 5 and is NOT a winner.
// CRITICAL: 5-card attack requires TWO DISTINCT RANKS for the pairs. Four-of-a-kind
//           (e.g. 7♣ 7♦ 7♥ 7♠ + kicker) is INVALID despite being two pairs by raw rank.
//           This is the most subtle attack rule.
// CRITICAL: Bottom card of the deck (deck[0]) is the trump face. It STAYS in the deck.
//           It is drawn last (after deck.pop() has emptied everything above it).
// CRITICAL: The "next clockwise" player after partial defence is left of the DEFENDER,
//           not left of the original attacker. Verify with the seat-index lookup helper.
// CRITICAL: PendingAttack.beatenPairs are NOT in discard until stopDefending resolves
//           the turn as a full defence. While the turn is in flight, beaten cards live
//           inside pendingAttack. (See "Contradictions flagged" #1 — proposed resolution.)
```

---

## Implementation Blueprint

### Data models (src/core/types.ts)

Define, in this order, exporting every symbol:

```ts
// Shared Contract — frozen
export type Suit = 0 | 1 | 2 | 3;
export type Rank = 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14;
export interface Card { id: string; suit: Suit; rank: Rank; }
export type TurnState = "Dealing" | "AwaitingAttack" | "AwaitingDefense" | "Resolving" | "RoundEnded" | "MatchEnded";
export type ValidationError = { code: string; message: string; details?: unknown };
export type ActionResult<T = unknown> =
  | { ok: true; state: MatchState; events: GameEvent[]; value?: T }
  | { ok: false; error: ValidationError };

// Domain entities
export interface Player {
  id: string;
  name: string;
  hand: Card[];
  score: number;
  isActive: boolean;
  seatIndex: number;          // 0..playerCount-1, fixed for the match
}

export interface BeatenPair { attack: Card; counter: Card; }

export interface PendingAttack {
  attackerId: string;
  defenderId: string;
  unbeatenCards: Card[];      // attack cards not yet beaten
  beatenPairs: BeatenPair[];  // beaten this turn; flushed to discard on stop
}

export interface RoundState {
  trump: Suit;
  dealerId: string;
  attackerId: string;
  defenderId: string | null;
  phase: TurnState;
  pendingAttack: PendingAttack | null;
}

export interface MatchState {
  matchId: string;
  roundNumber: number;
  players: Player[];          // ordered by seatIndex
  deck: Card[];               // deck[0] = bottom (trump face); deck[length-1] = top (drawn next)
  discard: Card[];            // face-down; opponents see only count
  round: RoundState;
  winner: string | null;      // playerId or null
  rngSeed: number;            // seed used for the current round's shuffle
}

// Action union — discriminated on `kind`
export type Action =
  | { kind: "Attack"; playerId: string; cardIds: string[] }
  | { kind: "Beat"; playerId: string; attackCardId: string; counterCardId: string }
  | { kind: "Stop"; playerId: string };

// GameEvent union — append-only audit / animation trail
export type GameEvent =
  | { type: "RoundStarted"; roundNumber: number; dealerId: string; trump: Suit }
  | { type: "TrumpSelected"; trump: Suit; bottomCardId: string }
  | { type: "CardsDealt"; perPlayer: { playerId: string; count: number }[] }
  | { type: "AttackSubmitted"; attackerId: string; defenderId: string; cardIds: string[] }
  | { type: "CardBeaten"; defenderId: string; attackCardId: string; counterCardId: string }
  | { type: "DefenseStopped"; defenderId: string; takenCardIds: string[] }
  | { type: "FullDefense"; defenderId: string; discardedPairs: number }
  | { type: "CardsDrawn"; playerId: string; count: number }
  | { type: "TurnChanged"; nextAttackerId: string; phase: TurnState }
  | { type: "RoundWon"; winnerId: string }
  | { type: "MatchEnded"; winnerId: string };

// View projections — used by PRP 3 for UI + network
export interface HandSummary {
  ownerId: string;
  count: number;
  publiclyKnown: Card[];   // cards opponents must know per rules (currently empty in v2.0)
}

export interface PublicPlayerInfo {
  id: string;
  name: string;
  seatIndex: number;
  score: number;
  isActive: boolean;
  hand: HandSummary;
}

export interface PublicGameView {
  matchId: string;
  roundNumber: number;
  players: PublicPlayerInfo[];
  deckCount: number;
  discardCount: number;
  round: {
    trump: Suit;
    dealerId: string;
    attackerId: string;
    defenderId: string | null;
    phase: TurnState;
    pendingAttack: {
      attackerId: string;
      defenderId: string;
      unbeatenCards: Card[];   // public — visible on the table
      beatenPairs: BeatenPair[]; // public — visible on the table
    } | null;
  };
  winner: string | null;
}

export interface PrivatePlayerView extends PublicGameView {
  viewerId: string;
  viewerHand: Card[];        // full reveal of viewer's own hand
}
```

### Per-function pseudocode (rules.ts)

```ts
// ─── prng.ts ────────────────────────────────────────────────────────────
// CRITICAL: mulberry32 is a 32-bit PRNG; period 2^32, perfect for shuffle.
// CRITICAL: NEVER expose a function in core/ that calls Math.random.
export function mulberry32(seed: number): () => number {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// ─── createDeck ─────────────────────────────────────────────────────────
// Returns 52 unique cards. Order is canonical (suit-major, rank-ascending).
// `id` is "{suitLetter}-{rank}-{indexHex}", deterministic and unique.
function createDeck(): Card[] {
  const suits: Suit[] = [0, 1, 2, 3];
  const letters = ["C", "D", "H", "S"];
  const out: Card[] = [];
  for (const s of suits) {
    for (let r = 2 as Rank; r <= 14; r++) {
      const idx = s * 13 + (r - 2);
      out.push({ id: `${letters[s]}-${r}-${idx.toString(16).padStart(2, "0")}`, suit: s, rank: r as Rank });
    }
  }
  return out;
}

// ─── shuffleDeck ────────────────────────────────────────────────────────
// PATTERN: seeded Fisher-Yates on a COPY of input. Input is never mutated.
function shuffleDeck(deck: Card[], seed: number): Card[] {
  const out = deck.slice();
  const rand = mulberry32(seed);
  for (let i = out.length - 1; i > 0; i--) {
    const j = Math.floor(rand() * (i + 1));
    [out[i], out[j]] = [out[j], out[i]];
  }
  return out;
}

// ─── determineTrumpFromBottomCard ───────────────────────────────────────
// CRITICAL: bottom = deck[0]. The card is NOT removed. Trump suit = its suit.
function determineTrumpFromBottomCard(deck: Card[]): Suit { return deck[0].suit; }

// ─── dealInitialHands ───────────────────────────────────────────────────
// Deals 5 cards to each player by popping from the TOP (deck.pop()).
// Bottom card (trump face) remains and will be drawn last.
function dealInitialHands(deck: Card[], playerCount: 3 | 4): { hands: Card[][]; deck: Card[] } {
  const remaining = deck.slice();
  const hands: Card[][] = Array.from({ length: playerCount }, () => []);
  for (let round = 0; round < 5; round++) {
    for (let p = 0; p < playerCount; p++) {
      const c = remaining.pop();
      if (!c) throw new Error("INVARIANT: deck exhausted during initial deal");
      hands[p].push(c);
    }
  }
  return { hands, deck: remaining };
}

// ─── validateAttack ─────────────────────────────────────────────────────
function validateAttack(cards: Card[], hand: Card[]): { ok: true } | { ok: false; error: ValidationError } {
  if (![1, 3, 5].includes(cards.length)) return err("ATTACK_INVALID_SIZE", `Attack must be 1/3/5 cards, got ${cards.length}`);
  const seenIds = new Set<string>();
  for (const c of cards) {
    if (seenIds.has(c.id)) return err("ATTACK_DUPLICATE_CARD", `Duplicate card ${c.id}`);
    seenIds.add(c.id);
    if (!hand.find((h) => h.id === c.id)) return err("ATTACK_CARD_NOT_OWNED", `Card ${c.id} not in hand`);
  }
  if (cards.length === 1) return { ok: true };
  // group by rank
  const byRank = new Map<Rank, number>();
  for (const c of cards) byRank.set(c.rank, (byRank.get(c.rank) ?? 0) + 1);
  const pairs = [...byRank.entries()].filter(([, n]) => n >= 2);
  if (cards.length === 3) {
    if (pairs.length === 0) return err("ATTACK_NO_PAIR", "3-card attack needs a pair");
    return { ok: true };
  }
  // cards.length === 5
  const distinctPairRanks = pairs.length;       // # of DISTINCT ranks with count ≥ 2
  if (distinctPairRanks < 2) return err("ATTACK_NO_TWO_PAIRS", "5-card attack needs two pairs of DISTINCT ranks");
  return { ok: true };
}

// ─── canBeat ────────────────────────────────────────────────────────────
function canBeat(attack: Card, counter: Card, trump: Suit): boolean {
  if (attack.suit === trump) return counter.suit === trump && counter.rank > attack.rank;
  return (counter.suit === attack.suit && counter.rank > attack.rank) || counter.suit === trump;
}

// ─── submitAttack ───────────────────────────────────────────────────────
// PATTERN: validate → immutable update → emit events → advance phase.
function submitAttack(state: MatchState, playerId: string, cardIds: string[]): ActionResult {
  if (state.round.phase !== "AwaitingAttack") return errResult("PHASE_NOT_AWAITING_ATTACK", `Phase is ${state.round.phase}`);
  if (state.round.attackerId !== playerId) return errResult("NOT_YOUR_TURN", `${playerId} is not the attacker`);
  const attacker = findPlayer(state, playerId);
  const cards: Card[] = [];
  for (const cid of cardIds) {
    const card = attacker.hand.find((c) => c.id === cid);
    if (!card) return errResult("ATTACK_CARD_NOT_OWNED", `Card ${cid} not in hand`);
    cards.push(card);
  }
  const v = validateAttack(cards, attacker.hand);
  if (!v.ok) return { ok: false, error: v.error };

  // Immutable update
  const next = clone(state);
  const nAttacker = findPlayer(next, playerId);
  nAttacker.hand = nAttacker.hand.filter((c) => !cardIds.includes(c.id));
  const defenderId = leftOf(next, playerId);
  next.round.pendingAttack = { attackerId: playerId, defenderId, unbeatenCards: cards, beatenPairs: [] };

  // Refill attacker BEFORE win check
  const refill = drawToMinimum(nAttacker.hand, next.deck, 5);
  const drawn = refill.hand.length - nAttacker.hand.length;
  nAttacker.hand = refill.hand;
  next.deck = refill.deck;

  const events: GameEvent[] = [
    { type: "AttackSubmitted", attackerId: playerId, defenderId, cardIds },
    ...(drawn > 0 ? [{ type: "CardsDrawn", playerId, count: drawn } as GameEvent] : []),
  ];

  if (checkWin(next, playerId)) {
    next.round.phase = "RoundEnded";
    next.winner = playerId;
    events.push({ type: "RoundWon", winnerId: playerId });
    return { ok: true, state: next, events };
  }

  next.round.phase = "AwaitingDefense";
  next.round.defenderId = defenderId;
  events.push({ type: "TurnChanged", nextAttackerId: playerId, phase: next.round.phase });
  return { ok: true, state: next, events };
}

// ─── submitBeat ─────────────────────────────────────────────────────────
function submitBeat(state: MatchState, defenderId: string, attackCardId: string, counterCardId: string): ActionResult {
  if (state.round.phase !== "AwaitingDefense" && state.round.phase !== "Resolving")
    return errResult("PHASE_NOT_DEFENSE", `Phase is ${state.round.phase}`);
  if (state.round.defenderId !== defenderId) return errResult("NOT_YOUR_TURN", `${defenderId} is not the defender`);
  const pa = state.round.pendingAttack;
  if (!pa) return errResult("NO_PENDING_ATTACK", "No pending attack to beat");
  const attack = pa.unbeatenCards.find((c) => c.id === attackCardId);
  if (!attack) return errResult("BEAT_TARGET_NOT_FOUND", `${attackCardId} is not an unbeaten attack card`);
  const defender = findPlayer(state, defenderId);
  const counter = defender.hand.find((c) => c.id === counterCardId);
  if (!counter) return errResult("BEAT_CARD_NOT_OWNED", `${counterCardId} not in defender's hand`);
  if (!canBeat(attack, counter, state.round.trump)) return errResult("BEAT_ILLEGAL", `${counterCardId} cannot beat ${attackCardId}`);

  const next = clone(state);
  const nDefender = findPlayer(next, defenderId);
  nDefender.hand = nDefender.hand.filter((c) => c.id !== counterCardId);
  const npa = next.round.pendingAttack!;
  npa.unbeatenCards = npa.unbeatenCards.filter((c) => c.id !== attackCardId);
  npa.beatenPairs.push({ attack, counter });
  next.round.phase = npa.unbeatenCards.length === 0 ? "Resolving" : "AwaitingDefense";

  return {
    ok: true,
    state: next,
    events: [{ type: "CardBeaten", defenderId, attackCardId, counterCardId }],
  };
}

// ─── stopDefending ──────────────────────────────────────────────────────
function stopDefending(state: MatchState, defenderId: string): ActionResult {
  if (state.round.phase !== "AwaitingDefense" && state.round.phase !== "Resolving")
    return errResult("PHASE_NOT_DEFENSE", `Phase is ${state.round.phase}`);
  if (state.round.defenderId !== defenderId) return errResult("NOT_YOUR_TURN", `${defenderId} is not the defender`);
  const pa = state.round.pendingAttack;
  if (!pa) return errResult("NO_PENDING_ATTACK", "No pending attack to stop");

  const next = clone(state);
  const nDefender = findPlayer(next, defenderId);
  const npa = next.round.pendingAttack!;
  const events: GameEvent[] = [];

  if (npa.unbeatenCards.length === 0) {
    // FULL DEFENCE: flush all beaten pairs to discard, defender becomes attacker.
    for (const { attack, counter } of npa.beatenPairs) next.discard.push(attack, counter);
    events.push({ type: "FullDefense", defenderId, discardedPairs: npa.beatenPairs.length });
    const refill = drawToMinimum(nDefender.hand, next.deck, 5);
    const drawn = refill.hand.length - nDefender.hand.length;
    nDefender.hand = refill.hand;
    next.deck = refill.deck;
    if (drawn > 0) events.push({ type: "CardsDrawn", playerId: defenderId, count: drawn });

    // Win-check after refill (PRP-flag #3)
    if (checkWin(next, defenderId)) {
      next.round.phase = "RoundEnded";
      next.winner = defenderId;
      next.round.pendingAttack = null;
      events.push({ type: "RoundWon", winnerId: defenderId });
      return { ok: true, state: next, events };
    }

    next.round.attackerId = defenderId;
    next.round.defenderId = null;
    next.round.pendingAttack = null;
    next.round.phase = "AwaitingAttack";
    events.push({ type: "TurnChanged", nextAttackerId: defenderId, phase: "AwaitingAttack" });
    return { ok: true, state: next, events };
  }

  // PARTIAL / NO DEFENCE: defender takes unbeaten cards; beaten pairs ALSO go to discard
  // (they were beaten, after all — the pile of cards in the middle is the discard).
  const taken = npa.unbeatenCards.slice();
  for (const c of taken) nDefender.hand.push(c);
  for (const { attack, counter } of npa.beatenPairs) next.discard.push(attack, counter);
  events.push({ type: "DefenseStopped", defenderId, takenCardIds: taken.map((c) => c.id) });

  const refill = drawToMinimum(nDefender.hand, next.deck, 5);
  const drawn = refill.hand.length - nDefender.hand.length;
  nDefender.hand = refill.hand;
  next.deck = refill.deck;
  if (drawn > 0) events.push({ type: "CardsDrawn", playerId: defenderId, count: drawn });

  // Win-check on defender after partial-defence refill (PRP-flag #3)
  if (checkWin(next, defenderId)) {
    next.round.phase = "RoundEnded";
    next.winner = defenderId;
    next.round.pendingAttack = null;
    events.push({ type: "RoundWon", winnerId: defenderId });
    return { ok: true, state: next, events };
  }

  const nextAttacker = leftOf(next, defenderId);
  next.round.attackerId = nextAttacker;
  next.round.defenderId = null;
  next.round.pendingAttack = null;
  next.round.phase = "AwaitingAttack";
  events.push({ type: "TurnChanged", nextAttackerId: nextAttacker, phase: "AwaitingAttack" });
  return { ok: true, state: next, events };
}

// ─── drawToMinimum ──────────────────────────────────────────────────────
// CRITICAL: pops from the END of deck (top). Stops when deck empty.
function drawToMinimum(hand: Card[], deck: Card[], target: number): { hand: Card[]; deck: Card[] } {
  const h = hand.slice();
  const d = deck.slice();
  while (h.length < target && d.length > 0) {
    const c = d.pop()!;
    h.push(c);
  }
  return { hand: h, deck: d };
}

// ─── checkWin ───────────────────────────────────────────────────────────
function checkWin(state: MatchState, playerId: string): boolean {
  const p = findPlayer(state, playerId);
  return state.deck.length === 0 && p.hand.length === 0;
}

// ─── getLegalActions ────────────────────────────────────────────────────
// Used by bots and by the UI's "highlight legal cards" affordance.
// CRITICAL: enumerates all *minimal* attack combinations; full enumeration
// of 5-card combos can be exponential — cap at the player's hand only.
function getLegalActions(state: MatchState, playerId: string): Action[] { /* see Implementation Plan task T11 */ }

// ─── views ──────────────────────────────────────────────────────────────
function createPublicView(state: MatchState, _viewerId?: string): PublicGameView {
  return {
    matchId: state.matchId,
    roundNumber: state.roundNumber,
    players: state.players.map((p) => ({
      id: p.id, name: p.name, seatIndex: p.seatIndex, score: p.score, isActive: p.isActive,
      hand: { ownerId: p.id, count: p.hand.length, publiclyKnown: [] },
    })),
    deckCount: state.deck.length,
    discardCount: state.discard.length,
    round: {
      trump: state.round.trump,
      dealerId: state.round.dealerId,
      attackerId: state.round.attackerId,
      defenderId: state.round.defenderId,
      phase: state.round.phase,
      pendingAttack: state.round.pendingAttack
        ? {
            attackerId: state.round.pendingAttack.attackerId,
            defenderId: state.round.pendingAttack.defenderId,
            unbeatenCards: state.round.pendingAttack.unbeatenCards.slice(),
            beatenPairs: state.round.pendingAttack.beatenPairs.slice(),
          }
        : null,
    },
    winner: state.winner,
  };
}

function createPrivateView(state: MatchState, viewerId: string): PrivatePlayerView {
  const pub = createPublicView(state, viewerId);
  const viewer = findPlayer(state, viewerId);
  return { ...pub, viewerId, viewerHand: viewer.hand.slice() };
}

// ─── helpers ────────────────────────────────────────────────────────────
function findPlayer(state: MatchState, id: string): Player { /* throw on missing — invariant */ }
function leftOf(state: MatchState, id: string): string { /* (seatIndex + 1) mod playerCount */ }
function clone<T>(x: T): T { return structuredClone(x); }
function err(code: string, message: string): { ok: false; error: ValidationError } { return { ok: false, error: { code, message } }; }
function errResult(code: string, message: string): ActionResult { return { ok: false, error: { code, message } }; }
export function pendingAttackCardCount(pa: PendingAttack | null): number {
  if (!pa) return 0;
  return pa.unbeatenCards.length + 2 * pa.beatenPairs.length;
}
```

### List of tasks (in order)

```yaml
T1 — SCAFFOLD package:
  CREATE @lab/ll-CARDSHED/apps/core/package.json
    - name: "@cardshed/core"
    - type: "module"
    - scripts: { build, typecheck, lint, test }
    - devDependencies: typescript ^5.7, vitest ^2.1, eslint ^9, @typescript-eslint/* ^8, fast-check ^3.23, tsx ^4
  CREATE @lab/ll-CARDSHED/apps/core/tsconfig.json
    - MIRROR pattern from: @lab/ll-RELIQUARY/apps/ui/tsconfig.json
    - REMOVE jsx setting (no React in core)
    - REMOVE DOM lib (Node-only)
  CREATE @lab/ll-CARDSHED/apps/core/vitest.config.ts
    - includeSource: src/**/*.ts
    - test.include: src/**/__tests__/**/*.test.ts
  CREATE @lab/ll-CARDSHED/apps/core/.eslintrc.cjs
    - rule: "no-restricted-syntax" forbidding Math.random, Date.now, new Date(), performance.now, crypto.getRandomValues in src/core/**

T2 — TYPES first:
  CREATE src/core/types.ts
    - EXPORT every symbol listed under "Data models" above
    - VERIFY: tsc --noEmit passes with zero errors

T3 — PRNG:
  CREATE src/core/prng.ts
    - EXPORT mulberry32(seed): () => number
    - EXPORT shuffleInPlaceCopy(arr, seed): T[]  (used by shuffleDeck)

T4 — RULES skeleton:
  CREATE src/core/rules.ts
    - IMPORT all types from ./types
    - IMPORT mulberry32 from ./prng
    - DECLARE all function signatures from the Rules Engine API
    - LEAVE bodies as `throw new Error("TODO")` to keep tsc green

T5 — Implement createDeck + shuffleDeck + determineTrumpFromBottomCard:
  - createDeck returns 52 unique cards in canonical order
  - shuffleDeck uses mulberry32 + Fisher-Yates on a COPY
  - determineTrumpFromBottomCard reads deck[0].suit

T6 — Implement dealInitialHands + drawToMinimum:
  - dealInitialHands pops 5 per player from top
  - drawToMinimum stops at deck empty (no reshuffle)

T7 — Implement validateAttack + canBeat:
  - validateAttack covers all 9 listed error cases
  - canBeat handles trump-vs-trump, non-trump-vs-non-trump, mixed

T8 — Implement submitAttack:
  - validate → clone → mutate clone → emit events → check win → advance phase
  - PROPAGATE validation errors via ActionResult { ok: false }

T9 — Implement submitBeat + stopDefending:
  - submitBeat moves attack from unbeatenCards into beatenPairs
  - stopDefending branches on unbeatenCards.length === 0
    - FULL DEFENCE: flush pairs to discard, refill defender, checkWin, defender becomes attacker
    - PARTIAL: take unbeaten into hand, flush pairs to discard, refill, checkWin, rotate to leftOf(defender)

T10 — Implement startNewRound + rotateDealer + advanceTurn* helpers:
  - startNewRound(null, seed) creates fresh MatchState (caller supplies player roster via a thin overload or a separate setup step)
  - startNewRound(prev, seed) rotates dealer + reshuffles + redeals + new trump
  - advanceTurnAfterFullDefense / advanceTurnAfterPartialDefense are pure helpers around stopDefending's branches

T11 — Implement getLegalActions:
  - If phase === AwaitingAttack and playerId === attackerId:
    - emit one Attack action per legal singleton (every card in hand)
    - emit one Attack action per (pair-rank, kicker-card) combination
    - emit one Attack action per (pair1-rank, pair2-rank, kicker-card) combination with pair1 != pair2
  - If phase === AwaitingDefense and playerId === defenderId:
    - for each unbeaten attack card, emit one Beat action per legal counter in hand
    - emit one Stop action
  - Else: empty array
  - CAP combinatorial blow-up by deduplicating by card-id-set

T12 — Implement createPublicView + createPrivateView:
  - PublicGameView strips hand contents (only count)
  - PrivateView extends Public + reveals viewer's hand
  - Both are pure projections; mutating the view MUST NOT affect state (use .slice() on arrays)

T13 — Helper utilities:
  - findPlayer (throws on missing — invariant violation)
  - leftOf (next clockwise by seatIndex)
  - pendingAttackCardCount
  - clone (structuredClone wrapper)

T14 — TESTS — deck + shuffle:
  CREATE __tests__/deck.test.ts
    - 52 unique cards, 4 suits × 13 ranks
    - ids unique
  CREATE __tests__/shuffle.test.ts
    - shuffleDeck(d, 42) is reproducible (compare two runs)
    - shuffleDeck(d, 42) !== shuffleDeck(d, 43)
    - shuffleDeck preserves multiset (same 52 cards)
    - input deck is NOT mutated (frozen check)

T15 — TESTS — attack validation (all 9 cases from brief):
  CREATE __tests__/attack-validation.test.ts

T16 — TESTS — canBeat (all 8 cases from brief):
  CREATE __tests__/can-beat.test.ts

T17 — TESTS — submitAttack, submitBeat, stopDefending:
  CREATE __tests__/submit-attack.test.ts
  CREATE __tests__/submit-beat.test.ts
  CREATE __tests__/stop-defending.test.ts
    - cover full-defence counterattack
    - cover partial-defence rotation to leftOf(defender)
    - cover win on partial-defence with deck empty + 0 hand

T18 — TESTS — turn flow + endgame:
  CREATE __tests__/turn-flow.test.ts
  CREATE __tests__/check-win.test.ts
    - win only fires when deck.length === 0
    - dealer rotates clockwise across rounds

T19 — TESTS — views:
  CREATE __tests__/views.test.ts
    - createPublicView has no Card[] in opponents' hand
    - createPrivateView reveals only viewer's hand
    - mutating the returned view does not mutate state

T20 — TESTS — legal-actions:
  CREATE __tests__/legal-actions.test.ts
    - Stop is included whenever defender is awaiting
    - every returned Attack passes validateAttack

T21 — TESTS — property-based conservation:
  CREATE __tests__/conservation.property.test.ts
    - fast-check: for any sequence of legal actions, conservation holds
    - fast-check: no card duplication across (hands ∪ deck ∪ discard ∪ pendingAttack)
    - fast-check: hidden hands absent from createPublicView for non-viewers
    - fast-check: 1000 random legal sequences terminate

T22 — TESTS — integration:
  CREATE __tests__/integration.test.ts
    - scripted 3-player round to RoundEnded
    - scripted 4-player round to RoundEnded
    - full-defence → counterattack → wraps correctly
    - reconnection snapshot: createPrivateView is sufficient to resume

T23 — Simulation smoke:
  CREATE scripts/sim-smoke.ts
    - run 1000 random-legal-bot games
    - assert 0 conservation violations
    - assert 100% reach RoundEnded
    - measure mean turns/round (sanity, not balance)
    - exit non-zero on failure

T24 — Lint + type-check + test gate:
  - npm run typecheck (npx tsc --noEmit) → 0 errors
  - npm run lint (npx eslint src/) → 0 errors, 0 warnings
  - npm test (npx vitest run) → all green
  - npx tsx scripts/sim-smoke.ts → 0 violations
```

### Integration Points

```yaml
PACKAGE:
  - location proposal: "@lab/ll-CARDSHED/apps/core"
  - name: "@cardshed/core"
  - exports: src/core/index.ts (re-exports rules.ts + types.ts)
  - consumers: PRP 3's UI, AI, and simulation modules import from "@cardshed/core"

CONFIG:
  - tsconfig: strict, ES2022, bundler resolution, no DOM lib
  - eslint: forbid Math.random, Date.now, new Date, performance.now in src/core/**
  - vitest: includeSource for __tests__; reporters: default + junit (optional CI)

NO OTHER INTEGRATION POINTS:
  - No DATABASE — core is pure
  - No ROUTES — core is pure
  - No NETWORK — core is pure
```

---

## Validation Loop

### Level 1: Syntax & Style

```bash
cd @lab/ll-CARDSHED/apps/core
npm install
npx tsc --noEmit
npx eslint src/

# Expected: 0 errors, 0 warnings. If errors, READ the message and fix at the source.
# The ESLint config forbids Math.random / Date.now / new Date / performance.now
# inside src/core/** — any violation is a determinism bug, not a style nit.
```

### Level 2: Unit + Property Tests

```bash
cd @lab/ll-CARDSHED/apps/core
npx vitest run src/core

# Expected: every test in §"Test cases" below passes.
# Property-based tests run with { numRuns: 200 } minimum.
# A single failure on a property test produces a shrunken counterexample — record it,
# fix the bug, re-run; never widen the property to make red green.
```

### Level 3: Simulation Smoke

```bash
cd @lab/ll-CARDSHED/apps/core
npx tsx scripts/sim-smoke.ts

# Acceptance:
#   - completes in < 30 seconds on a developer laptop
#   - reports 0 conservation violations
#   - reports 100% of games reaching RoundEnded
#   - prints mean / p50 / p95 turns per round (sanity only; no thresholds)
# Failure modes:
#   - hang → infinite-loop in turn rotation; suspect leftOf or phase advance
#   - conservation drift → suspect stopDefending's discard accounting
#   - 0% RoundEnded → suspect checkWin never firing; verify deck exhaustion path
```

### Test cases (lifted from brief §"Test cases" — every one must be a Vitest `it()`)

**Deck & shuffle (`deck.test.ts`, `shuffle.test.ts`)**
- `createDeck` returns 52 unique cards (4 × 13).
- `shuffleDeck(d, 42)` is reproducible for the same seed.
- `shuffleDeck(d, 42)` differs from `shuffleDeck(d, 43)`.
- Bottom card (`deck[0]`) determines trump.
- Bottom trump card remains drawable (drawn last; no special exclusion).
- `shuffleDeck` does not mutate its input.

**Attack validation (`attack-validation.test.ts`)**
- 1-card attack → valid.
- 3-card with pair + kicker → valid.
- 5-card with two distinct pairs + kicker → valid.
- 0 / 2 / 4 / 6 card attack → `ATTACK_INVALID_SIZE`.
- 3-card no pair → `ATTACK_NO_PAIR`.
- 5-card with only one pair (e.g. trips + 2 unrelated) → `ATTACK_NO_TWO_PAIRS`.
- 5-card with same-rank quad as both pairs → `ATTACK_NO_TWO_PAIRS` (two **distinct** ranks required).
- Cards not in hand → `ATTACK_CARD_NOT_OWNED`.
- Duplicate card IDs → `ATTACK_DUPLICATE_CARD`.

**Defence (`can-beat.test.ts`)**
- Same suit, higher rank, non-trump attack → true.
- Same suit, lower rank, non-trump attack → false.
- Same suit, equal rank → false.
- Different non-trump suit (counter is non-trump) → false.
- Trump vs non-trump attack → true.
- Higher trump vs trump attack → true.
- Lower trump vs trump attack → false.
- Non-trump (different non-trump suit) vs trump attack → false.

**Turn flow (`submit-attack.test.ts`, `submit-beat.test.ts`, `stop-defending.test.ts`, `turn-flow.test.ts`)**
- Attacker sends 3-card, refills to 5, phase becomes `AwaitingDefense`.
- Defender beats one of three cards, stops → 2 unbeaten cards added to hand, defender refills to ≥ 5, next clockwise player becomes attacker.
- Defender beats all (full defence) → discards all, refills to 5, defender becomes attacker, must send next attack.
- Deck exhaustion: `drawToMinimum` stops, hand may end below 5.
- Win triggers only when end-of-turn hand size is 0 AND deck is empty.
- Dealer rotates clockwise on new round (`rotateDealer`).
- `submitAttack` rejects when `phase !== AwaitingAttack`.
- `submitAttack` rejects when caller is not the current attacker.
- `submitBeat` rejects when `phase` is neither `AwaitingDefense` nor `Resolving`.
- `submitBeat` rejects when `counter` cannot beat `attack`.

**Views (`views.test.ts`)**
- `createPublicView` has no `Card[]` in opponents' `hand` (only count).
- `createPublicView` has `deckCount` and `discardCount` (no order leak).
- `createPrivateView` reveals only the viewer's own hand.
- Mutating the returned `view.players[0].hand` does NOT mutate `state`.

**Legal actions (`legal-actions.test.ts`)**
- `getLegalActions` returns `Stop` whenever defender is awaiting.
- Every returned `Attack` action's `cardIds` passes `validateAttack`.
- Every returned `Beat` action satisfies `canBeat(attack, counter, trump)`.
- A wrong-phase or wrong-player call returns `[]`.

**Property-based (`conservation.property.test.ts`, ≥ 200 iters)**
- Card conservation: `Σ player.hand.length + deck.length + discard.length + pendingAttackCardCount(round.pendingAttack) === 52` across every legal action.
- No card duplication: the union of all card-locations contains exactly 52 distinct ids.
- Hidden hands: for any non-viewer, `createPublicView` omits their hand contents.
- Turn index validity: `attackerId` and `defenderId` always reference a real player.
- Termination: under random legal actions, every game reaches `RoundEnded` within a bounded number of turns (e.g. ≤ 500).

**Integration (`integration.test.ts`)**
- Complete 3-player round runs to `RoundEnded` under scripted actions.
- Complete 4-player round runs to `RoundEnded` under scripted actions.
- Full defence → counterattack → wraps correctly (defender's hand size, deck count, discard count all balance).
- Reconnection snapshot: `createPrivateView(state, viewerId)` is sufficient to resume — i.e. it includes everything the UI needs to render the current legal moves.

## Final Validation Checklist

- [ ] All tests pass: `npx vitest run src/core`
- [ ] No type errors: `npx tsc --noEmit`
- [ ] No lint errors: `npx eslint src/` (the no-`Math.random` rule must be active and passing)
- [ ] Simulation smoke passes: `npx tsx scripts/sim-smoke.ts` (1000 games, < 30s, 0 violations)
- [ ] Conservation invariant verified in property test (≥ 200 iters)
- [ ] `createPublicView` leaks no hidden hands (covered by `views.test.ts` and the property test)
- [ ] `shuffleDeck(d, 42)` returns the recorded fixture (deterministic across runs)
- [ ] No `Math.random` in `src/core/**` (`grep -R "Math.random" src/core` is empty)
- [ ] No `Date.now` / `new Date()` / `performance.now` in `src/core/**`
- [ ] No mutation of input `MatchState` (every reducer returns a fresh object; covered by an `Object.freeze` test wrapper)
- [ ] Every action either returns `{ ok: true, state, events }` or `{ ok: false, error }` — `grep -R "throw " src/core/rules.ts` returns only invariant-violation throws (`INVARIANT:` prefix)
- [ ] `TurnState` vocabulary matches the locked Shared Contract verbatim (no extra or renamed members)
- [ ] Shared Contract block in `types.ts` is byte-identical to PRP 3's
- [ ] All cross-PRP contradictions flagged at the top of this PRP have been reviewed by a human

---

## Anti-Patterns to Avoid (pure-logic core specific)

- ❌ **Throwing on validation errors.** Return `{ ok: false, error }`. Throws are reserved for INVARIANT violations (e.g. "deck exhausted during initial deal" — that's a programmer bug, not user input).
- ❌ **Mutating `state` in place.** Every reducer returns a fresh `MatchState` via `structuredClone` (or Immer if introduced — but `structuredClone` is enough).
- ❌ **Calling `Math.random()` anywhere outside `prng.ts`.** Bots, tests, and shuffles all go through `mulberry32(seed)`. ESLint enforces this.
- ❌ **Leaking hidden hands into `createPublicView`.** Opponent `hand` MUST be a count, not a `Card[]`.
- ❌ **Reshuffling the discard pile back into the deck.** Explicitly forbidden by Rules v2.0.
- ❌ **Inventing new rule variants.** CARD SHED v2.0 is frozen. Variant exploration belongs to PRP 3's simulation harness, behind an explicit `RuleVariant` flag — and is NOT this PRP's scope.
- ❌ **Allowing a win check before the refill attempt has run.** `checkWin` is always called *after* `drawToMinimum`. This is a one-line bug that costs hours to debug.
- ❌ **Coupling to UI, networking, analytics, or time.** Those live in PRP 3. The core does not import React, fetch, ws, console, or Date.
- ❌ **Diverging the Shared Contract from PRP 3.** Any change here requires a coordinated change to `PRPs/03-experience-distribution.md`.
- ❌ **In-place Fisher-Yates on the caller's deck.** Always shuffle a `.slice()`. Reducers do not mutate inputs.
- ❌ **Parsing `Card.id` to extract suit/rank.** The id is opaque; always read `card.suit` / `card.rank`.
- ❌ **Time-dependent behavior.** No timeouts, no `setTimeout`, no "default if undefined" branches that touch wall-clock time.
- ❌ **Hidden global state.** No module-level mutable variables in `src/core/**`. The engine is referentially transparent given `(state, action)`.

---

## Self-Scored Confidence

**8 / 10 for one-pass implementation success.**

Why 8 and not 10:
- The brief is unusually complete (frozen rules, frozen types, explicit pseudocode, explicit test list), which is what an 8 looks like — almost everything is decided.
- Two points withheld for the three real risks: (a) the `beatenPairs` custody ambiguity flagged at the top — if the human review resolves it differently from the proposed answer, the `stopDefending` + conservation property test both need a small refactor; (b) the partial-defence win-check edge case is not in the brief and may not match PRP 3's expectation if PRP 3 assumes win only fires on attacker turns; (c) `getLegalActions` for 5-card attacks has exponential potential and the brief is silent on whether to cap or deduplicate — the proposed plan caps via id-set dedup, which is defensible but not validated against a bot consumer yet.

Confidence rises to 9 if a human pre-resolves the three contradictions before execution starts.
