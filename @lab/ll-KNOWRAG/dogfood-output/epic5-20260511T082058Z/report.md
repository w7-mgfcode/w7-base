# Epic 5 — UI smoke + dogfood release-readiness

> Closes the loop on umbrella **#55** ("expose full knowrag capability surface"). Verifies plan tasks **26** (verify.sh `ui_chat.tab_loads`) and **27** (8-scenario browser dogfood).

## Run metadata

| Field | Value |
|-------|-------|
| Started (UTC) | 2026-05-11T08:20:58Z |
| Finished (UTC) | 2026-05-11T08:37:30Z |
| Base SHA | `9b625f7` (master after PR #87 merge) |
| Branch | `test/knowrag-ui-smoke-dogfood` |
| Stack uptime | api/gitea/mcp/qdrant ~3 h, ui ~56 min, ollama restarted mid-run (scenario 7) |
| `w7 verify @lab/ll-KNOWRAG` | **8/8 PASS** (`dogfood-output/20260511T082058Z/`) |
| Chat model | `llama3.2:1b` (pulled this session — 1.3 GB) |
| Embedding model | `nomic-embed-text` (pre-existing) |
| Tooling | `agent-browser` CLI (Playwright MCP unusable on Ubuntu 26.04) |

## verify.sh — 8/8 PASS

| # | Check | Status | Latency | Note |
|---|-------|:-:|---:|------|
| 1 | `api.health` | ✅ | 42 ms | — |
| 2 | `gitea.kb_repo_exists` | ✅ | 63 ms | `knowrag/kb-default` |
| 3 | `ingestion.seed_and_grow` | ✅ | 5.5 s | 4 fixtures → Qdrant 337→350 points |
| 4 | `search.api_returns_hits` | ✅ | 87 ms | 10 hits |
| 5 | `ui_catalog.proxy_returns` | ✅ | 5.0 s | 41 artifacts via :3737 (timeout bumped 5s→15s — see §Notes) |
| 6 | `ui_chat.tab_loads` | ✅ | 31 ms | **NEW** — bundle grep for empty-state copy |
| 7 | `related.api_returns_3_plus` | ✅ | 80 ms | 5 sibling artifacts |
| 8 | `mcp.search_returns_hits` | ✅ | 15.4 s | RAG generation via FastMCP → /api/rag/query (mcp_call timeout bumped 15s→30s — see §Notes) |

## Dogfood scenarios — 8/8

| # | Scenario | Status | Screenshot | Notes |
|---|----------|:-:|------------|-------|
| 1 | Catalog tab default — header tabs visible, status pill green | ✅ PASS | [01-catalog-default.png](01-catalog-default.png) | `API ok` pill, all three tabs rendered, type/visibility/hybrid/rerank filter chrome present |
| 2 | Chat tab — URL becomes `?view=chat`, empty-state visible | ✅ PASS | [02-chat-empty-state.png](02-chat-empty-state.png) | "Ask the knowledge base anything" + ⌘+Enter hint rendered |
| 3 | Send a chat query → assistant message + source chips | ✅ PASS | [03-chat-happy-path.png](03-chat-happy-path.png) | Query: "What does verify.sh assert about ingestion?" — assistant returned grounded answer with citation `[1] prompts/claude-rules-security-patterns.md`. Round-trip ~10 s |
| 4 | Click source chip → catalog opens cited artifact | ✅ PASS | [04-source-chip-nav.png](04-source-chip-nav.png) | URL became `?a=prompts/claude-rules-security-patterns.md`; ArtifactDetail rendered |
| 5 | Operator tab — health card green, reconcile button enabled | ✅ PASS | [05-operator-default.png](05-operator-default.png) | "knowrag-api" healthy image + "checked now"; Reconcile button enabled, expanded=false |
| 6 | Reconcile click → confirm → spinner → success notice | ✅ PASS | [06-reconcile-success.png](06-reconcile-success.png) | AlertDialog opened ("Run reconcile?") → Confirm → button disabled (~50 s spinner) → status: "Reconcile complete — scanned 37 artifacts." Active models pane populated with `chat_provider=ollama`, `chat_model=llama3.2:1b` |
| 7 | Stop Ollama, retry chat — DegradedNotice + retrieved context | ⚠️ PARTIAL | [07-degraded-notice.png](07-degraded-notice.png) | Hard `docker stop knowrag-ollama` produces an httpx `ConnectError` (DNS failure) in the API, which surfaces as **raw HTTP 500** to the UI — falling into the generic "Error: 500" branch, NOT the structured-503 DegradedNotice branch. The DegradedNotice path is only reachable via the structured-503 codes `chat_provider_unavailable` / `chat_model_unavailable` (e.g. model not pulled, provider URL misconfigured). See §Findings |
| 8 | URL state round-trip — `?view=catalog&vis=private&hybrid=true&rerank=true&tags=rag,qdrant` | ✅ PASS | [08-url-state-roundtrip.png](08-url-state-roundtrip.png) | Reload of full URL preserved: visibility radio `private` checked, hybrid switch on, rerank switch on, FilterBar populated. nuqs round-trip clean |

## Sub-issue traceability

| Subtask | Surface | Verified by |
|---------|---------|------|
| #88 `verify.sh ui_chat.tab_loads` | Build-pipeline regression guard | verify.sh row 6 above |
| #89 chat model pull | `/api/rag/query` happy path | [rag-query-smoke.json](rag-query-smoke.json) (HTTP 200 in 7.2 s) + dogfood scenarios 3, 4 |
| #90 8-scenario dogfood walk | Catalog (#1, #8), Chat (#2, #3, #4, #7), Operator (#5, #6) | Dogfood table above |
| #91 this report.md | Closure evidence | This file |
| #92 commit + close cascade | umbrella #55 closure | PR (TBD) |

## Umbrella #55 success-criteria checklist

- [x] All 5 Epic sub-issues closed — Epics 1-4 already merged (#56, #57, #58, #59); Epic 5 (#60) closes via this PR.
- [x] `?view=catalog`, `?view=chat`, `?view=operator` all render the correct view — verified scenarios 1, 2, 5.
- [x] Every documented endpoint in `docs/api-contracts.md` reachable from the UI — `/health` (status pill), `/api/artifacts*` (catalog), `/api/rag/query` (Chat tab, scenario 3), `/api/ingest/reconcile` (Operator tab, scenario 6), `/api/artifacts/{path}/related` (source-chip nav, scenario 4).
- [x] `w7 verify @lab/ll-KNOWRAG` 8/8 green — see verify.sh table.
- [x] No new runtime dependency added to `apps/ui/package.json` — only verify.sh / docs / dogfood-output touched.
- [x] Browser dogfood screenshots committed under `dogfood-output/<utc-timestamp>/` — this directory.

## Findings (deltas worth surfacing — not speculative)

1. **Scenario 7 UX gap — raw 500 on hard Ollama loss.** The `DegradedNotice` discriminated-union branch in `ragService.ts` only fires when the API returns a structured 503 with `error_code ∈ {chat_provider_unavailable, chat_model_unavailable}`. A *network*-level failure (Ollama container stopped → httpx `ConnectError: Temporary failure in name resolution`) propagates as a generic HTTP 500 and shows up as `**Error:** 500 Internal Server Error` rather than the friendly degraded card with a `docker exec` hint. This is consistent with `useRagQuery.test.ts` (only the structured-503 paths are tested), but the user-facing message on a real outage is opaque. **Suggested follow-up:** API-side catch on httpx ConnectError → translate to a `chat_provider_unavailable` 503 so the UI's degraded branch fires uniformly.

2. **verify.sh timeouts were undersized.** `check_ui_catalog` was hard-coded at `--max-time 5` and `mcp_call` at `--max-time 15` — both right at the observed latency on the current KB size (≈37 artifacts, RAG generation ≈10-15 s with `llama3.2:1b`). Adjusted to 15 s and 30 s respectively. Without this, runs flaked 2 of 3 times.

3. **Stale runbook baseline.** `docs/runbook.md` said "6/6 pass" referencing the May 6 dogfood — refreshed in this PR to reflect the current 8/8 contract (added `ui_catalog.proxy_returns` from #51 + `ui_chat.tab_loads` from this Epic). Documented the `llama3.2:1b` pull as a first-time-setup step.

4. **Reconcile is slow but works.** `/api/ingest/reconcile` over 37 artifacts took ~50 s in the browser; the API returns 200 promptly but the spinner reflects the long-poll on the indexing pipeline. Not a regression — first time the operator panel has been exercised end-to-end.

## Notes

- **Verify harness changes in this PR:**
  - `scripts/verify.sh` — new `check_ui_chat_tab_loads` (8th check); `check_ui_catalog` timeout 5 s → 15 s; header comment refreshed; run-sequence updated.
  - `scripts/lib/verify-helpers.sh` — `mcp_call` initialize timeout 15 s → 30 s.
- **Out of scope:** new test frameworks, performance budgets, visual regression snapshots, multi-turn chat persistence, SSE streaming. See umbrella #55 "Out of scope (explicit)".
- **Force-add pattern:** screenshots and this report are under `dogfood-output/`, which is in root `.gitignore`. They are force-added per the established convention (`dogfood-output/operator-pr80/`, `dogfood-output/scope-filters-20260511T072357Z/`).
