# BRAINSTORM — Reliquary

> Living document. Dump everything. Stays loose. Tighten in `STORYBOARD.md` and `ARCHITECTURE.md` once the shape emerges.

---

## 1. One-line pitch (fill in)

> _A browser-played card/artifact collector where every relic you keep raises the next one's pull-rate, and your shelf is yours — visible, finite, and persistent._

(Replace with your own version. The frame is fixed: **browser game, collectable cards/artifacts, retention-by-design.**)

---

## 2. Core vision pillars

These are the rails. Everything below must defend one of them.

| # | Pillar | What it means |
|---|--------|---------------|
| 1 | **Browser-first** | Zero install. URL → playable in ≤3 seconds. PWA-installable later. |
| 2 | **Collectable artifacts** | Cards, relics, tokens — each one has identity, lineage, scarcity. |
| 3 | **Ragaszkodás (stickiness)** | The player *cares* about their shelf. Loss-aversion done ethically: visible progress, no dark patterns. |
| 4 | **Local-first runtime** | Runs entirely in W7-Base. No external accounts to play. |
| 5 | **Design-driven** | UI/UX is the product. Stitch generates → agent-browser validates → Playwright proves. |

---

## 3. Open questions — answered (`2026-05-20`, draft v0)

> Filled by Claude as reasoned product defaults. **Every answer is overridable** — push back on any line and we'll re-derive everything downstream from the change.

### Game loop

- **Single-player first**, async social later.
  - v0 is a curator experience. No live PvP, no real-time trade.
  - In v2, *async lineage exchange* — players can "gift" a copy of a duplicate artifact and the original gains a small permanent badge ("seen by N curators"). No power asymmetry.
- **Session length: 30-second core beat, optional 3–5 min linger.**
  - The minimum-viable session is open the shelf, see today's relic, react, close. 30 seconds, no friction.
  - The maximum-engaged session is open the codex, read lineage, reorder shelf. 3–5 minutes.
  - We do **not** chase a 15-minute "deep play" session — that path leads to slot-machine mechanics.
- **Core verb: COLLECT.**
  - Everything else (combine, narrate, share) is a refinement of collect.
  - Anti-verbs: battle, defeat, conquer. Reliquary is not adversarial.

### Card economics

- **Earn pacing: hybrid of earn-by-time + earn-by-task, no earn-by-pay.**
  - One artifact arrives **per day** automatically (daily relic).
  - Additional artifacts unlock through **codex tasks** — small reading/curation actions ("annotate three relics", "complete a lineage chain"). Tasks are intrinsic, not grindy.
  - No purchase. No randomized pulls beyond the *content* of the day's relic.
- **Rarity: finite editions, not opaque tiers.**
  - Every artifact has an `edition_size`: `unlimited` (everyday relics), `100`, `25`, `7` (rare ceremonial relics tied to events).
  - We display **the actual print number** ("Print 17 of 100"). No hidden odds, no gacha.
  - Replaces Common/Uncommon/Rare/Mythic — we believe scarcity should be *known* not *implied*.
- **Cards leave the collection only by player choice.**
  - "Gift" (v2 async social) — transfers a duplicate; original stays.
  - "Release" — player intentionally retires an artifact from their shelf (it joins a public "released" gallery). No accidental loss.
  - No sacrifice/fusion that destroys. Loss-aversion stays ethical.

### Retention design

- **Daily relic is the heartbeat.** One relic per UTC day. Not a streak (no streak-break punishment), but each day's relic is unique and dated.
- **Progress surfaced as shelf-fill + codex story-step.**
  - Numeric counts (cards/decks/etc.) are **secondary**. The shelf itself is the primary progress indicator — visible, finite, beautiful.
  - The codex shows narrative threads emerging: "you've unlocked 3 of 7 in the Ember sequence".
- **First-hour vs first-month:**
  - **Hour 1**: wonder. The shelf goes from empty → three relics with story. The lineage system is *visible but locked*.
  - **Day 7**: pattern recognition. The player sees lineage threads emerging across their relics.
  - **Day 30**: curator pride. The shelf has personality — annotated, reordered, arranged. The "release" gallery exists as social signal.
- **Anti-retention**: no notification spam, no streak-shame, no FOMO countdowns on premium drops. The daily relic is always there when you open the app — it doesn't expire.

### Theme

- **Working name `Reliquary` — keep through v0.** Re-evaluate after first 10 external playtesters. The metaphor (shelf of meaningful objects) is load-bearing for the design.
- **Aesthetic: *modern-museum meets quiet occult*.**
  - Think: Wellcome Collection × Cabinet of Curiosities × calm-tech.
  - Dark warm surface (deep amber/black), gold accent, parchment-tone text.
  - **Not** dungeon (too violent), **not** botanical (too soft), **not** cyber-occult (too edgy).
  - Card art style: illustrated, restrained, slight grain. Editions feel printed, not pixelated.
