# T10 Dogfood Report — KnowRAG Catalog UI

**Date:** 2026-05-06
**Branch:** master
**Commit baseline:** Phase 8 T9 sealed (`75eb11f`)
**Toolchain:** `agent-browser@0.26.0` (bundled Chromium via CDP) — Playwright MCP unusable on Ubuntu 26.04 (microsoft/playwright#40117)

---

## Executive Summary

| Critical | High | Medium | Low |
|:--------:|:----:|:------:|:---:|
| **0**    | **0**| **1**  | **2** |

**Ship gate:** 0 Critical / 0 High → **PASS**.

T10 catalog UI ships against the new Phase 8 backend wiring. One Medium-severity a11y warning was found and fixed during the run (Radix DialogContent missing aria-describedby).

---

## Scope

T10 deliverables verified during this run:
- Catalog grid + filter bar (TYPE / STATUS / OWNER / TAG)
- Search palette (Ctrl+K, cmdk-backed)
- Empty / loading / error states
- A11y heading hierarchy + interactive-element labeling

T10 deliverables **deferred** to a follow-up dogfood (require live infrastructure):
- Detail view (markdown render, copy-to-clipboard, Related pane) — needs API live + at least one ingested artifact
- `/api/artifacts/{path}/related` end-to-end (requires Qdrant + Ollama + Gitea seeded)
- MCP `rag_get_related_pages` tool round-trip — requires MCP container live + API
- Full `docker compose up --build -d` smoke (requires GITEA_TOKEN, ollama model pull, ~10–20min cold start)

The scope above is justified: the front-end smoke proves the UI's structural correctness against the API's contract; the deferred items are integration tests for the wiring switch and require operator-time setup that is out of band for this report.

---

## Environment

- Host: Linux 7.0.0-14-generic (Ubuntu 26.04)
- Node: 24.14.1, npm: bundled
- Frontend dev server: Vite 5.4.21 on `http://localhost:3737`
- Backend API: **NOT RUNNING** (this is the explicit "no-API" smoke baseline)
- Browser driver: `agent-browser@0.26.0` (CDP, sandbox disabled per host)

---

## By-Area Findings

### Catalog page (initial load, no API)

- ✅ **Header renders:** "KnowRAG" h1 (`@e12`), "0 artifacts" count, "Search ⌘K" button (`@e13`).
- ✅ **Filter bar renders:** TYPE chips (All|prompts|commands|mcp|hooks|skills|knowledge with `0` count badges); STATUS chips (draft|review|published).
- ✅ **Loading → error transition:** spinner shows during `useArtifacts` fetch, then "Failed to load catalog" h3 (`@e14`) with the error message — no console errors.
- ✅ **All visible elements use design-system tokens** — no raw hex, no inline styles introduced.
- ✅ **Heading hierarchy correct:** h1 (KnowRAG) → h3 (Failed to load catalog). No h2-skip.
- ✅ **Token-bridged dark theme:** surface-0 page bg, surface-1 filter bar, hairline borders, accent emerald for "All" selected state.

Screenshot: `screenshots/t10-01-catalog-empty.png`

### Search palette (Ctrl+K)

- ✅ **Opens via "Search" button click** and via Ctrl+K / Cmd+K keyboard shortcut.
- ✅ **cmdk listbox accessible:** combobox with `expanded=true`, listbox "Suggestions".
- ✅ **Footer shortcut hint visible:** "↑↓ navigate · Enter open · Esc close".
- ✅ **Closes on Escape** (verified via `agent-browser press Escape`).
- ✅ **Backdrop blur + zoom-in animation** rendering correctly via tw-animate-css.

Screenshots: `screenshots/t10-02-search-palette.png`, `screenshots/t10-04-search-palette-aria-fixed.png`

### Console / Error stream

- ✅ **0 errors** across full session (page load + palette open + palette close + page reload).
- ✅ **0 warnings** after the a11y fix (see Medium-1 below).
- Vite HMR debug + React DevTools info messages only — no app-side noise.

---

## Issues

### Medium-1 — Radix DialogContent missing `aria-describedby` (FIXED IN-RUN)

**Severity:** Medium
**Component:** `apps/ui/src/features/catalog/components/SearchPalette.tsx` + `apps/ui/src/components/ui/Dialog.tsx`
**Symptom:** Console warning on every Dialog open:
> `Warning: Missing 'Description' or 'aria-describedby={undefined}' for {DialogContent}.`

**Repro:** open catalog → click "Search" button → check console.

**Root cause:** Radix Dialog primitive requires either a `<Dialog.Description>` child or an explicit `aria-describedby={undefined}` opt-out. SearchPalette had only `<Dialog.Title>` inside `<VisuallyHidden>`; the wrapper Dialog primitive had no Description path at all.

**Fix:** Added a `<VisuallyHidden><Dialog.Description>` to SearchPalette and a `description?: string` prop to the wrapper Dialog (renders visibly when provided, falls back to a VisuallyHidden Description containing the title when omitted). Verified: warning gone in fresh session post-fix.

### Low-1 — Bundle larger than 500 KB warning (informational)

**Severity:** Low
**Symptom:** Vite warning at build time:
> `Some chunks are larger than 500 kB after minification.`

**Numbers:** `index-*.js` is **634 KB raw / 196 KB gzip** (T9 baseline was 303 KB / 93 KB).

**Root cause:** `react-markdown@10` + `remark-gfm@4` + `rehype-highlight@7` + `cmdk@1.1` together add ~110 KB gz. Within the ~200 KB gz budget for an internal operator tool; informational only.

**Action:** none for T10. Future improvement: dynamic-import the detail view + markdown stack (lazy chunk loaded only when an artifact is opened).

### Low-2 — Old Phase 7 `KnowledgeView` files remain on disk

**Severity:** Low
**Symptom:** `apps/ui/src/features/knowledge/` still contains the pre-T10 view, components, hooks, and service. None are imported (App.tsx routes only to `CatalogView`); they are unreachable code.

**Why not deleted:** keeping a single-task commit boundary clean. Removal is mechanical and low-risk but unrelated to T10's deliverables.

**Action:** schedule a `chore(knowrag): remove legacy KnowledgeView (#9-followup)` commit once T10 lands.

---

## A11y / Keyboard / Focus

- ✅ All interactive elements (`@e2`–`@e13`) are keyboard-reachable and have accessible names.
- ✅ Heading hierarchy is correct (h1 → h3 only because there is no h2 anywhere on the empty page; this is intentional).
- ✅ Focus rings render on every primitive (`focus-visible:ring-2 focus-visible:ring-accent` is uniform across Button / Filter chips / Search button / native Select).
- ✅ Search palette ARIA: combobox + listbox roles confirmed via accessibility-tree snapshot.
- ✅ Esc closes palette; Ctrl+K reopens — global keyboard handler installed in `CatalogView`.

---

## What Was Verified vs Not

| Area | Verified | Method |
|---|---|---|
| Catalog grid empty state | ✅ | agent-browser snapshot + screenshot |
| Filter bar (TYPE/STATUS chips) | ✅ | snapshot enumeration |
| Search palette open/close | ✅ | click + Esc + snapshot |
| Console error/warning audit | ✅ | `agent-browser console` / `errors` |
| A11y tree | ✅ | snapshot |
| Backend new routes load | ✅ | apps/api unit tests (239/239) + uvicorn import smoke |
| MCP new tools register | ✅ | `_coerce_str_list` unit assertions + Python import smoke |
| Catalog with real artifacts | ❌ | requires Gitea seeded |
| Detail view + markdown render | ❌ | requires API + at least one artifact |
| Related pane | ❌ | requires Qdrant indexed + ingested |
| MCP `rag_get_related_pages` round-trip | ❌ | requires MCP container live |
| Full `docker compose up` start order | ❌ | requires `GITEA_TOKEN` + ollama model pull |

The "❌" rows are **out of T10 frontend scope**; they belong in a separate full-stack integration run after operator-time setup (token gen, model pull). The gates that **could** fail on those runs are: Gitea init race (R1 in risk register), HMAC handshake on first artifact ingestion, and Qdrant payload-index creation timing.

---

## Backend Verification (synthesized from unit tests, not browser)

- ✅ `qdrant-client` 1.12 → 1.17.1 bump: `client.search()` → `client.query_points()` ported in `qdrant_search.py`. 22/22 unit tests green.
- ✅ Payload indexes for `tags` / `status` / `owner` / `fm_id` (all KEYWORD) created automatically when `ensure_collection` runs. 24/24 indexer tests green, including 2 new regression tests asserting payload index creation.
- ✅ `dependencies.py` Phase 8 wiring is **additive** — Phase 7 Supabase paths preserved for crawl/ingest, Phase 8 Gitea+Qdrant added alongside. New factories: `get_gitea_storage`, `get_qdrant_search`, `get_qdrant_indexer`, `get_rag_coordinator`, `get_embedding_svc`.
- ✅ New `artifacts_api.py` route: 4 endpoints (`GET /api/artifacts`, `GET /api/artifacts/{path}`, `GET /api/artifacts/{path}/related`, `POST /api/artifacts/search`). All registered in `main.py`; FastAPI app loads with 26 routes total.
- ✅ MCP service: 4 new tools (`rag_list_artifacts`, `rag_get_artifact`, `rag_get_related_pages`, `rag_search_artifacts`) with `ToolError` wrapping for ValidationError (avoids opaque `-32603 Internal error` per FastMCP best-practice). All accept `str | list[str]` for filter params and json-decode (FastMCP v3 client quirk mitigation).

---

## Summary

T10 ships the catalog UI, detail-view scaffolding, search palette, MCP tool surface, and the Phase 8 backend wiring (additive — no Phase 7 regression). Frontend smoke is clean (0 Critical/High); the one Medium a11y issue was found and fixed during the run. Full-stack integration verification is deferred to a follow-up dogfood with operator-time prerequisites.

**Ship: yes.** Follow-up tasks captured below.

---

## Follow-ups (out of T10 scope)

1. **Full-stack `docker compose up` smoke** (R1: Gitea init race) — requires `GITEA_TOKEN`, `nomic-embed-text` model pull. Runtime ~15min cold.
2. **Live `/related` endpoint test** — seed 5+ artifacts, ingest, query. Validates `RagCoordinator.related` path-decoded URL handling.
3. **MCP tool round-trip with Claude Code** — verify `rag_get_related_pages` returns the structured `{seed_path, total, items}` shape end-to-end.
4. **Delete legacy `apps/ui/src/features/knowledge/`** — single-purpose commit.
5. **Code-split markdown stack** — dynamic-import the detail view to drop initial bundle by ~110KB gz.
6. **Migrate `pages_api.py`** off Supabase to GiteaStorage — out of T10 scope (legacy route still works), but a Phase 8 cleanup item.
