# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> **Phase 8 in progress.** The Phase 7 architecture (Supabase + PostgREST + pgvector) is being replaced by **Gitea + Qdrant + Ollama**. See `BLUEPRINT.md` for canon and `.omg/state/taskboard.md` for the 10-subtask plan.

## Project Overview

ll-KNOWRAG is a local-first, 100% private knowledge-base + RAG system. Markdown artifacts live in a **Gitea** repo (the source-of-truth); a **Qdrant** vector index drives semantic search; **Ollama** generates embeddings locally; a React/Vite/Tailwind UI and a FastMCP server expose the KB to operators and external agents.

Part of the W7 platform (`@lab` zone). Archon-derived RAG core, but the storage backend has been completely rebuilt.

## Architecture (Phase 8)

Six services, all in `compose.yml`:

- **knowrag-api** (`apps/api/`) — FastAPI backend. Owns Gitea CRUD, frontmatter parsing, chunking, embedding (via Ollama), Qdrant upsert + query, RAG retrieval. Entry point: `src/server/main.py`.
- **knowrag-mcp** (`apps/mcp/`) — FastMCP server. **Thin HTTP proxy** to the API; never reimplements KB logic. Entry point: `src/mcp_server/server.py`.
- **knowrag-ui** (`apps/ui/`) — React + Vite + TypeScript + **Tailwind** frontend (Phase 8). Operator console for browsing the catalog and querying the KB.
- **gitea** — local Gitea instance. Hosts the KB repo (`knowrag/kb-default` by default). Git history = audit log.
- **qdrant** — vector index. Collections per visibility scope (`kb_public`, `kb_private`).
- **ollama** — embedding provider (default model: `nomic-embed-text`).
- **open-webui** — optional chat surface (enable with `--profile webui`).

No external dependencies — the stack is fully self-contained on a single host.

### API Service Internals

Dependency wiring: `apps/api/src/server/dependencies.py` — global singleton services initialized at import time, exposed via factory functions for FastAPI injection.

Service layers under `apps/api/src/server/services/`:
- `crawling/` — URL discovery (`llms.txt`, `sitemap.xml`), Crawl4AI manager, crawl orchestration. **Output is markdown commits to Gitea**, not direct DB writes.
- `storage/` — Gitea API client (Phase 8). Treats the KB repo as the artifact CRUD backend.
- `knowledge/` — frontmatter parser, ingestion coordinator, reconcile service.
- `embeddings/` — provider abstraction (Ollama / OpenAI-compatible), batch embedding.
- `search/` — Qdrant client, vector search, hybrid (sparse + BM25), RAG coordinator.

API routes: `knowledge_api.py` (CRUD via Gitea), `rag_api.py` (search), `pages_api.py` (artifact retrieval + `/related`), `ingest_api.py` (Gitea webhook receiver, HMAC-verified).

### MCP Service Internals

`KnowRagApiClient` (`apps/mcp/src/mcp_server/api_client.py`) is the HTTP client. Tools registered in `features/rag/rag_tools.py`. All tools forward to the API — never call Qdrant or Gitea directly.

## Common Commands

### Run the full stack
```bash
docker compose up --build -d
```

### Run with optional Open WebUI
```bash
docker compose --profile webui up -d
```

### Pull the embedding model (one-time)
```bash
docker exec -it knowrag-ollama ollama pull nomic-embed-text
```

### UI development (hot-reload outside Docker)
```bash
cd apps/ui && npm install && npm run dev
```

### API development (hot-reload outside Docker)
```bash
cd apps/api && pip install -r requirements.txt
PYTHONPATH=src uvicorn server.main:app --host 0.0.0.0 --port 8181 --reload
```

## KB Repo Layout

The Gitea repo (`${GITEA_KB_REPO}`, default `kb-default`) follows this directory shape:

