# S01 — MainMenu

> **Status:** Stitch-origin, implemented as `apps/ui/src/features/menu/MainMenu.tsx`.
> **DS version:** DS-1.
> **Engine state owned:** none — pre-match landing.

## Storyboard reference

- `docs/STORYBOARD.md` §3 (inventory row S01)
- `docs/STORYBOARD.md` §5 (S01 wireframe)
- `docs/STORYBOARD.md` §1 (premise — drives the aesthetic anchor)
- `PRPs/cardshed-03-experience-prp.md` §B (screen inventory, M3 milestone, lines 758–773)

## Stitch provenance

| Field | Value |
|-------|-------|
| Project | `projects/4083518914509964664` ("ll-CARDSHED — MVP hot-seat") |
| Screen | `projects/4083518914509964664/screens/cb1645e2f8f84834914174930efbbfb6` ("Main Menu — CARD SHED") |
| Design system | `assets/a70557bcdeed4f9ca600d28ffca0d467` ("Tournament Card Elite" / DS-1) |
| Source HTML | `.stitch/designs/S01-main-menu.html` (9.5 KB) |
| Source PNG | `.stitch/designs/S01-main-menu.png` (166 KB, 2560 × 2714 source res) |
| UTC | 2026-05-21 |
| Decision doc | [`docs/DECISIONS/2026-05-21-stitch-run-2.md`](../DECISIONS/2026-05-21-stitch-run-2.md) |

## Component contract

`MainMenu` is a stateless presentational component.

```tsx
import { MainMenu, type MainMenuAction } from "./features/menu/MainMenu";

<MainMenu
  onAction={(action: MainMenuAction) => { /* "play" | "rules" | "settings" */ }}
  version="v0.x"
/>
```

| Prop | Type | Required | Notes |
|------|------|----------|-------|
| `onAction` | `(action: "play" \| "rules" \| "settings") => void` | yes | Caller owns routing. App.tsx delegates to its `screen` state. |
| `version` | `string` | no, default `"v0.x"` | Rendered into the footer chip. |

## Layout regions (1440 × 900 desktop canonical)

```
┌──────────────────────────────────────────────────────────────┐
│                  (felt radial gradient bg)                   │
│                                                              │
│                         WELCOME TO                           │  ← label-caps eyebrow
│                                                              │
│                       CARD  SHED                             │  ← display-lg brand (h1)
│                                                              │
│         A shifting-trump card game for three or four         │  ← body-lg tagline
│                          friends.                            │
│                                                              │
│                  ┌──────────────────┐                        │
│                  │       PLAY       │  ← gold pill, glow     │
│                  └──────────────────┘                        │
│                  ┌──────────────────┐                        │
│                  │      RULES       │  ← ghost pill          │
│                  └──────────────────┘                        │
│                  ┌──────────────────┐                        │
│                  │     SETTINGS     │  ← ghost pill          │
│                  └──────────────────┘                        │
│  ╱╱╱╱                                                        │
│ ╱╱╱╱╱                                                        │  ← fanned-cards motif
│╱╱╱╱╱╱                                                        │     (lower-left, 7% opacity)
│                                                              │
│                  v0.x  ·  MVP  ·  hot-seat browser           │  ← footer
└──────────────────────────────────────────────────────────────┘
```

## Token consumption (DS-1)

| UI element | DS-1 token |
|------------|------------|
| Page background | radial-gradient(`var(--color-felt-glow)` → `var(--color-felt-base)` → `var(--color-bg-page)`) |
| Eyebrow "WELCOME TO" | `var(--font-body)` 12px/600 + `letter-spacing: 0.05em` + `var(--color-ink-muted)` |
| Brand "CARD SHED" | `var(--font-display)` 48px/700 + `letter-spacing: 0.15em` + `var(--color-ink-strong)` |
| Tagline | `var(--font-body)` 18px/400 + `var(--color-ink-muted)` |
| Primary PLAY pill | `bg var(--color-accent)`, `color var(--color-accent-ink)`, `border-radius var(--radius-pill)`, glow `0 0 24px rgba(245,158,11,0.25)` |
| Ghost pill | `border var(--color-outline-variant)`, `color var(--color-ink)`, hover swaps to `bg var(--color-surface-high)` + `border var(--color-outline)` |
| Footer dividers | 1×12px bars in `var(--color-outline-variant)` |
| Fanned cards | `bg var(--color-ink-strong)`, `border var(--color-outline-variant)`, `border-radius var(--radius-lg)` |

No inline hex colors. No bespoke spacing. Every value above is sourced from `.stitch/DESIGN.md` §9 → `apps/ui/src/index.css`.

## Accessibility

- Brand-mark is a semantic `<h1>` — single h1 per route.
- Each button: `<button type="button">` with `aria-label` matching visible text.
- Tab order: PLAY → RULES → SETTINGS (DOM order).
- Buttons 280 × 56 px — well above the 44 × 44 WCAG 2.1 minimum.
- Focus ring: `focus-visible:outline-2 focus-visible:outline-offset-2` (Tailwind default ring color over felt background remains visible).
- Footer is `pointer-events-none` — purely informational, not interactive.
- Decorative fanned cards `aria-hidden="true"`.

## Engine coupling

**None.** S01 is pre-match. No `@cardshed/core` calls. The component is pure presentation.

## What this PR does NOT do

- **Does not implement RULES dialog** — that's S09, lands at M11. The Rules button routes to a placeholder.
- **Does not implement SETTINGS dialog** — that's S10, lands at M11. Settings button routes to a placeholder.
- **Does not wire Play to actual PlayerSetup** — PlayerSetup (S02) lands at M4. Play routes to a placeholder labelled "Coming at M4 (S02)".
- **Does not implement framer-motion animations** beyond Tailwind transitions — micro-interactions (hover scale, click scale) ship; named motion tokens (`--motion-snap`, `--motion-card-snap`) wire up at M14.
- **No `agent-browser` audio interaction logic** from the Stitch HTML — that was a commented-out demo; we don't ship audio in MVP.

## Verification log

See `dogfood-output/20260521T195710Z/m3-main-menu/`:

- `01-mainmenu-1440x900.png` — initial render.
- `02-play-click-routes-to-m4-placeholder.png` — Play click navigates correctly to the M4 placeholder.
- `03-back-to-mainmenu.png` — Back-to-menu navigation restores MainMenu state.
- `report.md` — full agent-browser acceptance log.
