# Runbook

Operational guidance for deploying and maintaining the KnowRAG stack.

## Local Setup

### 1. Configure Environment
Copy `.env.example` to `.env` and adjust settings.
- **GITEA_TOKEN**: PAT with `repo` scope. SOPS-encrypt this.
- **GITEA_WEBHOOK_SECRET**: HMAC secret for webhook verification.
- **GITEA_BASE_URL**, **GITEA_KB_OWNER**, **GITEA_KB_REPO**: which Gitea repo backs the KB (defaults: `http://gitea:3000`, `knowrag/kb-default`).
- **OLLAMA_BASE_URL**, **EMBEDDING_MODEL**: embedding provider (defaults: `http://ollama:11434`, `nomic-embed-text`).
- **QDRANT_HOST**, **QDRANT_PORT**: vector store (defaults: `qdrant:6333`).

### 2. Launch Services
Run the containerized stack:
```bash
docker compose up -d
```
This launches:
- **knowrag-api**: FastAPI backend — Gitea CRUD, frontmatter parsing, chunking, embedding, Qdrant upsert + query, RAG retrieval.
- **knowrag-mcp**: FastMCP server — thin HTTP proxy to the API.
- **knowrag-ui**: React + Vite + Tailwind operator console.
- **gitea**: artifact source-of-truth (Markdown + YAML frontmatter; Git history = audit log).
- **qdrant**: vector index. Collections per visibility scope (`kb_public`, `kb_private`).
- **ollama**: local embedding provider.

Optional Open WebUI chat surface:
```bash
docker compose --profile webui up -d
```

### 3. Initialize Models
Pull the required embedding model (one-time):
```bash
# For embeddings
docker exec -it knowrag-ollama ollama pull nomic-embed-text
# For contextual embeddings (only if USE_CONTEXTUAL_EMBEDDINGS=true)
docker exec -it knowrag-ollama ollama pull llama3
```

### 4. Knowledge Base Bootstrap
The `gitea` service auto-provisions `${GITEA_KB_OWNER}/${GITEA_KB_REPO}` (default `knowrag/kb-default`) on first start, with the directory shape `prompts/`, `commands/`, `mcp/`, `hooks/`, `skills/`, `knowledge/`. Each artifact is a `.md` file with YAML frontmatter (`id`, `tags`, `status`, `version`, `owner`, `visibility`).

On every push to the KB repo, Gitea fires an HMAC-signed webhook. The API verifies the signature, chunks the markdown, embeds via Ollama, and upserts into Qdrant. A periodic reconcile job catches missed events.

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
