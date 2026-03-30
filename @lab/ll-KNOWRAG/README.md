# ll-KNOWRAG

W7-aligned local-first Knowledge Base and RAG system.

## Overview
This project is an extraction and adaptation of the Archon KB/RAG core, optimized for local operation within the W7 platform. It provides a full ingestion, embedding, and retrieval pipeline tailored for autonomous agents and local operators.

## Architecture
- **API**: FastAPI backend orchestrating crawling, ingestion, chunking, embeddings, and RAG retrieval.
- **MCP**: FastMCP service providing standard agentic tools, serving as a thin wrapper around the API.
- **UI**: React frontend operator console for managing sources, adding knowledge via crawl, and querying the KB.
- **Store**: Local Supabase (PostgreSQL + pgvector).
- **Embeddings/LLM**: Ollama (local) or OpenAI-compatible cloud (defaults to Ollama).

## Getting Started
1. Copy `.env.example` to `.env`.
2. Configure your `SUPABASE_URL` and `SUPABASE_SERVICE_KEY`.
3. (Optional) Run `docker compose up -d ollama` and pull your model: `docker exec -it knowrag-ollama ollama pull nomic-embed-text`
4. Run `docker compose up --build`.

## Current Status
- **Core Pipeline**: Implemented.
  - Repo foundation, DB migrations (001-006)
  - Crawl discovery (`llms.txt`, `sitemap.xml`)
  - Ingestion and chunking (Blueprint Section 10)
  - Embedding pipeline (Ollama / OpenAI-compatible)
  - Retrieval engine (Vector + Hybrid + Page grouping)
  - MCP Tool Server (KB-focused tools)
  - React UI Operator Console (source management, search, add knowledge)
  - Feature flags wired into config (`USE_HYBRID_SEARCH`, `USE_RERANKING`, etc.)
- **Pending**:
  - Reranking implementation (feature flag exists, no logic yet)
  - Contextual embeddings (feature flag exists, no logic yet)
  - Code examples table and endpoints (optional, deferred)
  - Comprehensive integration and end-to-end test coverage
- **Ready for**: Local dev execution and testing.
