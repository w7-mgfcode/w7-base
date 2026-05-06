# Disaster Recovery Guide

This document outlines the procedures for backing up and restoring the W7-Base platform.

## 1. Core Data Persistence
All W7 stacks use the `./data` directory for persistent storage.

- **Automated Backup:** `w7 backup <stack>` creates a `.tar.gz` in the root `./backups` directory.
- **Critical Stacks:**
  - `@ops/gitea`: Contains all Git repositories and database state.
  - `@ops/webhook`: Contains deployment hook configurations.
  - `@ops/grafana`: Contains dashboard definitions.

## 2. Secret Recovery (SOPS)
If you lose your AGE secret key, you cannot decrypt `.env.sops` files.

- **Backup your key:** `cp ~/.config/sops/age/keys.txt /path/to/secure/storage`
- **Rotation:** If a key is compromised, update `.sops.yaml` and re-encrypt all stacks:
  ```bash
  w7 secret rotate all
  ```

## 3. Restoration Procedure
1. **Prepare Host:** Install Docker and the `w7` CLI bridge.
2. **Clone Repo:** `git clone ...`
3. **Restore Secrets:** Copy your `keys.txt` to the host and verify with `sops`.
4. **Restore Data:** 
   ```bash
   tar -xzf backup_stack_date.tar.gz -C @zone/stack/data
   ```
5. **Boot Infrastructure:** `w7 up all`

## 4. Gitea Repository Recovery
If the Gitea volume is lost but repositories exist elsewhere:
1. Re-deploy `@ops/gitea`.
2. Re-create users and repositories.
3. Force-push existing local copies of repositories to the new instance.
4. Update `@ops/webhook` secrets to match the new Gitea webhooks.
