# PRP 1 / 3 — CARD SHED Strategy & Blueprint

> **Layer:** Strategy.
> **Output:** A decisions document — tech-stack choice, system architecture, deliverables outline. **No production code, no concrete data structures.** PRPs 2 and 3 will consume the choices made here.
> **Sibling briefs (do NOT duplicate their scope):**
> - `PRPs/02-deterministic-core.md` — pure rules engine + data models + tests (TypeScript)
> - `PRPs/03-experience-distribution.md` — MVP/UI/Networking/AI/Analytics

---

## Goal

Produce a complete technical **blueprint** for CARD SHED: a 3–4-player turn-based shedding card game using a standard 52-card deck with a shifting trump suit. The blueprint is the load-bearing planning artifact that downstream implementation PRPs will follow.

The blueprint must:

- Lock the backend tech stack (Rust **or** Go, with justified choice)
- Lock the frontend stack (one of: TS+React, TS+Svelte, TS+PixiJS, Godot, Unity)
- Diagram the modular separation of concerns
- Define the server-authoritative synchronization model
- Outline the 20-section deliverable structure other PRPs will fill in

The blueprint must **not**:

- Write production code (only pseudocode / type-shape sketches where they clarify a decision)
- Specify the rules engine internals — that belongs to PRP 2
- Specify UI screens, networking message bodies, or AI evaluation functions — those belong to PRP 3

## Why

CARD SHED's first implementation target is a **local hot-seat browser MVP** (TypeScript frontend, no backend). The architecture must remain compatible with a later evolution to **online multiplayer with a Rust or Go server**. Locking the architecture now prevents costly rewrites when the project crosses from local to networked, and gives the two parallel PRPs (Core + Experience) a frozen scaffold to attach to.

## What

### Success Criteria

- [ ] **Backend Tech Stack (Option A: Rust, Option B: Go)** — both options fully described with: web framework, WebSocket lib, serialization format, shuffle/RNG, state-machine pattern, test framework, persistence, deployment. A justified recommendation between A vs B is required.
- [ ] **Frontend Tech Stack** — one primary recommendation with explicit reasoning across five evaluation axes: Browser MVP, Mobile-friendly web, Future native apps, Online multiplayer, Fast iteration.
- [ ] **State-Sync Model** — pick one of {full-snapshot, event-sourcing, hybrid} with tradeoff analysis; describe reconnection, replay, anti-cheat, idempotency.
- [ ] **Module Separation Diagram** — text/ASCII diagram of `GameManager / Deck / TurnController / RulesEngine / ActionValidator / StateReducer / EventBus / UIHandler / PersistenceAdapter` with each module's responsibility one-paragraph each.
- [ ] **20-Section Deliverable Outline** — a skeleton (heading + 1-line synopsis each) for: Executive Summary, Tech Stack, Backend Arch, Frontend Arch, State Model, Rules Engine Design, Turn-Flow State Machine, MVP Scope, Roadmap, Networking, Message Protocol, Reconnection, Analytics, UI/UX, AI, Testing, Security/Anti-Cheat, Deployment, Future Enhancements, Risks/Mitigations.
- [ ] **Implementation Roadmap** — sequenced milestones from "empty repo" to "online multiplayer", with explicit `now | next | later` tags. The "now" tier must be the **hot-seat browser MVP** per Additional Instruction below.

---

## All Needed Context

### CARD SHED — Rules v2.0 (canonical)

**Objective.** Be the first to end your turn with zero cards. Because the rules force a refill to 5 after every turn while the deck has cards, winning is only possible after the deck is fully exhausted.

**Players & Deck.** 3–4 players, standard 52-card deck, clockwise turn order.

**Ranks.** 2 < 3 < 4 < 5 < 6 < 7 < 8 < 9 < 10 < J(11) < Q(12) < K(13) < A(14). Four suits: Clubs(0), Diamonds(1), Hearts(2), Spades(3).

**Trump.** At setup, the bottom card of the deck is revealed (rotated 90° so its suit stays visible) and remains in the draw pile. Its suit is trump for the round. Any trump beats any non-trump. Trumps compare by rank.

**Setup.** Dealer chosen first round (config / random / oldest), rotates clockwise each round. Shuffle. Reveal bottom card → trump. Deal 5 to each. Dealer's left = first Attacker.

**Attacker turn.** Send exactly one of:
- 1-card attack: any single card
- 3-card combo: a pair (two of the same rank) + 1 kicker
- 5-card combo: two pairs of *different* ranks + 1 kicker

Then draw back to 5 (if the deck has cards). If hand is exactly 0 after the refill attempt (only possible when the deck is empty), **Attacker wins**. Otherwise the player to the left becomes Defender.

**Defender turn.** May beat any number of received cards (zero allowed), in any order:
- A non-trump card can be beaten by a same-suit higher rank OR any trump.
- A trump card can only be beaten by a higher trump.
- Beaten card + counter → discard (face-down). Defender may stop at any time.

