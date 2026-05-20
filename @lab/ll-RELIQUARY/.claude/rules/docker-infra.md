# Docker & Infrastructure Rules — ll-RELIQUARY

## Compose topology

Four services in `compose.yml`:

| Service | Container port | Host port (default) | Purpose |
|---------|----------------|---------------------|---------|
| `reliquary-ui` | 8080 | 4242 | React + Vite + Tailwind v4 (nginx in prod) |
| `reliquary-api` | 8282 | 8282 | FastAPI backend |
| `reliquary-db` | 5432 | 5454 | Postgres 16 — persistent game state |
| `reliquary-cache` | 6379 | 6464 | Redis 7 — sessions, leaderboards, pub/sub |

No external dependencies. Single-host. Everything in `./data/` survives restarts.

## Start order

Healthcheck-gated. Operators do **not** coordinate manually:

1. `reliquary-db`, `reliquary-cache` start in parallel.
2. `reliquary-api` waits until both are `healthy`.
3. `reliquary-ui` waits until `reliquary-api` is `healthy`.

## Common commands

```bash
# Full stack
docker compose up --build -d

# From the W7 CLI (preferred — merges env files, sets COMPOSE_PROJECT_NAME)
w7 up @lab/ll-RELIQUARY

# Live logs
w7 logs @lab/ll-RELIQUARY

# Tear down (keeps data/)
w7 down @lab/ll-RELIQUARY

# Validate compose syntax against the schema
docker compose --env-file .env.example config -q
```

## Image pinning

All images version-pinned. **Never `:latest`.** Bump in a `chore(deps): bump <image> to <version>` commit with local validation.

Current pins:
- `postgres:16.6-alpine`
- `redis:7.4.1-alpine`
- Application images (`reliquary-api`, `reliquary-ui`) built locally — pin base images in the Dockerfile, not floating tags.

## Required env vars

`.env` (or decrypted `.env.sops`) must define:

- `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` — db credentials.
- `REDIS_PASSWORD` — required even in dev; never blank.
- `API_SESSION_SECRET` — 32-byte hex; generate with `openssl rand -hex 32`.
- `API_CORS_ORIGINS` — comma-separated UI origins.

`compose.yml` uses `${VAR:?msg}` for hard requirements — startup fails fast if missing.

## Secret hygiene

- Never commit `.env`.
- `.env.example` is the schema (placeholders only).
- Persisted secrets go in `.env.sops` (AGE-encrypted) once they exist.
- `w7 secret edit @lab/ll-RELIQUARY` is the sanctioned editor.

## Volumes

All persistent state under `./data/`:

- `./data/postgres/` — game state
- `./data/redis/` — RDB snapshots (60s/1-key save cadence)

Volumes are gitignored. Backups via `w7 backup ll-RELIQUARY` (tar.gz of `./data/`).

## Networking

Single user-defined bridge: `reliquary-net`. Inter-service hostnames match service names — UI talks to `reliquary-api`, API talks to `reliquary-db` and `reliquary-cache`.

Traefik labels deferred until first deploy. Boilerplate exposes host ports directly for local dev.

## Resource defaults

No `deploy:` constraints in v0 — runs as-is on dev host. Add CPU/memory caps when the stack stabilises and we have real numbers.

No GPU dependency — unlike KNOWRAG, Reliquary has no local-LLM inference path in scope.
