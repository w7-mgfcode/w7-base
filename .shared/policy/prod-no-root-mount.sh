#!/usr/bin/env bash
# Policy: No Root Volume Mounts in @prod

# Input: $1 = zone, $2 = stack, $3 = stack_path
check_policy() {
  local zone="$1"
  local stack_path="$3"

  if [[ "$zone" == "@prod" ]]; then
    # Check for mounting root (/) or /etc, /usr, /bin etc.
    # We look for lines starting with whitespace, a dash, and then /: or /etc:
    if grep -qP '^\s*-\s+/[[:space:]]*:' "${stack_path}/compose.yml" 2>/dev/null || \
       grep -qP '^\s*-\s+/etc[[:space:]]*:' "${stack_path}/compose.yml" 2>/dev/null || \
       grep -qP 'source:[[:space:]]*/[[:space:]]*$' "${stack_path}/compose.yml" 2>/dev/null; then
      echo "[POLICY FAIL] Stack '@prod/$(basename "$stack_path")' attempts to mount system-critical host paths (root or /etc)."
      return 1
    fi
  fi
  return 0
}
