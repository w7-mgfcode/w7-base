# Runbook

Operational guidance for deploying and maintaining the KnowRAG stack.

## Local Setup
1. **Docker Compose Boot**: `docker compose up -d` to launch the API, MCP, and UI services along with the local Ollama instance.
2. **Supabase Migration**: Apply migrations in `db/migrations/` to your target Supabase instance before testing ingestion.
3. **Ollama Model Pull**: To use local embeddings, pull the expected model.
   ```bash
   docker exec -it knowrag-ollama ollama pull nomic-embed-text
   ```

## API Operations
- The API is available at `http://localhost:8181`
- Auto-generated Swagger docs at `http://localhost:8181/docs`

## MCP Integration
- The MCP server listens on port `8051`
- It is a thin proxy; all business logic remains in `knowrag-api`
- Can be added to local agents via standard FastMCP / SSE or stdio bridges if running directly.

## UI Operator Console
- The UI runs at `http://localhost:3737`
- Use the UI to verify sources, crawl new URLs, and test the chunk and page-level retrieval.
