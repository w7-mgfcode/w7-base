# PRP 3 / 3 — CARD SHED Experience & Distribution

> **Layer:** I/O surface — everything that touches a user, another machine, or wall-clock time.
> **Output:** MVP build plan + UI/UX spec + WebSocket protocol + analytics taxonomy + AI bot design. **No rules logic.**
> **Sibling briefs (do NOT duplicate their scope):**
> - `PRPs/01-strategy-blueprint.md` — tech-stack + architecture decisions
> - `PRPs/02-deterministic-core.md` — pure rules engine + data models + tests
> **Parallel safe:** this brief embeds the Shared Contract (data model and rules-engine surface) verbatim, so it does not need PRP 2's output to start.

---

## Goal

Design the full **experience layer** around the deterministic core: the playable MVP, the visual + interaction design, the online-multiplayer transport, the analytics taxonomy, and the AI bot ladder. The work is **wrapping logic**, not authoring logic.

The deliverable is five tightly-coupled sub-artifacts in one PRP:

1. **MVP feature checklist + implementation milestones** (FU4)
2. **UI/UX specification with screens, table layout, interaction flows, juice roadmap** (FU5)
3. **WebSocket protocol with full client↔server message catalogue, JSON examples, room/reconnect/spectator flows** (FU3)
4. **Analytics event taxonomy + balance metric set + simulation harness** (FU6)
5. **AI bot ladder: Level 0 random, Level 1 heuristic, Level 2 information-set Monte Carlo** (FU7)

## Why

The deterministic core (PRP 2) is invisible without an experience layer. Players don't see `MatchState` — they see card animations, a turn timer, a "Send Attack" button, and an opponent's hand counter. The same core can ship as a hot-seat browser MVP, a networked multiplayer game, or a 100k-game simulation harness for balance work — but only if this layer is designed thoughtfully.

This PRP also separates the parts of "shipping a game" that **don't need rules expertise**, so it can run in parallel with PRP 2.

## What

### Success Criteria

- [ ] **MVP scope is locked**: feature checklist + 17 milestones + acceptance tests per milestone + estimated complexity + folder structure
- [ ] **Every screen in the screen inventory has a wireframe-level description** (no Stitch generation required for the PRP itself; PRP can defer to a follow-up Stitch session)
- [ ] **Every client-to-server and server-to-client message has a JSON schema + example payload + validation rules + error cases**
- [ ] **Every metric in the analytics list has a trigger, payload, privacy classification, and a balance hypothesis it answers**
- [ ] **AI Level 0/1/2 each have decision pseudocode, an evaluation function (where applicable), and a difficulty knob**
- [ ] **Reconnection, spectator, and async-play flows are fully described**
- [ ] **Out-of-scope items (rules logic, type definitions, architecture decisions) are explicitly deferred to PRP 1 and PRP 2 by reference**

---

## All Needed Context

### CARD SHED — Rules v2.0 (canonical summary)

3–4 players, 52-card deck, clockwise. Trump = suit of bottom card of shuffled deck. Attacker sends 1 / 3 (pair+kicker) / 5 (two distinct pairs + kicker) cards to left. Defender beats any number (non-trump → higher same-suit OR any trump; trump → higher trump only); beaten card + counter discard. Defender may stop at any time. **Full defence** → discard all, refill to 5, defender becomes attacker and must immediately send a new attack. **Partial/no defence** → unbeaten cards into defender's hand, refill to ≥5, next clockwise player becomes attacker. After every turn, attacker/defender refill to 5 *if the deck has cards*. No reshuffles. Once the deck is empty, hands may shrink below 5 and a win becomes possible: end-of-turn hand size 0 + deck empty = round win. Dealer rotates clockwise per round.

### Shared Contract (frozen — must match PRP 2 verbatim)

```ts
export type Suit = 0 | 1 | 2 | 3;
export type Rank = 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14;

export interface Card { id: string; suit: Suit; rank: Rank; }

export type TurnState =
  | "Dealing"
  | "AwaitingAttack"
  | "AwaitingDefense"
  | "Resolving"
  | "RoundEnded"
  | "MatchEnded";

export type ValidationError = { code: string; message: string; details?: unknown };

export type ActionResult<T = unknown> =
  | { ok: true; state: MatchState; events: GameEvent[]; value?: T }
  | { ok: false; error: ValidationError };
```

