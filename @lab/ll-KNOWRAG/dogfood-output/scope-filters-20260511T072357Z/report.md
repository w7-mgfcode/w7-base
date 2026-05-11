# Dogfood — Epic 4 (#59) catalog scope filters

**Date:** 2026-05-11 07:23 UTC
**Branch:** `feat/ui-catalog-scope-filters`
**Stack:** live `@lab/ll-KNOWRAG` (knowrag-ui rebuilt from current branch)
**Tooling:** `agent-browser 0.26.0` (bundled Chromium — Playwright MCP cannot install Chromium on Ubuntu 26.04 per `reference_agent_browser_ubuntu26.md`)

## Sub-issues exercised

- `#81` — CatalogView nuqs URL params (`vis`, `hybrid`, `rerank`)
- `#82` — FilterBar Scope subsection (visibility ToggleGroup + 2 Switches)
- `#83` — SearchPalette threads params + active-modifier caption
- `#84` — Round-trip + regression vitest (verified in `npm test`, not visual)
- `#85` — this dogfood pass

## Screenshots

### 01-catalog-default.png — `?view=catalog` (all defaults)

URL: `http://localhost:3737/?view=catalog`

Scope subsection visible on the right edge of the FilterBar: `SCOPE [public] [private] [○ hybrid] [○ rerank]` — `public` highlighted (accent), both switches OFF (thumb left, no fill). Catalog shows 37 artifacts.

### 02-catalog-vis-private.png — `?view=catalog&vis=private`

URL: `http://localhost:3737/?view=catalog&vis=private`

`private` is now the highlighted toggle (accent fill); `public` deselected. Switches still OFF. Catalog body refreshes (loading state captured mid-fetch — expected behavior).

### 03-catalog-all-modifiers-on.png — all three modifiers active

URL: `http://localhost:3737/?view=catalog&vis=private&hybrid=true&rerank=true`

`private` highlighted, **both `hybrid` and `rerank` switches ON** (thumb right, accent fill). Round-trips from URL on initial page load — verifies `parseAsBoolean` + `parseAsStringLiteral` hydration.

### 04-searchpalette-caption.png — palette with active-modifier caption row

URL: `http://localhost:3737/?view=catalog&vis=private&hybrid=true&rerank=true` then `Ctrl+K`

Caption row visible below the search input: **`Scope: private · hybrid · rerank`**. The palette is otherwise unchanged from prior behavior. Caption renders only when ≥1 modifier is non-default (verified in `SearchPalette.test.tsx` — see PR test plan).

## Verifications

| Acceptance criterion (issue #59) | Status |
|---|---|
| All 3 plan tasks (22–24) complete with VALIDATE commands green | ✅ `npx tsc --noEmit` + `npm run build` + `npm test` (57/57) green per commit |
| URL `?view=catalog&vis=private&hybrid=true&rerank=true&tags=...` round-trips | ✅ Screenshots 03 + vitest `CatalogView.test.tsx` |
| `SearchPalette` POST body includes `use_hybrid: true` when URL param is true | ✅ vitest `SearchPalette.test.tsx` ("POSTs use_hybrid:true and visibility:'private'...") |
| Active-modifier caption row renders in the palette when any modifier is non-default | ✅ Screenshot 04 + vitest assertion |
| No regression in existing catalog filter behavior (category / tags / status / owner) | ✅ Screenshot 01 (chip counts intact); existing tests still pass |

## Notes / non-blocking observations

- Catalog body chip counts (`prompts 0`, `0 artifacts`) in screenshots 02/03 are caught mid-load (spinner visible). The `useArtifacts` list endpoint does not currently re-key on `visibility` — that is intentional for #59's scope (the visibility flow targets search/RAG, not catalog list). A follow-up could thread `vis` into `useArtifacts` for full UI parity if desired.

## Files referenced

- `apps/ui/src/features/catalog/views/CatalogView.tsx` (#81)
- `apps/ui/src/features/catalog/components/FilterBar.tsx` (#82)
- `apps/ui/src/features/catalog/components/SearchPalette.tsx` (#83)
- `apps/ui/src/test/setup.ts` (ResizeObserver polyfill — needed for cmdk in jsdom)
- `apps/ui/src/features/catalog/{components,views}/__tests__/{FilterBar,SearchPalette,CatalogView}.test.tsx` (#82 / #83 / #84)
