# ll-KNOWRAG Blueprint — Phase 8

> **Status:** Phase 8 canon. Supersedes the Phase 7 Supabase/PostgREST blueprint.
> Phase 7 sealed at commit `2393302`; the previous blueprint is preserved in git history.

## 1. Purpose

ll-KNOWRAG is a **100% private, self-hosted, local-first knowledgebase** with semantic retrieval. The architecture is built on:

- **Gitea** — artifact source-of-truth (Markdown + YAML frontmatter, Git history = audit log)
- **Qdrant** — vector index for semantic search and "related" similarity queries
- **Ollama** — local embedding provider (default model `nomic-embed-text`)
- **FastAPI** — backend API (`knowrag-api`)
- **FastMCP** — MCP server for agent/tool access (`knowrag-mcp`)
- **React + Vite + TypeScript + Tailwind** — operator UI (`knowrag-ui`)
- **Open WebUI** — optional chat surface over the local Ollama (`--profile webui`)

Phase 7 took the system to UI/Backend parity on a Supabase + PostgREST + pgvector stack. **Phase 8 rips out Supabase entirely.** Git is now the artifact CRUD backend; commits = mutations.

## 2. Architectural Pivot — Phase 7 → Phase 8

| Concern | Phase 7 (sealed) | Phase 8 (canon) |
|---------|------------------|-----------------|
| Artifact storage | Supabase (Postgres) tables `kb_sources`, `kb_pages`, `kb_chunks` | **Gitea repo** with directory shape `prompts/`, `commands/`, `mcp/`, `hooks/`, `skills/`, `knowledge/` |
| Vector index | pgvector column on `kb_chunks` | **Qdrant** collections, payload-encoded metadata |
| Hybrid search | Postgres `tsvector` + trigram | **Qdrant sparse-vector + BM25** at chunk-time |
| Mutation API | PostgREST (REST over Postgres) | **Gitea API** (REST over Git, commits = audit log) |
| Auth | Supabase service-role keys | Gitea personal-access-tokens (SOPS-encrypted) |
| Refresh trigger | Internal scheduler | **Git webhook** (HMAC-signed, instant) + periodic reconcile |
| Schema migrations | SQL files in `db/migrations/` | **Frontmatter Pydantic schema** in `services/knowledge/frontmatter.py` |
| Backup | `pg_dump` | `git clone` (and the volume) |

## 3. Non-Goals

- Multi-tenant SaaS architecture (single-user / small-team only).
- Advanced RBAC beyond Gitea visibility rules (`public` / `private` per repo).
- Legacy Supabase/PostgREST/pgvector — **fully deprecated**. Old SQL migrations under `db/migrations/` were removed in #12 (recoverable via tag `pre-knowrag-cleanup`).
- Real-time collaborative editing — **Git is the SSoT**. Mutations are commits; conflicts surface as merge conflicts, not last-write-wins.

## 4. Target Topology

```
┌─────────────────────────────────────────────────────────────────────┐
│ Operator (browser)         External Agents (MCP clients)            │
└────────────┬─────────────────────────────┬──────────────────────────┘
             │                             │
             ▼                             ▼
      ┌──────────────┐              ┌──────────────┐
      │ knowrag-ui   │              │ knowrag-mcp  │
      │ React + Vite │              │ FastMCP      │
      └──────┬───────┘              └──────┬───────┘
             │ HTTP                        │ HTTP
             └─────────────┬───────────────┘
                           ▼
                    ┌─────────────┐
                    │ knowrag-api │  ◄──── webhook (HMAC) ────┐
                    │ FastAPI     │                            │
                    └──┬────┬──┬──┘                            │
                       │    │  │                               │
            ┌──────────┘    │  └──────────┐                    │
            ▼               ▼             ▼                    │
       ┌─────────┐    ┌──────────┐   ┌─────────┐               │
       │ ollama  │    │  qdrant  │   │  gitea  │ ──────────────┘
       │embeddings│   │  vector  │   │   git   │  (push triggers webhook)
       └─────────┘    └──────────┘   └─────────┘
                                          ▲
                                          │ git push
                                  ┌───────┴───────┐
                                  │ Operator CLI, │
                                  │ Gitea web UI, │
                                  │ external IDE  │
                                  └───────────────┘
```

Two data flows:

**Read path:** UI/MCP → API → Qdrant (semantic search) → API hydrates payloads from Gitea on demand → return to UI/MCP.

**Write path:** Operator/IDE/web UI commits markdown to Gitea → Gitea webhook fires → API verifies HMAC → API chunks + embeds via Ollama → upserts into Qdrant. Reconcile job catches missed events.

