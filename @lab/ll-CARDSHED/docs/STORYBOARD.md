# STORYBOARD — CARD SHED (MVP, hot-seat browser)

> **Scope:** PRP 3 Sub-deliverable A (M1–M17). Local hot-seat browser, 3–4 humans pass-and-play, TypeScript + React + Tailwind v4 + Radix + framer-motion + Zustand. No server, no online, no AI beyond Level-0 filler, no audio, no accounts.
>
> **Purpose of this file:** mandatory input to `Skill: stitch-design`. Per `.claude/rules/ui-design-pipeline.md` §2, no Stitch generation runs without §5 wireframes locked here. Every screen in §3 has a wireframe in §5 and an entry in `docs/SCREENS/<slug>.md` once Stitch produces a mockup.
>
> **Source-of-truth:** `PRPs/cardshed-03-experience-prp.md` (lines 694–1169). `apps/core/src/core/types.ts` + `rules.ts` are the engine contract — every wireframe references state the engine exposes.

---

## §1 — Premise

CARD SHED is a 3–4 player, single-deck, shifting-trump card game derived from Russian Durak. One device, one room, friends around a table — the MVP is **pass-and-play hot-seat in a browser**.

Three properties hold the game together:

1. **Hidden hands.** Every player's hand is private. When the device passes, the previous viewer's hand vanishes and the next viewer's hand reveals only after they confirm. (S04 — Privacy splash.)
2. **One trump per round, picked by the deck.** At deal time, the bottom card's suit is the round's trump. Trump beats anything else; same-suit cards beat lower same-suit. The trump shifts every round.
3. **Attack, beat, or take.** The attacker plays 1, 3, or 5 cards in a valid combo. The defender either beats every card (full defence → becomes the next attacker) or stops early (partial / no defence → unbeaten cards enter their hand → next clockwise player attacks).

