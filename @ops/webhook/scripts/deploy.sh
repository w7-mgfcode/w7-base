#!/usr/bin/env sh
# W7-Base GitOps Deployment Script
# Triggered by webhook listener when Gitea registers a push.

set -e

REPO_NAME="$1"
REF="$2"

echo "[INFO] Received webhook for $REPO_NAME on $REF"

# 1. Map repository + branch to a stack path via .w7-meta
# This requires searching the W7_ROOT for matching configurations.
# Note: For security, the listener only executes stacks matching the exact branch.
BRANCH="${REF#refs/heads/}"

# Basic implementation: Search for metadata matching the git trigger
MATCHING_STACKS=$(find /w7-localbase -maxdepth 3 -name ".w7-meta" -exec grep -l "repository: \"$REPO_NAME\"" {} + | xargs -r grep -l "branch: \"$BRANCH\"" | xargs -r dirname)

if [ -z "$MATCHING_STACKS" ]; then
  echo "[WARN] No stack configured for $REPO_NAME on branch $BRANCH. Ignoring."
  exit 0
fi

for STACK_DIR in $MATCHING_STACKS; do
  echo "[INFO] Processing deployment for stack at $STACK_DIR"
  
  # Extract Zone and Stack name
  REL_PATH=$(echo "$STACK_DIR" | sed 's|/w7-localbase/||')
  ZONE=$(echo "$REL_PATH" | cut -d'/' -f1)
  STACK=$(echo "$REL_PATH" | cut -d'/' -f2)

  # 2. Protection: Do not auto-deploy to @prod unless specifically explicitly allowed
  if [ "$ZONE" = "@prod" ]; then
    echo "[ERROR] Webhook attempted auto-deploy to @prod. This is explicitly blocked by W7-Base GitOps policy."
    echo "[INFO] @prod updates require manual operator approval via CLI or an advanced pipeline."
    # We skip this stack but continue the loop
    continue
  fi

  # 3. Validation: Pre-deploy sanity check using dry-run/config
  # Note: The actual source code of the stack must be pulled first.
  # Assuming the stack directory is a git repo itself or we pull the config into a temp dir.
  # For local-first, the stack dir is usually bound to a git worktree.
  
  cd "$STACK_DIR"
  echo "[INFO] Pulling latest changes in $STACK_DIR..."
  # If the directory is a git repo, pull safely.
  if [ -d ".git" ]; then
    PREV_COMMIT=$(git rev-parse HEAD 2>/dev/null || echo "")
    git fetch origin "$BRANCH"
    git reset --hard "origin/$BRANCH"
  else
    echo "[WARN] Directory is not a git repository. Cannot pull. Proceeding with existing files."
  fi

  # 4. Pre-deploy configuration validation
  # If the compose file or env file is syntactically invalid, fail before restart.
  echo "[INFO] Validating docker compose configuration..."
  if ! docker compose config -q; then
    echo "[ERROR] Invalid compose configuration detected. Aborting deploy for $STACK."
    if [ -n "$PREV_COMMIT" ]; then
      echo "[INFO] Rolling back to $PREV_COMMIT"
      git reset --hard "$PREV_COMMIT"
    fi
    continue
  fi

  # 5. Execute w7 up (Controlled deploy flow)
  echo "[INFO] Configuration valid. Executing w7 up..."
  /w7-localbase/.bin/w7 up "$ZONE/$STACK" --force
  
  echo "[SUCCESS] Deployment completed for $ZONE/$STACK"
done
