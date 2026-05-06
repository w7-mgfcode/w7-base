# TASKBOARD: ll-KNOWRAG — Phase 8 (Re-architecture & Pivot)

## 1. Goal & Non-Goals

**Goal**: Pivot `ll-KNOWRAG` into a 100% private, self-hosted knowledgebase stack. Transition from Supabase/PostgREST to a Git-backed source of truth (**Gitea**) for artifacts and a vector database (**Qdrant**) for semantic search. Deliver a Tailwind-driven card-catalog UI, rich frontmatter metadata, a robust webhook-driven ingestion pipeline, and an optional Open WebUI integration — all dockerized for a small VPS or laptop.

**Non-Goals**:
- Multi-tenant SaaS architecture (single-user / small-team only).
- Advanced RBAC beyond Gitea visibility rules (public/private).
- Legacy Supabase/pgvector support — fully deprecated.
- Real-time collaborative editing (Git is the SSoT).

---

## 2. Phase 8 — 10-Subtask Plan

### Critical-Path Map

```
T1 ──┬─► T2 ──► T4 ──► T5 ──┬─► T7 ──► T8 ──┬─► T10
     │                       │                │
     └─► T3 ──► T4           └─► T6           │
                                              │
                              T9 ─────────────┘
```

### Tasks

| ID | Task | Owner | Depends | Parallel | Validation | Status |
|----|------|-------|---------|----------|------------|--------|
| **T1** | Working-tree triage & atomic baseline | omg-executor | — | ❌ | `git status` clean OR ≤ 1 deliberate WIP file; CI green | ✅ verified |
| **T2** | BLUEPRINT.md + architecture docs rewrite | omg-architect | T1 | ✅ w/ T3 | No Supabase/PostgREST refs except deprecation notes; new diagrams | ✅ verified |
| **T3** | `compose.yml` finalization | omg-executor | T1 | ✅ w/ T2 | `docker compose config -q` passes; `w7 doctor` clean; pinned image tags | ✅ verified |
| **T4** | Gitea bootstrap & KB repo seed | omg-executor | T3 | ❌ | Fresh `up` produces populated `kb-default` repo with 6-dir shape; idempotent | ✅ verified |
| **T5** | Storage layer port (PostgREST → Gitea API) | omg-executor | T4 | ✅ w/ T6 | `tests/test_storage_operations.py` pass against live Gitea; CRUD round-trip | ✅ verified |
| **T6** | Markdown frontmatter metadata parser | omg-executor | T1 | ✅ w/ T5 | `tests/test_frontmatter.py` ≥ 80% coverage; adversarial inputs handled | ✅ verified |
| **T7** | Qdrant ingestion pipeline | omg-executor | T5, T6 | ❌ | Push to Gitea → chunk in Qdrant within 30s; idempotent re-runs | todo |
| **T8** | Retrieval layer port to Qdrant | omg-executor | T7 | ❌ | Search p95 < 500ms on 10k chunks; `/related` returns ≥ 3 relevant items | todo |
| **T9** | UI design system foundation | omg-editor | T1 | ✅ all-backend | `grep 'style={{'` returns 0; `04-UI-REVIEW.md` ≥ 20/24; per `.claude/rules/ui-design.md` | todo |
| **T10** | Catalog UI + detail view + MCP + E2E dogfood | omg-editor + omg-verifier | T8, T9 | ❌ | All checklist items pass; `agent-browser` clean; dogfood report 0 Critical/High | todo |

### Subtask Detail

#### T1 — Working-Tree Triage
- Sort 234 dirty files into atomic commits: `chore(platform): drift across @ops, .shared, .bin, .sops.yaml`, `chore(state): omg sync`, `feat(knowrag): finalize Phase 7 implementation`, `docs: refresh platform documentation`.
- Add untracked stack-level READMEs/AGENTS.md files for `@ops/*`.
- Result: clean baseline for Phase 8 code work.

#### T2 — BLUEPRINT & Doc Rewrite
- `BLUEPRINT.md`, `CLAUDE.md`, `_kb/KNOWLEDGE_BASE.md` — Gitea+Qdrant canon.
- `docs/archon-porting-map.md` — flag deprecated pgvector reuses.

#### T3 — compose.yml Finalization
- Remove `knowrag-db` + `knowrag-postgrest` services.
- Add `gitea` service; pin all `:latest` tags to specific versions.
- Healthcheck-gated start order (api waits for gitea + qdrant).

#### T4 — Gitea Bootstrap
- Init container or API startup hook auto-provisions `kb-default` repo via Gitea API.
- Directory shape: `prompts/`, `commands/`, `mcp/`, `hooks/`, `skills/`, `knowledge/`.
- PAT loaded from `.env.sops`. Idempotent on restart.

#### T5 — Storage Port
- Rewrite `apps/api/src/server/services/storage/storage_operations.py`.
- New `gitea_client.py` (HTTPX-based).
- Preserve API contract for `knowledge_api.py` callers.
- Adversarial input testing per `.claude/rules/security-patterns.md` (path traversal, oversized files).

#### T6 — Frontmatter Parser
- New `apps/api/src/server/services/knowledge/frontmatter.py`.
- Pydantic schema: `tags: list[str]`, `status: Literal[draft|review|published]`, `version`, `owner`, `visibility: Literal[public|private]`.
- Reject malformed YAML with clear errors.