The MVP ships a **single round = a match** (per PRP 3 NEW #9). Multi-round semantics ship post-MVP without wire-format changes.

**Aesthetic anchor.** The product is **a card game first** — the table is the protagonist. Visual language is calm, high-contrast, with playful but restrained motion. CARD SHED is NOT a luxury collectible (`@lab/ll-RELIQUARY`); do not import its modern-museum / quiet-occult tokens. Inspirations: *Hearthstone's* readability without its excess, *Slay the Spire's* card legibility, *Threes!* feel-of-snap.

---

## §2 — User Journey (MVP, one match, three players)

> Personas: **Ada** (host, picks device), **Bo**, **Cy**. All three around a kitchen table. One laptop. Friday night.

```
 ① Ada opens http://localhost:4343
        │
        ▼
 S01 MainMenu  ──── click "Play"
        │
        ▼
 S02 PlayerSetup ── enters "Ada", "Bo", "Cy" → "Start match"
        │       (matchStore.startMatch → @cardshed/core.startNewRound(null, seed))
        ▼
 S04 Privacy splash: "Pass device to Ada"  ── Ada confirms
        │
        ▼
 S03 Table (viewer = Ada)
   ├── Trump indicator shows bottom-card suit
   ├── Opponent bar: Bo (5), Cy (5)
   ├── Deck: 37, Discard: 0
   ├── Phase: AwaitingAttack — Ada is attacker
   ├── Hand: Ada's 5 cards (legal-action highlighting)
   └── Action bar: "Send Attack" (disabled until selection)
        │
        ▼
 S05 AttackSelect — Ada taps 1, 3, or 5 cards
        ├── Live preview chip: "3 cards (pair + kicker)"
        ├── validateAttack(...) result → Send enabled / "Invalid combo: ..."
        └── Send → optimistic UI; LocalDispatcher dispatches SubmitAttack
        │
        ▼
 S04 Privacy splash: "Pass device to Bo"  ── Bo confirms
        │
        ▼
 S03 Table (viewer = Bo)  → phase = AwaitingDefense
        │ pending-attack panel shows Ada's cards face-up
        ▼
 S06 DefenseSelect — Bo beats cards one by one OR stops
   ├── Tap an unbeaten card → legal counters in hand highlight; illegals dim
   ├── Tap a counter → pair flies to beatenPairs panel
   ├── "Stop defending" → tooltip warns "Unbeaten cards go to your hand."
   └── On full defence → "Full defence! You become attacker."
        │
        ▼ ── continue with @cardshed/core branches (full/partial defence) ──
        │
        ▼ ── repeat: attack → privacy → defense → privacy … ──
        │
        ▼
 S07 RoundResult — RoundWon event → "Bo wins!"
        │
        ▼
 S08 MatchResult — (MVP: single round = match) → "Bo wins the match. Play again?"
        │
        └─ "Play again" → S02 PlayerSetup pre-filled
        └─ "Main menu" → S01

 Overlays available from anywhere via header buttons:
   S09 RulesHelp  ("?" top-right) — Radix Dialog
   S10 Settings   ("≡" top-left) — Radix Dialog
```

**Error-path coverage**

- Invalid combo: validateAttack rejection chip stays on screen until selection changes.
- Illegal beat: counter card stays in hand; suit/rank reason appears as toast.
- Attempted Stop with full hand-beat available: allowed (it's the player's choice), but the next-attacker is *them* — they may want to think twice. No UI block.
- Resign / leave: not in MVP (PRP 3 §C MVP scope).

---

## §3 — Screen Inventory (MVP subset of PRP 3 §B)

| # | Slug | Parent state | Stitch spec | Owns |
|---|------|--------------|-------------|------|
| **S01** | main-menu | pre-match | `docs/SCREENS/main-menu.md` | Play / Rules / Settings buttons. Brand mark. Version chip. |
| **S02** | player-setup | pre-match | `docs/SCREENS/player-setup.md` | 3–4 name inputs. Start. Seed (optional advanced). |
| **S03** | table | every in-match phase | `docs/SCREENS/table.md` | Opponent bar, trump chip, deck/discard, pending-attack panel, hand, phase label, action buttons. |
| **S04** | privacy | between turns | `docs/SCREENS/privacy.md` | Pass-device blackout + confirm. |
| **S05** | attack-select | `AwaitingAttack` | `docs/SCREENS/attack-select.md` | Card multi-select on the table hand + Send. |
| **S06** | defense-select | `AwaitingDefense` + `Resolving` | `docs/SCREENS/defense-select.md` | Beat / Stop overlays on the table. |
| **S07** | round-result | `RoundEnded` | `docs/SCREENS/round-result.md` | Winner banner. (Next round button — disabled in MVP.) |
| **S08** | match-result | `MatchEnded` | `docs/SCREENS/match-result.md` | Match winner. Play again / Main menu. |
| **S09** | rules-help | overlay | `docs/SCREENS/rules-help.md` | Radix Dialog with rules sections. |
| **S10** | settings | overlay | `docs/SCREENS/settings.md` | Sound toggle (post-MVP), reduced motion, reset match. |

S05/S06/S07/S08 render **on top of** S03 — they're modal overlays or table-layer panels rather than independent pages.

---

## §4 — Engine Contract Referenced by the UI

> Every wireframe in §5 may only display state derivable from these. The UI MUST NOT reimplement rule logic; legality comes from the engine.

| UI element | Reads from | Engine source |
|------------|-----------|---------------|
| Opponent count chips | `PrivatePlayerView.players[i].hand.count` | `createPrivateView` |
| Trump indicator | `PrivatePlayerView.round.trump` | `startNewRound` / `determineTrumpFromBottomCard` |
| Deck / discard counts | `PrivatePlayerView.deckCount / discardCount` | `createPrivateView` |
| Pending attack panel | `PrivatePlayerView.round.pendingAttack` | `submitAttack` / `submitBeat` |
| Phase label | `PrivatePlayerView.round.phase` | reducers |
| Current viewer's hand | `PrivatePlayerView.viewerHand` | `createPrivateView(state, viewerId)` |
| Legal-attack highlight | `getLegalActions(state, viewerId)` filter Attack | `getLegalActions` |
| Legal-beat highlight | `canBeat(attack, counter, trump)` for each hand card | `canBeat` |
| Send-Attack disabled | `validateAttack(state, attackerId, cards)` ok? | `validateAttack` |
| RoundEnded / MatchEnded | `GameEvent` union | reducers emit |

All actions go through `LocalDispatcher.dispatch(action) → ActionResult`. The dispatcher is a thin wrapper over `submitAttack | submitBeat | stopDefending`.

---

## §5 — Wireframes (input to Stitch — DO NOT skip; the pipeline gates on this)

ASCII intent only. Stitch produces the visual design system + per-screen mockups. **Tokens (color, type, spacing, radius, motion) MUST come from `.stitch/DESIGN.md` once it exists** — do not transcribe pixel values from these wireframes.

> Canonical desktop viewport: **1440 × 900**. Mobile portrait 375 × 667 follows the same layout reflowed vertically (M13 owns mobile sweep).

### S01 — MainMenu

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                                                                 │
│                                                                 │
│                       CARD   SHED                               │
│                  (logotype + tagline)                           │
│                                                                 │
│                                                                 │
│                     ┌──────────────────┐                        │
│                     │      P L A Y     │                        │
│                     └──────────────────┘                        │
│                     ┌──────────────────┐                        │
│                     │      Rules       │                        │
│                     └──────────────────┘                        │
│                     ┌──────────────────┐                        │
│                     │     Settings     │                        │
│                     └──────────────────┘                        │
│                                                                 │
│                                                                 │
│                                            v0.x  •  MVP  •  hot-seat
└─────────────────────────────────────────────────────────────────┘
```

Intent: brand-forward, primary CTA visually dominant, the other two buttons quieter. Tone-setter for the whole UI.

### S02 — PlayerSetup

```
┌─────────────────────────────────────────────────────────────────┐
│  ◀ Main menu                                                    │
│                                                                 │
│                     Who's playing?                              │
│                                                                 │
│         Player 1    ┌─────────────────────────────┐             │
│                     │ Ada                         │             │
│                     └─────────────────────────────┘             │
│         Player 2    ┌─────────────────────────────┐             │
│                     │ Bo                          │             │
│                     └─────────────────────────────┘             │
│         Player 3    ┌─────────────────────────────┐             │
│                     │ Cy                          │             │
│                     └─────────────────────────────┘             │
│         Player 4    ┌─────────────────────────────┐  [ remove ] │
│                     │   (optional — leave blank)  │             │
│                     └─────────────────────────────┘             │
│                                                                 │
│              ▼ Advanced                                         │
│                Seed: 0x4a2c… [ randomize ]                      │
│                                                                 │
│                     ┌──────────────────┐                        │
│                     │  Start  match    │                        │
│                     └──────────────────┘                        │
└─────────────────────────────────────────────────────────────────┘
```

Intent: scannable form, big inputs (touch-friendly), Start disabled until ≥3 names. Advanced seed is collapsed by default.

### S03 — Table (the canonical in-match screen)

```
┌─────────────────────────────────────────────────────────────────┐
│ ≡          Bo (4) — defender    •    Cy (5) — waiting       ?  │
│                                                                 │
│        ┌──────────────┐         ┌───────┐    ┌───────┐         │
│        │ trump  ♠     │         │ Deck  │    │ Disc. │         │
│        │ (suit chip)  │         │  37   │    │   2   │         │
│        └──────────────┘         └───────┘    └───────┘         │
│                                                                 │
│        ╔═════════════════════════════════════════════════╗     │
│        ║  PENDING ATTACK  (phase = AwaitingDefense)      ║     │
│        ║  unbeaten:  [9♣]                                ║     │
│        ║  beaten:    [K♠ ▸ 7♠]                           ║     │
│        ╚═════════════════════════════════════════════════╝     │
│                                                                 │
│              Phase: Awaiting Defense   •   Defender: Bo         │
│                                                                 │
│   ┌────────────────────── YOUR HAND (Bo) ──────────────────┐   │
│   │  [10♦]  [J♦]  [Q♥]  [7♥]   ← horizontally scrollable   │   │
│   └────────────────────────────────────────────────────────┘   │
│                                                                 │
│   ┌──── action bar ───────────────────────────────────────┐    │
│   │   ▢ Select an unbeaten card to beat        [ Stop ]   │    │
│   └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

Header chips (opponent bar) compress as opponents grow. The pending-attack panel grows as more cards land. Hand is horizontally scrollable; never wraps to two rows on desktop.

### S04 — Privacy (Pass-Device splash)

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                                                                 │
│                                                                 │
│                                                                 │
│                       Pass device to                            │
│                                                                 │
│                            Bo                                   │
│                                                                 │
│                                                                 │
│                     ┌──────────────────┐                        │
│                     │  I'm Bo — reveal │                        │
│                     └──────────────────┘                        │
│                                                                 │
│                  ▲                                              │
│                  └──  previous viewer's hand is BLANK.          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

Intent: nothing else on screen. No leak surface. Full opaque background, big confirm.

### S05 — AttackSelect (overlay on S03 when phase = AwaitingAttack)

```
┌──────────────── (table chrome above unchanged) ────────────────┐
│                                                                 │
│   ┌──── YOUR HAND (Ada — attacker) ──────────────────────────┐ │
│   │   [10♦ ✓] [10♥ ✓] [J♣]  [Q♠ ✓]  [K♣]  ← selected ringed │ │
│   └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│   ┌─── preview ───────────────────────────────────────────┐    │
│   │  3 cards selected:  pair of 10s + Queen kicker  ✅     │    │
│   └────────────────────────────────────────────────────────┘    │
│                                                                 │
│   ┌── action bar ───────────────────────────────────────┐      │
│   │       [ Clear ]                  [  Send attack  ]  │      │
│   └─────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────┘
```

Selection state lives in `attackDraft` (uiStore). Preview chip live-reads `validateAttack`. Selected cards are ringed in the *accent* token from `.stitch/DESIGN.md`. Invalid combos show the validation code instead of `✅`.

### S06 — DefenseSelect (overlay on S03 when phase = AwaitingDefense | Resolving)

```
┌──────────────── (table chrome above unchanged) ────────────────┐
│                                                                 │
│        PENDING ATTACK                                           │
│        unbeaten: [9♣ ◉]      ← active target ringed             │
│        beaten:   [K♠ ▸ 7♠]                                      │
│                                                                 │
│   ┌──── YOUR HAND (Bo — defender) ────────────────────────────┐│
│   │  [10♦ ✓ legal] [J♦ ✓ legal] [Q♥ — dim] [7♥ — dim]         ││
│   └───────────────────────────────────────────────────────────┘│
│                                                                 │
│   ┌── action bar ───────────────────────────────────────┐      │
│   │      [ Clear target ]   [ Beat ]    [ Stop ]        │      │
│   └─────────────────────────────────────────────────────┘      │
│                                                                 │
│   Tooltip on hovered Stop:                                      │
│      "Unbeaten cards will go to your hand. Tap Stop again       │
│       to confirm."                                              │
└─────────────────────────────────────────────────────────────────┘
```

Tap an unbeaten card → it becomes the active target → cards in hand that satisfy `canBeat(attack, counter, trump)` light up as "legal", others dim to "illegal". Tap a legal counter → pair flies to `beatenPairs`. Repeat until all beaten OR Stop.

### S07 — RoundResult (overlay on S03 after RoundEnded event)

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                                                                 │
│                                                                 │
│                      Bo wins the round                          │
│                                                                 │
│                       (round 1 of 1 — MVP)                      │
│                                                                 │
│              ┌──────────────────────────────┐                   │
│              │     Continue to match end    │                   │
│              └──────────────────────────────┘                   │
│                                                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

Intent: clear, calm, brief. MVP single-round-match means this segues straight to S08. Multi-round semantics (post-MVP) would show a leaderboard + "Next round" button here.

### S08 — MatchResult

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                                                                 │
│                                                                 │
│                     🏆  Bo wins the match                       │
│                                                                 │
│                                                                 │
│              ┌──────────────────────────────┐                   │
│              │       Play again             │ ◀ pre-fills names │
│              └──────────────────────────────┘                   │
│              ┌──────────────────────────────┐                   │
│              │       Main menu              │                   │
│              └──────────────────────────────┘                   │
│                                                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

Intent: celebratory but not loud. The 🏆 glyph is a placeholder; Stitch may replace it with a real mark from the design system.

### S09 — RulesHelp (Radix Dialog overlay)

```
┌─── Dialog 800×640, centered, dim backdrop ─────────────────────┐
│  How to play CARD SHED                                  [ × ]  │
│ ───────────────────────────────────────────────────────────── │
│  ┌─ Tabs ──────────────────────────────────────┐               │
│  │  Basics  │  Attacks  │  Defence  │  Trump   │               │
│  └─────────────────────────────────────────────┘               │
│                                                                 │
│   Body text (markdown):                                         │
│      • 3–4 players, single deck.                                │
│      • Bottom card's suit is trump for the round.               │
│      • Attacker plays 1, 3, or 5 cards in a valid combo.        │
│      • Defender beats every card → becomes next attacker        │
│        (full defence). Otherwise unbeaten cards enter their     │
│        hand and next clockwise player attacks (partial).        │
│      • First to empty their hand with the deck exhausted wins.  │
│                                                                 │
│                                              [ Close ]          │
└─────────────────────────────────────────────────────────────────┘
```

Tabs are Radix Tabs. Body is markdown rendered through a safe renderer. No state, no engine interaction.

### S10 — Settings (Radix Dialog overlay)

```
┌─── Dialog 560×480, centered, dim backdrop ─────────────────────┐
│  Settings                                                [ × ]  │
│ ───────────────────────────────────────────────────────────── │
│   ┌──── Match ──────────────────────────────────────────────┐ │
│   │  [ ⟲ Reset current match ]                              │ │
│   │     ▸ keeps players, regenerates seed                   │ │
│   └─────────────────────────────────────────────────────────┘ │
│   ┌──── Accessibility ──────────────────────────────────────┐ │
│   │  ☐  Reduced motion                                       │ │
│   │  ☐  High-contrast cards                                  │ │
│   └─────────────────────────────────────────────────────────┘ │
│   ┌──── Audio ──────────────────────────────────────────────┐ │
│   │  ☐  Sound effects  (post-MVP — disabled)                 │ │
│   └─────────────────────────────────────────────────────────┘ │
│                                                                 │
│                                              [ Close ]          │
└─────────────────────────────────────────────────────────────────┘
```

Reset-match prompts a confirm step. Reduced-motion respects the OS `prefers-reduced-motion` by default.

---

## §6 — Out of Scope (this storyboard slice)

- Online lobby (S11), Reconnect (S12), Spectator (S13), Async list (S14) — those land in PRP 3 sub-deliverables C/D once the WebSocket protocol is implemented (M-future).
- Multi-round match scoring screen — MVP treats round = match (NEW #9). The post-MVP storyboard will add a Leaderboard panel between S07 and S08.
- Card art / illustrated suits — MVP uses Unicode suit glyphs ♠♥♦♣ plus rank text. Stitch may choose typography for the rank but no per-card illustrations.
- Onboarding tutorial overlay — MVP relies on S09 RulesHelp as the only learning surface.
- Mobile-specific gestures (swipe-to-fan hand, long-press preview) — captured in M13, not designed here.

---

## §7 — Stitch Provenance (filled by `Skill: stitch-design` runs)

Every Stitch run that touches this storyboard or `.stitch/DESIGN.md` MUST record a row here AND a corresponding file under `docs/DECISIONS/<utc>-stitch-run-N.md`.

| # | UTC | Prompt summary | DS version | Screens produced | Decision doc |
|---|-----|----------------|------------|-------------------|--------------|
| 1 | 2026-05-21 | Initial design system anchored on S03 Table (single canonical screen → derive tokens for whole system; per-screen mockups in M3+ per warm-session-drop constraint) | DS-1 | S03 Table (`.stitch/designs/S03-table.{html,png}`) | [`docs/DECISIONS/2026-05-21-stitch-run-1.md`](DECISIONS/2026-05-21-stitch-run-1.md) |