```
kb-default/
├── prompts/         System prompts, prompt templates
├── commands/        Slash commands, CLI invocations
├── mcp/             MCP server configs and notes
├── hooks/           Hook scripts and triggers
├── skills/          Agent skills, capabilities
└── knowledge/       General knowledge articles
```

Each artifact is a single `.md` file with YAML frontmatter:

```markdown
---
id: a3f2-9b1c
tags: [agents, mcp, claude]
status: published          # draft | review | published
version: 1.2.0
owner: w7-mgfcode
visibility: public         # public | private (must match repo visibility)
---

# Title
Markdown body — chunked at ingestion time.
```

## Configuration

Environment variables in `.env` (see `.env.example`). Key vars:

| Variable | Purpose |
|----------|---------|
| `GITEA_TOKEN` | **Required.** PAT with `repo` scope. SOPS-encrypt this. |
| `GITEA_WEBHOOK_SECRET` | **Required.** HMAC secret for webhook verification. |
| `GITEA_BASE_URL` | Gitea API endpoint (default: `http://gitea:3000`) |
| `GITEA_KB_OWNER`/`GITEA_KB_REPO` | Which repo to track (default: `knowrag/kb-default`) |
| `OLLAMA_BASE_URL` | Embedding provider (default: `http://ollama:11434`) |
| `EMBEDDING_MODEL` | Model identifier (default: `nomic-embed-text`) |
| `QDRANT_HOST` / `QDRANT_PORT` | Vector store (default: `qdrant:6333`) |
| `API_PORT` / `MCP_PORT` / `UI_PORT` | 8181 / 8051 / 3737 |

Feature flags: `USE_HYBRID_SEARCH`, `USE_RERANKING`, `USE_CONTEXTUAL_EMBEDDINGS`.

Config is loaded via Pydantic Settings in `apps/api/src/server/config/config.py`.

## Key Design Decisions (Phase 8)

- **Git is the source of truth.** Commits = mutations. Conflicts surface as merge conflicts, not last-write-wins.
- **Qdrant is the search index, not the storage.** Re-deriving the index from Git is always possible (reconcile job does this on a schedule).
- **Frontmatter drives filtering.** Tags, status, owner, visibility live in YAML headers. Pydantic schema rejects malformed metadata.
- **MCP stays a thin proxy.** No KB logic in the MCP service.
- **Chunking targets 1200–1800 chars with 150–250 char overlap.** Stricter than Archon's 5000 default.
- **Embedding providers in v1: Ollama and one OpenAI-compatible.** No Google / Anthropic / other providers.
- **HMAC-verified webhooks.** Every ingestion trigger must validate `X-Gitea-Signature`.

## Service Ports

| Service | Container Port | Host Port (default) |
|---------|----------------|---------------------|
| API     | 8181 | 8181 |
| MCP     | 8051 | 8051 |
| UI      | 80   | 3737 |
| Ollama  | 11434 | 11434 |
| Qdrant HTTP | 6333 | 6333 |
| Qdrant gRPC | 6334 | 6334 |
| Gitea HTTP | 3000 | 3030 |
| Gitea SSH  | 22 | 2222 |
| Open WebUI (optional) | 8080 | 3000 |

## Reference Docs

- `BLUEPRINT.md` — full system design (Phase 8 canon)
- `docs/api-contracts.md` — API endpoints and MCP tools
- `docs/runbook.md` — operational guidance
- `docs/archon-porting-map.md` — Archon source mapping (with Phase 8 deprecation notes)
- `.omg/state/taskboard.md` — Phase 8 10-subtask plan and current status

## Phase 7 Notes (deprecated)

The Phase 7 stack used Supabase + PostgREST + pgvector for storage. The SQL migrations under `db/migrations/00{1..8}_*.sql` were removed in #12; recover via tag `pre-knowrag-cleanup` if needed. Schema now lives in `apps/api/src/server/services/knowledge/frontmatter.py` (Pydantic models).
