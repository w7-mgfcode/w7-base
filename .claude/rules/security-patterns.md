# Security Patterns

> Vision principle: **Credential safety + zone isolation.** Secrets never travel as plaintext outside the host. The webhook + act-runner mount `/var/run/docker.sock`, which is root-equivalent — the platform's threat model assumes anything that reaches them is trusted.

These patterns are enforced on ALL code in this repository. Violations must be fixed before committing.

## Forbidden — never generate

- `eval()`, `exec()`, `compile()` with any user-controlled input
- `subprocess` calls with `shell=True` and user input
- Hardcoded secrets, API keys, passwords, or tokens — anywhere
- Credentials embedded in Git remote URLs (`https://user:token@…`) — use SSH keys or PATs in env
- `pickle.loads()` on untrusted data
- Logging of passwords, API keys, or credential values
- Path traversal via unsanitized `..` in file operations
- Writing credentials into manifest files, install records, or compose `command:` lines
- `verify=False` or `rejectUnauthorized: false` in HTTP/TLS clients
- Plaintext `.env` files committed to git
- Webhook signature verification disabled or stubbed (`X-Gitea-Signature` HMAC must validate)

## Required patterns

### Secrets handling (W7-Base specific)

The three-file model is mandatory:
- `.env.example` — committed schema only (key names + placeholders)
- `.env` — real values, NEVER committed (`.gitignore` enforces)
- `.env.sops` — AGE-encrypted `.env`, committed, GitOps-safe

Rules:
- New stacks MUST ship `.env.example`. Stacks with real secrets MUST also ship `.env.sops`.
- AGE keys live in `~/.config/sops/age/keys.txt` on the operator host. Public keys go into root `.sops.yaml`.
- `w7 secret edit <stack>` is the only sanctioned editor — direct edits to `.env.sops` are not safe.
- Never log decrypted secret values, even at debug level. Log key names if needed.
- KNOWRAG-specific secrets (`GITEA_TOKEN`, `GITEA_WEBHOOK_SECRET`, `OLLAMA_*`) all live in `@lab/ll-KNOWRAG/.env.sops`.

### File operations

- Validate all file paths before read/write
- Reject paths containing `..` that escape intended directories
- Validate file extensions against an allow-list
- Check file sizes before reading (prevent memory exhaustion)
- Use `pathlib.Path` over string manipulation for path construction
- `pathlib.Path.resolve()` to canonicalize paths at boundaries

### Git operations

- Never embed credentials in Git URLs
- Sanitize repository URLs before passing to Git commands
- Validate Git output before parsing — don't assume format
- `subprocess` runs with `shell=False` for all Git operations
- Never invoke `git push --force` against `master` — this is enforced by `.shared/SECRETS_DESIGN.md` and the safety memory

### Webhook + GitOps

- Every webhook payload MUST verify `X-Gitea-Signature` (HMAC-SHA256) before any side effect
- `docker compose config` validation MUST run before `w7 up` from a webhook trigger; failure rolls back the commit
- `@prod` zone MUST NOT be deployed via webhook — that path requires Gitea Actions + manual approval

### Input validation

- Validate at system boundaries (CLI args, webhook payloads, Gitea/Qdrant API responses)
- Allow-lists over deny-lists where feasible
- YAML: `yaml.safe_load()`, never `yaml.load()` without `SafeLoader`
- JSON: validate structure (Pydantic / dataclass) before accessing nested fields

### Compose / container security

- Production-grade stacks (`@prod/*`) MUST NOT use `privileged: true` — `.shared/policy/prod-privileged.sh` enforces
- `@prod/*` MUST NOT mount host `/` or `/etc` — `.shared/policy/prod-no-root-mount.sh` enforces
- Ingress hostnames MUST follow `*.w7.local` — `.shared/policy/zone-ingress-naming.sh` enforces
- Pin image tags (`image: foo:1.2.3`) over floating tags (`:latest`); SHA digests are even better

### Action / workflow security

- Pin third-party GitHub Actions by full 40-char SHA (`uses: foo/bar@<sha> # v1.2.3`)
- First-party `actions/*` MAY use major-version (`@v4`)
- Dependabot watches `.github/workflows/` weekly — keep its PRs current
- Webhook-style auto-deploy paths cannot bypass branch protection

## When adding new features

1. Validate all input at the entry point
2. `pathlib.Path.resolve()` to canonicalize file paths
3. Never interpolate user input into shell commands
4. Log security-relevant events (deploy attempts, secret operations, policy violations)
5. Test with adversarial input (paths with `..`, oversized files, malformed YAML, malformed HMAC)
6. If the feature touches `@ops/webhook` or `@ops/act-runner`, get a second pair of eyes — those containers run with Docker socket access

## Memory + context

- Never copy secret values into `.memo/` artifacts, daily logs, or session-pattern docs
- Never echo secret values in tool results — even truncated
- Memory may store key NAMES, never values
