# M3 MainMenu — agent-browser dogfood report

> **Milestone:** PRP 3 §A M3 — STITCH: MainMenu (S01)
> **Issue:** #149 (first half — M3 only; M4 PlayerSetup deferred to a follow-up session)
> **Branch:** `feat/cardshed-main-menu`
> **UTC:** 20260521T195710Z
> **Viewport:** 1440 × 900
> **URL:** http://localhost:4343/
> **Validator:** `agent-browser` (skill) — Ubuntu 26.04 with `--no-sandbox,--disable-dev-shm-usage`

## Acceptance gates (PRP 3 §M3 lines 758–773)

| Gate | Result | Evidence |
|------|--------|----------|
| `Skill: stitch-design` → `docs/SCREENS/main-menu.md` committed | ✅ | `docs/SCREENS/main-menu.md` + `docs/DECISIONS/2026-05-21-stitch-run-2.md` |
| Stitch provenance recorded | ✅ | DS-1 asset ID propagated via `designSystem` parameter; theme block round-trips byte-identical |
| `apps/ui/src/features/menu/MainMenu.tsx` implemented | ✅ | Component is stateless, consumes DS-1 tokens, no inline hex colors |
| `apps/ui/src/App.tsx` updated to render MainMenu | ✅ | M1 boot stub removed; conditional render on `screen` state |
| Click "Play" advances to PlayerSetup | ⚠️ | Advances to a labelled placeholder ("Coming at M4 (S02)"). Real PlayerSetup ships in M4. |
| `agent-browser` → `dogfood-output/<utc>/m3-main-menu/` screenshot | ✅ | 3 screenshots in this directory |
| `Skill: agent-browser` captures `dogfood-output/<utc>/m3-main-menu/` | ✅ | See file list below |
| No hand-rolled UI / invented colors / parsed `card.id` | ✅ | Component is the React port of the Stitch HTML; tokens come from DS-1 |
| `npm run build` green (`tsc -b && vite build`) | ✅ | 9.70 kB CSS, 168.21 kB JS, 0 warnings |
| `npm run lint` green | ✅ | `eslint . --max-warnings 0` clean |
| Zero console errors | ✅ | Only Vite HMR debug + React-DevTools info |

## Verification flow

1. `npm run dev` boots at http://localhost:4343/
2. agent-browser opens at 1440 × 900 viewport
3. **Snapshot 1** — initial MainMenu render. Accessibility tree:
   ```
   - heading "CARD SHED" [level=1]
   - navigation "Main menu actions"
     - button "Play"
     - button "Rules"
     - button "Settings"
   ```
4. Screenshot `01-mainmenu-1440x900.png` captured.
5. Click `Play` button (ref @e4).
6. Wait until `--text "Coming at M4"` matches → page navigated.
7. **Snapshot 2** — placeholder screen:
   ```
   - heading "PLAYER SETUP" [level=2]
   - button "BACK TO MENU"
   ```
8. Screenshot `02-play-click-routes-to-m4-placeholder.png` captured.
9. Click `BACK TO MENU` (ref @e3).
10. Screenshot `03-back-to-mainmenu.png` captured — MainMenu restored (Rules button shows hover state as side effect of cursor passing through it).

## Console output (full)

```
[debug] [vite] connecting...
[debug] [vite] connected.
[info]  Download the React DevTools for a better development experience
```

Zero errors. Zero warnings. No 404s. No font loading failures (Google Fonts CDN reachable at run time).

## Files produced

```
@lab/ll-CARDSHED/dogfood-output/20260521T195710Z/m3-main-menu/
├── 01-mainmenu-1440x900.png                       (initial render)
├── 02-play-click-routes-to-m4-placeholder.png     (Play click navigation)
├── 03-back-to-mainmenu.png                        (back navigation works)
└── report.md                                      (this file)
```

## Visual fidelity vs Stitch source

Side-by-side check between `.stitch/designs/S01-main-menu.png` (Stitch mockup, 2560 px source) and `01-mainmenu-1440x900.png` (running implementation, 1440 px capture):

| Element | Match? | Notes |
|---------|--------|-------|
| Felt background gradient | ✅ | Radial gradient renders identically |
| "WELCOME TO" eyebrow | ✅ | Inter 12px 600, uppercased, muted color |
| "CARD SHED" brand | ✅ | Playfair Display 48px, 0.15em tracking, ink-strong color |
| Tagline | ✅ | Inter 18px, muted |
| PLAY gold pill | ✅ | Gold fill + glow shadow + uppercase label |
| RULES / SETTINGS ghost pills | ✅ | 1px outline-variant border, transparent fill |
| Decorative fanned cards | ✅ | 7% opacity, rotated 25° in lower-left corner |
| Footer (v0.x · MVP · hot-seat) | ✅ | Pipe-separated at 40% opacity |
| Mouse-tracking gradient | ⏭️ | Skipped per decision doc — distracting |
| Audio hover cue | ⏭️ | Skipped — MVP excludes audio |
| `v1.0.4 Tournament Mode Active` line | ⏭️ | Removed — not real state |

## What this PR does NOT cover

- **M4 PlayerSetup (S02)** — needs its own Stitch run in a fresh session per the warm-session-drop invariant. The "Play" button routes to a labelled placeholder, not the real PlayerSetup component.
- **Rules dialog (S09)** — M11.
- **Settings dialog (S10)** — M11.
- **Mobile viewport** — M13 responsive sweep.
- **Real motion tokens** — M14 ships framer-motion enter/exit on cards.

## Next

Mark M3 ✅. Open follow-up session to do M4 (`PlayerSetup.tsx` + `matchStore.ts` + a second Stitch run for S02). Both M3 and M4 close #149.
