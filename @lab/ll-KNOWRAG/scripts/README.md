# `@lab/ll-KNOWRAG/scripts/`

End-to-end smoke harness for the KNOWRAG stack.

## Files

| File | Purpose |
|---|---|
| `verify.sh` | Asserts the Phase 8 contract on a live, running stack. Six checks in order. |
| `lib/verify-helpers.sh` | Pure-bash helpers: HTTP wrappers, polling, JSON/MD result emitters. |
| `fixtures/*.md` | Four seed artifacts (baseline + 3 related) committed to a temp Gitea branch. |

## How to run

```bash
# Standalone (assumes stack is up)
bash scripts/verify.sh

# Via the W7 CLI
w7 verify @lab/ll-KNOWRAG

# With a cold-start (brings the stack up first; takes 10–20 min on first ollama pull)
w7 verify @lab/ll-KNOWRAG --cold

# Seed from your Claude Code memory directory instead of built-in fixtures
w7 verify @lab/ll-KNOWRAG --seed-from-memory

# Keep the temp branch + Qdrant points around for inspection
w7 verify @lab/ll-KNOWRAG --keep
```

## Exit codes

| Code | Meaning |
|---|---|
| `0` | All checks passed |
| `1` | At least one check failed (see `result.json` and `report.md`) |
| `2` | Setup error (missing `GITEA_TOKEN`, can't bring stack up, etc.) |
| `127` | Required command missing (`curl`, `jq`, `base64`, `docker`) |

## What gets checked (in order)

1. **`api.health`** — `GET /health` returns `{"status":"ok"}`
2. **`gitea.kb_repo_exists`** — `GET /repos/${OWNER}/${REPO}` returns the repo metadata
3. **`ingestion.seed_and_grow`** — fixtures committed to a temp branch; Qdrant `points_count` grows past pre-count within 60s
4. **`search.api_returns_hits`** — `POST /api/artifacts/search` returns ≥1 hit
5. **`related.api_returns_3_plus`** — `GET /api/artifacts/.../related?k=5` returns ≥3
6. **`mcp.search_returns_hits`** — MCP `rag_search_knowledge_base` tool returns content

Order is cheap-first → expensive-last so a fast failure aborts before slow polls.

## Outputs

Each run writes to `dogfood-output/<utc-timestamp>/`:

- `result.json` — machine-readable envelope (CI gate)
- `report.md` — human-readable summary
- `curl-trace.log` — raw HTTP errors (only relevant when something fails)

## Cleanup

By default, the cleanup hook (trap on EXIT) removes:
- the temp Gitea branch (`verify-<utc-ts>-<pid>`)
- Qdrant points whose `artifact_path` matches the seeded paths

`--keep` skips both. Useful for post-mortem inspection.

## Adding a new fixture

1. Drop a new `.md` under `fixtures/` with valid Phase 8 frontmatter (see `apps/api/src/server/services/knowledge/frontmatter.py` for the schema).
2. Make sure the body is at least ~1500 bytes so the chunker emits at least one chunk.
3. If the new fixture should also be a related-pane anchor, share the `verify` and `retrieval` tags with `01-baseline.md`.

## Adding verify to a new stack

Drop a `scripts/verify.sh` into the stack root that exits 0 on success and writes `result.json` + `report.md` to `${W7_VERIFY_OUTPUT_DIR}`. The CLI dispatcher will auto-discover it — no `.bin/w7` changes needed.