## 5. Service Roles

### `knowrag-api`
- Owns: Gitea CRUD client, frontmatter parsing, chunking, embedding (via Ollama), Qdrant upsert + query, RAG retrieval, page lookup.
- Endpoints: `/health`, `/api/knowledge-items/*`, `/api/rag/*`, `/api/pages/*`, `/api/ingest/webhook`.
- New in Phase 8: `GET /api/pages/{id}/related` (Qdrant kNN-driven).

### `knowrag-mcp`
- Owns: MCP tool registration. **Thin HTTP proxy to API** — never reimplements KB logic.
- Tools (Phase 8): `health_check`, `session_info`, `rag_get_available_sources`, `rag_search_knowledge_base`, `rag_list_pages_for_source`, `rag_read_full_page`.

### `knowrag-ui`
- Owns: card-grid catalog, search bar, filtering (type/tags/status/owner), detail view with markdown render + copy-to-clipboard + "Related/Similar" pane.
- Phase 8 stack: React + Vite + TypeScript + **Tailwind CSS** + Stitch-generated component primitives.

### `gitea`
- Owns: Markdown artifact storage. Each artifact is one file under `<category>/<id>.md` with YAML frontmatter.
- Visibility is the repo-level setting (`public` / `private`). One repo = one visibility scope.
- Default repo: `knowrag/kb-default` (overridable via env).

### `qdrant`
- Owns: chunk vector index. Collections are scoped per visibility (`kb_public`, `kb_private`).
- Payload includes: `source_path`, `commit_sha`, `chunk_index`, `frontmatter` (denormalized for filtering).

### `ollama`
- Owns: embedding generation. Default model `nomic-embed-text`. Same provider used by Open WebUI when enabled.

## 6. Data Model

**Single source of truth:** the file on disk in the Gitea repo.

### Artifact contract

```markdown
---
id: a3f2-9b1c
tags: [agents, mcp, claude]
status: published          # draft | review | published
version: 1.2.0
owner: w7-mgfcode
visibility: public         # public | private (must match repo visibility)
created_at: 2026-04-15
updated_at: 2026-05-06
---

# Title

Markdown body — chunked at ingestion time.
```

### Directory shape (in the KB repo)

```
kb-default/
├── prompts/         # System prompts, prompt templates
├── commands/        # Slash commands, CLI invocations
├── mcp/             # MCP server configs and notes
├── hooks/           # Hook scripts and triggers
├── skills/          # Agent skills, capabilities
└── knowledge/       # General knowledge articles
```

Categorization is **directory-driven**, not metadata-driven — the parent directory determines the artifact type.

### Qdrant payload

Each chunk in Qdrant carries:

| Field | Source |
|-------|--------|
| `source_path` | e.g. `knowledge/example.md` |
| `commit_sha` | Git SHA at ingestion time (used by reconcile) |
| `chunk_index` | 0-based position within the artifact |
| `frontmatter.tags` | denormalized for filtering |
| `frontmatter.status` | denormalized for filtering |
| `frontmatter.owner` | denormalized for filtering |
| `frontmatter.visibility` | denormalized — collection name must match |
| `content` | the chunk text (for context, not for matching) |
| `vector` | embedding (Ollama, dim varies by model) |

## 7. Ingestion Flow

```
git push to gitea (KB repo)
   │
   ▼
gitea fires webhook → POST /api/ingest/webhook
   │
   ▼
api verifies HMAC (X-Gitea-Signature, sha256)
   │
   ├── reject if signature mismatch
   │
   ▼
fetch changed files via gitea API (compare base..head)
   │
   ▼
for each changed file:
   ├── parse frontmatter (Pydantic — reject malformed)
   ├── if deleted: remove all chunks where source_path = path AND commit_sha != head
   ├── if added/modified:
   │     ├── chunk (structural split → fallback windowing)
   │     ├── embed batch via ollama
   │     ├── upsert into qdrant (collection = visibility scope)
   │     └── tag payload with current commit_sha
   │
   ▼
periodic reconcile job (every 5 min):
   ├── compare git HEAD sha vs max(commit_sha) in qdrant per repo
   ├── if drift: re-ingest the diff
```

**Idempotency:** killing the API mid-ingest is safe. Re-ingesting the same `(source_path, commit_sha)` produces deterministic vectors (Ollama is deterministic for the same input + model).

## 8. Retrieval Flow

