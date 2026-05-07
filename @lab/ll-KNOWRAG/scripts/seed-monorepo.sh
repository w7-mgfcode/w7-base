#!/usr/bin/env bash
# seed-monorepo.sh — Stage / push W7-Base monorepo docs into KNOWRAG.
#
# Modes (#37 / #41):
#   --dry-run   Print plan, write nothing (default of `w7 seed`)
#   (default)   Stage tree under dogfood-output/seed-<utc>/
#   --apply     Stage AND push every artifact via Gitea API (idempotent:
#               GET → byte-compare → skip-or-PUT-with-sha → POST-if-new)
#
# Usage:
#   scripts/seed-monorepo.sh                       # stage only
#   scripts/seed-monorepo.sh --dry-run             # print plan
#   scripts/seed-monorepo.sh --apply               # stage + push to Gitea
#   MANIFEST=alt.txt scripts/seed-monorepo.sh --apply
#
# Required env when --apply (loaded from <stack>/.env or w7 setup_env):
#   GITEA_TOKEN, GITEA_KB_OWNER, GITEA_KB_REPO, GITEA_HTTP_PORT (default 3030)
#
# Exit codes:
#   0   staged / applied successfully
#   1   manifest entry references missing source file (or apply failed for ≥1)
#   2   setup error (missing manifest, can't resolve repo root, no GITEA_TOKEN)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STACK_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
REPO_ROOT="$(cd "${STACK_DIR}/../.." && pwd)"

MANIFEST="${MANIFEST:-${STACK_DIR}/_kb/llms.txt}"
DRY_RUN=0
APPLY=0
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
    --apply)   APPLY=1 ;;
    -h|--help) sed -n '2,21p' "$0"; exit 0 ;;
    *) echo "unknown arg: $arg" >&2; exit 2 ;;
  esac
done

if [[ "$DRY_RUN" -eq 1 && "$APPLY" -eq 1 ]]; then
  echo "--dry-run and --apply are mutually exclusive" >&2; exit 2
fi

[[ -f "$MANIFEST" ]] || { echo "manifest not found: $MANIFEST" >&2; exit 2; }
[[ -f "${REPO_ROOT}/.bin/w7" ]] || { echo "repo root resolution failed: ${REPO_ROOT}" >&2; exit 2; }

# --apply needs verify-helpers.sh hard (gitea_api, _curl_json). For
# stage / dry-run we tolerate its absence and stub the log_* helpers.
if [[ "$APPLY" -eq 1 ]]; then
  HELPERS="${SCRIPT_DIR}/lib/verify-helpers.sh"
  [[ -f "$HELPERS" ]] || { echo "--apply requires lib/verify-helpers.sh" >&2; exit 2; }
  # shellcheck source=lib/verify-helpers.sh disable=SC1091
  source "$HELPERS"
  verify_check_deps || exit 127

  # Load .env so GITEA_TOKEN is available. setup_env from `w7 seed`
  # populates this; standalone invocation falls back to .env / .env.example.
  if [[ -f "${STACK_DIR}/.env" ]]; then
    # shellcheck disable=SC1091
    set -a; source "${STACK_DIR}/.env"; set +a
  fi
  : "${GITEA_TOKEN:?--apply requires GITEA_TOKEN — w7 secret decrypt @lab/ll-KNOWRAG}"
  GITEA_HOST_PORT="${GITEA_HTTP_PORT:-3030}"
  GITEA_URL="${VERIFY_GITEA_URL:-http://localhost:${GITEA_HOST_PORT}/api/v1}"
  KB_OWNER="${GITEA_KB_OWNER:-knowrag}"
  KB_REPO="${GITEA_KB_REPO:-kb-default}"
  KB_BASE_BRANCH="${GITEA_KB_BRANCH:-main}"
elif [[ -f "${SCRIPT_DIR}/lib/verify-helpers.sh" ]]; then
  # shellcheck source=lib/verify-helpers.sh disable=SC1091
  source "${SCRIPT_DIR}/lib/verify-helpers.sh"
else
  log_step() { echo "🔄 $*" >&2; }
  log_pass() { echo "✅ $*" >&2; }
  log_fail() { echo "❌ $*" >&2; }
  log_warn() { echo "⚠️  $*" >&2; }
  log_info() { echo "   $*" >&2; }
  log_skip() { echo "⏭️  $*" >&2; }
fi

