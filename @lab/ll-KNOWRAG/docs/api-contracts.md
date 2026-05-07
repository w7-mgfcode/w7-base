# KnowRAG API Contracts

> Authoritative reference for the HTTP surface served by `knowrag-api`
> (see `apps/api/src/server/main.py`) and the FastMCP tool surface served
> by `knowrag-mcp` (see `apps/mcp/src/mcp_server/features/rag/rag_tools.py`).
> The Phase 8 backend is **Gitea + Qdrant + Ollama** — there is no
> `/api/pages`, `/api/rag/*`, `/api/knowledge-items`, or `/api/upload`
> route in the running service.

## Artifacts

### `GET /api/artifacts`

List artifacts (optionally filtered by category) with parsed frontmatter.
Body is omitted — use `GET /api/artifacts/{path}` for full content.

| Query param | Type | Required | Notes |
|---|---|---|---|
| `category` | string | no | One of `prompts`, `commands`, `mcp`, `hooks`, `skills`, `knowledge` |

Response — `200 OK`, `List[ArtifactSummary]`:

```json
[
  {
    "path": "knowledge/rag-101.md",
    "frontmatter": { "id": "...", "tags": [...], "status": "...", "owner": "...", "version": "...", "visibility": "..." },
    "commit_sha": "abc1234...",
    "size": 4231
  }
]
```

Status codes: `200`, `400` (bad category), `502` (Gitea storage error).

### `GET /api/artifacts/{path}`

Fetch one artifact (frontmatter + full body + commit SHA) for the detail view.

| Param | Type | Required | Notes |
|---|---|---|---|
| `path` | path | yes | `<category>/<name>.md` (URL-encoded) |
| `ref` | query | no | Read at a specific commit / branch / tag (default: repo branch) |

Response — `200 OK`, `Artifact`:

```json
{
  "path": "knowledge/rag-101.md",
  "frontmatter": { ... },
  "body": "# Title\n\nMarkdown body...",
  "commit_sha": "abc1234...",
  "size": 4231
}
```

Status codes: `200`, `400` (invalid path), `404` (not found), `502` (Gitea error).

### `GET /api/artifacts/{path}/related`

Find `k` artifacts semantically similar to the given one. Computes the centroid
of the seed artifact's chunks and runs a kNN on Qdrant, deduplicated by
`artifact_path` (one entry per related artifact, not per chunk).

| Param | Type | Required | Default | Notes |
|---|---|---|---|---|
| `path` | path | yes | — | Seed artifact path |
| `visibility` | query | no | `public` | `public` or `private` |
| `k` | query | no | `5` | 1–20 |

Response — `200 OK`, `List[RelatedArtifact]`:

```json
[
  {
    "artifact_path": "knowledge/related-1.md",
    "score": 0.86,
    "section_title": "Intro",
    "snippet": "Truncated 180-char preview...",
    "tags": ["rag", "qdrant"],
    "status": "published",
    "owner": "w7-mgfcode",
    "shared_tags": ["rag"]
  }
]
```

Status codes: `200`, `400` (bad visibility), `502` (search error). Returns `[]` if the seed artifact does not exist.

### `POST /api/artifacts/search`

Semantic search over Qdrant chunks with frontmatter filter pushdown. Always
returns page-grouped results (`mode="page"`).

Request body — `SearchRequest`:

```json
{
  "query": "how does ingestion work",
  "visibility": "public",
  "tags": ["ingestion"],
  "status": ["published"],
  "owner": "w7-mgfcode",
  "top_k": 20,
  "use_hybrid": false,
  "use_rerank": false
}
```

Response — `200 OK`:

```json
{
  "hits":  [ { "artifact_path": "...", "chunk_index": 0, "content": "...", "score": 0.91, "section_title": "...", "commit_sha": "...", "tags": [...], "status": "...", "owner": "..." } ],
  "pages": [ { "artifact_path": "...", "top_score": 0.91, "top_chunk_index": 0, "section_titles": [...], "chunk_count": 3, "owner": "...", "tags": [...] } ]
}
```

Status codes: `200`, `400` (empty query / bad visibility / `top_k <= 0`), `502` (search backend error).

## Ingestion

### `POST /api/ingest/webhook`

Gitea webhook receiver. HMAC-SHA256 verified via `X-Gitea-Signature` against
`GITEA_WEBHOOK_SECRET`. Diffs the push, chunks affected markdown, embeds via
Ollama, and upserts into Qdrant. Idempotent on re-runs.

Status codes: `200` (processed), `401` (HMAC failure), `400` (malformed payload), `502` (downstream Gitea/Qdrant/Ollama error).

### `POST /api/ingest/reconcile`

Manually trigger the reconcile job — compares Git HEAD against Qdrant payload
metadata and re-ingests anything that drifted. Use after operator-side ingest
gaps (webhook downtime, manual repo edits).

Status codes: `200`, `502`.

## Health

- `GET /health` — `{ "status": "ok", "service": "knowrag-api" }`
- `GET /api/health` — same payload, alternate mount point for proxies

## OpenAPI

The full OpenAPI 3 schema is served at `GET /openapi.json`; the Swagger UI is at
`GET /docs` and the ReDoc view at `GET /redoc`.

---

# MCP Tools

Served by `knowrag-mcp` (FastMCP). Every tool is a thin HTTP proxy to the API
above — no KB logic lives in the MCP service.

| Tool | Forwards to | Purpose |
|---|---|---|
| `health_check` | `GET /health` | System health |
| `session_info` | — | Static info: API base URL, transport, registered tools |
| `rag_list_artifacts(category?)` | `GET /api/artifacts` | List artifacts with frontmatter |
| `rag_get_artifact(path, ref?)` | `GET /api/artifacts/{path}` | Full artifact (frontmatter + body + commit SHA) |
| `rag_get_related_pages(path, k?, visibility?)` | `GET /api/artifacts/{path}/related` | kNN related artifacts |
| `rag_search_artifacts(query, tags?, status?, owner?, visibility?, top_k?, use_hybrid?, use_rerank?)` | `POST /api/artifacts/search` | Semantic search with filter pushdown |

`tags` and `status` accept `List[str]`, comma-separated string, or JSON-encoded
array — the MCP layer normalizes via `_coerce_str_list` to tolerate the
FastMCP v3 client quirk where list params arrive as JSON strings.
