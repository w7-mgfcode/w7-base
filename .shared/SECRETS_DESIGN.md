# W7-Base Secret Management Foundation

## Principles
1. **Never commit `.env` files to git.** They remain local and ignored.
2. **Commit `.env.example`** to describe the schema for new developers.
3. **Use `.env.sops`** (encrypted via Mozilla SOPS) to safely store real secrets in Git.

## Component Interactions
- **`w7 up`:** Before executing Docker Compose, `w7` checks if `.env.sops` exists. If it does, and `.env` is either missing or older than the `.env.sops` file, `w7` will automatically attempt to decrypt `.env.sops` into `.env` using your local AGE key.
- **`w7 doctor`:** Validates your stack contract, ensuring you have at least one of `.env`, `.env.example`, or `.env.sops`. Warns if SOPS dependencies are missing.
- **`.gitignore`:** Automatically ignores all `.env` files globally while allowing `.env.sops` and `.env.example` to be version-controlled.

## SOPS Workflow (Recommended)
We strongly recommend using **age** as the encryption backend.

### 1. Setup Your Age Key
Generate a key for your environment (or use a shared operator key for a team):
```bash
age-keygen -o ~/.config/w7/age.key
export SOPS_AGE_KEY_FILE=~/.config/w7/age.key
```

### 2. Configure `.sops.yaml`
Place a `.sops.yaml` file in the root of the framework `~/w7-localbase/.sops.yaml` to govern encryption rules:
```yaml
creation_rules:
  - path_regex: \.env\.sops$
    key_groups:
    - age:
      - age1... # Your public key here
```

### 3. Managing Secrets via CLI
Instead of manually typing SOPS commands, you can use the integrated wrappers:

- **Create new encrypted file:**
  ```bash
  w7 secret init @prod/my-stack
  ```
  *(Encrypts an existing `.env` into `.env.sops`, or creates an empty one)*

- **Edit existing encrypted secrets:**
  ```bash
  w7 secret edit @prod/my-stack
  ```

- **Decrypt manually (useful for debugging):**
  ```bash
  w7 secret decrypt @prod/my-stack
  ```

## Security Guardrails
- **GitOps Webhook (`@ops/webhook`):** The deployment script simply runs `w7 up`. By ensuring `w7 up` auto-decrypts secrets, the deployment seamlessly receives the latest encrypted secrets pushed to Git, provided the webhook container has access to the `SOPS_AGE_KEY_FILE`.
- **Precedence:** `w7 up` respects manually created `.env` files if they are *newer* than `.env.sops`. If you edit `.env` directly, `w7 up` won't overwrite it immediately, but it is highly recommended to only edit via `w7 secret edit`.