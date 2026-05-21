# M4 PlayerSetup — agent-browser dogfood report

> **Milestone:** PRP 3 §A M4 — STITCH: PlayerSetup (S02) + matchStore
> **Issue:** #149 (closes — second half; M3 closed via #159)
> **Branch:** `feat/cardshed-player-setup`
> **UTC:** 20260521T202659Z
> **Viewport:** 1440 × 900
> **URL:** http://localhost:4343/
> **Validator:** `agent-browser` (CLI) — Ubuntu 26.04 with `--no-sandbox,--disable-dev-shm-usage`

## Acceptance gates (PRP 3 §M4 lines 776–793)

| Gate | Result | Evidence |
|------|--------|----------|
| `Skill: stitch-design` → `docs/SCREENS/player-setup.md` committed | ✅ | `docs/SCREENS/player-setup.md` + `docs/DECISIONS/2026-05-21-stitch-run-3.md` |
| Stitch provenance recorded | ✅ | DS-1 asset ID propagated via `designSystem` parameter; third independent screen confirms DS-1 propagates cleanly |
| `apps/ui/src/features/lobby/PlayerSetup.tsx` implemented | ✅ | Presentational, DS-1 tokens via CSS vars, no invented hex colors |
| `apps/ui/src/state/matchStore.ts` implemented | ✅ | zustand store wrapping `@cardshed/core.startNewRound` |
| Click "Play" advances to PlayerSetup | ✅ | `02-player-setup-empty-1440x900.png` |
| Enter 3 names → Start enabled, `matchStore.match` is valid `MatchState` | ✅ | `03-player-setup-3-names-1440x900.png` + matchStore unit test |
| Enter 4 names → Start enabled, `matchStore.match.players.length === 4` | ✅ | `04-player-setup-4-names-advanced-1440x900.png` + matchStore unit test |
| < 3 names → Start disabled | ✅ | `07-player-setup-1-name-disabled-1440x900.png` (1 name); also `02-player-setup-empty-1440x900.png` (0 names) |
| > 4 names → rejected | ✅ | `matchStore.test.ts` — "rejects more than 4 names" |
| Seed via `crypto.getRandomValues()` ONCE, outside `@cardshed/core` | ✅ | `matchStore.ts` `generateMatchSeed()` — single `crypto.getRandomValues(new Uint32Array(1))[0]` call; PlayerSetup reuses via default prop |
| Match state throttled to round boundaries in localStorage | ⏭️ | Persistence deferred to M5+ when round boundaries are observable — see `docs/DECISIONS/2026-05-21-stitch-run-3.md` |
| `agent-browser` → `dogfood-output/<utc>/m4-setup/` | ✅ | 7 screenshots in this directory |
| No hand-rolled UI / invented colors / `Math.random` | ✅ | Stitch-origin screen, DS-1 tokens only, `crypto.getRandomValues` for seed |
| `npm run lint` green | ✅ | `eslint . --max-warnings 0` clean |
| `npm run build` green (`tsc -b && vite build`) | ✅ | 12.16 kB CSS, 178.69 kB JS, 0 warnings |
| `npm test` green | ✅ | 7/7 tests pass in `matchStore.test.ts` |
| Zero console errors | ✅ | Only Vite HMR debug + React-DevTools info |

## Verification flow

1. `npm run dev` boots at `http://localhost:4343/`.
2. agent-browser opens at 1440 × 900 viewport.
3. **Snapshot 1** — initial MainMenu render (sanity check that M3 still works):
   ```
   - heading "CARD SHED" [level=1]
   - navigation "Main menu actions"
     - button "Play"
     - button "Rules"
     - button "Settings"
   ```
4. Screenshot `01-mainmenu-1440x900.png` captured.
5. Click `Play` (ref `@e4`) → routes to PlayerSetup.
6. **Snapshot 2** — empty PlayerSetup:
   ```
   - sectionheader
     - button "Back to main menu"
   - heading "WHO'S PLAYING?" [level=1]
   - LabelText "PLAYER 1" → textbox "PLAYER 1"
   - LabelText "PLAYER 2" → textbox "PLAYER 2"
   - LabelText "PLAYER 3" → textbox "PLAYER 3"
   - LabelText "PLAYER 4" → textbox "PLAYER 4" + button "Remove player 4"
   - button "ADVANCED" [expanded=false]
   - status "ENTER AT LEAST 3 NAMES TO START"
   - button "START MATCH" [disabled]
   ```