After defending:
- **Full defence** (beat all): discard all, draw to 5 if needed, Defender immediately becomes Attacker and **must** send a fresh attack.
- **Partial / no defence**: unbeaten cards go into Defender's hand, draw to ≥5 if possible, next clockwise player becomes Attacker.

**Endgame.** No reshuffles. When the deck is empty, players may end turns with <5 cards. Winning happens at end-of-turn with exactly 0 cards in hand.

**New round.** Record winner, rotate dealer, gather + reshuffle, new bottom-card trump reveal, deal 5.

### Scope IN this PRP — Master Prompt sections to expand

**§1A. Tech Stack (both Rust and Go options).** For each backend option, name and justify:
web framework, WebSocket handling, serialization, RNG/shuffle, state-machine design, test framework, persistence, deployment approach. Also recommend a frontend stack with reasoning across browser MVP, mobile-friendly web, future native apps, online multiplayer, fast iteration.

**§1B. Game State Modeling (decisions only — no full type defs).** Decide which entities exist (Card, Deck, Player, MatchState, RoundState, PendingAttack, DiscardPile, TurnState, Action, ActionResult, GameEvent) and what the public/private/per-player visibility partitioning is. **Do not write the actual struct/interface bodies — PRP 2 owns that.** Just declare the entities, their visibility class, and how hidden hands are represented to opponents.

**§1C. Server-Authoritative Synchronization.** Full description: snapshot vs event-sourcing vs hybrid, pros/cons, recommendation, plus reconnection / replay / anti-cheat / idempotency / simultaneous-connections-but-turn-based handling.

**§1D. Clean Local Architecture.** ASCII diagram of `GameManager + Deck + TurnController + RulesEngine + ActionValidator + StateReducer + EventBus + UIHandler + PersistenceAdapter`. One paragraph per module on responsibility. Map each module to: hot-seat MVP, browser single-player, online server-authoritative, test/sim harness.

**§9. Deliverables outline.** 20-section blueprint headers with one-line synopses (Executive Summary, Tech Stack, Backend Arch, Frontend Arch, State Model, Rules Engine Design, Turn-Flow State Machine, MVP Scope, Roadmap, Networking, Message Protocol, Reconnection, Analytics, UI/UX, AI, Testing, Security/Anti-Cheat, Deployment, Future Enhancements, Risks/Mitigations).

**Additional Instruction (load-bearing).** First implementation target = **local hot-seat browser MVP using TypeScript frontend**. Architecture must evolve into **online multiplayer with Rust or Go server**. Be explicit about `now` vs `later`. Do not invent rules; do not skip edge cases.

### Scope OUT (belongs to siblings)

- Full TypeScript / Rust struct definitions for Card / Deck / Player / etc → PRP 2
- Rules-engine pseudocode (validateAttack, canBeat, resolveBeat, drawToMinimum, checkWin, etc) → PRP 2
- Unit / integration / property test specifications → PRP 2
- MVP feature checklist & implementation order → PRP 3
- UI screen inventory, table layout, interaction flows, juice → PRP 3
- Networking message catalogue with JSON bodies → PRP 3
- Analytics event taxonomy → PRP 3
- AI bot design (Level 0/1/2) → PRP 3

If a decision in your blueprint forces a change in sibling scope (e.g., choice of event-sourcing forces a `sequenceNumber` field in every message), call it out in a **"Cross-PRP Implications"** section so PRPs 2 and 3 inherit the consequence cleanly.

## Validation Loop

This PRP produces a decisions document, not code, so validation is documentary rather than executable.

### Level 1: Coherence

- [ ] Tech-stack recommendation cites concrete tradeoffs (latency / ecosystem / hiring / dev-loop speed), not vague "X is good for Y".
- [ ] State-sync recommendation matches the turn-based nature of the game (high-frequency tick is not needed).
- [ ] Module diagram has no orphaned dependencies and no two modules with overlapping responsibility.

### Level 2: Round-trip with siblings

- [ ] Every entity listed in §1B has a clear handoff to PRP 2 (which will define its concrete shape).
- [ ] Every "later" item in the roadmap has a sibling that will own it (UI screens → PRP 3; rules engine pseudocode → PRP 2; etc).
- [ ] Cross-PRP Implications section is present and non-empty.

### Level 3: Authoritative-spec round-trip

- [ ] The 20-section deliverable outline covers every Master Prompt section without overflow or gap.
- [ ] Each section's one-line synopsis names the PRP that owns the detail (Self / PRP-2 / PRP-3).

---

## Anti-Patterns to Avoid

- ❌ Writing full type definitions — that's PRP 2's job.
- ❌ Specifying WebSocket message JSON bodies — that's PRP 3's job.
- ❌ Recommending a stack without a single concrete reason rooted in CARD SHED's actual needs (turn-based, hidden info, 3–4 players, browser-first).
- ❌ Skipping the Rust-vs-Go tradeoff (both must be designed; only the *recommendation between them* is a single pick).
- ❌ Drifting into game-balance discussion — analytics & balance belongs to PRP 3.
- ❌ Inventing rule variants. The rules above are v2.0 and frozen for this PRP cycle.
