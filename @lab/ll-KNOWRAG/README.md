# ll-KNOWRAG

W7-aligned local-first Knowledge Base and RAG system.

## Overview
This project is an extraction and adaptation of the Archon KB/RAG core, optimized for local operation within the W7 platform. It provides a full ingestion, embedding, and retrieval pipeline tailored for autonomous agents and local operators.

## Architecture
- **API**: FastAPI backend orchestrating Gitea CRUD, frontmatter parsing, chunking, embeddings, Qdrant upsert + query, and RAG retrieval.
- **MCP**: FastMCP service providing standard agentic tools, serving as a thin HTTP proxy to the API.
- **UI**: React + Vite + Tailwind frontend operator console for browsing the catalog, adding knowledge, and querying the KB.
- **Store**: Gitea (artifact source-of-truth — Markdown + YAML frontmatter; Git history = audit log) + Qdrant (vector index).
- **Embeddings/LLM**: Ollama (local) or OpenAI-compatible cloud (defaults to Ollama).

## Getting Started
1. **Configure Env**: Copy `.env.example` to `.env` and set `GITEA_TOKEN` (SOPS-encrypt this) and `GITEA_WEBHOOK_SECRET`.
2. **Boot Services**: `docker compose up -d`
3. **Initialize Models**:
   ```bash
   docker exec -it knowrag-ollama ollama pull nomic-embed-text
   # Optional: only needed if USE_CONTEXTUAL_EMBEDDINGS=true
   docker exec -it knowrag-ollama ollama pull llama3
   ```
4. **Access Console**: Open `http://localhost:3737` in your browser.
5. **Verify End-to-End**: Once the stack is up, prove the Phase 8 contract works:
   ```bash
   w7 verify @lab/ll-KNOWRAG
   ```
   Six checks (api.health → gitea → ingestion → search → /related → MCP) run in ~60 seconds against a live stack. Results land in `dogfood-output/<utc-timestamp>/`. See [`docs/runbook.md`](docs/runbook.md) (section: "End-to-End Verification") for run modes and troubleshooting.

## Current Status
- **Core Pipeline**: Implemented and Verified.
  - Crawl discovery (`llms.txt`, `sitemap.xml`)
  - **Recursive Crawling** with depth and page limits (Slice 7.6)
  - **LLMS.txt Task Expansion** for multi-page discovery (Slice 7.7)
  - Ingestion and chunking (Blueprint Section 10)
  - Embedding pipeline (Ollama / OpenAI-compatible)
  - Retrieval engine (Vector + Hybrid + Page grouping)
  - Advanced Retrieval (**Provider-ready Reranking** & Contextual Embeddings — gated)
  - MCP Tool Server (KB-focused tools)
  - React UI Operator Console (catalog, search, add knowledge)
  - Feature flags wired into config (`USE_HYBRID_SEARCH`, `USE_RERANKING`, etc.)
- **Phase 8 — Re-architecture**: Shipped (T1–T10 verified).
  - Storage backend pivoted from Supabase/PostgREST/pgvector to **Gitea + Qdrant + Ollama**
  - HMAC-verified Gitea webhook ingestion + reconcile job
  - Frontmatter Pydantic schema (tags/status/version/owner/visibility)
  - Tailwind v4 design system + Stitch primitives + card-grid catalog UI
  - **End-to-end verify harness** (`w7 verify @lab/ll-KNOWRAG`) — closes the deferred-items gap from the T10 dogfood
- **Ready for**: Local dev execution, testing, and agent integration.

## License
MIT
