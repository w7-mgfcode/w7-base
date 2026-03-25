# GitOps Design & Integration Model

## Mirroring Model
W7-Base uses a local Gitea instance (`@ops/gitea`) to mirror critical external repositories (e.g., from GitHub) and host local-only configuration repositories.
1. Gitea periodically pulls from the upstream remote (Mirror mode).
2. Upon sync/push, Gitea fires a webhook payload to the local Listener (`@ops/webhook`).

## Hybrid GitOps Model: Webhook vs. Runner

W7-Base supports two complementary deployment paths. As of Phase 5, the platform transitions from a purely webhook-driven model to a hybrid foundation.

| Feature | Webhook-Based (`@ops/webhook`) | Runner-Based (Gitea Actions) |
|---|---|---|
| **Trigger** | Instant (Webhook Push) | Event-driven (Push, PR, Manual, Schedule) |
| **Feedback** | Log file only (`w7 logs @ops/webhook`) | Rich UI, step-by-step logs, status checks |
| **Complexity** | Simple "Pull & Up" sync | Multi-stage (Test, Build, Lint, Deploy) |
| **@prod Policy** | **Explicitly Blocked** (Safety Gate) | **Allowed with Approvals** (RBAC) |
| **Trust Boundary** | Local container with Docker socket | Local runner with Docker socket |

### The Handoff Transition
1. **Low-Trust Sync:** Continue using the Webhook for internal `@dev` and `@lab` stacks where speed of synchronization is prioritized over build complexity.
2. **High-Integrity Pipeline:** Migrate `@ops` and `@prod` deployments to Gitea Actions. This enables pre-deployment testing and manual approval gates before a production stack is touched.

### RBAC & Safety Boundaries
- **Runner Scope:** The `act-runner` should be restricted to specific repositories or organizations if multi-tenancy is required. In a local homelab context, the runner is a "Trusted Operator."
- **Protected Environments:** Use Gitea's "Protected Branches" and "Required Reviews" to gate deployments to the `main` branch of production-linked repositories.
- **Docker Socket Risk:** Both the webhook and the runner share the same fundamental risk: mounting `/var/run/docker.sock` provides root-level access to the host. Users must never expose the Gitea instance or the Webhook port to the public internet without advanced zero-trust overlays (e.g., Tailscale, Cloudflare Tunnel).

## Implementation Path (Slice 12)
- **Phase 1:** Document the W7-Base Deployment Action (`deploy.yaml` template).
- **Phase 2:** Define the `.w7-meta` field `deployment_engine: "webhook" | "action" | "manual"`.
- **Phase 3:** Gradual migration of `@ops/traefik` and `@ops/gitea` to Action-based updates.

## Secret Handling Model
- **Rule:** DO NOT commit secrets to Git.
- Git repositories must only contain a `.env.example` file outlining the expected variables.
- The `deploy.sh` script **never** overwrites the `.env` file on disk. The `.env` file is maintained strictly out-of-band by the operator.
- If a new mandatory variable is added to `compose.yml` (e.g., `${NEW_API_KEY:?}`), Step 5 (Pre-Deploy Validation) will catch the missing variable in the local `.env` and intentionally fail the deployment, keeping the old stack safely running.

## Attack Surfaces & Mitigations
| Surface | Risk | Mitigation |
|---|---|---|
| **Webhook Endpoint** | Unauthorized triggering of deploy scripts by network actors. | `hooks.json` strictly requires an HMAC-SHA256 signature matching the shared secret configured in Gitea. |
| **Container Permissions** | The webhook container requires access to `/var/run/docker.sock` and the host `W7_ROOT` to execute `w7 up`. If compromised, the attacker has root-level control of the host. | Limit webhook listener to a local-only Docker network or strict firewall. Ensure the `almir/webhook` image is pinned to a specific SHA/version. *Enhancement:* Migrate `deploy.sh` to trigger via an SSH key to a dedicated restricted user rather than mounting the docker socket. |
| **Malicious Commits** | A compromised GitHub repo mirrored to Gitea could introduce a malicious `compose.yml` (e.g., mounting `/` as a volume). | Validation only checks syntax, not intent. This is a fundamental risk of automated GitOps. *Enhancement:* Implement a policy agent (like OPA/Conftest) in the `deploy.sh` script to statically analyze `compose.yml` for privileged mode or root volume mounts before running `w7 up`. |

## Recommended Action Boundary
- **Automatic:** `@dev`, `@lab` zone updates triggered by pushes. Syntax validation (`docker compose config`).
- **Approval-Gated:** Updates to `@prod` (blocked at the script level). Changes requiring new secrets (caught by syntax validation). Database migrations (`w7` handles container restarts, but operators should manually trigger schema migrations).