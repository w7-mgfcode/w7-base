#!/usr/bin/env bash
# Policy: No Privileged Containers in @prod

# Input: $1 = zone, $2 = stack, $3 = stack_path
check_policy() {
  local zone="$1"
  local stack_path="$3"

  if [[ "$zone" == "@prod" ]]; then
    if grep -q "privileged: true" "${stack_path}/compose.yml" 2>/dev/null; then
      echo "[POLICY FAIL] Stack '@prod/$(basename "$stack_path")' must not use 'privileged: true'."
      return 1
    fi
  fi
  return 0
}