This block is **identical** to the corresponding section in `02-deterministic-core.md`. If you change one, change both.

### Rules-engine surface this layer calls (PRP 2 owns the implementation)

```ts
createDeck() / shuffleDeck(deck, seed?) / dealInitialHands(deck, n)
startNewRound(prev?, seed?)
validateAttack(cards, hand)
submitAttack(state, playerId, cardIds)
canBeat(attack, counter, trump)
submitBeat(state, defenderId, attackCardId, counterCardId)
stopDefending(state, defenderId)
checkWin(state, playerId)
getLegalActions(state, playerId)     // for AI/highlighting
createPublicView(state, viewerId?)
createPrivateView(state, viewerId)
```

Treat these as a black box. If a need arises that this API doesn't satisfy, **flag it back to PRP 2 in a "Core API extensions requested" section** — do not paper over it in the experience layer.

---

## Scope IN this PRP

### Sub-deliverable A — MVP Implementation Plan (FU4 + Master §2)

Target: local hot-seat browser game, TypeScript + React **or** TypeScript + Svelte (pick one with justification). No backend.

Required features:
- Random card dealing
- Trump selection from bottom card
- 3–4 local players, pass-and-play / hot-seat
- Attacker sends 1, 3, or 5 cards with combo validation
- Defender beats / stops voluntarily
- Full-defence counterattack flow
- Partial / no-defence flow
- Refill rules, deck exhaustion
- Win detection + round reset + dealer rotation
- Simple text or sprite-based cards
- Illegal-move rejection with clear error messages

Excluded: AI, online, animation, audio, accounts, cosmetics, IAP.

Output: feature checklist, 17 milestones with goal/files/functions/acceptance tests/common bugs/suggested tests, recommended folder structure, suggested implementation order, complexity estimate per milestone.

### Sub-deliverable B — UI/UX Specification (FU5 + Master §4)

Screens: Main menu / Player setup / New-round setup / Game table / Pass-and-play privacy screen / Attack selection / Defence selection / Round result / Match result / Settings / Rules-help / *(later)* online lobby / *(later)* reconnect screen / *(later)* spectator view.

Table requirements: player names, current attacker, current defender, current acting player, opponent hand counts, deck count, discard count, trump suit, current phase, pending attack cards, beaten pairs, player hand, legal-move highlights, error messages, action buttons.

Interaction flows: attacker card selection (with live valid/invalid preview), defender card-pair beat selection, defender stop, full-defence transition feedback, partial-defence transition, pass-and-play privacy, win / round-reset.

Card visual states: normal / hovered / selected / legal / illegal / disabled / trump / recently-played / discarding / face-down.

Accessibility: colorblind-safe suit display, keyboard navigation, screen-reader labels, touch-friendly tap targets, mobile hand scrolling.

Juice roadmap (post-MVP): deal animation, card slide, discard animation, full-defence flourish, trump reveal animation, deck-exhaustion warning, victory animation, subtle SFX, haptics.

Layouts: desktop / tablet / mobile portrait / mobile landscape.

### Sub-deliverable C — Networking Protocol (FU3 + Master §5)

Transport: WebSocket for browser. Compare WebSocket / raw TCP / WebRTC / HTTP polling and recommend.

Room system: create, code generation, join, leave, seat assignment, ready checks, start, lifecycle, inactive cleanup.

Message catalogue — for each message: direction, JSON schema, required + optional fields, validation rules, example payload, error cases:
- **Client→Server**: `CreateRoom, JoinRoom, LeaveRoom, ReadyUp, StartGame, SubmitAttack, SubmitBeat, StopDefending, RequestSnapshot, Reconnect, SendEmote, Resign`
- **Server→Client**: `RoomCreated, RoomJoined, PlayerJoined, PlayerLeft, ReadyStateChanged, GameStarted, Snapshot, PrivateSnapshot, PublicStateUpdated, ActionAccepted, ActionRejected, AttackSubmitted, CardBeaten, DefenseEnded, TurnChanged, RoundEnded, MatchEnded, PlayerDisconnected, PlayerReconnected, SpectatorJoined, Error`

