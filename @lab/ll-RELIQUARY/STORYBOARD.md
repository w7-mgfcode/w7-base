# STORYBOARD — Reliquary

> The narrative of the *first session* and the *first month*. Every screen sketched here gets a Stitch-generated mockup before any code lands.

---

## 0. How to use this doc

1. **Section 2** (User Journeys) is the spine — write it before screens.
2. **Section 3** (Screen Inventory) lists every screen the journeys touch.
3. For each screen, run **`Skill stitch-design`** and link the generated mockup under `docs/SCREENS/<screen-slug>.md`.
4. **Section 4** (Flows) records how screens chain — this becomes the Playwright test plan later.
5. **Section 5** (Pillanatképek / snapshots) captures pre-Stitch wireframe text so design intent survives review churn.

> ⚠️ Per `.claude/rules/ui-design-pipeline.md`: **no UI code is written by hand** — Stitch generates, agent-browser verifies, Playwright proves.

---

## 1. World premise (fill)

> _Players are curators of a personal Reliquary — a shelf of artifacts that grow in meaning as they're collected. Each artifact has a story, a lineage, and a quiet pull on the next._

(Replace with your version. Keep it ≤3 sentences. The premise is the elevator pitch for the *feel*, not the mechanics.)

---

## 2. User journeys

Three journeys carry the product. Define each as a numbered beat list.

### Journey A — First-time visitor (cold landing → first artifact)

The "30-second" arc. The goal: by minute one, the player owns one artifact and understands the shelf metaphor.

1. Land at `/` → see the empty shelf with one **glowing slot**.
2. Click the slot → first artifact reveals (no signup gate).
3. Artifact lands on shelf → ambient hint: *"3 more to unlock the Codex"*.
4. CTA → "Keep your shelf" → soft account creation (passwordless / device-key first; email optional).

**Validation**: agent-browser captures screenshots at each beat. Playwright asserts: empty-state visible, artifact reveal animation runs ≤ 800ms, account-prompt is dismissible.

### Journey B — Returning player (day 2 → daily relic)

The retention beat. Goal: a reason to come back that doesn't feel mandatory.

1. Land → shelf restored, **today's relic** highlighted but optional.
2. Open today's relic → short "story card" reveal (no fail state).
3. Shelf updates → cross-link: *"This relic pairs with X you already own."*
4. Path forward → either close, or continue to the **Codex** view.

### Journey C — Curator (week 2 → arranging the shelf)

The deep-engagement beat. Goal: the player makes the shelf *theirs*.

1. Shelf overview → drag to reorder, tag, annotate.
2. Open an artifact → see its lineage (which relic it came from / leads to).
3. Optional share → static OG-image of the shelf (no live multiplayer yet).

---

## 3. Screen inventory

Every screen the journeys above touch. Each row links to a Stitch-generated mockup once produced.

| ID | Screen | Journey | Mockup | State |
|----|--------|---------|--------|-------|
| S01 | Landing / Shelf (empty) | A | _(stitch-design pending)_ | 🟡 wireframe ready |
| S02 | First-pull reveal modal | A | _(stitch-design pending)_ | 🟡 wireframe ready |
| S03 | Account claim (passwordless) | A | _(stitch-design pending)_ | 🟡 wireframe ready |
| S04 | Shelf (populated, day-2+) | B | _(stitch-design pending)_ | 📋 todo |
| S05 | Daily relic reveal | B | _(stitch-design pending)_ | 📋 todo |
| S06 | Codex / artifact detail | B/C | _(stitch-design pending)_ | 📋 todo |
| S07 | Shelf curator mode (drag/tag) | C | _(stitch-design pending)_ | 📋 todo |
| S08 | Lineage view (artifact relations) | C | _(stitch-design pending)_ | 📋 todo |
| S09 | Share / export OG-image | C | _(stitch-design pending)_ | 📋 todo |
| Sxx | Settings / accessibility | global | _(stitch-design pending)_ | 📋 todo |

---

## 4. Flow graph (text form)

```
                  ┌──────────────────┐
                  │ S01 Empty Shelf  │
                  └────────┬─────────┘
                           │ click slot
                           ▼
                  ┌──────────────────┐
                  │ S02 First Reveal │
                  └────────┬─────────┘
                           │ keep shelf
                           ▼
                  ┌──────────────────┐
                  │ S03 Claim Account│ ◄── skippable (device-only mode)
                  └────────┬─────────┘
                           ▼
                  ┌──────────────────┐
                  │ S04 Shelf v2     │ ◄─────────┐
                  └────┬────┬────────┘           │
                       │    │                    │
              ┌────────┘    └────────┐           │
              ▼                       ▼          │
       ┌──────────────┐       ┌──────────────┐  │
       │ S05 Daily    │       │ S06 Codex    │──┘
       │ Relic        │       │ + S08 Lineage│
       └──────────────┘       └──────┬───────┘
                                     ▼
                              ┌──────────────┐
                              │ S07 Curator  │
                              └──────┬───────┘
                                     ▼
                              ┌──────────────┐
                              │ S09 Share    │
                              └──────────────┘
```

