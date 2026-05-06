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
STACK_NAME="@lab/$(basename "${STACK_DIR}")"

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

TEMP_BRANCH="verify-$(date -u +%Y%m%dT%H%M%SZ)-$$"
SEEDED_PATHS=()
TEMP_FIXTURE_DIR=""
PRE_QDRANT_COUNT=0

cleanup() {
  local rc=$?
  if [[ "${W7_VERIFY_KEEP}" == "1" ]]; then
    log_warn "--keep set: leaving temp branch '${TEMP_BRANCH}' and Qdrant points in place"
    return $rc
  fi
  log_step "cleanup: deleting temp branch '${TEMP_BRANCH}' and seeded artifacts"
  # Delete each seeded artifact via Gitea API on the temp branch. The branch
  # itself is then deleted; this also drops any Qdrant points whose
  # commit_sha pointed to the removed commits, once a webhook reconcile fires.
  if [[ -n "${TEMP_FIXTURE_DIR}" && -d "${TEMP_FIXTURE_DIR}" ]]; then
    rm -rf "${TEMP_FIXTURE_DIR}"
  fi
  # Delete temp branch (best-effort; ignore failures since the branch may not
  # have been created yet).
  gitea_api DELETE "/repos/${KB_OWNER}/${KB_REPO}/branches/${TEMP_BRANCH}" \
    >/dev/null 2>>"${TRACE_LOG}" || true
  # Best-effort: delete Qdrant points by artifact_path filter for our seeds.
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

ensure_temp_branch() {
  # Create the temp branch from the base branch. Tolerates 'already exists'.
  local body
  body=$(jq -nc --arg new "$TEMP_BRANCH" --arg old "$KB_BASE_BRANCH" \
    '{new_branch_name:$new, old_branch_name:$old}')
  gitea_api POST "/repos/${KB_OWNER}/${KB_REPO}/branches" "$body" \
    >/dev/null 2>>"${TRACE_LOG}" || true
}

# Commit one local file under <category>/<id>.md on TEMP_BRANCH.
seed_one() {
  local local_file="$1"
  local id; id=$(awk '/^id:/ {print $2; exit}' "$local_file")
  [[ -z "$id" ]] && { CHECK_DETAIL="fixture missing id: $local_file"; return 1; }
  local target_path="knowledge/${id}.md"
  local content_b64
  content_b64=$(base64 < "$local_file" | tr -d '\n')
  local body
  body=$(jq -nc \
    --arg branch "$TEMP_BRANCH" \
    --arg msg   "verify: seed ${id}" \
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
  ensure_temp_branch

  # Pre-count
  PRE_QDRANT_COUNT=$(qdrant_point_count)

  # Pick fixtures: --seed-from-memory wins if available, else built-ins.
  local fixtures=()
  if [[ "${W7_VERIFY_SEED_FROM_MEMORY}" == "1" ]]; then
    local mem_dir="${CLAUDE_PROJECT_DIR:-${HOME}/.claude/projects/-home-w7-hector-w7-localbase}/memory"
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

  # Wait for Qdrant to grow
  local target=$((PRE_QDRANT_COUNT + ${#fixtures[@]}))
  if ! wait_until "Qdrant points_count > ${PRE_QDRANT_COUNT}" \
    "[[ \$(curl -sS '${QDRANT_URL}/collections/kb_public' | jq -r '.result.points_count // 0') -gt ${PRE_QDRANT_COUNT} ]]" \
    60 2; then
    CHECK_DETAIL="Qdrant did not grow within 60s (pre=${PRE_QDRANT_COUNT}, target>${PRE_QDRANT_COUNT})"
    return 1
  fi

  local post; post=$(qdrant_point_count)
  CHECK_DETAIL="seeded ${#fixtures[@]} artifacts; Qdrant ${PRE_QDRANT_COUNT} → ${post} points"
  return 0
}

check_search() {
  local body
  body=$(api_post "/api/artifacts/search" \
    '{"query":"verify baseline retrieval smoke","visibility":"public","top_k":10}' \
    2>>"${TRACE_LOG}") || { CHECK_DETAIL="search endpoint not reachable"; return 1; }
  # Response shape: list of {artifact_path, score, ...}
  local hits
  hits=$(jq 'length' <<<"$body" 2>/dev/null || echo 0)
  if [[ "$hits" -ge 1 ]]; then
    CHECK_DETAIL="search returned ${hits} hits"
    return 0
  fi
  CHECK_DETAIL="search returned 0 hits"
  return 1
}

check_related() {
  local body
  body=$(api_get "/api/artifacts/knowledge/verify-baseline.md/related?k=5" \
    2>>"${TRACE_LOG}") || {
    # Memory-mode: baseline is named differently — try the first seeded path.
    local first="${SEEDED_PATHS[0]:-}"
    [[ -z "$first" ]] && { CHECK_DETAIL="no seeded baseline path to query"; return 1; }
    body=$(api_get "/api/artifacts/${first}/related?k=5" 2>>"${TRACE_LOG}") || {
      CHECK_DETAIL="/related endpoint not reachable for ${first}"
      return 1
    }
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
  local args; args=$(jq -nc '{query:"verify baseline retrieval smoke", source_id:"", match_count:5}')
  body=$(mcp_call "rag_search_knowledge_base" "$args" 2>>"${TRACE_LOG}") || {
    CHECK_DETAIL="MCP server not reachable at ${MCP_URL}"
    return 1
  }
  # FastMCP HTTP returns either a JSON-RPC envelope or an SSE event. Inspect
  # body content; success means a non-error response with non-empty content.
  if grep -qE '"error"|"isError"[[:space:]]*:[[:space:]]*true' <<<"$body"; then
    CHECK_DETAIL="MCP returned an error response"
    return 1
  fi
  # Look for any of: result.content, content array, hits text — be tolerant
  # of FastMCP version shape variations.
  if grep -qE '"result"|"content"|"text"|"hits"|"results"' <<<"$body"; then
    CHECK_DETAIL="MCP rag_search_knowledge_base responded"
    return 0
  fi
  CHECK_DETAIL="MCP response empty/unrecognized: $(head -c 120 <<<"$body")"
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
