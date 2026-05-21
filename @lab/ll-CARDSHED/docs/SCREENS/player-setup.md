# S02 — PlayerSetup

> **Status:** Stitch-origin, implemented as `apps/ui/src/features/lobby/PlayerSetup.tsx`.
> **DS version:** DS-1.
> **Engine state owned:** none directly — the Start callback bubbles `(players, seed)` upward; the App-level `matchStore` owns the `MatchState` produced by `@cardshed/core.startNewRound`.

## Storyboard reference

- `docs/STORYBOARD.md` §3 (inventory row S02)
- `docs/STORYBOARD.md` §5 (S02 wireframe)
- `PRPs/cardshed-03-experience-prp.md` §A (M4 milestone, lines 776–793) + §B (screen inventory)

## Stitch provenance

| Field | Value |
|-------|-------|
| Project | `projects/4083518914509964664` ("ll-CARDSHED — MVP hot-seat") |
| Screen | `projects/4083518914509964664/screens/956dbc597742437da0c8c3309f3e0503` ("Player Setup — CARD SHED") |
| Design system | `assets/a70557bcdeed4f9ca600d28ffca0d467` ("Tournament Card Elite" / DS-1) — propagated via `designSystem` parameter |
| Source HTML | `.stitch/designs/S02-player-setup.html` (~13 KB) |
| Source PNG | `.stitch/designs/S02-player-setup.png` (~59 KB, 2560 × 2714 source res) |
| UTC | 2026-05-21 |
| Decision doc | [`docs/DECISIONS/2026-05-21-stitch-run-3.md`](../DECISIONS/2026-05-21-stitch-run-3.md) |

## Component contract

`PlayerSetup` is a stateless-shape presentational component. It owns local form state (name strings, seed value, advanced-disclosure toggle) but holds no match state — the Start callback hands `(players, seed)` up to `App.tsx`, which routes it into `matchStore.startMatch`.

```tsx
import { PlayerSetup } from "./features/lobby/PlayerSetup";

<PlayerSetup
  onStart={({ players, seed }) => {
    // App.tsx calls matchStore.startMatch({ players, seed }) here
  }}
  onBack={() => /* navigate back to MainMenu */}
  version="v0.x"
/>
```

| Prop | Type | Required | Notes |
|------|------|----------|-------|
| `onStart` | `(in: { players: string[]; seed: number }) => void` | yes | `players` is the trimmed non-empty subset of inputs (length 3 or 4). `seed` is a 32-bit unsigned integer from `crypto.getRandomValues`. |
| `onBack` | `() => void` | yes | App-level decides whether to reset the match before navigating. |
| `generateSeed` | `() => number` | no | Test injection. Defaults to `generateMatchSeed` (one-shot `crypto.getRandomValues(new Uint32Array(1))[0]`). |
| `version` | `string` | no, default `"v0.x"` | Footer chip. |

## Layout regions (1440 × 900 desktop canonical)

```
┌──────────────────────────────────────────────────────────────┐
│ ◀ MAIN MENU                                                  │  ← back link, top-left
│                                                              │
│                                                              │
│                      WHO'S PLAYING?                          │  ← h1 (Playfair 36 / 700)
│                                                              │
│   PLAYER 1  ┌──────────────────────────────────┐             │
│             │  (input)                         │             │
│             └──────────────────────────────────┘             │
│   PLAYER 2  ┌──────────────────────────────────┐             │
│             │  (input)                         │             │
│             └──────────────────────────────────┘             │
│   PLAYER 3  ┌──────────────────────────────────┐             │
│             │  (input)                         │             │
│             └──────────────────────────────────┘             │
│   PLAYER 4  ┌──────────────────────────────────┐  Remove     │
│             │  (input, optional)               │             │
│             └──────────────────────────────────┘             │
│                                                              │
│                       ▼ ADVANCED                             │
│                                                              │
│             Enter at least 3 names to start                  │  ← validation slot (h-5)
│                                                              │
│                  ┌─────────────────────┐                     │
│                  │     START MATCH     │  ← gold pill        │
│                  └─────────────────────┘                     │
│  ╱╱╱╱                                                        │
│ ╱╱╱╱╱                                                        │  ← fanned-cards motif
│╱╱╱╱╱╱                                                        │     (same as S01)
│                                                              │
│                  v0.x  ·  MVP  ·  hot-seat browser           │
└──────────────────────────────────────────────────────────────┘
```

Advanced expanded:

```
                     ▲ ADVANCED
       ┌──────────────────────────────────────────────────┐
       │  RNG SEED   0x4a2c88f1   [ RANDOMIZE ]           │
       └──────────────────────────────────────────────────┘
```

## Token consumption (DS-1)