This graph becomes the Playwright e2e test matrix.

---

## 5. Pillanatképek (text-wireframe snapshots)

Pre-Stitch wireframes for Journey A. These are the **load-bearing inputs** to the first `stitch-design` run — anything ambiguous here will get hallucinated downstream.

> Aesthetic anchor (from `BRAINSTORM.md` §3): modern-museum × quiet-occult. Dark warm surface, gold accent, parchment-tone text. Curatorial-mythic voice. Desktop-first canvas, WCAG AA.

---

### S01 — Empty Shelf (Journey A · beat 1)

**Purpose**: cold-landing → curiosity. The user understands within 3 seconds that this is a *shelf*, not a feed.

**Viewport**: desktop 1440×900 (primary). Mobile reflow defined separately.

```
┌──────────────────────────────────────────────────────────────────────┐
│                                                                      │
│  ✦ RELIQUARY                                              [?]  [ ⚙ ] │  ← header (translucent)
│                                                                      │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│       Your shelf is empty.                                           │
│       Begin — your first relic awaits.                               │
│       ──────                                                         │  ← parchment rule
│                                                                      │
│                                                                      │
│   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐         │
│   │░░░░░░░░░░│   │░░░░░░░░░░│   │ ✦  glow  │   │░░░░░░░░░░│         │
│   │░ slot 1 ░│   │░ slot 2 ░│   │ slot 3   │   │░ slot 4 ░│   →     │  ← horizontal shelf
│   │░░░░░░░░░░│   │░░░░░░░░░░│   │ active   │   │░░░░░░░░░░│         │     dim slots = inactive
│   └──────────┘   └──────────┘   └──────────┘   └──────────┘         │     glowing = "begin"
│                                                                      │
│                       [ Reveal first relic ]                         │  ← single CTA, centered
│                                                                      │
│                                                                      │
├──────────────────────────────────────────────────────────────────────┤
│   shelves grow. nothing here is random. ─ ✦                          │  ← footer hint, italic
└──────────────────────────────────────────────────────────────────────┘
```