#### T7 — Ingestion Pipeline
- HMAC-verified webhook receiver in `apps/api/src/server/api_routes/ingest_api.py`.
- Chunker → Ollama embedder → Qdrant upserter.
- Periodic reconcile job comparing Git HEAD vs Qdrant payload metadata.

#### T8 — Retrieval Port
- `vector_search_strategy.py`, `hybrid_search_strategy.py`, `rag_service.py`, `reranker.py` → Qdrant client.
- New endpoint: `GET /pages/{id}/related` driving Qdrant kNN.
- Sparse-vector + BM25 token frequency for hybrid search (no PG fulltext available).

#### T9 — UI Design System (mandatory toolchain per `.claude/rules/ui-design.md`)
- Tailwind config + PostCSS pipeline in `apps/ui`.
- `.stitch/DESIGN.md` synthesized via `design-md` skill.
- Reusable primitives generated via `stitch-design` MCP, refined via `frontend-design` skill: `Card`, `Button`, `Badge`, `Input`, `Dialog`.
- All inline styles purged (`style={{` → 0 occurrences).
- Visual smoke test via `agent-browser` on `localhost:3737`.

#### T10 — Catalog UI + E2E Dogfood
- Card-grid `KnowledgeView.tsx` with filtering (type/tags/status/owner) + semantic search bar.
- Detail view: markdown render + copy-to-clipboard + "Related/Similar" pane.
- MCP server updated to expose new tools.
- Full-stack `docker compose up` verified via `agent-browser`.
- New `dogfood-output/report.md` with severity counts.

---

## 3. Risk Register

| # | Risk | Mitigation | Affects |
|---|------|------------|---------|
| R1 | Gitea init race on first `up` | Healthcheck-gated start, init container retry loop | T3, T4 |
| R2 | Stale Qdrant when Git pushes bypass webhook | Reconcile job (Git HEAD vs Qdrant payload metadata) | T7 |
| R3 | UI mid-refactor inline-style fragmentation | Purge in single PR; component contract enforced before catalog | T9 |
| R4 | Hybrid search regression (no PG fulltext) | Sparse-vector + BM25 at chunk-time | T8 |
| R5 | Working-tree drift mixing concerns | Atomic commit triage in T1 | T1 |
| R6 | Embedding cost spike on large KB | Embed-on-write only; rate-limit reconcile | T7 |

---

## 4. Definition of Phase Done

- [ ] All 10 subtasks marked `verified` in this taskboard
- [ ] `docker compose up` brings the full stack online with no manual steps
- [ ] A test markdown commit to Gitea appears in the catalog UI within 30s
- [ ] `/rag/search` returns relevant results for known queries
- [ ] `/pages/{id}/related` returns ≥ 3 semantically-similar items
- [ ] MCP server exposes the new tools and external agents consume them
- [ ] `04-UI-REVIEW.md` re-audit scores ≥ 20/24
- [ ] `dogfood-output/report.md` shows 0 Critical, 0 High severity
- [ ] CI green on master across both GitHub Actions and Gitea Actions
- [ ] `docs/`, `BLUEPRINT.md`, `CLAUDE.md` fully aligned with shipped behavior

---

## 5. Phase-Wide Conventions

| Concern | Source of Truth |
|---------|-----------------|
| Commit format | `.claude/rules/commit-format.md` — `type(scope): description` |
| UI toolchain | `.claude/rules/ui-design.md` — Stitch + skills + MCP + agent-browser **mandatory** for T9, T10 |
| Test coverage | `.claude/rules/test-requirements.md` — ≥ 80%, regression test per bug fix |
| Security | `.claude/rules/security-patterns.md` — adversarial input testing on T5/T6/T7 boundaries |
| Output format | `.claude/rules/output-formatting.md` |

---

## 6. Critical Files Touched in This Phase

1. `compose.yml` — infrastructure topology (T3)
2. `BLUEPRINT.md` — architecture canon (T2)
3. `apps/api/src/server/services/storage/storage_operations.py` — Gitea backend (T5)
4. `apps/api/src/server/services/knowledge/frontmatter.py` — new (T6)
5. `apps/api/src/server/api_routes/ingest_api.py` — new webhook (T7)
6. `apps/api/src/server/services/search/{vector,hybrid}_search_strategy.py` — Qdrant (T8)
7. `apps/api/src/server/services/search/rag_service.py` — Qdrant coordinator (T8)
8. `apps/ui/tailwind.config.ts` — new (T9)
9. `apps/ui/src/features/knowledge/views/KnowledgeView.tsx` — catalog redesign (T10)
10. `apps/mcp/src/mcp_server/features/rag/rag_tools.py` — backend rewire (T10)

---

## 7. Phase 7 — Sealed Reference

| Task ID | Task | Status |
|---|---|---|
| KB-7.5 | Reranking Provider Upgrade | verified |
| KB-7.6 | Recursive Crawling & Limit Enforcement | verified |
| KB-7.7 | LLMS.txt Task Expansion | verified |
| FIX-1 | Tag Storage Fix | verified |
| FIX-2 | Recursive Traversal & Normalization Fix | verified |
| ST-1 | Storage Logic Reconciliation (PostgREST) | verified |
| UI-1 | UI Implementation Audit & Sync | verified |
