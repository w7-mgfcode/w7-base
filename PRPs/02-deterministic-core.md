# PRP 2 / 3 — CARD SHED Deterministic Core

> **Layer:** Pure logic.
> **Output:** TypeScript data models + a pure rules engine module + a Vitest test suite. **No UI, no network, no I/O, no time.**
> **Sibling briefs (do NOT duplicate their scope):**
> - `PRPs/01-strategy-blueprint.md` — tech-stack + architecture decisions
> - `PRPs/03-experience-distribution.md` — MVP/UI/Networking/AI/Analytics
> **Parallel safe:** this brief embeds the rules and the data-model contract verbatim, so it does not need PRP 1's output to start.

---

## Goal

Build the **deterministic core** of CARD SHED: a pure, side-effect-free TypeScript module that encodes the v2.0 rules. Given a `MatchState` and a player `Action`, the core returns the next `MatchState` plus a list of emitted `GameEvent`s, or a structured `ValidationError`. Plus a Vitest suite that proves it.

The deliverable is:

1. A `src/core/types.ts` declaring every data structure
2. A `src/core/rules.ts` implementing every rule function
3. A `src/core/__tests__/*.test.ts` Vitest suite covering correctness, edge cases, and conservation invariants

## Why

The rules engine is the **truth machine** of CARD SHED. Everything else — UI, networking, AI, analytics — is a transformation over its state or its event stream. If the core is wrong, the whole game is wrong. If the core is impure, replay, anti-cheat, and bot simulation all break.

Building this layer first (and independently of UI/networking) lets PRP 3 wrap a black box with a stable interface, and lets bot simulators in PRP 3 generate millions of games for balance analytics.

## What

### Success Criteria

- [ ] All types defined in `src/core/types.ts` are referenced from `rules.ts` and exported.
- [ ] Every rule function listed in the **Rules Engine API** section is implemented and unit-tested.
- [ ] **Card conservation invariant**: `sum(hands) + deck + discard + pendingAttack === 52` at every state transition.
- [ ] **No hidden-info leak**: `createPublicView(state, playerId)` strips opponents' hand contents and the deck order.
- [ ] **Deterministic shuffling**: `shuffleDeck(seed)` is reproducible given the same seed.
- [ ] **All Vitest tests in §"Test cases" pass.**
- [ ] **No mutation of input state** — every reducer returns a new `MatchState`.
- [ ] **Every action either succeeds with `{ok: true, state, events}` or fails with `{ok: false, error: {code, message}}`. No throws on validation errors.**

---

## All Needed Context

### CARD SHED — Rules v2.0 (canonical)

**Objective.** Be the first to end your turn with zero cards. Because players refill to 5 while the deck has cards, winning is only possible after the deck is empty.

**Ranks.** 2 < 3 < 4 < 5 < 6 < 7 < 8 < 9 < 10 < J(11) < Q(12) < K(13) < A(14). Four suits: Clubs(0), Diamonds(1), Hearts(2), Spades(3).

**Trump.** Bottom card of shuffled deck declared trump; remains in deck and is drawn normally when its turn comes. Any trump beats any non-trump; trumps compare by rank.

**Attacker turn.** Send exactly one of:
- 1 card (any)
- 3 cards: pair (same rank) + 1 kicker
- 5 cards: two pairs of *different* ranks + 1 kicker

Refill to 5 from deck if hand < 5 (deck-permitting). Win check: hand size 0 *after* refill attempt (only possible when deck empty) → win.

**Defender turn.** Beat any number of received cards, in any order:
- Non-trump beatable by same-suit higher rank OR any trump.
- Trump beatable only by higher trump.
- Beaten card + counter → discard. Defender may stop at any time.

After defending:
- **Full defence**: discard all, draw to 5, Defender immediately becomes Attacker and must send a fresh attack.
- **Partial / no defence**: unbeaten cards → Defender's hand, draw to ≥5 if deck allows, next clockwise player becomes Attacker.

**Endgame.** No reshuffles. Players may end with <5 once deck is empty. Win = end-of-turn hand size 0.

**New round.** Record winner, rotate dealer clockwise, gather + reshuffle, new bottom-card trump, deal 5.

### Scope IN this PRP

- **Master §7 Rules Engine Requirements** — all six functions: `validateAttack`, `canBeat`, `resolveBeat`, `endDefense`, `drawToMinimum`, `checkWin`.
- **Master §8 Testing Strategy** — unit, integration, property-based, simulation.
- **FU1 Data Models** — complete TypeScript interfaces, plus Rust struct equivalents as a parallel section.
- **FU2 Rules Engine** — full implementation: `createDeck`, `shuffleDeck(seed?)`, `dealInitialHands`, `determineTrumpFromBottomCard`, `validateAttack`, `submitAttack`, `canBeat`, `submitBeat`, `stopDefending`, `drawToFive`, `checkWin`, `advanceTurnAfterPartialDefense`, `advanceTurnAfterFullDefense`, `startNewRound`, `rotateDealer`.
- **FU8 Test Cases** — Vitest suite covering deck, attack validation, defence validation, turn flow, invariants.

