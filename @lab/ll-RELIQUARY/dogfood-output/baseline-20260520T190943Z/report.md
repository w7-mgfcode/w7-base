# agent-browser baseline — ll-RELIQUARY (Phase 0)

**Date (UTC):** 2026-05-20 19:11:04Z
**Target:** http://localhost:4242
**Stack version:** boilerplate (no Stitch S01 in code yet)
**Tool:** agent-browser 0.26.0
**Browser args:** `--no-sandbox --disable-dev-shm-usage` (required on Ubuntu 26.04 — user-namespace sandbox restriction)
**Viewport:** 1440×900 (desktop primary)

---

## Why this baseline exists

This is the canonical "before any Stitch-generated screen lands in code" reference shot. Per `.claude/rules/ui-design-pipeline.md` inside the stack, every Phase ≥ 1 UI change must be validated against a fresh `agent-browser` run; **this baseline is the comparison anchor**.

When the Phase-1 implementation of S01 (Stitch-generated empty shelf) lands, a future dogfood run will diff against `01-boilerplate-landing.png`.

---

## Observations

### ✅ Page loads cleanly
- **Title**: `Reliquary` (matches `VITE_GAME_TITLE` env)
- **URL**: `http://localhost:4242/` (200 OK, 444 bytes)
- **No console messages**
- **No page-level errors**

### ✅ Wordmark present
- Rendered as an H1: *"Reliquary"*, Cormorant Garamond display serif, antique-gold color (`#c89f3c` from placeholder `@theme` tokens).

### ✅ Live API health probe wired correctly
The UI fetches `/health` on mount and surfaces the result. Snapshot text:
```
✓ reliquary-api — ok (boilerplate)
```
Source endpoint:
```
GET http://localhost:8282/health
{"status":"ok","service":"reliquary-api","phase":"boilerplate"}

GET http://localhost:8282/version
{"version":"0.0.0-boilerplate"}
```

### ✅ Boilerplate disclaimer footer
*"Boilerplate phase. Next: run Skill: stitch-design against STORYBOARD.md §5.S01."* — this is the self-flagging "this is a placeholder" hint baked into the stub. Will be removed when S01 ships.

---

## Accessibility tree snapshot

```
- generic "ReliquaryYour shelf is empty. The first relic awaits — but not in this boilerplate.API: ..." [ref=e1] clickable [onclick]
  - heading "Reliquary" [level=1, ref=e2]
```

Note: the snapshot collapsed the descendants under the main `generic` node — the placeholder `App.tsx` doesn't add intermediate landmarks. Expected for Phase 0; S01 implementation will introduce `<header>` / `<main>` / `<footer>` landmarks per the storyboard.

---

## What is NOT here yet (intentional)

- ❌ The horizontal **shelf of 4 slots** with slot #3 glowing (S01 spec)
- ❌ The **`[?]` help + `[⚙]` settings** icons in the header (S01 spec)
- ❌ The **gold 60px hairline rule** between subhead and shelf (S01 spec)
- ❌ The **"Reveal first relic" gold pill CTA** (S01 spec)
- ❌ The Stitch-generated grain texture on the surface

All of those land when Phase 1 implements `docs/SCREENS/S01-empty-shelf.md`.

---

## Stack status at capture time

| Container | Status | Notes |
|-----------|--------|-------|
| `lab-ll-reliquary-db` | healthy | Postgres 16.6-alpine |
| `lab-ll-reliquary-cache` | healthy | Redis 7.4.1-alpine |
| `lab-ll-reliquary-api` | healthy | FastAPI, /health returns 200 |
| `lab-ll-reliquary-ui` | healthy | nginx serving Vite build |

---

## Artifacts

- `01-boilerplate-landing.png` — full-viewport screenshot (1440×900)
- `report.md` — this file

---

## Result

✅ **PASS** — Phase-0 boilerplate baseline captured. Stack is fully operational. No console errors. API roundtrip working. Ready for Phase 1 (Stitch-generated S01 implementation).

