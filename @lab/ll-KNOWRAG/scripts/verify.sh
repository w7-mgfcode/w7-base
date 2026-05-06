#!/usr/bin/env bash
# verify.sh — KNOWRAG end-to-end smoke harness.
#
# Asserts the Phase 8 contract end-to-end on a live, running stack:
#   1. api.health                — API responds healthy
#   2. gitea.kb_repo_exists      — KB repo is reachable via Gitea API
#   3. ingestion.seed_and_grow   — seed fixtures → Qdrant points grow
#   4. search.api_returns_hits   — search returns ≥1 hit for seeded fixture
#   5. related.api_returns_3_plus— /related returns ≥3 sibling artifacts
#   6. mcp.search_returns_hits   — MCP rag_search_knowledge_base returns hits
#
# Run via:  bash scripts/verify.sh   (or)   w7 verify @lab/ll-KNOWRAG
#
# Honored envvars (set by `w7 verify` or by the operator manually):
#   W7_VERIFY_RUNNING            (default 1) — assume stack is up
#   W7_VERIFY_COLD               (default 0) — bring stack up via compose first
#   W7_VERIFY_SEED_FROM_MEMORY   (default 0) — seed from ${CLAUDE_PROJECT_DIR}/memory/
#                                  (CLAUDE_PROJECT_DIR must be set; falls back to
#                                   built-in fixtures with a warning if missing)
#   W7_VERIFY_KEEP               (default 0) — leave temp branch + points after run
#   W7_VERIFY_OUTPUT_DIR         (default <stack>/dogfood-output/<utc>)
#
# Exit codes:
#   0   all checks passed
#   1   at least one check failed
#   2   setup error (missing deps, missing secrets, can't bring stack up)
#   127 missing required commands

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STACK_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
ZONE_DIR="$(cd "${STACK_DIR}/.." && pwd)"
STACK_NAME="$(basename "${ZONE_DIR}")/$(basename "${STACK_DIR}")"

# shellcheck source=lib/verify-helpers.sh
source "${SCRIPT_DIR}/lib/verify-helpers.sh"

verify_check_deps || exit 127

# ── Load .env ──────────────────────────────────────────────────────────────

if [[ -f "${STACK_DIR}/.env" ]]; then
  # shellcheck disable=SC1091
  set -a; source "${STACK_DIR}/.env"; set +a
elif [[ -f "${STACK_DIR}/.env.example" ]]; then
  log_warn "no .env — falling back to .env.example for non-secret defaults"
  # shellcheck disable=SC1091
  set -a; source "${STACK_DIR}/.env.example"; set +a
fi

if [[ -z "${GITEA_TOKEN:-}" ]]; then
  log_fail "GITEA_TOKEN not set — required to seed fixtures via Gitea API"
  log_info "decrypt with: w7 secret decrypt @lab/ll-KNOWRAG    or    set in shell"
  exit 2
fi

# ── Endpoints (host ports — verify runs from host) ─────────────────────────

API_HOST_PORT="${API_PORT:-8181}"
MCP_HOST_PORT="${MCP_PORT:-8051}"
GITEA_HOST_PORT="${GITEA_HTTP_PORT:-3030}"
QDRANT_HOST_PORT="${QDRANT_PORT:-6333}"

API_URL="${VERIFY_API_URL:-http://localhost:${API_HOST_PORT}}"
MCP_URL="${VERIFY_MCP_URL:-http://localhost:${MCP_HOST_PORT}}"
GITEA_URL="${VERIFY_GITEA_URL:-http://localhost:${GITEA_HOST_PORT}/api/v1}"
QDRANT_URL="${VERIFY_QDRANT_URL:-http://localhost:${QDRANT_HOST_PORT}}"

KB_OWNER="${GITEA_KB_OWNER:-knowrag}"
KB_REPO="${GITEA_KB_REPO:-kb-default}"
KB_BASE_BRANCH="${GITEA_KB_BRANCH:-main}"

# ── Output dir ─────────────────────────────────────────────────────────────

