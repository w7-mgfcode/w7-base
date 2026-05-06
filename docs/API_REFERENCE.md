# API & Metadata Reference

Detailed reference for the `w7` CLI and the `.w7-meta` stack configuration schema.

## 1. The `w7` CLI Commands

| Command | Flags | Description |
|---|---|---|
| `w7 up [stack\|all]` | `--force`, `--yes` | Starts stacks. Merges `.env` and `.shared/global.env`. |
| `w7 down [stack\|all]` | | Gracefully stops containers. |
| `w7 stat` | `--json` | Fast cross-zone status matrix. |
| `w7 logs [stack]` | `-f`, `--tail` | Tails Docker Compose logs. |
| `w7 go [stack]` | | Changes directory to the target stack. |
| `w7 init [path]` | | Scaffolds a new stack directory structure. |
| `w7 doctor` | `--json`, `--audit` | Validates platform health and policies. |
| `w7 secret [init\|edit\|rotate] [stack]` | | Manages SOPS-encrypted secrets. |
| `w7 backup [stack]` | | Creates a tarball of the stack's `data/` folder. |
| `w7 prune [stack]` | | Destroys stack resources (restricted to `@lab`). |

## 2. The `.w7-meta` Schema
Every stack directory MUST contain a `.w7-meta` file for the CLI and GitOps engine to function.

```yaml
version: "1.0"
name: "stack-display-name"
owner: "team-or-agent-id"
zone: "@dev"  # Automatically detected but can be overridden
gitops:
  enabled: true
  repo: "git.w7.local/org/repo"
  branch: "main"
  webhook_secret_env: "WEBHOOK_SECRET"
policy:
  allow_privileged: false
  allow_root_host_mount: true
  min_health_check: true
```

## 3. Global Environment Bridge
Variables in `.shared/global.env` are inherited by ALL stacks. Use for:
- `DOMAIN=w7.local`
- `TZ=UTC`
- `LOG_LEVEL=info`

*Note: Never store secrets in the global environment.*
