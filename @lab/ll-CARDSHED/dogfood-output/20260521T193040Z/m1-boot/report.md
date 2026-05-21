# M1 Boot — agent-browser dogfood report

> **Milestone:** PRP 3 §A M1 — SCAFFOLD apps/ui
> **Issue:** #148 (chained under umbrella #146)
> **Branch:** `feat/cardshed-ui-scaffold`
> **UTC:** 20260521T193040Z
> **Viewport:** 1440 × 900
> **URL:** http://localhost:4343/
> **Validator:** `agent-browser` (skill) — Ubuntu 26.04 with `--no-sandbox,--disable-dev-shm-usage`

## Acceptance gates (PRP 3 §M1)

| Gate | Result | Evidence |
|------|--------|----------|
| `npm install` succeeds | ✅ | 271 packages, 0 errors |
| `npm run build` green (`tsc -b && vite build`) | ✅ | `dist/index.html` + 143.68 kB JS bundle |
| `npm run lint` green (`eslint . --max-warnings 0`) | ✅ | 0 errors, 0 warnings |
| `npm run dev` serves on :4343 | ✅ | Vite 5.4.21 — `host: true`, `port: 4343` |
| Boot screen renders "CARD SHED — MVP M1" | ✅ | See `boot-screen-1440x900.png` |
| `agent-browser` evidence captured | ✅ | This report + screenshot |
| Zero console errors | ✅ | Only Vite HMR-debug + React-DevTools info |

## Smoke check — `@cardshed/core` workspace link

- `App.tsx` calls `createDeck()` from `@cardshed/core`.
- Rendered output reads **`deck: 52 cards`** — matches the conservation invariant from PRP 2 (`apps/core/.claude/rules/core-determinism.md` §3).
- Proves the `file:../core` link in `apps/ui/package.json` resolves correctly through Vite's bundler resolution.

## Console output (full)

```
[debug] [vite] connecting...
[debug] [vite] connected.
[info]  Download the React DevTools for a better development experience
```

Zero errors. Zero warnings. No 404s, no missing assets, no React StrictMode complaints.

## Accessibility snapshot

```
- generic "CARD SHED — MVP M1Scaffold boots..." [ref=e1] clickable
  - heading "CARD SHED — MVP M1" [level=1, ref=e2]
```

Heading is an `<h1>` and is in the document landmark structure (`<main>`).

## What was NOT verified (deferred per scope)

- **No design tokens** — index.css ships placeholder `@theme` values that will be **completely replaced** by M2's `Skill: stitch-design` output. Per `.claude/rules/ui-design-pipeline.md` §5: "inventing tokens" is forbidden past the placeholder phase.
- **No screens** — every screen lands at M3+ via Stitch. No hand-rolled UI past this stub boot screen.
- **No mobile viewport** — first storyboard wireframe (M2) determines whether mobile gets captured.
- **No game actions** — M1 has no engine wiring beyond the smoke `createDeck()` call. Actions land at M5+.

## Files produced

```
@lab/ll-CARDSHED/dogfood-output/20260521T193040Z/m1-boot/
├── boot-screen-1440x900.png   (visual proof)
└── report.md                  (this file)
```

## Next

Mark #148 M1 ✅. Begin M2 — `docs/STORYBOARD.md` §1/§2/§5 + first `Skill: stitch-design` run that replaces `.stitch/DESIGN.md` placeholder. Provenance into `docs/DECISIONS/<date>-stitch-run-1.md`.