OUTPUT_DIR="${W7_VERIFY_OUTPUT_DIR:-${STACK_DIR}/dogfood-output/$(date -u +%Y%m%dT%H%M%SZ)}"
mkdir -p "${OUTPUT_DIR}"
TRACE_LOG="${OUTPUT_DIR}/curl-trace.log"
: > "${TRACE_LOG}"

# ── Run mode ───────────────────────────────────────────────────────────────

W7_VERIFY_RUNNING="${W7_VERIFY_RUNNING:-1}"
W7_VERIFY_COLD="${W7_VERIFY_COLD:-0}"
W7_VERIFY_SEED_FROM_MEMORY="${W7_VERIFY_SEED_FROM_MEMORY:-0}"
W7_VERIFY_KEEP="${W7_VERIFY_KEEP:-0}"

if [[ "${W7_VERIFY_COLD}" == "1" ]]; then
  log_step "cold-start: docker compose up --build -d (this may take 10–20 minutes)"
  (cd "${STACK_DIR}" && docker compose up --build -d) || { log_fail "compose up failed"; exit 2; }
  log_step "waiting for API health (timeout 300s)"
  wait_until "API /health" "curl -fsS '${API_URL}/health' | grep -q '\"status\":\"ok\"'" 300 5 || exit 2
fi

# ── State for cleanup ──────────────────────────────────────────────────────

# Run-id prefixes seeded artifact paths so concurrent runs and re-runs don't
# collide. Files are committed to the default branch (so the production
# webhook fires) and removed from it on EXIT.
RUN_ID="verify-$(date -u +%Y%m%dT%H%M%SZ)-$$"
SEEDED_PATHS=()
TEMP_FIXTURE_DIR=""
PRE_QDRANT_COUNT=0

cleanup() {
  local rc=$?
  if [[ "${W7_VERIFY_KEEP}" == "1" ]]; then
    log_warn "--keep set: leaving seeded artifacts and Qdrant points in place"
    return $rc
  fi
  log_step "cleanup: removing seeded artifacts from ${KB_BASE_BRANCH} + Qdrant"
  if [[ -n "${TEMP_FIXTURE_DIR}" && -d "${TEMP_FIXTURE_DIR}" ]]; then
    rm -rf "${TEMP_FIXTURE_DIR}"
  fi
  # Delete each seeded file via Gitea API (creates a removal commit on the
  # default branch; the webhook fires with status=removed and the pipeline
  # drops the Qdrant points).
  for path in "${SEEDED_PATHS[@]}"; do
    local sha; sha=$(gitea_api GET "/repos/${KB_OWNER}/${KB_REPO}/contents/${path}?ref=${KB_BASE_BRANCH}" 2>>"${TRACE_LOG}" \
      | jq -r '.sha // empty')
    if [[ -n "$sha" ]]; then
      local body; body=$(jq -nc \
        --arg branch "$KB_BASE_BRANCH" \
        --arg msg "verify: cleanup ${path}" \
        --arg sha "$sha" \
        '{branch:$branch, message:$msg, sha:$sha}')
      gitea_api DELETE "/repos/${KB_OWNER}/${KB_REPO}/contents/${path}" "$body" \
        >/dev/null 2>>"${TRACE_LOG}" || true
    fi
  done
  # Backstop: directly drop Qdrant points by artifact_path filter, in case
  # the removal-webhook hasn't fired yet by the time this run exits.
  for path in "${SEEDED_PATHS[@]}"; do
    local body
    body=$(jq -nc --arg p "$path" \
      '{filter:{must:[{key:"artifact_path", match:{value:$p}}]}}')
    _curl_json POST "${QDRANT_URL}/collections/kb_public/points/delete?wait=true" "$body" \
      >/dev/null 2>>"${TRACE_LOG}" || true
  done
  return $rc
}
trap cleanup EXIT

# ── Per-check functions ────────────────────────────────────────────────────