# ── Apply helpers (only used when --apply) ─────────────────────────────────
# apply_one TARGET_PATH LOCAL_STAGED_FILE
#   Idempotent push of one staged file:
#     GET → compare base64 → skip-if-unchanged → PUT-with-sha → POST-if-new
#   Sets APPLY_RESULT to one of: created | updated | skipped | failed
apply_one() {
  local target="$1" local_file="$2"
  APPLY_RESULT="failed"
  local content_b64; content_b64=$(base64 -w0 < "$local_file")
  local existing
  existing=$(gitea_api GET "/repos/${KB_OWNER}/${KB_REPO}/contents/${target}?ref=${KB_BASE_BRANCH}" 2>/dev/null || echo "")
  if [[ -n "$existing" ]] && jq -e '.sha' <<<"$existing" >/dev/null 2>&1; then
    local existing_b64; existing_b64=$(jq -r '.content // ""' <<<"$existing" | tr -d '\n ')
    if [[ "$existing_b64" == "$content_b64" ]]; then
      APPLY_RESULT="skipped"; return 0
    fi
    local existing_sha; existing_sha=$(jq -r '.sha' <<<"$existing")
    local body
    body=$(jq -nc \
      --arg branch  "$KB_BASE_BRANCH" \
      --arg msg     "kb-seed: update ${target} (${SOURCE_SHA:0:12})" \
      --arg c       "$content_b64" \
      --arg sha     "$existing_sha" \
      '{branch:$branch, message:$msg, content:$c, sha:$sha}')
    gitea_api PUT "/repos/${KB_OWNER}/${KB_REPO}/contents/${target}" "$body" >/dev/null 2>&1 || return 1
    APPLY_RESULT="updated"
  else
    local body
    body=$(jq -nc \
      --arg branch  "$KB_BASE_BRANCH" \
      --arg msg     "kb-seed: add ${target} (${SOURCE_SHA:0:12})" \
      --arg c       "$content_b64" \
      '{branch:$branch, message:$msg, content:$c}')
    gitea_api POST "/repos/${KB_OWNER}/${KB_REPO}/contents/${target}" "$body" >/dev/null 2>&1 || return 1
    APPLY_RESULT="created"
  fi
}

