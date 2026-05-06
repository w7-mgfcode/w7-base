# Runbook

Operational guidance for deploying and maintaining the KnowRAG stack.

## Local Setup

### 1. Configure Environment
Copy `.env.example` to `.env` and adjust settings.
- **JWT_SECRET**: Ensure this is at least 32 characters long.
- **SUPABASE_SERVICE_KEY**: This is the JWT signed with `JWT_SECRET`. The default in `.env.example` works with the default secret.

### 2. Launch Services
Run the containerized stack:
```bash
docker compose up -d
```
This launches:
- **knowrag-db**: PostgreSQL with pgvector.
- **knowrag-postgrest**: REST API gateway for the DB.
- **knowrag-proxy**: Nginx proxy for PostgREST.
- **knowrag-api**: Main logic, crawling, ingestion, and search.
- **knowrag-mcp**: Agentic tools server.
- **knowrag-ui**: Operator console.
- **ollama**: Local LLM and embedding provider.

### 3. Initialize Models
To use the default configuration, pull the required models to the local Ollama instance:
```bash
# For embeddings
docker exec -it knowrag-ollama ollama pull nomic-embed-text
# For contextual embeddings (if enabled)
docker exec -it knowrag-ollama ollama pull llama3
```

### 4. Database Migrations
Migrations are applied automatically during `knowrag-db` startup via `./db/migrations` volume.
If you need to apply them manually to an external database, run the SQL files in `db/migrations/` in order (001 to 007).

## Advanced Retrieval Features

### Reranking (Slice 6.1, 6.2)
To enable second-pass reranking:
1. Set `USE_RERANKING=true` in `.env`.
2. The system will use a Lexical Boost fallback if no dedicated reranker model is configured.
3. Toggle "Reranking" in the UI Search Interface or use `use_reranking=True` in MCP tools.

### Contextual Embeddings (Slice 6.3, 6.4)
To enable LLM-situated contextual embeddings during ingestion:
1. Set `USE_CONTEXTUAL_EMBEDDINGS=true` in `.env`.
2. Ensure `CHAT_MODEL` (e.g., `llama3`) is pulled in Ollama.
3. New crawls will generate 1-2 sentences of context for each chunk before embedding.
4. Note: This significantly increases ingestion time per page.

## API Operations
- **Base URL**: `http://localhost:8181`
- **Health**: `http://localhost:8181/health`
- **Swagger Docs**: `http://localhost:8181/docs`

## MCP Integration
- **Port**: `8051` (Transport: SSE)
- **Tools**: `health_check`, `session_info`, `rag_search_knowledge_base`, `start_crawl_job`, etc.

## UI Operator Console
- **URL**: `http://localhost:3737`
- Use the console to manage sources, monitor crawl progress, and perform verified RAG queries.
