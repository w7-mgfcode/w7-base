#!/usr/bin/env bash
# .claude/hooks/check-commit-format.sh
#
# PreToolUse hook — blocks `git commit` when the message violates
# .claude/rules/commit-format.md. Wired in .claude/settings.json.
#
# Reads the JSON payload Claude Code passes on stdin, looks for a `git commit`
# bash invocation, extracts the -m message (or .git/COMMIT_EDITMSG), and
# regex-checks it. On failure, emits a JSON deny verdict so the tool call is
# blocked before it runs.
#
# Exit 0 with no output  → ALLOW
# Exit 0 with deny JSON  → BLOCK (preferred; lets Claude see the reason)
# Exit 2                 → silent BLOCK (use only if the JSON encoder fails)
#
# Reference: https://code.claude.com/docs/en/hooks
set -u

INPUT="$(cat || true)"

# Extract the bash command from the input JSON. Best-effort jq; fallback to grep.
extract_command() {
  if command -v jq >/dev/null 2>&1; then
    printf '%s' "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null
  else
    printf '%s' "$INPUT" | grep -oE '"command"[[:space:]]*:[[:space:]]*"[^"]*"' \
      | head -1 | sed -E 's/^"command"[[:space:]]*:[[:space:]]*"//; s/"$//'
  fi
}

CMD="$(extract_command)"

# Only act on `git commit`.  Allow `git commit --help` and `git commit --no-verify`
# checks to fall through to git's own handling (we still scan if -m is present).
if ! printf '%s' "$CMD" | grep -qE '(^|[[:space:]])git[[:space:]]+commit([[:space:]]|$)'; then
  exit 0
fi

# Extract the commit message.
# Priority:
#   1. -m "<msg>"  (handles double quotes, naive escape support)
#   2. -m '<msg>'
#   3. -F <path>   (read the file)
#   4. .git/COMMIT_EDITMSG (commit-via-editor)
MSG=""

# Pull -m "<msg>" / -m '<msg>'
if printf '%s' "$CMD" | grep -qE -- '-m[[:space:]]+'; then
  MSG="$(printf '%s' "$CMD" \
    | sed -nE 's/.*-m[[:space:]]+"([^"]*)".*/\1/p; s/.*-m[[:space:]]+\x27([^\x27]*)\x27.*/\1/p' \
    | head -1)"
fi

# -F <path>
if [[ -z "$MSG" ]] && printf '%s' "$CMD" | grep -qE -- '-F[[:space:]]+'; then
  PATH_TO_MSG="$(printf '%s' "$CMD" | sed -nE 's/.*-F[[:space:]]+([^[:space:]]+).*/\1/p' | head -1)"
  if [[ -n "$PATH_TO_MSG" && -f "$PATH_TO_MSG" ]]; then
    MSG="$(cat -- "$PATH_TO_MSG")"
  fi
fi

# Fall back to .git/COMMIT_EDITMSG (editor flow).
if [[ -z "$MSG" && -f .git/COMMIT_EDITMSG ]]; then
  MSG="$(cat .git/COMMIT_EDITMSG)"
fi

# Nothing to validate? Allow (git will prompt the user via its own editor).
if [[ -z "$MSG" ]]; then
  exit 0
fi

SUBJECT="$(printf '%s\n' "$MSG" | head -1)"

# --- Validation ----------------------------------------------------------

# 1. Subject grammar.
SCOPE_ALLOW='knowrag|reliquary|cardshed|api|ui|mcp|ingest|repo|platform|stacks|state|ops|ci|docs|release'
# Description: starts lowercase, may contain any non-newline (incl. internal
# periods like SemVer `v0.1.0`), but must NOT end with a trailing period
# immediately before the ` (#N)` issue ref.
SUBJECT_RE="^(feat|fix|docs|refactor|test|chore|release)(\\((${SCOPE_ALLOW})(,(${SCOPE_ALLOW}))?\\))?: [a-z].*[^.] \\(#[0-9]+\\)$"

REASONS=()

if ! printf '%s' "$SUBJECT" | grep -qE "$SUBJECT_RE"; then
  REASONS+=("subject does not match \`type(scope): description (#issue)\` (scope must be in: ${SCOPE_ALLOW//|/, })")
fi

# 2. AI co-author / generated trailer detection (any line in the body).
if printf '%s\n' "$MSG" | grep -qE '^Co-Authored-By:[[:space:]]+Claude'; then
  REASONS+=('forbidden: `Co-Authored-By: Claude` trailer detected')
fi
if printf '%s\n' "$MSG" | grep -qE 'Generated with \[Claude Code\]'; then
  REASONS+=('forbidden: `Generated with [Claude Code]` line detected')
fi
if printf '%s\n' "$MSG" | grep -qE '^🤖[[:space:]]+Generated'; then
  REASONS+=('forbidden: AI-generated trailer line detected')
fi

# --- Verdict -------------------------------------------------------------

if [[ ${#REASONS[@]} -eq 0 ]]; then
  exit 0
fi

# Build the JSON deny verdict.
JOINED_REASONS=""
for r in "${REASONS[@]}"; do
  JOINED_REASONS+="• $r\n"
done

# Use jq if available for safe JSON encoding; else hand-encode.
if command -v jq >/dev/null 2>&1; then
  REASON_TEXT=$(printf 'commit message violates .claude/rules/commit-format.md:\n%s\nsee BRANCHING.md and CLAUDE.md.' "$JOINED_REASONS")
  jq -n --arg reason "$REASON_TEXT" '{
    "hookSpecificOutput": {
      "hookEventName": "PreToolUse",
      "permissionDecision": "deny",
      "permissionDecisionReason": $reason
    }
  }'
else
  ESCAPED=$(printf '%s' "$JOINED_REASONS" | sed 's/"/\\"/g; s/$/\\n/' | tr -d '\n')
  printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"commit message violates .claude/rules/commit-format.md:\\n%s see BRANCHING.md and CLAUDE.md."}}' "$ESCAPED"
fi

exit 0
