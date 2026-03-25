# W7-Base Knowledge Base

> Comprehensive operational reference for the W7-Base local orchestration platform. Optimized for human operators and LLM maintenance.

## 1. Platform Overview
W7-Base is a local-first orchestration framework that provides PaaS-like ergonomics using Docker Compose. It standardizes deployments across isolated zones with built-in GitOps, security, and observability.

### Core Architecture
- **Engine:** Docker Compose with standardized metadata (`.w7-meta`).
- **Isolation:** Directory-based zones with strictly enforced lifecycle policies.
- **Delivery:** Hybrid model using Webhooks (fast sync) and Gitea Actions (pipelines).
- **Interface:** Unified `w7` CLI wrapper.

## 2. Zone Responsibilities
| Zone | Purpose | Trust Level | Policy |
|---|---|---|---|
| `@ops` | Infrastructure services (Gitea, Traefik, Monitoring) | Critical | High uptime, runner-based updates |
| `@dev` | Active development and experimentation | Low | Webhook-based auto-sync |
| `@prod` | Stable, production-grade local services | High | Interactive confirmation, strict policy audit |
| `@lab` | Disposable sandboxes and temporary tests | None | Pruning permitted, no persistent guarantees |

## 3. Component Roles
- **Gitea (`@ops/gitea`):** Local Git server, OCI registry, and CI/CD control plane.
- **Traefik (`@ops/traefik`):** Edge proxy managing `*.w7.local` routing.
- **Webhook (`@ops/webhook`):** Lightweight sync engine for low-trust zones.
- **Act Runner (`@ops/act-runner`):** Gitea Actions executor with host Docker access.
- **W7 Exporter (`@ops/w7-exporter`):** Bridges CLI diagnostics to Prometheus metrics.

## 4. Operational Model

### Common Workflows
- **New Stack:** `w7 init @dev/myapp` -> Define `compose.yml` -> `w7 up myapp`.
- **Secret Setup:** `w7 secret init <stack>` -> Edit `.env` -> Commit `.env.sops`.
- **Compliance Audit:** Run `w7 doctor` regularly to check for policy violations.
- **Maintenance:** Use `w7 backup <stack>` before major config changes.

### Troubleshooting (Checklist)
1. **Connectivity:** Ensure `127.0.0.1 *.w7.local` is in `/etc/hosts`.
2. **Environment:** Run `w7 doctor` to find missing dependencies or invalid configs.
3. **Deployment:** Check `@ops/webhook` logs for sync failures or rollback events.
4. **Permissions:** Monitoring stacks require specific UID/GID (root or chown).

## 5. Security & Hardening
- **Secret Sealing:** Real secrets live in `.env` (ignored by Git) or encrypted in `.env.sops`.
- **Production Guardrails:**
  - `w7 up` requires `--yes` in `@prod`.
  - `.w7-lock` file prevents any deployment to the target stack.
  - No `privileged: true` or root host mounts permitted in `@prod`.
- **Trust Boundary:** CLI services use the host Docker socket; restrict network access accordingly.

## 6. Observability
- **Metrics:** Scraped by Prometheus from `node-exporter` and `w7-exporter`.
- **Visualization:** Grafana dashboard at `grafana.w7.local` (UID: `w7-global-health`).
- **Diagnostics:** `w7 doctor --json` provides machine-readable compliance state.

## 7. Project History (Compact)
- **Phase 1-4:** Foundation (CLI, Gitea, Webhook, Traefik).
- **Phase 5:** Gitea Actions & Hybrid CI/CD model.
- **Phase 6:** Production Hardening (Interactive prompts & locks).
- **Phase 7:** Policy Enforcement (Static compliance scripts).
- **Phase 8:** Advanced Observability (JSON metrics & Dashboards).

## 8. Glossary
- **Stack:** A directory containing `.w7-meta` and `compose.yml`.
- **Zone:** A root-level directory (prefixed with `@`) grouping stacks by lifecycle.
- **Contract:** The required file layout for a stack to be manageable by `w7`.
- **Sealing:** The act of encrypting a stack's secrets via SOPS.

## 9. Key References
- **Main CLI:** `.bin/w7`
- **Shell Bridge:** `.shared/w7.sh`
- **Policies:** `.shared/policy/*.sh`
- **Design Docs:** `.shared/GITOPS_DESIGN.md`, `README.md`, `docs/README-LLM.md`
