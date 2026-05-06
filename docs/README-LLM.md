# W7-Base Platform Guide

> W7-Base is a local-first orchestration framework and GitOps engine using Docker Compose. It standardizes multi-zone deployments with built-in security, compliance, and observability.

## Core Architecture

### Zone Isolation Model
The framework uses directory-based zones to enforce lifecycle policies:
- **@ops**: Core platform services (Gitea, Traefik, Prometheus). High-trust zone.
- **@dev**: Local development and integration testing. Automatic sync enabled.
- **@prod**: Production-grade local stacks. Requires manual confirmation and strict policy compliance.
- **@lab**: Temporary sandboxes. Only zone where `w7 prune` (destructive cleanup) is permitted.

### Stack Contract
A valid stack must contain:
- `.w7-meta`: Routing and GitOps metadata.
- `compose.yml`: Standard Docker Compose definition.
- `data/`: Isolated persistent storage.
- `.env.example`: Template for required secrets.

## Operational CLI (`w7`)

The `w7` utility is the primary entrypoint for all operations.

| Command | Usage | Context |
|---|---|---|
| `init <@zone/stack>` | Scaffolds a new stack directory | All zones |
| `up <stack>` | Starts/restarts a stack | @prod requires `--yes` |
| `go <stack>` | Jumps shell CWD to stack path | Shell wrapper required |
| `stat` | Cross-zone health matrix | Global |
| `logs <stack>` | Tails container logs | All zones |
| `backup <stack>` | Archives `data/` directory | All zones |
| `doctor` | Environment and compliance audit | Global / `--json` available |
| `secret <cmd>` | Manages SOPS/AGE encryption | All zones |
| `prune <stack>` | Destroys stack resources | **@lab only** |

## GitOps & CI/CD

W7-Base implements a hybrid delivery model:
1. **Webhook-Based**: Instant sync for `@dev` and `@lab`. Triggers `deploy.sh` on push.
2. **Runner-Based**: Gitea Actions (`act-runner`) for `@ops` and `@prod`. Supports multi-stage pipelines and pre-deployment testing.

**Rule**: Secrets are NEVER committed. Use `.env.sops` for encrypted secrets in Git.

## Security & Policy Enforcement

### @prod Protection
- **Interactive Gates**: `w7 up` prompts for confirmation in `@prod`.
- **Deployment Locks**: Presence of a `.w7-lock` file blocks all deployment attempts.
- **Branch Protection**: Production repositories should require signed commits and PR approvals in Gitea.

### Compliance Policies (`.shared/policy/`)
Automated checks run during `w7 doctor`:
- `prod-privileged.sh`: Blocks `privileged: true` in `@prod`.
- `prod-no-root-mount.sh`: Blocks host root (`/`) or `/etc` mounts in `@prod`.
- `zone-ingress-naming.sh`: Enforces `*.w7.local` domain naming.

## Observability

- **Metrics**: Prometheus (`prom.w7.local`) scrapes `node-exporter` and the custom `w7-exporter`.
- **Dashboards**: Grafana (`grafana.w7.local`) provides a "W7 Global Health" view.
- **Logs**: Dozzle (`logs.w7.local`) provides real-time container log streaming.

## Operator Starting Flow

1. **Bootstrap**: `source .shared/w7.sh` to initialize the CLI wrapper.
2. **Validate**: Run `w7 doctor` to check host dependencies and DNS.
3. **Scaffold**: `w7 init @dev/my-app` to create a new workspace.
4. **Deploy**: `w7 up my-app` to start the containers.
5. **Monitor**: Check `w7 stat` or the Grafana dashboard for health.

---
*See `.shared/GITOPS_DESIGN.md` for deep-dive on deployment logic.*

## Deep-Dive Documentation
- [docs/OBSERVABILITY.md](docs/OBSERVABILITY.md): Metrics, Grafana, and alerting.
- [docs/SECURITY_POLICY.md](docs/SECURITY_POLICY.md): Zone isolation and trust model.
- [docs/CI_CD_EXAMPLES.md](docs/CI_CD_EXAMPLES.md): Gitea Actions workflow templates.
- [docs/ARCHITECTURE_DIAGRAM.md](docs/ARCHITECTURE_DIAGRAM.md): Network and deployment topology.
- [docs/BACKUP_SCRIPTS.md](docs/BACKUP_SCRIPTS.md): Automation for data protection.
- [docs/DISASTER_RECOVERY.md](docs/DISASTER_RECOVERY.md): Platform restoration guide.
