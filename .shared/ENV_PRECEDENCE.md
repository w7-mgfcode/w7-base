# Environment Precedence & Ergonomics

## Overrides & Bridging
The `w7` CLI executes Docker Compose using multiple `--env-file` flags to achieve an overriding bridge. Docker Compose reads these files sequentially, with later files overriding earlier ones.

The CLI executes:
```bash
docker compose --env-file .shared/global.env --env-file .env up -d
```

### Precedence Hierarchy
1. **Host Environment:** OS-level exported variables override everything.
2. **Stack Local (`.env`):** Target-specific variables.
3. **Global Bridge (`.shared/global.env`):** Shared fallback values (e.g., domain names, timezone).

## Secret Safety
- **Rule:** Never place database passwords, API keys, or secret tokens in `.shared/global.env`.
- **Rule:** Ensure `.env` is universally ignored in the global `.gitignore`.
- **Practice:** Use `.env.example` to track the *shape* of secrets required by a stack.

## Missing Key Validation
`w7 doctor` compares keys defined in `.env.example` against those present in `.env` and warns about any missing entries. Stacks should also use Docker Compose's built-in mandatory variable syntax (`${REQUIRED_KEY:?Error: REQUIRED_KEY missing}`) in their `compose.yml` to fail fast on boot.

## Encrypted Secrets (SOPS)
For stacks where secrets must be recoverable or committed safely (especially `@ops` and `@prod`), W7-Base supports Mozilla SOPS with AGE encryption:

- **`.env.sops`** — An AGE-encrypted copy of `.env`, safe to commit.
- **Auto-decryption** — `w7 up` automatically decrypts `.env.sops` to `.env` if SOPS is installed and the encrypted file is newer.
- **Configuration** — The root `.sops.yaml` defines encryption rules for all stacks.

See `.shared/SECRETS.md` for full operator setup instructions.