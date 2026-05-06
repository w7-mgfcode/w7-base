# Secret Management Guide

## The Three-File Model

Every stack can have up to three environment files. Each serves a distinct purpose:

| File | Committed? | Contains | Purpose |
|------|-----------|----------|---------|
| `.env.example` | Yes | Key names with placeholder values | Documents the **shape** of required secrets |
| `.env` | **Never** | Real secrets | Used at runtime by `docker compose` |
| `.env.sops` | Yes (encrypted) | AGE-encrypted copy of `.env` | Enables GitOps without exposing secrets |

**Rule:** `.env` is excluded from Git by the root `.gitignore`. Never override this.

## Lifecycle

```text
Operator creates .env.example (committed)
    |
    v
Operator copies to .env and fills real values (local only)
    |
    v
(Optional) Operator encrypts: w7 secret init <stack>
    |
    v
.env.sops is committed to Git (safe — encrypted with AGE)
    |
    v
On deploy, w7 up auto-decrypts .env.sops -> .env if sops is installed
```

## Zone-Specific Guidance

### @dev — Development Stacks
- Plain `.env` files are sufficient.
- Use `.env.example` so other developers know which keys to set.
- SOPS is optional but recommended if sharing the repo.

### @lab — Experimental Stacks
- Plain `.env` is fine. These stacks are disposable.
- Minimal secret hygiene required — but still never commit `.env`.

### @ops — Infrastructure Services
- **Use SOPS encryption.** These stacks hold infrastructure secrets (webhook HMAC keys, Gitea DB passwords).
- The operator must set up AGE keys before first use.
- Run `w7 secret init @ops/<stack>` after configuring `.env`.

### @prod — Production Stacks
- **SOPS encryption is strongly recommended.**
- Production secrets must never exist only in a local `.env` with no backup.
- Encrypted `.env.sops` provides a recoverable, auditable secret store.
- The `w7 up` command blocks automated deployment to `@prod` — secrets must be configured manually.

## Setting Up SOPS + AGE

### 1. Install Tools
```bash
# Debian/Ubuntu
sudo apt install age
# Install sops from https://github.com/getsops/sops/releases

# macOS
brew install age sops
```

### 2. Generate an AGE Key
```bash
age-keygen -o ~/.config/sops/age/keys.txt
```
The public key (`age1...`) is printed to stderr. Copy it.

### 3. Configure .sops.yaml
Edit the root `.sops.yaml` and replace the placeholder with your public key:
```yaml
creation_rules:
  - path_regex: \.env\.sops$
    age: "age1your_actual_public_key_here"
```

### 4. Verify Setup
```bash
w7 doctor
```
Doctor will confirm SOPS and AGE are installed and `.sops.yaml` is configured.

## CLI Commands

| Command | Description |
|---------|-------------|
| `w7 secret init <stack>` | Encrypt existing `.env` into `.env.sops` |
| `w7 secret edit <stack>` | Open `.env.sops` in SOPS editor (decrypts in memory) |
| `w7 secret decrypt <stack>` | Decrypt `.env.sops` to `.env` on disk |

## Safety Rules

1. **Never commit `.env` files.** The `.gitignore` enforces this.
2. **Never put secrets in `.shared/global.env`.** That file is committed and shared.
3. **Never store AGE private keys in the repository.** They live in `~/.config/sops/age/`.
4. **Use `.env.example` to document required keys.** This is the contract between the stack author and the operator.
5. **Run `w7 doctor` after changes.** It validates key coverage between `.env` and `.env.example`.

## How Auto-Decryption Works

When `w7 up <stack>` is called:
1. If `.env.sops` exists and is newer than `.env` (or `.env` is missing):
2. And `sops` is installed:
3. The CLI automatically decrypts `.env.sops` to `.env` before starting compose.
4. If decryption fails (wrong key, corrupted file), the command aborts safely.

This means operators with the AGE key can simply `git pull && w7 up` — secrets are decrypted transparently.

## What Is NOT Covered (Future Enhancements)

- **Multi-recipient encryption:** Currently single-key. Multi-operator setups would need multiple AGE recipients in `.sops.yaml`.
- **Key rotation:** Operator must manually re-encrypt with `sops updatekeys` if keys change.
- **External secret backends:** HashiCorp Vault, AWS KMS, etc. are out of scope for W7-Base.
- **Per-key encryption:** SOPS supports encrypting individual values, but W7-Base encrypts the entire `.env` file for simplicity.