```
POST /api/rag/query  { query, filters, mode }
   │
   ▼
embed(query) via ollama
   │
   ▼
qdrant search:
   ├── filter by visibility scope (collection)
   ├── filter by frontmatter (tags, status, owner) if provided
   ├── top-K vector hits
   │
   ▼ optional
hybrid merge with BM25 sparse-vector hits
   │
   ▼ optional
rerank via provider (lexical / cohere / openai)
   │
   ▼
group by source_path → "page mode" with chunk highlights
   │
   ▼
hydrate top hits with full file content from gitea (cached by commit_sha)
   │
   ▼
return { hits: [...], pages: [...], query_time_ms }
```

**Related/Similar endpoint:** `GET /api/pages/{path:.+}/related?k=5` does Qdrant kNN starting from the centroid of the source's chunks.

## 9. API Surface

### Knowledge management
- `GET  /api/knowledge-items` — list artifacts (filtered by category, tags, status)
- `GET  /api/knowledge-items/{path:.+}` — fetch one artifact (frontmatter + content)
- `POST /api/knowledge-items` — create artifact (commits to Gitea, triggers ingestion)
- `PUT  /api/knowledge-items/{path:.+}` — update artifact (commit + re-ingest)
- `DELETE /api/knowledge-items/{path:.+}` — delete artifact (commit + remove chunks)

### Retrieval
- `POST /api/rag/query` — semantic search with filters
- `GET  /api/pages/{path:.+}` — fetch full artifact
- `GET  /api/pages/{path:.+}/related?k=5` — semantic neighbors

### Ingestion (machine-only)
- `POST /api/ingest/webhook` — Gitea webhook receiver (HMAC-verified)
- `POST /api/ingest/reconcile` — manual reconcile trigger (admin)

### Health
- `GET  /health`
- `GET  /api/health` (detailed: gitea, qdrant, ollama reachability)

> Note: Phase 8 also exposes `/api/artifacts/*` (list, get, related, search) — the canonical contract that the catalog UI and the verify harness assert against. The `/api/knowledge-items/*` and `/api/rag/query` routes above are kept for backward compatibility with Phase-7 callers; new clients should target `/api/artifacts`.

## 9.5 Operational Verification

The Phase 8 contract is **"git push → searchable in 30 seconds, end-to-end, on real running infrastructure"**. `w7 verify @lab/ll-KNOWRAG` proves the contract on a live stack via six in-order checks:

1. `api.health` — API responds healthy
2. `gitea.kb_repo_exists` — KB repo reachable via Gitea API
3. `ingestion.seed_and_grow` — fixtures committed to a temp branch grow Qdrant `points_count` within 60s
4. `search.api_returns_hits` — `POST /api/artifacts/search` returns ≥1 hit
5. `related.api_returns_3_plus` — `GET /api/artifacts/.../related?k=5` returns ≥3 sibling artifacts
6. `mcp.search_returns_hits` — MCP `rag_search_knowledge_base` returns content over the FastMCP HTTP transport

The harness is non-destructive by default: a temp branch (`verify-<utc-ts>-<pid>`) is created, fixtures are committed, the Qdrant collection grows, all assertions run, and the EXIT trap deletes the temp branch and Qdrant points. The KB's `main` branch is never touched.

Each run writes `dogfood-output/<utc-timestamp>/{result.json,report.md,curl-trace.log}`. The JSON envelope is suitable for CI gating (`exit_code == 0` ∧ `summary.{critical,high}` both 0).

Operator guide: [`docs/runbook.md`](docs/runbook.md) (section: "End-to-End Verification") and [`scripts/README.md`](scripts/README.md).

## 10. Security Model

| Surface | Threat | Mitigation |
|---------|--------|------------|
| Gitea token | Leaked token = full repo write | Stored only in `.env.sops` (AGE-encrypted); never logged; never written to manifests |
| Webhook endpoint | Unauthorized ingestion trigger | HMAC-SHA256 signature verification; secret rotates with `GITEA_WEBHOOK_SECRET` |
| Markdown frontmatter | YAML deserialization attack | `yaml.safe_load()` only; Pydantic schema rejects unknown types |
| File paths | Path traversal (`../etc/passwd`) | Canonicalize via `pathlib.Path.resolve()`; reject paths escaping the repo root |
| Upload size | Memory exhaustion | `MAX_UPLOAD_SIZE_MB` enforced before reading file body |
| Qdrant exposure | Direct vector queries bypass auth | Qdrant only listens on the docker-internal network; no host port exposure in production builds |

## 11. Configuration Surface

Required (`.env`, must be SOPS-encrypted in `.env.sops` for any non-throwaway deployment):

