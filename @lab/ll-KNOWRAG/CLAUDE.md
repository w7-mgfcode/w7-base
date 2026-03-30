# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ll-KNOWRAG is a local-first Knowledge Base and RAG system extracted and adapted from the Archon project. It ingests websites/documents, chunks and embeds content, and provides retrieval via API, MCP tools, and a React UI. The core data model is **source -> page -> chunk**.

Part of the W7 platform (`@lab` zone). Uses local Supabase (PostgreSQL + pgvector) for storage and Ollama for embeddings.

## Architecture

Three services plus infrastructure:

- **knowrag-api** (`apps/api/`) - FastAPI backend. Owns all KB logic: crawling, discovery, ingestion, chunking, embedding, storage, and RAG retrieval. Entry point: `src/server/main.py`.
- **knowrag-mcp** (`apps/mcp/`) - FastMCP server. Thin HTTP proxy to the API, never reimplements KB logic. Entry point: `src/mcp_server/server.py`.
- **knowrag-ui** (`apps/ui/`) - React + Vite + TypeScript frontend. Operator console for managing sources and querying the KB.
- **ollama** - Local embedding model server (default model: `nomic-embed-text`).

External dependency: local Supabase instance (not in this compose, assumed running on `host.docker.internal:8000`).

### API Service Internals

Dependency wiring is in `apps/api/src/server/dependencies.py` — global singleton services initialized at import time, exposed via factory functions for FastAPI injection.

Service layers under `apps/api/src/server/services/`:
- `crawling/` — discovery (`llms.txt`, `sitemap.xml`), crawler manager (Crawl4AI), crawl orchestration
- `storage/` — source/page/chunk persistence to Supabase
- `knowledge/` — ingestion pipeline (storage + embedding coordination)
- `embeddings/` — provider abstraction (Ollama/OpenAI-compatible), batch embedding
- `search/` — vector search strategy, hybrid search strategy, RAG service (coordinator pattern: embed query -> vector search -> optional hybrid -> optional rerank -> page grouping)

API routes: `knowledge_api.py` (CRUD + crawl), `rag_api.py` (search), `pages_api.py` (page retrieval).

### MCP Service Internals

`KnowRagApiClient` (`apps/mcp/src/mcp_server/api_client.py`) is the HTTP client. Tools registered in `features/rag/rag_tools.py`. All tools forward to the API.

## Common Commands

### Run the full stack
```bash
docker compose up --build
```

### Run individual services
```bash
docker compose up -d knowrag-api
docker compose up -d knowrag-mcp
docker compose up -d knowrag-ui
docker compose up -d ollama
```

### Pull the embedding model
```bash
docker exec -it knowrag-ollama ollama pull nomic-embed-text
```

### UI development
```bash
cd apps/ui && npm install && npm run dev
```

### API development (local, outside Docker)
```bash
cd apps/api && pip install -r requirements.txt
PYTHONPATH=src uvicorn server.main:app --host 0.0.0.0 --port 8181 --reload
```

## Database

Migrations live in `db/migrations/` (001-006), applied manually to the Supabase instance. Order matters — they create extensions, then `kb_settings`, `kb_sources`, `kb_pages`, `kb_chunks`, and search functions (`match_kb_chunks`, `hybrid_search_kb_chunks`).

Tables use `kb_` prefix. Chunks have a `vector` column for embeddings and a `tsvector` for full-text search.

## Configuration

Environment variables in `.env` (see `.env.example`). Key vars:
- `SUPABASE_URL`, `SUPABASE_SERVICE_KEY` — database connection
- `OLLAMA_BASE_URL` — embedding provider
- `API_PORT` (8181), `MCP_PORT` (8051), `UI_PORT` (3737)
- Feature flags: `USE_HYBRID_SEARCH`, `USE_RERANKING`, `USE_CONTEXTUAL_EMBEDDINGS`, `ENABLE_CODE_EXAMPLES`

Config is loaded via Pydantic Settings in `apps/api/src/server/config/config.py`.

## Key Design Decisions

- This is an **extraction-and-adaptation** from Archon, not a greenfield project. Archon's KB/RAG patterns must be preserved or simplified, not rewritten without justification (see `BLUEPRINT.md` Section 5).
- MCP is a mandatory separate service — it must not contain KB logic.
- Chunking targets 1200-1800 chars with 150-250 char overlap (stricter than Archon's 5000-char default).
- v1 embedding providers: Ollama and one OpenAI-compatible provider only.

## Service Ports

| Service | Port |
|---------|------|
| API     | 8181 |
| MCP     | 8051 |
| UI      | 3737 |
| Ollama  | 11434 |

## Reference Docs

- `BLUEPRINT.md` — full system design, porting map, data model, and implementation slices
- `docs/api-contracts.md` — API endpoints and MCP tools
- `docs/schema.md` — database schema overview
- `docs/runbook.md` — operational guidance
- `docs/archon-porting-map.md` — mapping from Archon source files