**Interactive elements**
- `[ Reveal first relic ]` — primary, gold; keyboard: `Enter`/`Space` with focus auto-set.
- Glowing slot (#3) — also clickable, same action; aria-label `Begin — reveal your first relic`.
- `[?]` — opens a 1-paragraph "what is this" overlay; aria-label `What is Reliquary`.
- `[⚙]` — settings (sound, motion, contrast); aria-label `Settings`.

**Motion**
- Glowing slot: gentle pulse (1.4s ease-in-out, 12% opacity sweep). `prefers-reduced-motion` → static.
- Dim slots: hairline gold border + 6% inner shadow. Static.

**Empty-state copy**
- Headline: *"Your shelf is empty."*
- Subhead: *"Begin — your first relic awaits."*
- Footer: *"shelves grow. nothing here is random."*

**Stitch prompt cues**
- Surface: `--color-surface` deep warm black, slight grain.
- Slots: rectangular `--radius-slot`, asymmetric 5:7 portrait ratio (card-shaped).
- Type: display font for headline, body for subhead, mono for footer hint.

---

### S02 — First Reveal (Journey A · beat 2)

**Purpose**: the wonder moment. Card flips, fills slot #3, becomes ownable.

**Viewport**: desktop 1440×900, modal-style overlay over S01 (shelf dimmed behind).

```
┌──────────────────────────────────────────────────────────────────────┐
│  ░░░░░░░░░░ shelf dimmed 60% behind ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │
│                                                                      │
│        ┌────────────────────────────────────────────────────┐        │
│        │                                                    │        │
│        │              ┌──────────────────┐                  │        │
│        │              │ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │                  │        │
│        │              │ ▓ illustrated  ▓ │  ← flips 3D      │        │
│        │              │ ▓ artifact art ▓ │     720ms        │        │
│        │              │ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │                  │        │
│        │              │                  │                  │        │
│        │              │  EMBER OF        │                  │        │
│        │              │  FIRST LIGHT     │                  │        │
│        │              │  ─────           │                  │        │
│        │              │  Print 1 of 7    │  ← edition visible│       │
│        │              └──────────────────┘                  │        │
│        │                                                    │        │
│        │      one of seven. always remembered.              │        │  ← lore line
│        │                                                    │        │
│        │      ┌────────────────────┐                        │        │
│        │      │  Place on shelf →  │                        │        │  ← primary CTA
│        │      └────────────────────┘                        │        │
│        │                                                    │        │
│        │            (esc to dismiss)                        │        │  ← muted secondary
│        └────────────────────────────────────────────────────┘        │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

**Interactive elements**
- `[ Place on shelf → ]` — primary; on click, modal closes + card animates into slot #3.
- `esc` / click-outside — defers placement; revisits S01 with the relic visible but not yet "placed" (stored client-side; placement is committed by clicking the CTA, with a soft fallback on next visit).

**Motion**
- Card-flip: 720ms cubic-bezier(0.2, 0.8, 0.2, 1). `prefers-reduced-motion` → cross-fade 240ms.
- Modal entry: scrim fades in 160ms, then card flips. Background shelf stays dimmed throughout.
- Placement: card scales to slot size in 320ms; slot's "glow" transfers to slot #4 (next active).

**Voice / lore line**
- Below card title + edition: one italic sentence in `--color-ink-muted`. Always 5–9 words. Always tied to the artifact's frontmatter `lore` field.

**Stitch prompt cues**
- Card frame: `--radius-card`, thin gold rule, parchment inset.
- Edition label: small caps, mono, italic.
- Modal scrim: 60% black with 2% warm tint (not pure black).

---

### S03 — Account Claim (Journey A · beat 3, skippable)

**Purpose**: the player has *one relic*. Offer to keep it across devices, but never gate. Soft passwordless first; email later.

**Viewport**: same modal slot as S02. Appears AFTER the relic places into the shelf.

```
┌──────────────────────────────────────────────────────────────────────┐
│  ░░░░░░░░░░ shelf shows relic in slot #3, dimmed 50% ░░░░░░░░░░░░░░  │
│                                                                      │
│        ┌────────────────────────────────────────────────────┐        │
│        │                                                    │        │
│        │           ✦  Keep your shelf?                      │        │
│        │           ────                                     │        │
│        │                                                    │        │
│        │      This shelf is yours.                          │        │  ← reassurance copy
│        │      Save it to this device, or carry              │        │
│        │      it across sessions.                           │        │
│        │                                                    │        │
│        │     ┌──────────────────────────────────┐           │        │
│        │     │  Keep on this device  (default)  │           │        │  ← primary, gold
│        │     └──────────────────────────────────┘           │        │
│        │                                                    │        │
│        │     ┌──────────────────────────────────┐           │        │
│        │     │  Add an email (optional)         │           │        │  ← secondary, parchment
│        │     └──────────────────────────────────┘           │        │
│        │                                                    │        │
│        │            ─ or ─                                  │        │
│        │                                                    │        │
│        │      [ Skip — I'll decide later ]                  │        │  ← tertiary, muted
│        │                                                    │        │
│        │                                                    │        │
│        │   tiny print: no passwords. no tracking.           │        │  ← trust hint
│        │   we use a device key stored only in your browser. │        │
│        └────────────────────────────────────────────────────┘        │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

**Interactive elements**
- `[ Keep on this device ]` — primary. Generates a device-key (UUID v4) client-side, posts to `POST /session`, sets a long-lived session cookie. No email required.
- `[ Add an email (optional) ]` — expands inline into an email field + magic-link send. Does **not** block the primary path.
- `[ Skip — I'll decide later ]` — closes modal; the relic persists locally only, with a subtle banner on next visit reminding *"your shelf is on this device only"*.

**Motion**
- Modal entry: 220ms slide-up + 160ms scrim fade.
- Email expand: 180ms height-grow + cross-fade of buttons.

**Voice / copy**
- Headline: *"Keep your shelf?"* — question, not command.
- Trust hint at the bottom uses literal language: *"no passwords. no tracking."*
- Avoid: "Sign up", "Register", "Create an account". The frame is *"keep what you have"*, not *"join a service"*.

**Accessibility**
- Focus order: primary → secondary → tertiary → close.
- Trust hint is announced by screen reader at modal open (`aria-describedby`).
- All three buttons reachable with Tab; Enter activates focus; Esc = Skip.

**Stitch prompt cues**
- Modal sized identically to S02 (visual continuity).
- Primary button styling consistent with S02's "Place on shelf".
- Tertiary "Skip" button styled like a parchment link, not a CTA.

---

_(S04–S09 wireframes deferred until Journey A's first Stitch generation is reviewed.)_

---

## 6. Out of scope (this storyboard)

- Multiplayer / trade
- In-game currency / monetization
- Mobile gestures (deferred to v2)
- Server-side animations / streamed assets

---

## Next checkpoint

When Section 2 + 5 are filled for **S01–S03 (Journey A)**, invoke:

```
Skill: stitch-design
```

Feed it Sections 1 (premise), 2.A (journey), and 5.S01/S02/S03 (wireframes). Stitch returns a coherent design system seed for the first three screens. Save outputs under `docs/SCREENS/`.