### Scope OUT (belongs to siblings)

- Tech-stack justification → PRP 1
- Architecture diagrams / module separation → PRP 1
- UI rendering / interaction → PRP 3
- WebSocket protocol → PRP 3
- Analytics event emission *into a sink* (the engine emits `GameEvent`s; analytics is the wiring) → PRP 3
- AI bot decision functions → PRP 3 (but the engine MUST expose a `getLegalActions(state, playerId)` helper so PRP 3 can build bots — include it)
- MVP UI build plan → PRP 3

### Shared Contract (do NOT diverge from this — siblings depend on it)

```ts
// Suit and Rank encoding — frozen across all three PRPs
export type Suit = 0 | 1 | 2 | 3;   // Clubs, Diamonds, Hearts, Spades
export type Rank = 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14;

export interface Card {
  id: string;          // immutable per card instance (e.g. "S-14-uuid")
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

This block is **identical** to the corresponding section in `03-experience-distribution.md`. If you change one, change both.

### Rules Engine API (the surface PRP 3 will call)

```ts
// Pure deterministic functions — no I/O, no Math.random unless seeded
createDeck(): Card[]
shuffleDeck(deck: Card[], seed?: number): Card[]
dealInitialHands(deck: Card[], playerCount: 3 | 4): { hands: Card[][]; deck: Card[] }
determineTrumpFromBottomCard(deck: Card[]): Suit
startNewRound(prev: MatchState | null, seed?: number): MatchState

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

getLegalActions(state: MatchState, playerId: string): Action[]   // for bots/tests
createPublicView(state: MatchState, viewerId?: string): PublicGameView
createPrivateView(state: MatchState, viewerId: string): PrivatePlayerView
```

## Implementation Blueprint

### Data models

Define in `src/core/types.ts`:

- `Card`, `Suit`, `Rank` (from Shared Contract above)
- `Player` — `{id, name, hand: Card[], score: number, isActive: boolean, seatIndex: number}`
- `Deck` — typed as `Card[]` with helper accessors `peekBottom`, `drawTop`
- `PendingAttack` — `{attackerId, defenderId, unbeatenCards: Card[], beatenPairs: {attack: Card; counter: Card}[]}`
- `DiscardPile` — `Card[]` (face-down; rendered as count for clients)
- `RoundState` — `{trump: Suit, dealerId: string, attackerId: string, defenderId: string | null, phase: TurnState, pendingAttack: PendingAttack | null}`
- `MatchState` — `{matchId, roundNumber, players: Player[], deck: Card[], discard: Card[], round: RoundState, winner: string | null}`
- `Action` — discriminated union of attack/beat/stop submissions
- `GameEvent` — discriminated union: `RoundStarted | TrumpSelected | CardsDealt | AttackSubmitted | CardBeaten | DefenseStopped | FullDefense | CardsDrawn | TurnChanged | RoundWon | MatchEnded`
- `PublicGameView` — opponents' hands replaced by counts, deck reduced to count, discard reduced to count
- `PrivatePlayerView` — viewer's hand revealed; everything else as `PublicGameView`

### Per-function pseudocode

```
// validateAttack(cards, playerHand)
// PATTERN: pure, returns structured error
function validateAttack(cards, hand) {
  if cards.length not in {1, 3, 5} → error ATTACK_INVALID_SIZE
  if any cardId not in hand → error ATTACK_CARD_NOT_OWNED
  if duplicate cardIds → error ATTACK_DUPLICATE_CARD
  if cards.length === 1 → ok
  group by rank
  if cards.length === 3 → must have at least one rank with count ≥ 2 → else ATTACK_NO_PAIR
  if cards.length === 5 → must have at least two distinct ranks with count ≥ 2 → else ATTACK_NO_TWO_PAIRS
  ok
}

// canBeat(attack, counter, trump)
// CRITICAL: non-trump cannot beat trump regardless of rank
if attack.suit === trump → return counter.suit === trump && counter.rank > attack.rank
else                     → return (counter.suit === attack.suit && counter.rank > attack.rank)
                              || (counter.suit === trump)

// submitAttack(state, playerId, cardIds)
// PATTERN: validate → mutate-immutably → emit events → advance phase
require state.round.phase === AwaitingAttack
require state.round.attackerId === playerId
let cards = cardIds.map(id => find in attacker.hand)
validateAttack(cards, attacker.hand) → propagate error
remove cards from attacker.hand
state.round.pendingAttack = { attackerId, defenderId: leftOf(attackerId), unbeatenCards: cards, beatenPairs: [] }
{hand, deck} = drawToMinimum(attacker.hand, state.deck, 5)
attacker.hand = hand
state.deck = deck
if checkWin(state, attackerId) → emit RoundWon → phase = RoundEnded → return ok
emit AttackSubmitted
state.round.phase = AwaitingDefense
state.round.defenderId = pendingAttack.defenderId
emit TurnChanged
return ok

