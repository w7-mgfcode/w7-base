# Design System: CARD SHED

**Stitch project:** `projects/4083518914509964664` — "ll-CARDSHED — MVP hot-seat"
**Generated from:** S03 Table (canonical in-match screen) — Stitch screen `5ff3a87d9ffc4425a79c418d68be0b2e`
**Generated:** 2026-05-21 (UTC) — first Stitch run for cardshed
**Source seed:** `docs/STORYBOARD.md` §1 premise + §5 wireframes + `apps/core/src/core/types.ts` engine vocabulary
**DS version:** **DS-1**
**Owner of regenerations:** `Skill: stitch-design` only — see `.claude/rules/ui-design-pipeline.md` §2

> **Do not hand-edit tokens.** When the design needs to evolve, run `Skill: stitch-design` and bump the DS version. Every screen mockup under `docs/SCREENS/` is keyed to a specific DS version.

---

## 1. Visual theme

**One-line:** *a quiet tournament table — calm, focused, decisive.*

- **Aesthetic anchor:** card-game-first. Readability over decoration. The table is the protagonist, not the chrome.
- **References (positive):** *Hearthstone* clarity, *Slay the Spire* card legibility, *Threes!* snap.
- **References (negative):** no poker-felt cliché texture, no playing-card-house ornament, no Western-saloon kitsch, no luxury-museum hush (that's `@lab/ll-RELIQUARY`, deliberately distinct).
- **Mood:** the moment a defender is about to beat or stop. Quiet, weighted, never frantic.

## 2. Palette

Tokens are presented as `--name: value /* role */`. Every UI surface MUST source color from this list — no inline hex outside this file.

### 2.1 Felt + chrome (background + ink)

```css
--color-felt-base:           #1A2421; /* table felt (deep green-charcoal) */
--color-felt-glow:           #232d29; /* radial-gradient center on felt */
--color-bg-page:             #101415; /* page background outside the felt */
--color-surface-lowest:      #0b0f10; /* the deepest panel (e.g. trump chip cluster) */
--color-surface-low:         #191c1e; /* secondary surface (header background) */
--color-surface:             #1d2022; /* default container surface */
--color-surface-high:        #272a2c; /* raised chip / inactive opponent pill */
--color-surface-highest:     #323537; /* hover state for header buttons */
--color-surface-bright:      #363a3b; /* brightest surface — modal scrim contrast */
```

### 2.2 Ink (text + glyphs)

```css
--color-ink:                 #e0e3e5; /* default body text on dark surface */
--color-ink-strong:          #bec9c4; /* primary heading + brand-mark "CARD SHED" */
--color-ink-muted:           #c3c8c5; /* secondary text on surface */
--color-ink-faint:           #8d928f; /* tertiary, dividers, faint labels */
```

### 2.3 Accent — primary / "your turn" / defender highlight (gold)

```css
--color-accent:              #ee9800; /* the gold accent — defender pill, Stop CTA */
--color-accent-soft:         #ffb95f; /* hovered / fixed-dim variant of gold */
--color-accent-ink:          #5b3800; /* ink on top of accent surfaces */
--color-accent-on:           #472a00; /* deeper ink on accent (badge dots) */
--color-accent-fixed:        #ffddb8; /* tonal-fixed gold (extra-soft surface) */
```

### 2.4 Accent — secondary / "legal beat" / success (teal)

```css
--color-legal:               #6bd8cb; /* legal-counter highlight + attacker chip dot */
--color-legal-soft:          #89f5e7; /* hover / fixed-dim variant of teal */
--color-legal-ink:           #00201d; /* ink on teal surfaces */
--color-legal-surface:       #002723; /* container surface for teal-bg chips */
--color-legal-strong:        #1a998d; /* high-contrast teal text on dark */
```

### 2.5 Error / illegal / danger (warm red — NOT alarm crimson)

```css
--color-danger:              #ffb4ab; /* error text on dark */
--color-danger-soft:         #ffdad6; /* hover surface for danger */
--color-danger-strong:       #93000a; /* danger container background */
--color-danger-ink:          #690005; /* ink on danger surfaces */
```

### 2.6 Card face (always white — cards are always readable)

```css
--color-card-face:           #ffffff; /* card background — always */
--color-card-border:         #434846; /* outline-variant on idle card */
--color-card-ink-black:      #101415; /* ♠ ♣ glyphs + black ranks */
--color-card-ink-red:        #ef4444; /* ♥ ♦ glyphs + red ranks */
--color-card-back:           #1A2421; /* face-down card back (matches felt) */
```

### 2.7 Outlines + dividers

```css
--color-outline:             #8d928f; /* primary outline */
--color-outline-variant:     #434846; /* subtle divider / card border */
```

### 2.8 Suit semantics (colorblind-safe — color + glyph)

| Suit | Color token         | Glyph | Engine `Suit` enum |
|------|---------------------|-------|--------------------|
| Clubs    | `--color-card-ink-black` | ♣ | 0 |
| Diamonds | `--color-card-ink-red`   | ♦ | 1 |
| Hearts   | `--color-card-ink-red`   | ♥ | 2 |
| Spades   | `--color-card-ink-black` | ♠ | 3 |

Every card MUST render both a color AND a glyph. Never color-only.

## 3. Typography

Two families. No third family without a new Stitch run.

```css
--font-display:  "Playfair Display", "Iowan Old Style", "Palatino", serif; /* brand-mark + result banners */
--font-body:     "Inter", "Segoe UI", system-ui, sans-serif;               /* everything else */
--font-card:     "Inter", system-ui, sans-serif;                           /* card ranks (bold tabular) */
```

### 3.1 Type scale (load-bearing — match Stitch's choices)

| Token            | Size  | Line  | Weight | Tracking | Family   | Use                                    |
|------------------|-------|-------|--------|----------|----------|----------------------------------------|
| `--type-display` | 48px  | 1.2   | 700    | 0        | display  | brand-mark "CARD SHED"; result banners |
| `--type-headline`| 24px  | 1.4   | 600    | 0        | display  | section heads (Pending Attack, Who's playing) |
| `--type-body-lg` | 18px  | 1.6   | 400    | 0        | body     | dialog body copy, RulesHelp prose      |
| `--type-body`    | 14px  | 1.5   | 400    | 0        | body     | default UI text                        |
| `--type-card`    | 28px  | 1.0   | 700    | 0        | card     | rank glyph on every card               |
| `--type-label`   | 12px  | 1.0   | 600    | 0.05em   | body     | UPPERCASE CHIP LABELS, phase tags      |

Brand-mark "CARD SHED" is always uppercased with **widest tracking** (`letter-spacing: 0.15em`+).

## 4. Geometry — spacing + radius

```css
--space-unit:           8px;   /* base step — every other space is a multiple */
--space-gutter:         16px;  /* page padding + header padding-x */
--space-panel-padding:  24px;  /* internal padding for panels (pending-attack, dialogs) */
--space-table-margin:   32px;  /* outer breathing room around the felt arena */
--space-card-overlap:   -40px; /* horizontal overlap when fanning the hand */
```

```css
--radius-sm:    0.25rem;  /* 4px — small chips, hairline cards */
--radius-md:    0.5rem;   /* 8px — buttons, chips */
--radius-lg:    0.75rem;  /* 12px — cards (the card itself) */
--radius-xl:    40px;     /* the felt-arena recessed rectangle */
--radius-pill:  9999px;   /* opponent chips, primary action buttons */
```

Card aspect-ratio is locked: **80 × 112 px** on desktop (≈ 1 : 1.4). Mobile may scale ≤ ×0.85 keeping the same ratio.

## 5. Elevation — shadows

```css
--shadow-card:        0 8px 16px rgba(0, 0, 0, 0.30);  /* resting card */
--shadow-card-active: 0 12px 24px rgba(0, 0, 0, 0.50); /* hovered / selected card */
--shadow-glow-defender: 0 0 12px rgba(245, 158, 11, 0.30); /* active-defender chip ring */
--shadow-panel-inset: inset 0 4px 12px rgba(0, 0, 0, 0.50); /* recessed felt panel */
```

No glassmorphism. No neumorphism. The pending-attack panel uses **inset** shadow only.

## 6. Motion

| Token                  | Value          | Easing       | When                                            |
|------------------------|----------------|--------------|-------------------------------------------------|
| `--motion-snap`        | 140ms          | ease-out     | button press, chip toggle                       |
| `--motion-base`        | 200ms          | ease-out     | card lift, panel reveal                         |
| `--motion-deliberate`  | 320ms          | ease-out     | screen transition, dialog open                  |
| `--motion-card-snap`   | 220ms          | spring 280/22| card-play overshoot (framer-motion `spring`)    |
| `--motion-defender-pulse` | 3000ms       | ease-in-out  | active-defender ring pulse                      |

Honor `prefers-reduced-motion: reduce` — collapse `--motion-card-snap` to a 100ms opacity fade.

## 7. Components — domain vocabulary

These are the named building blocks. Every screen composes from this list; no novel components without a new Stitch run.

### 7.1 Card

- Surface: `--color-card-face` (always white). Border: `--color-card-border` (1px).
- Radius: `--radius-lg`. Size: 80 × 112 desktop.
- Shadow: `--shadow-card` idle → `--shadow-card-active` on hover/selected.
- Top-left + bottom-right (rotated 180°): rank + suit glyph in suit color.
- Center: large 4xl suit glyph in suit color.
- States: `normal | hovered | selected | legal | illegal | disabled | trump-suit | recently-played | discarding | face-down`.
- `selected` + `legal`: 2px border in `--color-accent` (gold).
- `illegal`: opacity 0.5, no hover lift, no border.
- `recently-played`: framer-motion enter via `--motion-card-snap`.

### 7.2 Player chip (opponent bar)

- Surface: `--color-surface-high`. Border: `--color-outline-variant`.
- Padding-x: 16px / padding-y: 6px / radius: `--radius-pill`.
- Inside: 8px dot (role-colored) + label `Name · count (role)` in `--type-label`.
- **Active role** (current attacker OR defender): swap surface for `--color-accent` family + `--shadow-glow-defender` + pulsing dot.
- Dot color map: defender → `--color-accent-on`, attacker → `--color-legal`, waiting → `--color-outline`.

### 7.3 State chip (trump / deck / discard)

- Surface: `--color-surface-lowest` at 80% opacity over felt.
- Border: `--color-outline-variant` at 30% opacity.
- Padding: 12px / radius: `--radius-md`.
- Inside: stacked — big glyph or number (top, `--type-headline`) + caption (bottom, `--type-label`, uppercase).

### 7.4 Pending-attack panel

- Outer: 800 × 400 desktop. Radius: `--radius-xl` (40px).
- Shadow: `--shadow-panel-inset`. Border: 1px white at 5% opacity.
- Header label: `--type-headline` ink at 40% opacity, uppercase, tracking 0.2em ("PENDING ATTACK").
- Sub-label: `--type-label` ink-muted at 50% opacity ("Awaiting Defense · Defender: Bo").
- Unbeaten cards: each ringed with a 2px dashed `--color-accent` at 50% opacity, 4px outset.
- Beaten pairs: counter card rotated 12° + translated (4, 2) px, z-index above the attack card.

### 7.5 Action button (pill)

- Pill (`--radius-pill`), padding-x: 24px, padding-y: 10px, `--type-body` weight 600.
- **Primary** ("Send attack", "Stop", "Play"): surface `--color-accent`, ink `--color-accent-on`.
- **Secondary** ("Clear", "Pass", "Main menu"): surface `--color-surface-high`, ink `--color-ink`.
- **Destructive-confirm** ("Reset match" 2nd tap): surface `--color-danger-strong`, ink `--color-danger-soft`.
- Active state: `transform: scale(0.95)` via `--motion-snap`.

### 7.6 Icon button (header)

- 40 × 40 px, circular (`--radius-pill`), no surface idle, hover surface `--color-surface-highest`.
- Material Symbols Outlined, weight 400, optical size 24, ink `--color-ink-strong`.

### 7.7 Dialog (Radix Dialog overlay)

- Backdrop: `--color-bg-page` at 60% opacity + `backdrop-filter: blur(6px)`.
- Surface: `--color-surface-high` with `--shadow-card-active` at higher intensity.
- Radius: `--radius-lg`. Padding: `--space-panel-padding`.
- Header: `--type-headline` + close-X icon-button top-right.
- Tabs (RulesHelp): Radix Tabs, active tab gets a 2px `--color-accent` bottom-border.

### 7.8 Privacy splash (full-screen)

- Surface: `--color-bg-page` (opaque, blocks any leak).
- Center: `--type-display` ink-strong: "Pass device to {name}".
- Below: a single primary pill ("I'm {name} — reveal").
- No other UI surface visible — no header, no chips, no hand.

## 8. Voice + copy

- **Imperative, short, lowercase-leaning.** "Send attack" not "Submit Attack". "Stop" not "Stop Defending". "Pass device to Bo" not "It is now Bo's turn — please pass the device".
- **Engine-domain verbs verbatim.** "Awaiting Attack" / "Awaiting Defense" / "Resolving" / "Round Ended" / "Match Ended". Never invent synonyms like "Your move" — use the engine state.
- **Validation errors are direct, not apologetic.** "Invalid combo: ATTACK_NO_TWO_PAIRS — 5-card attack needs two pairs of distinct ranks." No "Sorry,".
- **Tooltips warn, don't scold.** "Unbeaten cards will go to your hand. Tap Stop again to confirm."

## 9. Tailwind v4 `@theme` block (drop into `apps/ui/src/index.css`)

> **Authoritative source.** When `apps/ui/src/index.css` changes, the diff against this block MUST be zero outside of comments. Run `Skill: stitch-design` to regenerate both at once.

```css
@import "tailwindcss";

@theme {
  /* —— color: felt + chrome —— */
  --color-felt-base: #1A2421;
  --color-felt-glow: #232d29;
  --color-bg-page: #101415;
  --color-surface-lowest: #0b0f10;
  --color-surface-low: #191c1e;
  --color-surface: #1d2022;
  --color-surface-high: #272a2c;
  --color-surface-highest: #323537;
  --color-surface-bright: #363a3b;

  /* —— color: ink —— */
  --color-ink: #e0e3e5;
  --color-ink-strong: #bec9c4;
  --color-ink-muted: #c3c8c5;
  --color-ink-faint: #8d928f;

  /* —— color: accents —— */
  --color-accent: #ee9800;
  --color-accent-soft: #ffb95f;
  --color-accent-ink: #5b3800;
  --color-accent-on: #472a00;
  --color-legal: #6bd8cb;
  --color-legal-soft: #89f5e7;
  --color-legal-ink: #00201d;
  --color-legal-strong: #1a998d;
  --color-danger: #ffb4ab;
  --color-danger-soft: #ffdad6;
  --color-danger-strong: #93000a;
  --color-danger-ink: #690005;

  /* —— color: card —— */
  --color-card-face: #ffffff;
  --color-card-border: #434846;
  --color-card-ink-black: #101415;
  --color-card-ink-red: #ef4444;
  --color-card-back: #1A2421;

  /* —— color: outlines —— */
  --color-outline: #8d928f;
  --color-outline-variant: #434846;

  /* —— typography —— */
  --font-display: "Playfair Display", "Iowan Old Style", "Palatino", serif;
  --font-body: "Inter", "Segoe UI", system-ui, sans-serif;
  --font-card: "Inter", system-ui, sans-serif;

  /* —— spacing —— */
  --spacing-unit: 8px;
  --spacing-gutter: 16px;
  --spacing-panel-padding: 24px;
  --spacing-table-margin: 32px;

  /* —— radius —— */
  --radius-sm: 0.25rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;
  --radius-xl: 40px;
  --radius-pill: 9999px;
}
```

## 10. Provenance

| # | UTC | Stitch project | Screen | DS version | Prompt summary | Decision doc |
|---|-----|----------------|--------|------------|----------------|--------------|
| 1 | 2026-05-21 | `projects/4083518914509964664` | `screens/5ff3a87d9ffc4425a79c418d68be0b2e` (S03 Table, 2880×2048 source → 1440×900 viewport) | **DS-1** | Canonical in-match screen — establishes felt+gold+teal palette, Playfair+Inter type pair, 80×112 card geometry, pending-attack panel as the felt's recessed hot zone. | [`docs/DECISIONS/2026-05-21-stitch-run-1.md`](../docs/DECISIONS/2026-05-21-stitch-run-1.md) |
