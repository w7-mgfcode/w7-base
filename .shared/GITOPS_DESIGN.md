# GitOps Design & Integration Model

## Mirroring Model
W7-Base uses a local Gitea instance (`@ops/gitea`) to mirror critical external repositories (e.g., from GitHub) and host local-only configuration repositories.
1. Gitea periodically pulls from the upstream remote (Mirror mode).
2. Upon sync/push, Gitea fires a webhook payload to the local Listener (`@ops/webhook`).

## Webhook Listener & Safe Sequence
The listener uses `adnanh/webhook` to execute a shell script (`deploy.sh`) upon receiving a valid payload.

**The Controlled Deploy Flow:**
1. **Receive & Authenticate:** Validate the `X-Gitea-Signature` using HMAC-SHA256 to ensure the payload is from the trusted Gitea instance.
2. **Metadata Mapping:** Parse the repository name and branch, then scan `W7_ROOT` for `.w7-meta` files that have matching `git_trigger` definitions.
3. **Protection Gate (`@prod`):** Any stack living in `@prod` is immediately rejected for automated updates. Production deployments require explicit operator approval (running `w7 up` manually).
4. **Pull/Update:** `git fetch` and `git reset --hard` the target branch to prevent merge conflicts in the local worktree.
5. **Pre-Deploy Validation:** Run `docker compose config -q`. If the newly pulled `compose.yml` or `.env` structure is invalid, abort the deployment before taking down the existing containers.
6. **Redeploy:** Execute `/w7-localbase/.bin/w7 up <zone>/<stack>`.

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