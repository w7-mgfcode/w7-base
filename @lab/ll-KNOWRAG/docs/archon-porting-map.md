# Archon Porting Map

This document tracks the extraction and adaptation of components from the Archon repository into `ll-KNOWRAG`, with Phase 8 deprecation notes.

> **Phase 8 status:** the storage backend has been replaced (Supabase/PostgREST → Gitea + Qdrant). Components below marked **🔴 deprecated** are preserved in git history but no longer canonical.

## Still Canonical in Phase 8

These Archon-derived components survive the Phase 8 pivot and remain in active use:

| Component | Archon source | Local path | Notes |
|-----------|---------------|------------|-------|
| **Discovery Service** | `discovery_service.py` | `apps/api/src/server/services/crawling/discovery_service.py` | `llms.txt` + `sitemap.xml` priority order, SSRF protections preserved |
| **Crawler Manager** | `crawler_manager.py` | `apps/api/src/server/services/crawling/crawler_manager.py` | Crawl4AI initialization pattern; Phase 7 added httpx fallback |
| **Crawling Orchestration** | `crawling_service.py` | `apps/api/src/server/services/crawling/crawling_service.py` | Crawl mode selection, progress mapping, cancellation |
| **Embedding Service** | `embedding_service.py` | `apps/api/src/server/services/embeddings/embedding_service.py` | Batch + partial-failure handling |
| **LLM Provider** | `llm_provider_service.py` | `apps/api/src/server/services/embeddings/llm_provider_service.py` | OpenAI-compatible client; Ollama for v1 |
| **MCP Server** | `mcp_server.py` | `apps/mcp/src/mcp_server/server.py` | Thin FastMCP service |
| **MCP RAG Tools** | `rag_tools.py` | `apps/mcp/src/mcp_server/features/rag/rag_tools.py` | KB-only tools; Phase 8 reroutes to new API endpoints (T10) |
| **Chunking Strategy** | `smart_chunk_text_async` | `apps/api/src/server/services/knowledge/ingestion_service.py` | Structural split → fallback windowing (1200–1800 chars, overlap 150–250) |
| **RAG Coordinator Pattern** | `rag_service.py` | `apps/api/src/server/services/search/rag_service.py` | embed → vector → optional hybrid → optional rerank → page grouping. Phase 8 swaps the *backend client* (T8), pattern stays. |

## 🔴 Deprecated in Phase 8

These components were canonical in Phase 7 but have been or are being replaced.

| Component | Archon source | Phase 7 location | Phase 8 replacement |
|-----------|---------------|------------------|---------------------|
| **Storage Operations** | `document_storage_operations.py`, `document_storage_service.py` | `apps/api/src/server/services/storage/storage_operations.py` (PostgREST client) | **T5** — Gitea API client. Markdown files = artifacts; commits = mutations. |
| **Source/Page/Chunk Schema** | Archon Postgres schema | `db/migrations/00{1..8}_*.sql` | **Frontmatter Pydantic schema** in `apps/api/src/server/services/knowledge/frontmatter.py` (T6). Tags/status/owner/visibility live in YAML headers. |
| **Vector Search Strategy** | `base_search_strategy.py` (pgvector RPC) | `apps/api/src/server/services/search/vector_search_strategy.py` | **T8** — Qdrant client; `match_kb_chunks` RPC removed. |
| **Hybrid Search** | `hybrid_search_strategy.py` (Postgres `tsvector` + trigram) | same path | **T8** — Qdrant **sparse-vector + BM25** at chunk-time. No PG fulltext available. |
| **`kb_settings` table** | Archon `settings` table | `db/migrations/002_settings.sql` | **Removed.** Runtime config moves to `.env` (SOPS-encrypted) + per-artifact frontmatter. |
| **Source Counts RPC** | `source_counts_rpc` | `db/migrations/008_source_counts_rpc.sql` | **Removed.** Counts derived from Qdrant payload aggregation. |
| **Contextual Schema** | Archon contextual extension | `db/migrations/007_contextual_schema.sql` | **Replaced by:** Qdrant payload metadata with frontmatter denormalization. |
| **Refresh trigger** | Internal Archon scheduler | API-side polling | **Gitea webhook (HMAC-verified) + reconcile job.** T7 deliverable. |
| **Auth model** | Supabase service-role keys | `SUPABASE_SERVICE_KEY` env | **Gitea PAT** (`GITEA_TOKEN`, SOPS-encrypted) for write paths; webhook HMAC for ingestion. |

## Excluded (Intentional Simplifications — unchanged from Phase 7)

These Archon modules were never ported and remain out of scope:

- Multi-agent routing
- Project, Task, and Workflow management
- Document/version management unrelated to KB pages
- Prompts table and prompt-builder flows
- Agent work orders
- Bug-report product features
- MCP dashboards or session UIs beyond basic health/config
- Multi-modal embeddings (text-only in v1)
- Google / Anthropic direct providers (Ollama + OpenAI-compatible only)

## SQL Migrations — Removed in #12

Phase 7 SQL migrations under `db/migrations/` were **removed in #12** (`chore(knowrag): remove deprecated Phase 7 SQL migrations`). Recover from tag `pre-knowrag-cleanup` if needed. Phase 8 does not run them.

| File (removed) | Phase 7 purpose | Replaced by |
|------|-----------------|-------------|
| `001_extensions.sql` | `vector`, `pgcrypto`, `pg_trgm` | n/a |
| `002_settings.sql` | `kb_settings` table | `.env` + frontmatter |
| `003_sources.sql` | `kb_sources` table | directory shape |
| `004_pages.sql` | `kb_pages` table | markdown files |
| `005_chunks.sql` | `kb_chunks` table | Qdrant collections |
| `006_search_functions.sql` | `match_kb_chunks`, `hybrid_search_kb_chunks` | Qdrant client |
| `007_contextual_schema.sql` | Contextual embedding columns | Qdrant payload |
| `008_source_counts_rpc.sql` | Source counts aggregation | Qdrant payload aggregation |