Cross-cutting concerns: room-code generation rules, reconnection token, sequence numbers, idempotency keys, server tick / event counter, snapshot versioning, rate limiting, spectator permissions (public vs hidden info), turn-timer message flow, reconnect flow, disconnect handling, bot-replacement fallback.

Turn timers: soft / hard / auto-action / extension / async-friendly variant.

Async play (Words-With-Friends style): long timers, push notifications, persistent state, action history, resignation, inactive-player handling.

### Sub-deliverable D — Analytics & Simulation (FU6 + Master §3)

Event taxonomy — for each: name, trigger, payload, JSON example, privacy class, replay-relevance, analytics-relevance:
`RoundStarted, TrumpSelected, CardsDealt, TurnStarted, AttackSubmitted, AttackRejected, BeatSubmitted, BeatRejected, DefenseStopped, FullDefenseAchieved, PartialDefenseResolved, CardsDrawn, DeckExhausted, PlayerHandSizeChanged, RoundWon, RoundEnded, IllegalActionAttempted`

Metrics: avg turns/round, round length distribution, attack-size frequency (1/3/5), full-defence rate, partial-defence rate, no-defence rate, trump use rate, rank usage heatmap, suit usage heatmap, avg hand size by turn, hand size at victory, win-rate by seat / dealer / starting-attacker, deck-exhaustion turn, illegal-move rate.

Export formats: CSV (metrics), JSONL (event log), replay log.

Simulation harness: random AI sim runner, heuristic AI sim runner, statistical report generator. Each bot drives `submitAttack` / `submitBeat` / `stopDefending` via the rules engine (PRP 2) and emits the analytics event stream.

Balance questions to answer with the analytics:
- Are 5-card attacks too rare?
- Does the starting attacker have too much advantage?
- Does full defence chain too often?
- Are trump cards too powerful?
- Are low cards dead weight?
- Does the game drag after deck exhaustion?
- Does 3-player feel different from 4-player?

Plus optional rule variants to A/B with the simulator: low-card powers, forced defence, trump rotation, max hand size, full-defence bonus, trump-counter restrictions. **All variants marked clearly as optional — they are not part of v2.0.**

### Sub-deliverable E — AI Opponents (FU7 + Master §6)

**Level 0 — Random Legal**: random valid attack from `getLegalActions`, random legal beat, random stop decision. Use cases: stress testing, sim, MVP filler.

**Level 1 — Heuristic.**
Attack: prefer 5-card when hand large, 3-card when pairs available, low singles when deck full, preserve trumps for defence, in endgame shed maximum.
Defence: beat low-cost attacks with minimal legal counter, avoid wasting high trumps early, choose to take cards if it improves future combo, fully defend if it creates a strong counterattack, in endgame prioritize hand-size reduction.

