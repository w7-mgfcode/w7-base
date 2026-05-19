---
paths:
  - "compose.yml"
  - "apps/*/Dockerfile"
  - ".env*"
---

# Docker & Infrastructure Rules (Phase 8)

## Compose topology

Six services in `compose.yml`:

| Service | Container port | Host port (default) | Purpose |
|---------|----------------|---------------------|---------|
| `knowrag-api` | 8181 | 8181 | FastAPI backend |
| `knowrag-mcp` | 8051 | 8051 | FastMCP proxy |
| `knowrag-ui` | 80 | 3737 | React/Vite/Tailwind UI |
| `ollama` | 11434 | 11434 | Embedding provider |
| `qdrant` | 6333 (HTTP), 6334 (gRPC) | 6333 / 6334 | Vector index |
| `gitea` | 3000 (HTTP), 22 (SSH) | 3030 / 2222 | Artifact source-of-truth |

Optional service (enabled via `--profile webui`):

| Service | Container port | Host port |
|---------|----------------|-----------|
| `open-webui` | 8080 | 3000 |

## No external dependencies

The stack is **fully self-contained**. Phase 7's `host.docker.internal:8000` Supabase dependency is **removed**. There is no external Postgres, no external auth service.

## Start order

Healthcheck-gated. Operators do **not** need to coordinate manually:

1. `ollama`, `qdrant`, `gitea` start in parallel (independent infrastructure).
2. `knowrag-api` waits until all three are `healthy`.
3. `knowrag-mcp`, `knowrag-ui` wait until `knowrag-api` is `healthy`.
4. `open-webui` (if enabled) waits for `ollama`.

## Common commands

```bash
# Full stack
docker compose up --build -d

# With optional Open WebUI
docker compose --profile webui up -d

# Pull the embedding model (one-time)
docker exec -it knowrag-ollama ollama pull nomic-embed-text

# Validate compose syntax
docker compose --env-file .env.example config -q
```

## Image pinning

All images are version-pinned. **Never** introduce a `:latest` tag. When bumping versions, do it deliberately in a `chore(deps): bump <image> to <version>` commit and validate locally.

Current pins:
- `ollama/ollama:0.30.0-rc20`
- `qdrant/qdrant:v1.12.5`
- `gitea/gitea:1.22.4`
- `ghcr.io/open-webui/open-webui:v0.4.8`

## Required env vars

`.env` (or `.env.sops`-decrypted) must define:

- `GITEA_TOKEN` — PAT with `repo` scope. **Never log, never write to manifests.**
- `GITEA_WEBHOOK_SECRET` — HMAC secret. Generate with `openssl rand -hex 32`.

The `compose.yml` uses `${VAR:?msg}` for these — startup fails fast if missing.

## Secret hygiene

- Never commit `.env` files with real values.
- Use `.env.example` as the schema (placeholders only).
- Use `.env.sops` (AGE-encrypted) for any persisted secrets.
- The W7-Base CLI (`w7 up`) auto-decrypts `.env.sops` to `.env` when newer.

## Volumes

All persistent state under `./data/`:

- `./data/ollama/` — model cache
- `./data/qdrant/` — vector index storage
- `./data/gitea/` — git repos, gitea database, configs
- `./data/open-webui/` — chat history (when enabled)

Volumes are gitignored. Backups happen via `w7 backup ll-knowrag` (tar.gz of `./data/`).

## Networking

Single user-defined bridge: `knowrag-net`. Inter-service hostnames match service names (`gitea`, `qdrant`, `ollama`, `knowrag-api`).