7. Screenshot `02-player-setup-empty-1440x900.png` captured. **Start is disabled, validation visible.**
8. Type `"Ada"` → P1, `"Bo"` → P2, `"Cy"` → P3.
9. **Snapshot 3** — Start no longer has `[disabled]`, the validation status still has the text but its opacity is 0 (DOM stays stable so the button doesn't shift). Screenshot `03-player-setup-3-names-1440x900.png` captured.
10. Type `"Di"` → P4. Click `ADVANCED` (ref `@e9`) → disclosure expands.
11. **Snapshot 4** — Advanced panel shows:
    ```
    - StaticText "RNG SEED"
    - code "0x32ed6430"       ← real crypto.getRandomValues output
    - button "RANDOMIZE"
    ```
    Screenshot `04-player-setup-4-names-advanced-1440x900.png` captured.
12. Click `START MATCH` (ref `@e10`) → routes to table placeholder.
13. **Snapshot 5** — placeholder screen:
    ```
    - heading "MATCH TABLE" [level=2]
    - paragraph "Coming at M5 (S03)."
    - button "BACK TO MENU"
    ```
    Screenshot `05-table-placeholder-1440x900.png` captured.
14. Click `BACK TO MENU` (ref `@e3`) → MainMenu restored, `matchStore.reset()` cleared the state.
15. Screenshot `06-back-to-mainmenu-after-start-1440x900.png` captured.
16. Click `Play` again → PlayerSetup re-mounts empty.
17. Type `"Only One"` into P1 (single name).
18. **Snapshot 7** — `STATIC MATCH [disabled]` + `ENTER AT LEAST 3 NAMES TO START` validation visible. Screenshot `07-player-setup-1-name-disabled-1440x900.png` captured.

## matchStore unit-test evidence

`apps/ui/src/state/matchStore.test.ts` — 7/7 pass:

```
✓ matchStore.startMatch
  ✓ produces a 3-player MatchState from 3 names
  ✓ produces a 4-player MatchState from 4 names
  ✓ rejects fewer than 3 names
  ✓ rejects more than 4 names
  ✓ the same seed produces an identical MatchState (replay invariant)
✓ generateMatchSeed
  ✓ returns a 32-bit unsigned integer
  ✓ returns distinct values across calls (probabilistic)
```

The replay-invariant test is the load-bearing one — it confirms the seed flows through `matchStore` → `@cardshed/core.startNewRound` byte-identically, which is the foundation for the PRP 3 replay/anti-cheat goals.

## Console output (full)

```
[debug] [vite] connecting...
[debug] [vite] connected.
[info]  Download the React DevTools for a better development experience
```

Zero errors. Zero warnings. No 404s. No font loading failures (Google Fonts CDN reachable at run time).

## Files produced

```
@lab/ll-CARDSHED/dogfood-output/20260521T202659Z/m4-setup/
├── 01-mainmenu-1440x900.png                              (M3 sanity)
├── 02-player-setup-empty-1440x900.png                    (0 names — Start disabled, validation visible)
├── 03-player-setup-3-names-1440x900.png                  (3 names — Start enabled, validation hidden)
├── 04-player-setup-4-names-advanced-1440x900.png         (4 names + Advanced expanded with real seed)
├── 05-table-placeholder-1440x900.png                     (Start routes to M5 placeholder)
├── 06-back-to-mainmenu-after-start-1440x900.png          (back navigation restores MainMenu)
├── 07-player-setup-1-name-disabled-1440x900.png          (1 name — Start still disabled)
└── report.md                                             (this file)
```

## Visual fidelity vs Stitch source

Side-by-side check between `.stitch/designs/S02-player-setup.png` (Stitch mockup, 2560 px source) and `04-player-setup-4-names-advanced-1440x900.png` (running implementation, 1440 px capture):

| Element | Match? | Notes |
|---------|--------|-------|
| Felt background gradient | ✅ | Inherited from `body` style |
| ◀ MAIN MENU back link (top-left) | ✅ | Unicode ◀ instead of Material Symbols `arrow_back_ios` (decision doc) |
| Header CARD SHED caption | ⏭️ | Skipped — single h1 per route, redundant chrome on a pre-match screen |
| WHO'S PLAYING? h1 | ✅ | Playfair Display 36 / 700, uppercase, ink color |
| Player N labels | ✅ | Inter 12 / 600, uppercase, muted color |
| Input rows (56 px tall) | ✅ | surface-low fill, outline-variant border, lg radius |
| Focus ring (teal) | ✅ | Switches border + 1 px ring to `var(--color-legal)` on focus |
| Remove button on P4 | ✅ | Ghost style; hover → danger color; clears the field |
| ▼ ADVANCED toggle | ✅ | Unicode ▼/▲ instead of Material Symbols `arrow_drop_down` |
| Seed code chip + RANDOMIZE | ✅ | Real `crypto.getRandomValues` seed, teal text on surface-low pill |
| Validation message | ✅ | `var(--color-danger)` uppercase; opacity toggles to keep button anchored |
| START MATCH (enabled) | ✅ | Gold pill, glow, hover scale 1.02 |
| START MATCH (disabled) | ✅ | surface-high fill, outline-variant text, no glow, cursor not-allowed |
| Footer (v0.x · MVP · hot-seat browser) | ✅ | Pipe-separated, 40% opacity |
| `© 2024 CARD SHED v1.0.4-beta. Tactical Precision Engine.` ornament | ⏭️ | Skipped — same reason as M3's `v1.0.4 Tournament Mode Active` line |
| Material Symbols Outlined font loads | ⏭️ | Skipped — defer to S09/S10 at M11 (decision doc) |
| Fanned-cards background motif | ✅ | Identical lower-left motif to S01 (same component pattern, duplicated) |

## What this PR does NOT cover

- **M5 Table render (S03)** — Start routes to a labelled placeholder, not a real Table. `matchStore.match` IS populated, but no consumer renders it yet.
- **M5 LocalDispatcher + action handling** — there's no `submitAttack` / `submitBeat` / `stopDefending` UI surface yet.
- **localStorage persistence of `MatchState`** — deferred to M5+ (round-boundary throttle).
- **Mobile viewport** — M13 responsive sweep.
- **Real motion tokens** — M14 ships framer-motion enter/exit on cards.

## Next

Mark M4 ✅. Close #149. Next sub-issue: `#147` (M5 + M6) — Table render + Privacy splash. Per the open question in PRP 3 §"Cross-PRP Contradictions Flagged", lock NEW #6–#10 in a doc-only PR before M5 starts (NEW #10 affects M5 directly, NEW #9 affects the data model M5 touches).
