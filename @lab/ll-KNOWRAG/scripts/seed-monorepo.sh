#!/usr/bin/env bash
# seed-monorepo.sh — Stage W7-Base monorepo docs for KNOWRAG ingestion.
#
# First-day slice (#37): reads the canonical seed manifest at
# `_kb/llms.txt`, categorizes each entry via path heuristic, generates
# frontmatter, and stages the result tree under
# `dogfood-output/seed-<utc>/`. No Gitea writes — operator inspects the
# staged tree to confirm the design before `--apply` lands in day 2.
#
# Usage:
#   scripts/seed-monorepo.sh             # stage to dogfood-output/seed-<utc>/
#   scripts/seed-monorepo.sh --dry-run   # print plan only, write nothing
#   MANIFEST=alt.txt scripts/seed-monorepo.sh
#
# Exit codes:
#   0   staged successfully
#   1   manifest entry references missing source file
#   2   setup error (missing manifest, can't resolve repo root)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STACK_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
REPO_ROOT="$(cd "${STACK_DIR}/../.." && pwd)"

MANIFEST="${MANIFEST:-${STACK_DIR}/_kb/llms.txt}"
DRY_RUN=0
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
    -h|--help) sed -n '2,16p' "$0"; exit 0 ;;
    *) echo "unknown arg: $arg" >&2; exit 2 ;;
  esac
done

[[ -f "$MANIFEST" ]] || { echo "manifest not found: $MANIFEST" >&2; exit 2; }
[[ -f "${REPO_ROOT}/.bin/w7" ]] || { echo "repo root resolution failed: ${REPO_ROOT}" >&2; exit 2; }

# Source verify-helpers if available for log_*; otherwise no-op stubs.
if [[ -f "${SCRIPT_DIR}/lib/verify-helpers.sh" ]]; then
  # shellcheck source=lib/verify-helpers.sh disable=SC1091
  source "${SCRIPT_DIR}/lib/verify-helpers.sh"
else
  log_step() { echo "🔄 $*" >&2; }
  log_pass() { echo "✅ $*" >&2; }
  log_fail() { echo "❌ $*" >&2; }
  log_warn() { echo "⚠️  $*" >&2; }
  log_info() { echo "   $*" >&2; }
fi

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

# ── Summary ────────────────────────────────────────────────────────────────

echo "" >&2
log_pass "staged ${staged} artifacts ($([[ $missing -gt 0 ]] && echo "${missing} missing — see warnings" || echo 'no missing sources'))"
for c in prompts skills hooks commands mcp knowledge; do
  count=${CATEGORY_COUNTS[$c]:-0}
  [[ $count -gt 0 ]] && log_info "  ${c}/  → ${count}"
done

if [[ "$DRY_RUN" -eq 0 ]]; then
  log_info ""
  log_info "stage tree at: ${STAGE}"
  log_info "next: review the tree, then re-run with --apply (day-2 slice) to push to Gitea."
fi

[[ $missing -gt 0 ]] && exit 1 || exit 0
