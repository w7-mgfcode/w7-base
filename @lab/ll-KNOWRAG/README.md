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
1. **Configure Env**: Copy `.env.example` to `.env` and set `JWT_SECRET` and `SUPABASE_SERVICE_KEY`.
2. **Boot Services**: `docker compose up -d`
3. **Initialize Models**:
   ```bash
   docker exec -it knowrag-ollama ollama pull nomic-embed-text
   docker exec -it knowrag-ollama ollama pull llama3
   ```
4. **Access Console**: Open `http://localhost:3737` in your browser.

## Current Status
- **Core Pipeline**: Implemented and Verified.
  - Repo foundation, DB migrations (001-007)
  - Crawl discovery (`llms.txt`, `sitemap.xml`)
  - **Recursive Crawling** with depth and page limits (Slice 7.6)
  - **LLMS.txt Task Expansion** for multi-page discovery (Slice 7.7)
  - Ingestion and chunking (Blueprint Section 10)
  - Embedding pipeline (Ollama / OpenAI-compatible)
  - Retrieval engine (Vector + Hybrid + Page grouping)
  - Advanced Retrieval (**Provider-ready Reranking** & Contextual Embeddings - gated)
  - MCP Tool Server (KB-focused tools)
  - React UI Operator Console (source management, search, add knowledge)
  - Feature flags wired into config (`USE_HYBRID_SEARCH`, `USE_RERANKING`, etc.)
- **Maintenance & Security (Phase 7)**: Implemented.
  - Environment variable interpolation in Compose
  - Hardened secret management (no hardcoded keys in Compose)
  - Startup model validation and improved logging
  - Log level configuration
  - Operator docs and Runbook updated
- **Ready for**: Local dev execution, testing, and agent integration.

## License
MIT
