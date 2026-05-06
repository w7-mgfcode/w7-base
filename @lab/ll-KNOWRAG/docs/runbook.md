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
- **Port**: `8051` (Transport: HTTP)
- **Tools**: `health_check`, `session_info`, `rag_search_knowledge_base`, `rag_get_available_sources`, `rag_list_pages_for_source`, `rag_read_full_page`.

## UI Operator Console
- **URL**: `http://localhost:3737`
- Use the console to manage sources, monitor crawl progress, and perform verified RAG queries.

## End-to-End Verification (`w7 verify @lab/ll-KNOWRAG`)

Use `w7 verify` to prove the deployed stack actually delivers the Phase 8 contract — not just that containers came up. The harness runs six checks in order against a live, running stack:

| # | Check | Asserts |
|---|---|---|
| 1 | `api.health` | `GET /health` returns `{"status":"ok"}` |
| 2 | `gitea.kb_repo_exists` | KB repo is reachable via the Gitea API |
| 3 | `ingestion.seed_and_grow` | Four fixtures committed to a temp branch grow Qdrant `points_count` within 60s |
| 4 | `search.api_returns_hits` | `POST /api/artifacts/search` returns ≥1 hit for the seeded baseline |
| 5 | `related.api_returns_3_plus` | `GET /api/artifacts/.../related?k=5` returns ≥3 sibling artifacts |
| 6 | `mcp.search_returns_hits` | MCP `rag_search_knowledge_base` tool returns content over the FastMCP HTTP transport |

### Run modes

```bash
# Standalone — assumes the stack is already up
bash scripts/verify.sh

# Via the W7 CLI — decrypts secrets, exports envvars, dispatches
w7 verify @lab/ll-KNOWRAG

# Cold start (compose up first; takes ~10–20 min on first ollama pull)
w7 verify @lab/ll-KNOWRAG --cold

# Seed from your Claude Code memory dir instead of built-in fixtures
w7 verify @lab/ll-KNOWRAG --seed-from-memory

# Keep the temp branch + Qdrant points around for inspection
w7 verify @lab/ll-KNOWRAG --keep
```

### Outputs

Each run writes to `dogfood-output/<utc-timestamp>/`:

- `result.json` — machine-readable envelope with per-check `status`, `duration_ms`, `severity`, `detail` and a top-level `summary` count (suitable for CI gating)
- `report.md` — human-readable summary
- `curl-trace.log` — raw HTTP errors (only relevant when something fails)

### Exit codes

| Code | Meaning |
|---|---|
| `0` | All checks passed |
| `1` | At least one check failed (inspect `result.json`) |
| `2` | Setup error: missing `GITEA_TOKEN`, can't bring stack up, no `scripts/verify.sh` for the target |
| `127` | Required command missing (`curl`, `jq`, `base64`, `docker`) |

### Cleanup

By default, the EXIT trap removes the temp Gitea branch (`verify-<utc-ts>-<pid>`) and the seeded artifacts' Qdrant points. The KB's `main` branch is never touched. `--keep` skips both for post-mortem inspection.

### Troubleshooting failed checks

| Failure | Likely cause | First thing to check |
|---|---|---|
| `api.health` | API container down or unreachable | `docker ps \| grep knowrag-api`, `curl http://localhost:8181/health` |
| `gitea.kb_repo_exists` | KB repo not auto-provisioned, or wrong `GITEA_KB_OWNER`/`GITEA_KB_REPO` | `curl -H "Authorization: token $GITEA_TOKEN" http://localhost:3030/api/v1/repos/$GITEA_KB_OWNER/$GITEA_KB_REPO` |
| `ingestion.seed_and_grow` | Webhook misfire, Ollama unhealthy, Qdrant collection missing | `docker logs knowrag-api`, `curl http://localhost:11434/api/tags`, `curl http://localhost:6333/collections` |
| `search.api_returns_hits` | Embeddings degenerate, hybrid-search misconfigured | re-run with `--keep`, query Qdrant directly with the same embedding |
| `related.api_returns_3_plus` | Fixtures didn't share enough vocabulary with the baseline, or chunker emitted too few chunks | inspect chunks via Qdrant; consider widening fixture vocabulary |
| `mcp.search_returns_hits` | MCP container down, FastMCP route shape changed | `docker ps \| grep knowrag-mcp`, `curl -X POST http://localhost:8051/mcp/` with a JSON-RPC body |

See `@lab/ll-KNOWRAG/scripts/README.md` for the full operator guide and how to add new fixtures.
