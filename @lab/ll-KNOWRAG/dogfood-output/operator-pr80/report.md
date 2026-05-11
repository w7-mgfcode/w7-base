# Operator panel — live-browser dogfood (PR #80, Epic 3 / #58)

**Date:** 2026-05-11
**Branch:** `feat/ui-operator-panel`
**Commit at capture:** `cda5d8e feat(ui): operator panel — health, reconcile, settings (#58)`
**Renderer:** `agent-browser` (Chromium 147 headless, `--no-sandbox`)
**Build path:** Vite dev server (`npm run dev --port 3738 --strictPort`), proxying `/api` → `http://localhost:8181`
**Live backend:** `knowrag-api` + `qdrant` + `gitea` + `ollama` stack already up

---

## Automated checks

| Check | Result |
|---|---|
| `npx tsc --noEmit` | ✅ clean |
| `npm test -- --run` | ✅ 43/43 (12 new across `operatorService.test.ts`, `HealthCard.test.tsx`, `ReconcileButton.test.tsx`, `SettingsPanel.test.tsx`) |
| `npm run build` | ✅ `✓ built in 2.08s` |

## Browser flow captured

| File | Step |
|---|---|
| `01-operator-default.png` | `GET /?view=operator` — all three cards render; header pill green; HealthCard "checked now"; SettingsPanel empty-state with three `—` rows and the deferred-followup hint. |
| `02-operator-alertdialog.png` | Click "Reconcile Git ↔ Qdrant" → Radix `AlertDialog` open with Title / Description / Cancel + Confirm. |
| `03-operator-cancelled.png` | Click Cancel → dialog dismisses; network log shows **zero** POST calls to `/api/ingest/reconcile`. |
| `04-operator-reconcile-success.png` | Click Confirm → live `POST /api/ingest/reconcile` returns `200`, `{"action":"reconciled","scanned":37,…}` (5882 B); trigger disabled while pending; green success notice **"Reconcile complete — scanned 37 artifacts."** rendered with `bg-status-ok/10 text-status-ok`. |

## Cross-tab regression

| Tab | Behavior |
|---|---|
| `?view=catalog` | Renders `FilterBar` + chips ("All", "prompts", …). No regression from the `App.tsx` swap. |
| `?view=chat` | Renders "Ask the knowledge base anything" empty state. No regression. |
| `?view=operator` | Renders all three new cards (this PR). |

## Notes

- `useHealth()` shares queryKey `['health']` with the existing `HeaderStatusPill`. TanStack Query dedupes — both surfaces reflect the same fetch.
- Browser dogfood for Epic 5 (`#60`) is the *formal* deliverable; this report is an ad-hoc validation pass attached to PR #80 to document the manual sanity check.
- `SettingsPanel` populated-state was NOT exercised in browser (would require `/api/rag/query` to succeed, which needs a chat model pulled into Ollama). Unit tests at `__tests__/SettingsPanel.test.tsx` cover both populated and empty branches with the real `RAG_LAST_SUCCESS_KEY` import path.