# ── Categorization heuristic ───────────────────────────────────────────────
# .claude/rules/* + .claude/agents/* → prompts/
# .claude/skills/*                    → skills/
# .claude/hooks/*                     → hooks/
# *apps/mcp/*                         → mcp/
# .claude/commands/*                  → commands/
# everything else                     → knowledge/
categorize() {
  local p="$1"
  case "$p" in
    .claude/rules/*|.claude/agents/*|*/.claude/rules/*|*/.claude/agents/*)
      printf 'prompts'  ;;
    .claude/skills/*|*/.claude/skills/*)
      printf 'skills'   ;;
    .claude/hooks/*|*/.claude/hooks/*)
      printf 'hooks'    ;;
    .claude/commands/*|*/.claude/commands/*)
      printf 'commands' ;;
    */apps/mcp/*|apps/mcp/*)
      printf 'mcp'      ;;
    *)
      printf 'knowledge' ;;
  esac
}

# Slug: full source path flattened. Lowercase, drop .md, strip leading
# `@`/`.`, replace `/` and other non-alphanum with `-`, dedupe. This keeps
# slugs unique across `@ops/*/README.md`, `.claude/skills/*/SKILL.md`, etc.
slugify() {
  printf '%s' "${1%.md}" \
    | tr '[:upper:]' '[:lower:]' \
    | sed -E 's|^[@.]+||; s/[^a-z0-9]+/-/g; s/^-+//; s/-+$//'
}

# Stable id: 12-char prefix of sha1(source_path).
stable_id() {
  printf '%s' "$1" | sha1sum | cut -c1-12
}

# Tags: derived from path segments excluding the basename.
derive_tags() {
  local p="$1"
  local IFS='/'
  read -ra parts <<<"$p"
  local out=()
  for seg in "${parts[@]:0:${#parts[@]}-1}"; do
    [[ -z "$seg" || "$seg" == "." ]] && continue
    seg="${seg#@}"; seg="${seg#.}"
    out+=("$seg")
  done
  printf '%s' "$(IFS=, ; echo "${out[*]:-w7-base}")"
}

# ── Manifest parse ─────────────────────────────────────────────────────────

mapfile -t ENTRIES < <(grep -oE '\]\([^)]+\)' "$MANIFEST" | sed -E 's/^\]\(([^)]+)\)$/\1/')

if [[ ${#ENTRIES[@]} -eq 0 ]]; then
  log_fail "manifest contained no parseable bullet links: $MANIFEST"
  exit 2
fi

SOURCE_SHA="$(git -C "$REPO_ROOT" rev-parse HEAD 2>/dev/null || echo 'unknown')"
SOURCE_DATE="$(git -C "$REPO_ROOT" log -1 --format=%cs HEAD 2>/dev/null || date -u +%Y-%m-%d)"

UTC="$(date -u +%Y%m%dT%H%M%SZ)"
STAGE="${STACK_DIR}/dogfood-output/seed-${UTC}"
[[ "$DRY_RUN" -eq 0 ]] && mkdir -p "$STAGE"

log_step "manifest: ${MANIFEST}"
log_step "repo HEAD: ${SOURCE_SHA:0:12} (${SOURCE_DATE})"
log_step "stage:    ${STAGE}$([[ $DRY_RUN -eq 1 ]] && echo ' (dry-run)')"
echo "" >&2

declare -A CATEGORY_COUNTS=()
declare -i staged=0 missing=0

for src in "${ENTRIES[@]}"; do
  abs="${REPO_ROOT}/${src}"
  if [[ ! -f "$abs" ]]; then
    log_warn "missing source: ${src}"
    missing=$((missing + 1))
    continue
  fi

  cat="$(categorize "$src")"
  slug="$(slugify "$src")"
  id="$(stable_id "$src")"
  tags="$(derive_tags "$src")"
  target_rel="${cat}/${slug}.md"

  CATEGORY_COUNTS[$cat]=$((${CATEGORY_COUNTS[$cat]:-0} + 1))

  if [[ "$DRY_RUN" -eq 1 ]]; then
    printf '  %-10s  %-50s  ←  %s\n' "$cat" "$target_rel" "$src" >&2
    staged=$((staged + 1))
    continue
  fi

  mkdir -p "${STAGE}/${cat}"
  {
    printf -- '---\n'
    printf 'id: %s\n' "$id"
    printf 'tags: [%s]\n' "$tags"
    printf 'status: published\n'
    printf 'version: %s\n' "${SOURCE_SHA:0:12}"
    printf 'owner: w7-mgfcode\n'
    printf 'visibility: public\n'
    printf 'source_path: %s\n' "$src"
    printf 'source_sha: %s\n' "$SOURCE_SHA"
    printf 'source_date: %s\n' "$SOURCE_DATE"
    printf -- '---\n\n'
    cat "$abs"
  } > "${STAGE}/${target_rel}"
  staged=$((staged + 1))
done

# ── Stage summary ──────────────────────────────────────────────────────────

echo "" >&2
log_pass "staged ${staged} artifacts ($([[ $missing -gt 0 ]] && echo "${missing} missing — see warnings" || echo 'no missing sources'))"
for c in prompts skills hooks commands mcp knowledge; do
  count=${CATEGORY_COUNTS[$c]:-0}
  [[ $count -gt 0 ]] && log_info "  ${c}/  → ${count}"
done

if [[ "$DRY_RUN" -eq 1 ]]; then
  exit 0
fi

log_info ""
log_info "stage tree at: ${STAGE}"

if [[ "$APPLY" -eq 0 ]]; then
  log_info "next: re-run with --apply to push to Gitea, or use \`w7 seed @lab/ll-KNOWRAG --apply\`."
  [[ $missing -gt 0 ]] && exit 1 || exit 0
fi

# ── Apply phase ────────────────────────────────────────────────────────────

echo "" >&2
log_step "apply: pushing ${staged} artifacts to ${KB_OWNER}/${KB_REPO} (${KB_BASE_BRANCH})"
log_info "gitea: ${GITEA_URL}"

# Reachability + repo-exists pre-check.
if ! gitea_api GET "/repos/${KB_OWNER}/${KB_REPO}" >/dev/null 2>&1; then
  log_fail "Gitea unreachable or repo ${KB_OWNER}/${KB_REPO} not found at ${GITEA_URL}"
  log_info "is the stack up?  w7 up @lab/ll-KNOWRAG"
  exit 2
fi

declare -i created=0 updated=0 skipped=0 failed=0
APPLY_FAILS=()
while IFS= read -r staged_file; do
  rel="${staged_file#$STAGE/}"
  if apply_one "$rel" "$staged_file"; then
    case "$APPLY_RESULT" in
      created) created=$((created + 1)) ;;
      updated) updated=$((updated + 1)) ;;
      skipped) skipped=$((skipped + 1)) ;;
    esac
  else
    failed=$((failed + 1))
    APPLY_FAILS+=("$rel")
    log_warn "apply failed: $rel"
  fi
done < <(find "$STAGE" -type f -name '*.md' | sort)

echo "" >&2
log_pass "apply: ${created} created, ${updated} updated, ${skipped} skipped, ${failed} failed"
if [[ $failed -gt 0 ]]; then
  log_info "failures:"
  for f in "${APPLY_FAILS[@]}"; do log_info "  - $f"; done
  exit 1
fi
log_info "next: webhook should trigger Qdrant ingest within ~30s. Watch with:"
log_info "  curl -s http://localhost:\${QDRANT_PORT:-6333}/collections/kb_public | jq .result.points_count"
exit 0