- **Voice: curatorial-mythic.**
  - Object descriptions read like museum cards with a hint of folklore. Short. Sentence fragments allowed. Never breathless.
  - Example tone: *"Ember of First Light. One of seven. Always remembered."*
  - Not: solemn (too funeral), playful (too pixar), academic (too dry).

### Constraints

- **Devices: desktop-first, mobile-readable.**
  - The shelf is a horizontal canvas — desktop is the primary surface for v0.
  - Mobile is touch-optimised view, *not* a separate experience. Vertical shelf scroll, same data.
- **Latency budget for first card flip: ≤ 800ms** from click → relic visible.
  - Includes API roundtrip, reveal animation. Hard ceiling.
- **Accessibility floor: WCAG AA from day one.**
  - Color contrast verified by Stitch at design-system generation time.
  - Keyboard-navigable shelf (arrow keys + Enter).
  - `prefers-reduced-motion` honored — flip becomes fade.
  - Screen-reader: every artifact has a real `aria-label` from its frontmatter.

---

## 4. Inspiration shelf

Drop links + one-line "what we steal, what we leave":

| Source | Steal | Leave |
|--------|-------|-------|
| _(fill)_ | _(mechanic / vibe / loop)_ | _(antipattern we won't copy)_ |
| _(fill)_ | | |

Suggested seeds to react against (not copy): _Hearthstone_, _Marvel Snap_, _Slay the Spire_, _Inscryption_, _Stamps.fyi_, _Cabinets of curiosity_ (Wunderkammer), _Sims gallery_, museum-archive UIs.

---

## 5. Anti-goals (HARD NO)

- ❌ Pay-to-win mechanics. (Cosmetic-only monetization is fine, but later.)
- ❌ Dark patterns that exploit FOMO or sunk-cost.
- ❌ Hidden-rarity opaque pulls (we surface the actual odds).
- ❌ Cloud-only — must remain playable on a single host.
- ❌ Game engine creep. PixiJS for canvas, React for chrome. No Unity/Godot detour for MVP.

---

## 6. Risks and unknowns

| Risk | Severity | First mitigation |
|------|----------|------------------|
| Retention pillar collapses without social loop | High | Prototype the "shelf" before the "draw" |
| Card art pipeline (where do assets come from?) | High | Decide: AI-gen baseline → hand-touchup, or commission-curated |
| Game state sync (when do we need WebSockets vs. polling?) | Med | Default to REST + Redis pub/sub for v0; upgrade only on real lag |
| Frontend bundle blows past 1MB | Med | Code-split per route; lazy-load PixiJS only on canvas screens |
| Scope creep into "platform with cards" not "card game" | High | This doc owns the boundary. Quarterly re-read. |

---

## 7. Decision log (append-only)

Each decision: **what we chose, when, why, what we rejected.**

- `2026-05-20` — **Single-player v0** — chose curator experience over PvP. Rejected: live duel mechanic. Reason: retention through care, not competition.
- `2026-05-20` — **30-second core session** — chose minimum-viable beat over deep-play session. Rejected: 15-minute slot-machine loop. Reason: dark-pattern prevention.
- `2026-05-20` — **COLLECT as core verb** — chose collection-as-curation over battle/combine. Rejected: TCG-style duel. Reason: anti-adversarial framing.
- `2026-05-20` — **Finite editions over rarity tiers** — chose explicit "Print N of M" over hidden Common/Uncommon/Rare. Rejected: gacha. Reason: transparent scarcity is ethical scarcity.
- `2026-05-20` — **Daily relic, no streaks** — chose always-available daily artifact over streak-locked rewards. Rejected: Duolingo streak shame. Reason: opt-in retention.
- `2026-05-20` — **Modern-museum × quiet-occult aesthetic** — chose Wellcome × Wunderkammer × calm-tech. Rejected: dungeon, botanical, cyber-occult. Reason: dignifies the artifact.
- `2026-05-20` — **Desktop-first, mobile-readable** — chose horizontal shelf canvas on desktop. Rejected: mobile-first responsive. Reason: shelf metaphor needs lateral space.
- `2026-05-20` — **WCAG AA from day one** — chose accessibility floor at design-system level. Rejected: post-MVP a11y pass. Reason: cheaper to bake in than retrofit.

---

## Next checkpoints

1. Lock in Section 3 answers → write `STORYBOARD.md`.
2. From the storyboard, derive screens → invoke `Skill stitch-design` for the first three.
3. From the screens, derive data shapes → harden `ARCHITECTURE.md`.

Update this doc every session. Stale brainstorms ossify into bad assumptions.