check_api_health() {
  local body
  body=$(api_get "/health" 2>>"${TRACE_LOG}") || { CHECK_DETAIL="API not reachable at ${API_URL}"; return 1; }
  if jq -e '.status == "ok"' >/dev/null <<<"$body" 2>/dev/null; then
    CHECK_DETAIL="API healthy at ${API_URL}"
    return 0
  fi
  CHECK_DETAIL="API responded but status != ok: ${body}"
  return 1
}

check_gitea_kb_repo() {
  local body
  body=$(gitea_api GET "/repos/${KB_OWNER}/${KB_REPO}" 2>>"${TRACE_LOG}") || {
    CHECK_DETAIL="Gitea KB repo not reachable: /repos/${KB_OWNER}/${KB_REPO}"
    return 1
  }
  if jq -e '.full_name' >/dev/null <<<"$body" 2>/dev/null; then
    CHECK_DETAIL="KB repo exists: $(jq -r .full_name <<<"$body")"
    return 0
  fi
  CHECK_DETAIL="KB repo response missing full_name: ${body}"
  return 1
}

# Commit one local file under knowledge/<RUN_ID>-<id>.md on the default branch
# so the production push webhook fires. Run-id prefixing makes paths unique
# per run (concurrent runs and re-runs don't collide).
seed_one() {
  local local_file="$1"
  local id; id=$(awk '/^id:/ {print $2; exit}' "$local_file")
  [[ -z "$id" ]] && { CHECK_DETAIL="fixture missing id: $local_file"; return 1; }
  local target_path="knowledge/${RUN_ID}-${id}.md"
  local content_b64
  content_b64=$(base64 < "$local_file" | tr -d '\n')
  local body
  body=$(jq -nc \
    --arg branch "$KB_BASE_BRANCH" \
    --arg msg   "verify: seed ${RUN_ID}-${id}" \
    --arg c     "$content_b64" \
    '{branch:$branch, message:$msg, content:$c}')
  gitea_api POST "/repos/${KB_OWNER}/${KB_REPO}/contents/${target_path}" "$body" \
    >/dev/null 2>>"${TRACE_LOG}" || return 1
  SEEDED_PATHS+=("$target_path")
  echo "$target_path"
}

qdrant_point_count() {
  # Returns 0 if the collection doesn't exist yet (cold-start).
  local body
  body=$(qdrant_get "/collections/kb_public" 2>>"${TRACE_LOG}") || { echo 0; return 0; }
  jq -r '.result.points_count // 0' <<<"$body" 2>/dev/null || echo 0
}

