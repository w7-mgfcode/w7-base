# Archon Porting Map

This document tracks the extraction and adaptation of components from the Archon repository into `ll-KNOWRAG`.

## Successfully Ported & Adapted
- **Discovery Service**: `discovery_service.py` ported to `apps/api/src/server/services/crawling/` (Focuses strictly on `llms.txt` and `sitemap.xml`).
- **Crawler Manager**: `crawler_manager.py` ported to `apps/api/...` (Simplified to use `httpx` and `BeautifulSoup` for local-first reliability).
- **Crawling Orchestration**: `crawling_service.py` ported and wired as the authoritative upstream to ingestion.
- **Storage Operations**: Ported the `Source -> Page -> Chunk` hierarchical upsert pattern.
- **Ingestion Service**: Implemented the two-stage Blueprint Section 10 chunking strategy.
- **Embeddings**: `embedding_service.py` and `llm_provider_service.py` ported with batching support (Ollama/OpenAI compatible).
- **Retrieval Engine**: `rag_service.py`, `vector_search_strategy.py`, and `hybrid_search_strategy.py` ported to utilize direct Supabase RPCs (`match_kb_chunks`, `hybrid_search_kb_chunks`).
- **MCP Server**: Thin FastMCP wrapper forwarding directly to API, porting `rag_tools.py` logic.
- **UI Views**: `KnowledgeView` and `AddKnowledgeDialog` patterns recreated in a lightweight React/Vite operator console.

## Excluded (Intentional Simplifications)
- Archon multi-agent routing.
- Project, Task, and Workflow management concepts.
- Broad multi-modal embedding logic (restricted to Text/Vector initially).
- Reranking (Feature flag prepared, but omitted from the default happy path).
