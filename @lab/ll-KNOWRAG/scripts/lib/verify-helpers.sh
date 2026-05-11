#!/usr/bin/env bash
# verify-helpers.sh — bash library for stack-local verify.sh harnesses.
# Sourced by @lab/ll-KNOWRAG/scripts/verify.sh; functions are pure-bash + curl + jq.
# All HTTP runs from the host (not inside the compose net), so URLs use host ports.

# shellcheck disable=SC2034  # color constants are referenced by the sourcing script
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
DIM='\033[2m'
NC='\033[0m'

# ── Dep check ──────────────────────────────────────────────────────────────

verify_check_deps() {
  local missing=()
  for cmd in curl jq base64 docker date; do
    command -v "$cmd" >/dev/null 2>&1 || missing+=("$cmd")
  done
  if [[ ${#missing[@]} -gt 0 ]]; then
    echo "[verify] missing required commands: ${missing[*]}" >&2
    return 127
  fi
}

# ── Logging ────────────────────────────────────────────────────────────────

log_step()  { echo -e "${BLUE}🔄${NC} $*" >&2; }
log_pass()  { echo -e "${GREEN}✅${NC} $*" >&2; }
log_fail()  { echo -e "${RED}❌${NC} $*" >&2; }
log_warn()  { echo -e "${YELLOW}⚠️${NC} $*" >&2; }
log_skip()  { echo -e "${DIM}⏭️ $*${NC}" >&2; }
log_info()  { echo -e "${DIM}   $*${NC}" >&2; }

now_iso() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
now_ms()  { python3 -c 'import time; print(int(time.time()*1000))' 2>/dev/null \
            || date +%s%3N 2>/dev/null \
            || echo "$(($(date +%s) * 1000))"; }

# ── HTTP wrappers ──────────────────────────────────────────────────────────
# Each returns the response body on stdout and the HTTP status on stderr (last line).
# Caller checks $? — non-zero on connection error or non-2xx status.

_curl_json() {
  # _curl_json METHOD URL [BODY] [HEADER...] -> body on stdout, status on stderr
  local method="$1"; local url="$2"; shift 2
  local body=""
  if [[ $# -gt 0 && "$1" != "-H"* ]]; then
    body="$1"; shift
  fi
  # --post30{1,2,3} preserve POST/PUT body across 301/302/303 redirects.
  # Without these flags, curl -L silently downgrades POST→GET on those codes
  # (e.g. FastAPI/Starlette trailing-slash redirects), dropping the body.
  local args=(-sSL --post301 --post302 --post303 --max-time 15 -X "$method" -o /tmp/.verify-resp.$$ -w '%{http_code}')
  while [[ $# -gt 0 ]]; do
    args+=(-H "$1"); shift
  done
  if [[ -n "$body" ]]; then
    args+=(-H "Content-Type: application/json" --data-binary "$body")
  fi
  local code
  code=$(curl "${args[@]}" "$url" 2>/dev/null) || { rm -f /tmp/.verify-resp.$$; return 2; }
  cat /tmp/.verify-resp.$$
  rm -f /tmp/.verify-resp.$$
  echo "$code" >&2
  if [[ ! "$code" =~ ^2 ]]; then return 1; fi
}

api_get()  { _curl_json GET  "${API_URL}$1"; }
api_post() {
  local path="$1"; local body="$2"
  _curl_json POST "${API_URL}${path}" "$body"
}

mcp_call() {
  # Call a FastMCP tool via HTTP. FastMCP-HTTP requires a session: POST
  # `initialize` first, capture the `Mcp-Session-Id` response header, then
  # POST `tools/call` with that header. Returns the tool-call response body
  # on stdout; non-zero on any step failure.
  local tool_name="$1"; local args_json="$2"
  local hdr_file="/tmp/.mcp-hdr.$$"
  local body_file="/tmp/.mcp-body.$$"
  local init_rpc
  init_rpc='{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"w7-verify","version":"1.0.0"}}}'
  curl -sSL --post301 --post302 --post303 --max-time 30 -X POST "${MCP_URL}/mcp/" \
    -H "Content-Type: application/json" \
    -H "Accept: application/json, text/event-stream" \
    -D "$hdr_file" -o "$body_file" \
    --data-binary "$init_rpc" >/dev/null 2>&1 || { rm -f "$hdr_file" "$body_file"; return 2; }
  local session_id
  session_id=$(awk -F': ' 'tolower($1)=="mcp-session-id"{print $2}' "$hdr_file" | tr -d '\r\n')
  rm -f "$hdr_file"
  if [[ -z "$session_id" ]]; then
    cat "$body_file"; rm -f "$body_file"
    return 1
  fi
  # Notify initialized (best-effort; FastMCP requires this before tool calls)
  curl -sSL --post301 --post302 --post303 --max-time 5 -X POST "${MCP_URL}/mcp/" \
    -H "Content-Type: application/json" \
    -H "Accept: application/json, text/event-stream" \
    -H "Mcp-Session-Id: ${session_id}" \
    --data-binary '{"jsonrpc":"2.0","method":"notifications/initialized","params":{}}' \
    >/dev/null 2>&1 || true
  # Tool call
  local rpc
  rpc=$(jq -nc --arg name "$tool_name" --argjson args "$args_json" \
    '{jsonrpc:"2.0", id:2, method:"tools/call", params:{name:$name, arguments:$args}}')
  curl -sSL --post301 --post302 --post303 --max-time 30 -X POST "${MCP_URL}/mcp/" \
    -H "Content-Type: application/json" \
    -H "Accept: application/json, text/event-stream" \
    -H "Mcp-Session-Id: ${session_id}" \
    -o "$body_file" \
    --data-binary "$rpc" >/dev/null 2>&1 || { rm -f "$body_file"; return 2; }
  cat "$body_file"
  rm -f "$body_file"
}

gitea_api() {
  # gitea_api METHOD PATH [BODY] -> response body on stdout
  local method="$1"; local path="$2"; local body="${3:-}"
  if [[ -z "${GITEA_TOKEN:-}" ]]; then
    echo "[verify] GITEA_TOKEN not set" >&2
    return 2
  fi
  if [[ -n "$body" ]]; then
    _curl_json "$method" "${GITEA_URL}${path}" "$body" \
      "Authorization: token ${GITEA_TOKEN}"
  else
    _curl_json "$method" "${GITEA_URL}${path}" "" \
      "Authorization: token ${GITEA_TOKEN}"
  fi
}

qdrant_get() {
  _curl_json GET "${QDRANT_URL}$1"
}

# ── Polling ────────────────────────────────────────────────────────────────

wait_until() {
  # wait_until DESCRIPTION COMMAND TIMEOUT_S INTERVAL_S
  local desc="$1"; local cmd="$2"; local timeout_s="${3:-60}"; local interval_s="${4:-2}"
  local elapsed=0
  while ! eval "$cmd" >/dev/null 2>&1; do
    sleep "$interval_s"
    elapsed=$((elapsed + interval_s))
    if (( elapsed >= timeout_s )); then
      log_fail "TIMEOUT after ${timeout_s}s waiting for: ${desc}"
      return 1
    fi
  done
}

# ── Check recording ────────────────────────────────────────────────────────
# A check is a single assertion. record_check appends a row to a shell array
# and to the running JSON envelope.

VERIFY_CHECKS_JSON='[]'
VERIFY_FAILED=0

record_check() {
  # record_check ID STATUS DURATION_MS DETAIL [SEVERITY]
  local id="$1"; local status="$2"; local ms="$3"; local detail="$4"
  local severity="${5:-high}"
  local emoji="✅"
  case "$status" in
    pass) emoji="✅" ;;
    fail) emoji="❌"; VERIFY_FAILED=1 ;;
    warn) emoji="⚠️" ;;
    skip) emoji="⏭️" ;;
  esac
  echo -e "  ${emoji} [${id}] ${detail} ${DIM}(${ms}ms)${NC}" >&2
  VERIFY_CHECKS_JSON=$(jq -c \
    --arg id "$id" \
    --arg st "$status" \
    --arg de "$detail" \
    --arg se "$severity" \
    --argjson ms "$ms" \
    '. + [{id:$id, status:$st, duration_ms:$ms, detail:$de, severity:$se}]' \
    <<<"$VERIFY_CHECKS_JSON")
}

# Run a check function, time it, record result.
# A check function MUST set CHECK_DETAIL on success/failure and return 0/non-0.
run_check() {
  local id="$1"; local fn="$2"; local severity="${3:-high}"
  local started; started=$(now_ms)
  CHECK_DETAIL=""
  if "$fn"; then
    local finished; finished=$(now_ms)
    record_check "$id" "pass" "$((finished - started))" "${CHECK_DETAIL:-ok}" "$severity"
    return 0
  else
    local finished; finished=$(now_ms)
    record_check "$id" "fail" "$((finished - started))" "${CHECK_DETAIL:-failed}" "$severity"
    return 1
  fi
}

# ── Output emitters ────────────────────────────────────────────────────────

emit_result_json() {
  # emit_result_json STACK STARTED_AT FINISHED_AT DURATION_MS EXIT_CODE OUTPUT_DIR
  # DURATION_MS is precomputed by the caller using the portable now_ms() helper —
  # avoids GNU-only `date -u -d` which silently degrades to 0 on macOS/BSD.
  local stack="$1"; local started="$2"; local finished="$3"
  local duration_ms="$4"; local exit_code="$5"; local out_dir="$6"

  local critical high medium low
  critical=$(jq -r '[.[] | select(.severity=="critical" and .status=="fail")] | length' <<<"$VERIFY_CHECKS_JSON")
  high=$(jq -r     '[.[] | select(.severity=="high"     and .status=="fail")] | length' <<<"$VERIFY_CHECKS_JSON")
  medium=$(jq -r   '[.[] | select(.severity=="medium"   and .status=="fail")] | length' <<<"$VERIFY_CHECKS_JSON")
  low=$(jq -r      '[.[] | select(.severity=="low"      and .status=="fail")] | length' <<<"$VERIFY_CHECKS_JSON")

  jq -n \
    --arg stack "$stack" \
    --arg started "$started" \
    --arg finished "$finished" \
    --argjson duration_ms "$duration_ms" \
    --argjson exit_code "$exit_code" \
    --argjson critical "$critical" \
    --argjson high "$high" \
    --argjson medium "$medium" \
    --argjson low "$low" \
    --argjson checks "$VERIFY_CHECKS_JSON" \
    '{stack:$stack, started_at:$started, finished_at:$finished,
      duration_ms:$duration_ms, exit_code:$exit_code,
      summary:{critical:$critical, high:$high, medium:$medium, low:$low},
      checks:$checks}' \
    > "${out_dir}/result.json"
}

emit_report_md() {
  # emit_report_md STACK STARTED_AT FINISHED_AT EXIT_CODE OUTPUT_DIR
  local stack="$1"; local started="$2"; local finished="$3"; local exit_code="$4"; local out_dir="$5"
  local pass_emoji
  pass_emoji=$([[ "$exit_code" == "0" ]] && echo "PASS" || echo "FAIL")

  {
    echo "# Verify Report — ${stack}"
    echo
    echo "**Started:** ${started}  "
    echo "**Finished:** ${finished}  "
    echo "**Result:** ${pass_emoji} (exit code ${exit_code})"
    echo
    echo "## Summary"
    echo
    jq -r '"| Critical | High | Medium | Low |\n|:---:|:---:|:---:|:---:|\n| **\(.summary.critical)** | **\(.summary.high)** | **\(.summary.medium)** | **\(.summary.low)** |"' \
      "${out_dir}/result.json"
    echo
    echo "## Checks"
    echo
    echo "| ID | Status | ms | Detail |"
    echo "|---|---|---:|---|"
    jq -r '.checks[] | "| \(.id) | \(.status) | \(.duration_ms) | \(.detail) |"' \
      "${out_dir}/result.json"
  } > "${out_dir}/report.md"
}

# ── Memory seed helper ─────────────────────────────────────────────────────

seed_from_memory_dir() {
  # Stage memory markdown files into TEMP_FIXTURE_DIR, prepending Phase-8
  # frontmatter when missing. Echoes one absolute path per staged file.
  local mem_dir="$1"; local out_dir="$2"; local owner="${3:-w7-mgfcode}"
  local count=0
  if [[ ! -d "$mem_dir" ]]; then
    return 1
  fi
  mkdir -p "$out_dir"
  while IFS= read -r f; do
    [[ -z "$f" ]] && continue
    [[ "$(basename "$f")" == "MEMORY.md" ]] && continue  # index file
    local base; base=$(basename "$f" .md)
    local id="memory-${base}"
    local target="${out_dir}/${id}.md"
    if head -1 "$f" | grep -q '^---$'; then
      cp "$f" "$target"
    else
      {
        echo "---"
        echo "id: ${id}"
        echo "owner: ${owner}"
        echo "tags: [verify, memory]"
        echo "status: published"
        echo "version: 0.1.0"
        echo "visibility: public"
        echo "---"
        echo
        cat "$f"
      } > "$target"
    fi
    echo "$target"
    count=$((count + 1))
    [[ $count -ge 10 ]] && break
  done < <(find "$mem_dir" -maxdepth 1 -name '*.md' -type f | sort)
  # Memory mode requires >=4 markdown files to satisfy the harness floor
  # (1 baseline + 3 related). Caller falls back to built-in fixtures when
  # this returns non-zero.
  if (( count < 4 )); then
    return 1
  fi
}