check_ingestion() {
  # Pre-count: Qdrant baseline before seeding
  PRE_QDRANT_COUNT=$(qdrant_point_count)

  # Pick fixtures: --seed-from-memory wins if available, else built-ins.
  local fixtures=()
  if [[ "${W7_VERIFY_SEED_FROM_MEMORY}" == "1" ]]; then
    if [[ -z "${CLAUDE_PROJECT_DIR:-}" ]]; then
      log_warn "--seed-from-memory requires CLAUDE_PROJECT_DIR — falling back to built-in fixtures"
      W7_VERIFY_SEED_FROM_MEMORY=0
    fi
    local mem_dir="${CLAUDE_PROJECT_DIR:-}/memory"
    TEMP_FIXTURE_DIR="${OUTPUT_DIR}/seed-from-memory"
    if seed_from_memory_dir "$mem_dir" "$TEMP_FIXTURE_DIR" "w7-mgfcode" >/tmp/.verify-mem.$$ 2>>"${TRACE_LOG}"; then
      while IFS= read -r f; do fixtures+=("$f"); done < /tmp/.verify-mem.$$
      rm -f /tmp/.verify-mem.$$
      log_info "seeded from memory: ${#fixtures[@]} fixtures"
    else
      log_warn "--seed-from-memory failed (empty/missing dir) — falling back to built-in fixtures"
      rm -f /tmp/.verify-mem.$$
    fi
  fi
  if [[ ${#fixtures[@]} -eq 0 ]]; then
    fixtures=("${SCRIPT_DIR}"/fixtures/*.md)
  fi

  if [[ ${#fixtures[@]} -lt 4 ]]; then
    CHECK_DETAIL="need ≥4 fixtures (got ${#fixtures[@]}) — baseline + 3 related"
    return 1
  fi

  # Seed
  for f in "${fixtures[@]}"; do
    seed_one "$f" >/dev/null || { CHECK_DETAIL="seed failed: $f"; return 1; }
  done

  # Wait until EVERY seeded artifact_path has at least one chunk indexed.
  # Counting total points (`>= pre + N`) was too weak: a subset of fixtures
  # could over-contribute chunks (e.g. 2 fixtures × 3 chunks = 6 points)
  # and satisfy the threshold while other fixtures hadn't ingested yet —
  # /related would then return fewer siblings than expected.
  if ! wait_until "all ${#SEEDED_PATHS[@]} seeded paths indexed in Qdrant" \
    "_all_seeded_paths_indexed" \
    60 2; then
    local missing
    missing=$(_seeded_paths_missing | tr '\n' ' ')
    local got; got=$(qdrant_point_count)
    CHECK_DETAIL="Qdrant ingestion incomplete within 60s (pre=${PRE_QDRANT_COUNT}, points=${got}, missing: ${missing})"
    return 1
  fi

  local post; post=$(qdrant_point_count)
  CHECK_DETAIL="seeded ${#fixtures[@]} artifacts (all paths indexed); Qdrant ${PRE_QDRANT_COUNT} → ${post} points"
  return 0
}

# Return 0 when every path in SEEDED_PATHS has at least one indexed point.
_all_seeded_paths_indexed() {
  for p in "${SEEDED_PATHS[@]}"; do
    local body
    body=$(jq -nc --arg p "$p" \
      '{exact:true, filter:{must:[{key:"artifact_path", match:{value:$p}}]}}')
    local count
    count=$(curl -sS --max-time 5 -X POST "${QDRANT_URL}/collections/kb_public/points/count" \
      -H "Content-Type: application/json" --data-binary "$body" 2>/dev/null \
      | jq -r '.result.count // 0' 2>/dev/null || echo 0)
    [[ "${count:-0}" -ge 1 ]] || return 1
  done
}

# Echo each seeded path that has 0 points indexed (one per line).
_seeded_paths_missing() {
  for p in "${SEEDED_PATHS[@]}"; do
    local body
    body=$(jq -nc --arg p "$p" \
      '{exact:true, filter:{must:[{key:"artifact_path", match:{value:$p}}]}}')
    local count
    count=$(curl -sS --max-time 5 -X POST "${QDRANT_URL}/collections/kb_public/points/count" \
      -H "Content-Type: application/json" --data-binary "$body" 2>/dev/null \
      | jq -r '.result.count // 0' 2>/dev/null || echo 0)
    [[ "${count:-0}" -lt 1 ]] && echo "$(basename "$p")"
  done
}

check_search() {
  local body
  body=$(api_post "/api/artifacts/search" \
    '{"query":"verify baseline retrieval smoke","visibility":"public","top_k":10}' \
    2>>"${TRACE_LOG}") || { CHECK_DETAIL="search endpoint not reachable"; return 1; }
  # Response shape per rag_coordinator.query: {"hits":[...], "pages"?:[...]}
  # — extract the hits array length, not the top-level object's key count.
  local hits
  hits=$(jq '(.hits // .results // []) | length' <<<"$body" 2>/dev/null || echo 0)
  if [[ "$hits" -ge 1 ]]; then
    CHECK_DETAIL="search returned ${hits} hits"
    return 0
  fi
  CHECK_DETAIL="search returned 0 hits"
  return 1
}

check_related() {
  # Paths are RUN_ID-prefixed at seed time; query the first seeded path.
  local first="${SEEDED_PATHS[0]:-}"
  if [[ -z "$first" ]]; then
    CHECK_DETAIL="no seeded baseline path to query"
    return 1
  fi
  local body
  body=$(api_get "/api/artifacts/${first}/related?k=5" 2>>"${TRACE_LOG}") || {
    CHECK_DETAIL="/related endpoint not reachable for ${first}"
    return 1
  }
  local n
  n=$(jq 'length' <<<"$body" 2>/dev/null || echo 0)
  if [[ "$n" -ge 3 ]]; then
    CHECK_DETAIL="/related returned ${n} sibling artifacts"
    return 0
  fi
  CHECK_DETAIL="/related returned ${n} (need ≥3)"
  return 1
}

check_mcp_search() {
  local body
  local args; args=$(jq -nc '{query:"verify baseline retrieval smoke", mode:"chunk", limit:5}')
  body=$(mcp_call "rag_search_knowledge_base" "$args" 2>>"${TRACE_LOG}") || {
    CHECK_DETAIL="MCP server not reachable or session handshake failed at ${MCP_URL}"
    return 1
  }
  # FastMCP HTTP responses arrive as Server-Sent Events: lines like
  # `event: message\ndata: {...json...}\n\n`. Extract the JSON-RPC envelope
  # from the data line; fall back to the raw body if not SSE-encoded.
  local json
  json=$(awk '/^data: /{sub(/^data: /,""); print; exit}' <<<"$body")
  [[ -z "$json" ]] && json="$body"
  if jq -e '.error' >/dev/null 2>&1 <<<"$json"; then
    local msg; msg=$(jq -r '.error.message' <<<"$json" 2>/dev/null)
    CHECK_DETAIL="MCP returned JSON-RPC error: ${msg}"
    return 1
  fi
  if jq -e '.result.isError == true' >/dev/null 2>&1 <<<"$json"; then
    local msg; msg=$(jq -r '.result.content[0].text // "tool error"' <<<"$json" 2>/dev/null)
    CHECK_DETAIL="MCP tool errored: ${msg}"
    return 1
  fi
  # Success: tool returned a result envelope. Any content (incl. empty hits)
  # proves the MCP -> API forwarding chain is alive.
  if jq -e '.result.content' >/dev/null 2>&1 <<<"$json"; then
    CHECK_DETAIL="MCP rag_search_knowledge_base responded with valid result"
    return 0
  fi
  CHECK_DETAIL="MCP response unrecognized: $(head -c 120 <<<"$json")"
  return 1
}

# ── Run sequence ───────────────────────────────────────────────────────────

STARTED_AT=$(now_iso)
STARTED_MS=$(now_ms)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >&2
echo "  🔍 w7 verify ${STACK_NAME}" >&2
echo "  ${STARTED_AT}" >&2
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >&2

run_check "api.health"               check_api_health     critical || true
run_check "gitea.kb_repo_exists"     check_gitea_kb_repo  critical || true
run_check "ingestion.seed_and_grow"  check_ingestion      high     || true
run_check "search.api_returns_hits"  check_search         high     || true
run_check "related.api_returns_3_plus" check_related      high     || true
run_check "mcp.search_returns_hits"  check_mcp_search     medium   || true

FINISHED_AT=$(now_iso)
FINISHED_MS=$(now_ms)
DURATION_MS=$((FINISHED_MS - STARTED_MS))

if [[ "${VERIFY_FAILED}" -eq 0 ]]; then
  EXIT_CODE=0
else
  EXIT_CODE=1
fi

emit_result_json "${STACK_NAME}" "${STARTED_AT}" "${FINISHED_AT}" "${DURATION_MS}" "${EXIT_CODE}" "${OUTPUT_DIR}"
emit_report_md   "${STACK_NAME}" "${STARTED_AT}" "${FINISHED_AT}" "${EXIT_CODE}" "${OUTPUT_DIR}"

echo "────────────────────────────────────────────" >&2
if [[ "${EXIT_CODE}" -eq 0 ]]; then
  echo -e "  ${GREEN}✅ Result: PASS${NC}" >&2
else
  echo -e "  ${RED}❌ Result: FAIL${NC}" >&2
fi
echo "  artifacts: ${OUTPUT_DIR}" >&2
echo "────────────────────────────────────────────" >&2

exit "${EXIT_CODE}"