| UI element | DS-1 token |
|------------|------------|
| Page background | inherited from `body` (`radial-gradient` over `--color-felt-glow` → `--color-felt-base` → `--color-bg-page`) |
| Back-link "◀ Main menu" | `var(--font-body)` 12px/600 uppercase, `var(--color-ink-muted)` @ 0.7 opacity |
| Page title "WHO'S PLAYING?" | `var(--font-display)` 36px/700 + `letter-spacing: 0.05em` + `var(--color-ink)` |
| Player N label | `var(--font-body)` 12px/600 uppercase + `var(--color-ink-muted)` |
| Input field | `bg var(--color-surface-low)`, `border var(--color-outline-variant)`, `radius var(--radius-md)`, `text var(--color-ink)`; focus swaps border + ring to `var(--color-legal)` (1px) |
| Remove button (P4) | ghost (transparent + no border), `var(--color-ink-muted)` text, hover `var(--color-danger)` |
| Advanced toggle | `var(--font-body)` 12px/600 uppercase, `var(--color-ink-muted)` |
| Advanced panel | `bg var(--color-surface-highest)` @ 0.95 + `var(--radius-md)` |
| RNG seed code | `bg var(--color-surface-low)`, `radius var(--radius-sm)`, `text var(--color-legal)` (semantic: same color as the focus / "valid" indicator) |
| Validation message | `var(--color-danger)` uppercase 12px/600 |
| Start match (enabled) | `bg var(--color-accent)`, `text var(--color-accent-ink)`, `radius var(--radius-pill)`, glow `0 0 24px rgba(238,152,0,0.3)` |
| Start match (disabled) | `bg var(--color-surface-high)`, `text var(--color-outline-variant)`, no glow, `cursor: not-allowed` |
| Footer dividers | 1×12px bars in `var(--color-outline-variant)` |
| Fanned cards | `bg var(--color-ink-strong)`, `border var(--color-outline-variant)`, `radius var(--radius-lg)` — identical to S01 |

No inline hex colors. No bespoke spacing. Every value above is sourced from `.stitch/DESIGN.md` §9 → `apps/ui/src/index.css`.

## Material-3-to-DS-1 token bridge (what changed from Stitch's raw HTML)

Stitch's `tailwind.config` declares Material-3-style names. DS-1 renames them to domain names. The implementation consumes DS-1 directly via CSS variables; the bridge is informational.

| Stitch (M3) | DS-1 | Hex |
|-------------|------|-----|
| `bg-secondary-container` (PLAY/START fill) | `--color-accent` | `#ee9800` |
| `text-on-secondary-container` | `--color-accent-ink` | `#5b3800` |
| `bg-surface-container-low` (inputs) | `--color-surface-low` | `#191c1e` |
| `bg-surface-container-high` (Start disabled) | `--color-surface-high` | `#272a2c` |
| `bg-surface-container-highest` (advanced panel) | `--color-surface-highest` | `#323537` |
| `border-outline-variant` (inputs, dividers) | `--color-outline-variant` | `#434846` |
| `text-on-surface` (input text, page title) | `--color-ink` | `#e0e3e5` |
| `text-on-surface-variant` (labels, back link) | `--color-ink-muted` | `#c3c8c5` |
| `text-tertiary` (seed code, focus ring) | `--color-legal` | `#6bd8cb` |
| `text-error` (validation msg) | `--color-danger` | `#ffb4ab` |
| `bg-primary` (decorative cards) | `--color-ink-strong` | `#bec9c4` |
| `border-outline` (decorative card border) | `--color-outline-variant` | `#434846` |

## Accessibility

- `WHO'S PLAYING?` is a single semantic `<h1>` — single h1 per route.
- Each `Player N` label is a real `<label htmlFor>` bound to its input.
- Tab order: P1 → P2 → P3 → P4 → Remove (when shown + P4 has text) → Advanced toggle → (if open) Randomize → Start match → Back link.
- `Start match` while invalid is `aria-disabled="true"` with `aria-describedby` pointing to the live validation slot. The slot itself is `role="status" aria-live="polite"` so a screen reader reads the rule the moment Start is reached without meeting the threshold.
- Inputs are 56 px tall — well above the WCAG 2.1 44 × 44 minimum.
- The decorative fanned cards stay `aria-hidden="true"` (visual only).
- The advanced disclosure uses native `aria-expanded` + `aria-controls`.
- Hover styles are applied via direct inline handlers (consistent with the `MainMenu` pattern; no Tailwind hover utility for DS-1 tokens until M5's wrapper components decide otherwise).

## Engine coupling

- The seed is generated **once, outside `@cardshed/core`**, via `crypto.getRandomValues(new Uint32Array(1))[0]`. The component owns the seed state so Randomize can re-roll without leaving the screen.
- The Start callback hands `(players, seed)` upward. `App.tsx` calls `matchStore.startMatch({ players, seed })`, which in turn calls `@cardshed/core.startNewRound(null, seed, { matchId, players })`.
- `matchStore` packages the player list as `PlayerSetup[]` of `{ id, name }` (`id = "p1" | "p2" | "p3" | "p4"`, `matchId = "m-<seed-hex>"`). The core is the source of truth for the resulting `MatchState`.

## What this PR does NOT do

- **Does not render the Table screen** — Start routes to a labelled placeholder "Match table — Coming at M5 (S03)". M5 owns the real Table render against `createPrivateView`.
- **Does not persist the MatchState to localStorage** — per PRP 3 M4 common-bug warning, persistence is throttled and lands with the Table screen (M5+) where round boundaries become observable.
- **Does not allow custom seed entry.** The advanced disclosure shows the current seed and offers Randomize. Allowing a typed seed is deferred — useful for bug-repro but not load-bearing for MVP.
- **Does not implement avatar/colour pickers.** Name-only roster — same as the storyboard direction.
- **Does not implement room codes / online sync.** Hot-seat MVP.

## Verification log

See `dogfood-output/<UTC>/m4-setup/`:

- `01-mainmenu-1440x900.png` — MainMenu before Play click (sanity check that M3 is still intact).
- `02-player-setup-empty-1440x900.png` — initial render (all inputs empty, Start disabled, validation visible).
- `03-player-setup-3-names-1440x900.png` — three names entered, Start enabled, validation hidden.
- `04-player-setup-4-names-advanced-1440x900.png` — four names + Advanced expanded, seed visible.
- `05-table-placeholder-1440x900.png` — Start click routes to the M5 placeholder.
- `report.md` — full agent-browser acceptance log.