**Level 2 — Monte Carlo / Information-Set.**
- Information-set construction (what's known: own hand, trump, discard pile, opponent hand counts; what's unknown: opponents' specific cards, deck order)
- Unknown-card sampling: deal opponents random consistent hands from the unknown-card pool
- Opponent-hand inference (Bayesian update from observed plays)
- Rollout policy (Level 1 as the rollout default)
- Evaluation function (hand size / deck size / trump count / high-card count / pair availability / current attack pressure / distance to deck exhaustion / chance of full defence / seat position)
- Time budget (e.g. 500ms per decision)
- Branch pruning
- Risk management
- Endgame-specific strategy

Difficulty knobs: rollout count, eval-function weights, mistake injection rate. Document how the AI plugs into the disconnected-player bot-replacement flow from sub-deliverable C.

### Scope OUT (belongs to siblings)

- Tech-stack justification → PRP 1
- Module separation diagram → PRP 1
- Server-authoritative state-sync model → PRP 1 (this PRP picks up its message catalogue from there)
- Card type, deck shuffle, rule validators, win check → PRP 2
- Unit tests for the rules → PRP 2

---

## Implementation Blueprint (sketch only — full code lives in downstream tasks)

### MVP folder structure (TS + React variant)

```
src/
├── core/                  # OWNED BY PRP 2 — do not author here
├── ui/
│   ├── App.tsx
│   ├── screens/
│   │   ├── MainMenu.tsx
│   │   ├── PlayerSetup.tsx
│   │   ├── Table.tsx
│   │   ├── Privacy.tsx
│   │   ├── AttackSelect.tsx
│   │   ├── DefenseSelect.tsx
│   │   ├── RoundResult.tsx
│   │   └── MatchResult.tsx
│   ├── components/
│   │   ├── Card.tsx
│   │   ├── Hand.tsx
│   │   ├── OpponentBar.tsx
│   │   ├── TrumpIndicator.tsx
│   │   ├── PendingAttackPanel.tsx
│   │   └── ActionButton.tsx
│   ├── state/             # local store (e.g. Zustand) wrapping core MatchState
│   └── lib/cn.ts
├── analytics/
│   ├── events.ts          # event types
│   ├── logger.ts          # console + JSONL sink
│   └── report.ts          # CSV/HTML reports
├── ai/
│   ├── level0-random.ts
│   ├── level1-heuristic.ts
│   └── level2-ismcts.ts
├── net/                   # ONLINE PHASE ONLY — stubs in MVP
│   ├── protocol.ts        # message types
│   └── client.ts          # WebSocket wrapper
└── sim/
    └── runner.ts          # bot-vs-bot simulation harness
```

### Message-protocol sketch (one example — full catalogue in PRP output)

```jsonc
// Client → Server: SubmitAttack
{
  "type": "SubmitAttack",
  "seq": 42,                    // monotonic per client
  "idempotencyKey": "uuid-...", // safe to retry
  "roomId": "RM-7K3",
  "playerId": "p1",
  "cardIds": ["S-14-abc", "H-14-def", "C-9-ghi"]
}

// Server → Client: ActionAccepted + AttackSubmitted broadcast
{
  "type": "ActionAccepted",
  "ack": 42,
  "eventCounter": 117
}
{
  "type": "AttackSubmitted",
  "eventCounter": 117,
  "attackerId": "p1",
  "cardIds": ["S-14-abc", "H-14-def", "C-9-ghi"],
  "defenderId": "p2",
  "trumpSuit": 3
}

// Server → Client: ActionRejected example
{
  "type": "ActionRejected",
  "ack": 42,
  "error": { "code": "ATTACK_NO_PAIR", "message": "3-card attack must contain a pair." }
}
```

## Validation Loop

### Level 1: Coherence

- [ ] Every screen in §B has a parent state in `TurnState` (no orphan UI)
- [ ] Every server-to-client message has a matching event in the analytics taxonomy where appropriate
- [ ] Every AI level can be implemented exclusively through the **Rules-engine surface** declared above — no AI reaches into core internals
- [ ] Reconnection flow's `PrivateSnapshot` payload matches the output of `createPrivateView` from PRP 2

### Level 2: Cross-PRP consistency

- [ ] Shared Contract block is byte-identical to PRP 2's
- [ ] Card-ID format used in message examples matches PRP 2's `Card.id` shape
- [ ] No invention of rules engine functions not already on the API surface (if needed: list in "Core API extensions requested")

### Level 3: Build-readiness

- [ ] MVP milestone 1 has an executable acceptance test that doesn't require any core function PRP 2 isn't producing
- [ ] Simulation harness can run with Level 0 bots only (no Level 1+ dependency) for the first balance smoke
- [ ] Analytics events can be emitted purely by observing the `GameEvent` stream PRP 2's `submitAttack` / `submitBeat` / `stopDefending` return

## Anti-Patterns to Avoid

- ❌ Reimplementing any rule (combo validation, beat legality, win check) in the UI or in the network layer — call PRP 2.
- ❌ Trusting the client. The server must re-validate every action via the rules engine before broadcasting.
- ❌ Sending the full `MatchState` (including hidden hands and deck order) to clients. Always use `createPublicView` / `createPrivateView`.
- ❌ Designing AI with perfect information. CARD SHED has hidden hands; Level 2 must sample.
- ❌ Folding analytics into game logic. The engine emits `GameEvent`s; the analytics layer subscribes.
- ❌ Inventing rule variants outside the explicit "(optional)" section of sub-deliverable D.
- ❌ Adding screens not derivable from the rules (no leaderboards, no profile pages — MVP only).
- ❌ Drifting the Shared Contract from `02-deterministic-core.md`.