// stopDefending(state, defenderId)
require state.round.phase in {AwaitingDefense, Resolving}
require defenderId === state.round.defenderId
let pa = state.round.pendingAttack
if pa.unbeatenCards.length === 0:
    // FULL DEFENCE
    move all beatenPairs flat → discard (already there, no-op)
    {hand, deck} = drawToMinimum(defender.hand, state.deck, 5)
    state.round.attackerId = defenderId       // counterattack
    state.round.defenderId = null
    state.round.pendingAttack = null
    state.round.phase = AwaitingAttack
    emit FullDefense, CardsDrawn, TurnChanged
else:
    // PARTIAL / NO DEFENCE
    defender.hand.push(...pa.unbeatenCards)
    {hand, deck} = drawToMinimum(defender.hand, state.deck, 5)
    state.round.attackerId = leftOf(defenderId)
    state.round.defenderId = null
    state.round.pendingAttack = null
    state.round.phase = AwaitingAttack
    emit DefenseStopped, CardsDrawn, TurnChanged

// drawToMinimum(hand, deck, target = 5)
// CRITICAL: never reshuffle; never draw past deck.length
while hand.length < target and deck.length > 0:
    hand.push(deck.pop())  // top of deck
return {hand, deck}

// checkWin(state, playerId)
// CRITICAL: must be called AFTER refill attempt
return state.deck.length === 0 && player.hand.length === 0
```

### Test cases (Vitest)

Group under `src/core/__tests__/`:

**Deck & shuffle**
- `createDeck` returns 52 unique cards (4 × 13)
- `shuffleDeck(d, 42)` is reproducible for the same seed
- Bottom card determines trump
- Bottom trump card remains drawable (no special exclusion)

**Attack validation**
- 1-card attack → valid
- 3-card with pair + kicker → valid
- 5-card with two distinct pairs + kicker → valid
- 0/2/4/6 card attack → invalid (`ATTACK_INVALID_SIZE`)
- 3-card no pair → `ATTACK_NO_PAIR`
- 5-card with only one pair (e.g. trips + 2 unrelated) → `ATTACK_NO_TWO_PAIRS`
- 5-card with same-rank quad as both pairs → `ATTACK_NO_TWO_PAIRS` (two **distinct** ranks required)
- Cards not in hand → `ATTACK_CARD_NOT_OWNED`
- Duplicate card IDs → `ATTACK_DUPLICATE_CARD`

**Defence (canBeat)**
- Same suit, higher rank, non-trump attack → true
- Same suit, lower rank, non-trump attack → false
- Same suit, equal rank → false
- Different non-trump suit → false
- Trump vs non-trump → true
- Higher trump vs trump → true
- Lower trump vs trump → false
- Non-trump vs trump → false

**Turn flow**
- Attacker sends 3-card, refills to 5, phase = AwaitingDefense
- Defender beats one of three cards, stops → 2 cards added to hand, refills to 5+, next clockwise player becomes Attacker
- Defender beats all (full defence) → discards all, refills to 5, becomes Attacker, must send next attack
- Deck exhaustion: drawToMinimum stops, hand may end below 5
- Win triggers only when end-of-turn hand size is 0 AND deck is empty
- Dealer rotates clockwise on new round

**Property-based (use `fast-check` or fast-check-style oracle)**
- Card conservation: `sum(hands) + deck + discard + sum(pendingAttack)` = 52 across every legal action
- No card duplication across all locations
- Hidden hands are absent from `createPublicView` for non-viewers
- Turn index is always a valid player seat
- Game eventually progresses under random legal actions (no infinite loops with deck ≤ N)

**Integration**
- Complete 3-player round runs to RoundEnded under scripted actions
- Complete 4-player round runs to RoundEnded under scripted actions
- Full defence → counterattack → wraps correctly
- Reconnection snapshot: `createPrivateView(state, viewerId)` is sufficient to resume

## Validation Loop

### Level 1: Type & Lint

```bash
cd <project>
npx tsc --noEmit
npx eslint src/core
```

### Level 2: Unit + Property tests

```bash
npx vitest run src/core
```

Every test described above must pass. Property-based tests run with at least 200 iterations each.

### Level 3: Simulation smoke

```bash
# A 1000-game random-legal-bot simulation must complete in <30s and report:
# - 0 invariant violations
# - 100% of games reach RoundEnded
# - Mean turns per round within plausible bounds (sanity, not balance)
npx tsx scripts/sim-smoke.ts
```

## Anti-Patterns to Avoid

- ❌ Throwing on validation errors — return `{ok: false, error}`.
- ❌ Mutating `state` in place — every reducer returns a fresh object (Immer / structural sharing acceptable).
- ❌ Calling `Math.random()` anywhere outside a seeded shuffle helper.
- ❌ Leaking hidden hands into `createPublicView`.
- ❌ Reshuffling the discard pile back into the deck — explicitly forbidden by the rules.
- ❌ Inventing new rule variants. CARD SHED v2.0 is frozen.
- ❌ Allowing a win check before the refill attempt has run.
- ❌ Coupling to UI, networking, or analytics — those live in PRP 3.
- ❌ Diverging the Shared Contract from `03-experience-distribution.md`.
