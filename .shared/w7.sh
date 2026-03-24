#!/usr/bin/env bash
# W7-Base Shell Integration & Ergonomics

# Dynamically resolve the W7 root directory based on this script's location
export W7_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

# Add .bin to PATH so `w7` is available even without the wrapper
export PATH="$W7_ROOT/.bin:$PATH"

# Zone Navigation Aliases
# Using aliases instead of functions for zone roots because the logic is purely static 0(1) cd operations.
alias @ops="cd $W7_ROOT/@ops"
alias @dev="cd $W7_ROOT/@dev"
alias @prod="cd $W7_ROOT/@prod"
alias @lab="cd $W7_ROOT/@lab"

# w7 shell wrapper to intercept 'go' (child processes cannot `cd` the parent shell)
w7() {
  local cmd=$1
  local target=$2

  if [[ "$cmd" == "go" ]]; then
    if [[ -z "$target" ]]; then
      echo "[ERROR] Stack name required." >&2
      return 1
    fi
    
    # Call the actual binary to resolve the path using dynamic W7_ROOT
    local stack_path
    stack_path=$("$W7_ROOT/.bin/w7" resolve "$target")
    
    if [[ $? -eq 0 && -d "$stack_path" ]]; then
      cd "$stack_path" || return 1
      echo -e "\033[0;32m[w7]\033[0m Entered stack: $(basename "$stack_path")"
    else
      return 1
    fi
  else
    # Pass all other commands directly to the underlying binary
    command "$W7_ROOT/.bin/w7" "$@"
  fi
}

# Export w7 so subshells inherit the wrapper function
export -f w7