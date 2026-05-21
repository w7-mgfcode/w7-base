# Core Determinism — MANDATORY for `apps/core/`

> **Load-bearing.** The rules engine is the *truth machine*. If purity breaks, replay breaks, anti-cheat breaks, bot simulation breaks, and online clients desync. This rule encodes the PRP 2 success criteria as a permanent guardrail.

This rule applies to **every file under `@lab/ll-CARDSHED/apps/core/src/core/`**. It does NOT apply to `apps/ui/`, `apps/server/`, `scripts/`, or tests.

---

## 1. Forbidden in `src/core/**`

The following are **banned**, enforced by ESLint:

- `Math.random()` — randomness goes through `prng.mulberry32(seed)`.
- `Date.now()`, `new Date()`, `performance.now()` — the engine has no concept of wall-clock time. Timestamps belong to PRP 3's event emitter.
- `crypto.getRandomValues()` — same reason as `Math.random`; the seed source lives outside core.
- `setTimeout`, `setInterval`, `requestAnimationFrame` — the engine is synchronous.
- `console.*` — emit events via the `GameEvent` union, not log lines.
- `fetch`, `XMLHttpRequest`, `WebSocket`, `fs`, `child_process`, `process.env` — no I/O.
- Module-level mutable state — every reducer derives next-state from inputs only.

The only exception: `prng.ts` itself uses `Math.imul` (a math operation, not randomness). It does NOT call `Math.random`.

---

## 2. Required patterns

### 2.1 Errors are values

Validation failures MUST return `{ ok: false, error: { code, message, details? } }`. Throws are reserved for **invariant violations** — programmer bugs that should crash the process so the test suite catches them.

```ts
// CORRECT — user-facing validation
return { ok: false, error: { code: "ATTACK_INVALID_SIZE", message: "..." } };

// CORRECT — invariant (cannot happen if the engine is correct)
if (!c) throw new Error("INVARIANT: deck exhausted during initial deal");

// WRONG — throwing on user input
if (cards.length !== 1 && cards.length !== 3 && cards.length !== 5) {
  throw new Error("Invalid attack size");  // ❌ should return ok:false
}
```

### 2.2 Pure reducers

Every state-mutating function MUST return a fresh `MatchState`. The input is treated as read-only.

```ts
// CORRECT
function submitAttack(state: MatchState, ...): ActionResult {
  const next = structuredClone(state);  // or .slice() per array
  // ...mutate next, never state
  return { ok: true, state: next, events };
}

// WRONG
function submitAttack(state: MatchState, ...): ActionResult {
  state.round.phase = "AwaitingDefense";  // ❌ mutates input
  return { ok: true, state, events };
}
```

### 2.3 Seeded randomness only

`shuffleDeck(deck, seed)` is the **only** randomness entry-point. The `seed` parameter is REQUIRED (per PRP 3 NEW #6). Same seed in → byte-identical permutation out, on every JS runtime.

```ts
// CORRECT
const shuffled = shuffleDeck(deck, matchState.rngSeed);

// WRONG
const shuffled = deck.slice().sort(() => Math.random() - 0.5);  // ❌ ban
```

### 2.4 Hidden information is law

`createPublicView(state, viewerId?)` MUST NOT leak opponent hand contents or deck order. `createPrivateView(state, viewerId)` reveals only the viewer's own hand.

```ts
// CORRECT
players: state.players.map((p) => ({
  ...,
  hand: { ownerId: p.id, count: p.hand.length, publiclyKnown: [] },
}))

// WRONG
players: state.players.map((p) => ({ ..., hand: p.hand }))  // ❌ leaks
```

### 2.5 Card.id is opaque

Consumers MUST use `card.suit` and `card.rank` for game logic. Never parse `card.id` to extract them. The id format is presentational and may change.

```ts
// CORRECT
if (card.suit === trump && card.rank > attack.rank) return true;

// WRONG
const [suit, rank] = card.id.split("-");  // ❌ never
```

---

## 3. Conservation invariant

Across every legal state transition, exactly 52 cards must be accounted for:

```
sum(player.hand.length) + deck.length + discard.length + pendingAttackCardCount(round.pendingAttack) === 52
```

The property test `conservation.property.test.ts` enforces this across ≥200 random-legal-action sequences. **Any change that breaks this invariant is a bug — never widen the property to make red green.**

---

## 4. Win-check ordering

`checkWin(state, playerId)` MUST run **after** `drawToMinimum` in every refill path. A player at 0 cards with a non-empty deck will be refilled to 5 and is NOT a winner.

`checkWin` MUST run on BOTH the full-defence and partial-defence branches of `stopDefending` (per PRP 2 #3) — a defender CAN win on the trailing edge of a round.

---

## 5. No reshuffles

Once `deck.length === 0`, draws stop. The discard pile NEVER goes back into the deck. This is Rules v2.0 and is non-negotiable.

---

## 6. When adding new functions

1. Add the type signature to the Rules Engine API in `src/core/index.ts` exports.
2. Write the test FIRST under `src/core/__tests__/<function>.test.ts`.
3. Implement the function with `structuredClone` for any state derivation.
4. Confirm the function returns `ActionResult` (or a pure value type) — never `void`, never `throw` on user input.
5. Re-run the property test `conservation.property.test.ts` to confirm the invariant still holds.
6. Re-run `sim-smoke.ts` (1000 games) to confirm no regressions.

---

## 7. Validation

These commands MUST pass on every PR that touches `apps/core/`:

```bash
cd @lab/ll-CARDSHED/apps/core
npm run typecheck    # 0 errors
npm run lint         # 0 errors, 0 warnings (the no-Math.random rule must be active)
npm test             # all 82+ tests pass
npm run sim-smoke    # 1000 games, <30s, 0 conservation violations
```

If any of these go red, the engine is broken until they're green — no exceptions, no skip-failing-test commits.

---

## 8. Why this rule exists

The deterministic core is what lets us:

- **Replay any match** from `(matchSeed, actions[])` — bug reproduction, balance analysis, anti-cheat audit.
- **Run millions of bot-vs-bot games** for balance metrics — only possible because the engine has zero I/O.
- **Mechanically port to Rust** for the online server (PRP 1 §2.3) — the TS implementation is the canonical spec; non-deterministic JS hides in plain sight when ported.
- **Trust client-side legal-action highlighting** — the client and server agree because both run the same engine.

One `Math.random()` slip in this layer breaks all four. The rule is mechanical because the consequence is invisible until it bites.