| Variable | Purpose |
|----------|---------|
| `GITEA_TOKEN` | Personal-access-token, `repo` scope |
| `GITEA_WEBHOOK_SECRET` | HMAC secret for webhook verification |

Tunable (`.env`, plain):

| Variable | Default | Purpose |
|----------|---------|---------|
| `GITEA_BASE_URL` | `http://gitea:3000` | API endpoint |
| `GITEA_KB_OWNER` | `knowrag` | Owner of the KB repo |
| `GITEA_KB_REPO` | `kb-default` | KB repo name |
| `GITEA_KB_BRANCH` | `main` | Branch to track |
| `EMBEDDING_PROVIDER` | `ollama` | `ollama` or OpenAI-compatible |
| `EMBEDDING_MODEL` | `nomic-embed-text` | Model identifier |
| `USE_HYBRID_SEARCH` | `false` | Enable BM25 sparse-vector merge |
| `USE_RERANKING` | `false` | Enable reranker stage |

Full list in `.env.example`.

## 12. Build Standard (Phase 8)

The implementation is correct only if:

- ✅ `docker compose up` brings the full stack online with **no manual steps** beyond setting `GITEA_TOKEN` (or accepting the bootstrap-generated one)
- ✅ A test markdown commit to Gitea appears in the catalog UI within 30 seconds
- ✅ `/api/rag/query` returns relevant results for known queries
- ✅ `/api/pages/{path}/related` returns ≥ 3 semantically-similar items
- ✅ MCP server exposes the new tools and external agents consume them
- ✅ `04-UI-REVIEW.md` re-audit scores ≥ 20/24
- ✅ `dogfood-output/report.md` shows 0 Critical, 0 High severity
- ✅ CI green on master (GitHub + Gitea Actions)
- ✅ All `.claude/rules/*.md` constraints respected (commit format, security patterns, test coverage, UI toolchain)

## 13. Implementation Slices — Phase 8

These are the 10 subtasks tracked in `.omg/state/taskboard.md`:

| ID | Slice | Status |
|----|-------|--------|
| T1 | Working-tree triage & atomic baseline | ✅ verified |
| T2 | BLUEPRINT.md & architecture docs rewrite | 🔄 (this document) |
| T3 | `compose.yml` finalization | 🔄 (Gitea added, healthcheck-gated) |
| T4 | Gitea bootstrap & KB repo seed | todo |
| T5 | Storage layer port (PostgREST → Gitea API) | todo |
| T6 | Markdown frontmatter metadata parser | todo |
| T7 | Qdrant ingestion pipeline | todo |
| T8 | Retrieval layer port to Qdrant | todo |
| T9 | UI design system foundation | todo |
| T10 | Catalog UI + detail view + MCP + E2E dogfood | todo |

## 14. Deprecated From Phase 7

These components were canonical in Phase 7 and are **deprecated** in Phase 8. Code remains in git history; references in active docs are removed.

- `db/migrations/00{1..8}_*.sql` — Postgres extensions, settings, sources, pages, chunks, search functions, contextual schema, source counts RPC. **Removed in #12** (recoverable via tag `pre-knowrag-cleanup`). **Replaced by:** Gitea directory shape + Qdrant collections + frontmatter Pydantic schema.
- `apps/api/src/server/services/storage/storage_operations.py` (PostgREST client) — **Replaced by:** Gitea API client (T5).
- `apps/api/src/server/services/search/{vector,hybrid}_search_strategy.py` (pgvector + tsvector queries) — **Replaced by:** Qdrant client (T8).
- The `kb_sources / kb_pages / kb_chunks` table model — **Replaced by:** Markdown files in Gitea + frontmatter metadata.
- `host.docker.internal:8000` Supabase dependency — **Removed:** stack is fully self-contained.

See `docs/archon-porting-map.md` for the full deprecation table.

## 15. Reuse From Archon (still valid)

Phase 7 ported these from Archon and they remain canonical for Phase 8:

- **Crawling and discovery** — `discovery_service.py`, `crawling_service.py`, `crawler_manager.py` (URL ingestion still pipes through these into the markdown-commit path)
- **Embedding abstraction** — provider adapter pattern, batch embedding with partial-failure handling
- **MCP architecture** — separate FastMCP service, thin proxy to API
- **Chunking strategy** — structural split → fallback windowing (1200–1800 chars, overlap 150–250)
- **RAG coordinator pattern** — embed → vector → optional hybrid → optional rerank → page grouping

These do not change in Phase 8; only their storage backend changes.
