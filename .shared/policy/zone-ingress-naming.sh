#!/usr/bin/env bash
# Policy: Zone-Aware Ingress naming

# Input: $1 = zone, $2 = stack, $3 = stack_path
check_policy() {
  local zone="$1"
  local stack_path="$3"

  if [[ "$zone" == "@prod" ]]; then
    # Find Traefik Host labels
    local host_labels=$(grep -oP 'Host\(`[^`]+`\)' "${stack_path}/compose.yml" 2>/dev/null || true)
    
    if [[ -n "$host_labels" ]]; then
      while IFS= read -r label; do
        domain=$(echo "$label" | sed -E 's/Host\(`([^`]+)`\)/\1/')
        if [[ ! "$domain" =~ \.w7\.local$ ]]; then
          echo "[POLICY FAIL] Stack '@prod/$(basename "$stack_path")' uses non-standard domain '$domain'. Production domains must end in '.w7.local'."
          return 1
        fi
      done <<< "$host_labels"
    fi
  fi
  return 0
}
