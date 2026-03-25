# W7-Base

W7-Base is a local orchestration framework designed for developers and homelab operators who want the ergonomics of a PaaS without leaving the terminal. It standardizes Docker Compose deployments across isolated zones, provides a unified `w7` CLI, and integrates a secure, local-first GitOps deployment engine.

---

## 🚀 Quick Start & Installation

**Prerequisites:** `bash` or `zsh`, `docker`, `docker-compose-plugin`, and `tar`.

1. **Clone the Framework**
   ```bash
   git clone https://github.com/your-org/w7-localbase.git ~/w7-localbase
   cd ~/w7-localbase
   ```

2. **Shell Integration**
   Add the following line to your `~/.bashrc` or `~/.zshrc` to unlock the `w7` CLI wrapper, `w7 go` path jumping, and zone aliases:
   ```bash
   source ~/w7-localbase/.shared/w7.sh
   ```
   *Reload your shell (`source ~/.bashrc`).*

3. **Verify Installation**
   ```bash
   w7 stat
   ```
   You should see the (currently empty) W7-Base Health Matrix.

---

## 🏗️ Architecture & Directory Contract

The framework is divided into isolated deployment zones. A "stack" is any directory inside a zone that contains a `.w7-meta` file.

```text
~/w7-localbase/
├── @ops/           # Core framework services (Gitea, Webhook, Dozzle)
├── @dev/           # Active local development stacks
├── @prod/          # Local production-grade stacks (Protected)
├── @lab/           # Sandboxes & experiments (Disposable)
├── .shared/        # Global configuration bridge and shell scripts
└── .bin/           # The compiled w7 CLI executable
```

### The Strict Stack Contract
Every stack inside a zone **must** follow this exact layout to be discovered by the CLI:

```text
@dev/my-database/
├── .w7-meta        # YAML: Defines GitOps routing and metadata
├── compose.yml     # The standard Docker Compose definition
├── data/           # Directory for local persistent volumes (Targeted by w7 backup)
├── .env.example    # Required secrets schema (committed to git)
└── .env            # Actual secrets (NEVER committed)
```

> **Note:** To prevent daemon-level collisions when running identical stacks in different zones (e.g., `@dev/db` vs `@prod/db`), the CLI automatically isolates networks by prefixing `COMPOSE_PROJECT_NAME="<zone>-<stack>"`.

---

## 🛠️ The `w7` CLI Reference

The CLI is a thin, ergonomic wrapper around `docker compose`.

| Command | Description |
|---|---|
| `w7 up <stack>` | Starts the stack. Safely merges `.shared/global.env` and the stack's `.env`. Automatically blocks unforced executions in the `@prod` zone. |
| `w7 go <stack>` | Changes your shell's current working directory to the targeted stack. Understands ambiguity and suggests paths if multiple exist. |
| `w7 stat` | Prints a fast, O(1) cross-zone matrix showing the up/down status of all discovered stacks. |
| `w7 logs <stack>` | Tails the logs for the stack, preserving native Docker ANSI colors. |
| `w7 backup <stack>` | Creates a timestamped `.tar.gz` archive of the stack's `data/` directory. Explicitly ignores `.env` files to prevent secret leakage. |
| `w7 prune` | Destroys containers, networks, and volumes for a stack. **Hard-limited to the `@lab` zone only** to prevent accidental data loss. |

**Usage Example:**
```bash
w7 up @dev/postgres
w7 logs @dev/postgres
w7 backup @dev/postgres
```

---

## 🌍 The Global Environment Bridge

Instead of repeating variables (like domain names or timezones) in every stack, W7-Base uses an overriding bridge. 

When you run `w7 up`, the CLI executes:
```bash
docker compose --env-file .shared/global.env --env-file .env up -d
```

**Precedence Hierarchy:**
1. Host OS exported variables (Highest)
2. Stack Local (`<zone>/<stack>/.env`)
3. Global Bridge (`.shared/global.env`) (Lowest)

**Security Rule:** Never place secrets in `.shared/global.env`. Use it strictly for shared ergonomics.

---

## 🔄 GitOps & Webhook Safety

W7-Base includes an automated deployment engine (`@ops/webhook`) designed to listen to a local Gitea instance (`@ops/gitea`).

### How It Works
1. You push a commit to your local Gitea repository.
2. Gitea fires a webhook. The listener authenticates it using an HMAC-SHA256 signature (`X-Gitea-Signature`).
3. The deployment script (`deploy.sh`) maps the Git repository and branch to a local stack via the stack's `.w7-meta` file.
4. It performs a safe `git pull`.
5. **Pre-Deploy Gate:** It runs `docker compose config`. If the new configuration is invalid, it rolls back the `git` commit and aborts before taking the containers down.
6. It executes `w7 up` to redeploy.

### ⚠️ Security Attack Surface
The `@ops/webhook` container requires access to `/var/run/docker.sock` to execute deployments. While restricted to your local network, if this container is compromised, the attacker gains root-level access to the host machine. Ensure the webhook port (9000) is never exposed to the public internet.

---

## 🚑 Troubleshooting & Recovery

**"Command 'go' is not working or says 'directory not found'"**
You are executing the `.bin/w7` binary directly instead of the shell wrapper. Ensure `source ~/w7-localbase/.shared/w7.sh` is active in your current terminal session.

**"My GitOps deployment failed silently"**
Check the webhook listener logs:
```bash
w7 logs @ops/webhook
```
If a deployment fails the `docker compose config` validation step (e.g., missing a mandatory variable in `.env`), the system will safely abort and roll back the repository state to the previous commit.

**"w7 up in @prod is failing"**
By design, the MVP blocks automated or accidental `w7 up` commands inside the `@prod` zone. You must explicitly bypass this using manual docker compose commands or await the Phase 2 `--force` flag.

---

## 🔐 Secret Management

W7-Base uses a three-file model for secrets:

| File | Committed? | Purpose |
|------|-----------|---------|
| `.env.example` | Yes | Documents required keys (shape only) |
| `.env` | **Never** | Real secrets, used at runtime |
| `.env.sops` | Yes (encrypted) | AGE-encrypted secrets for safe Git storage |

**Auto-decryption:** When `w7 up` finds a `.env.sops` newer than `.env`, it automatically decrypts using SOPS + AGE — enabling true GitOps without exposing secrets.

**Validation:** `w7 doctor` checks that `.env` keys match `.env.example` and that SOPS configuration is present.

```bash
# Setup SOPS encryption
age-keygen -o ~/.config/sops/age/keys.txt   # Generate key
# Edit .sops.yaml with your public key
w7 secret init @ops/gitea                    # Encrypt existing .env
w7 secret edit @ops/gitea                    # Edit encrypted secrets
```

See `.shared/SECRETS.md` for full operator guide.

---

## 🗺️ Phase 2 Roadmap

| Feature | Status |
|---------|--------|
| `w7 init` — Scaffolding engine | Implemented |
| `w7 doctor` — System validation | Implemented |
| Secret management (SOPS/AGE) | Implemented |
| Interactive `@prod` approvals | Planned |
| Webhook audit logging | Planned |
| Backup retention / restore | Planned |
---

## 🌐 Network Routing & Ingress

W7-Base utilizes **Traefik** (`@ops/traefik`) as its global reverse proxy. This eliminates port conflicts and allows you to access services via clean local domain names instead of mapping everything to `localhost:PORT`.

### Default Local Domains
| Service | Domain |
|---|---|
| Traefik Dashboard | `http://localhost:8080` |
| Dozzle Logs | `http://logs.w7.local` |
| Gitea | `http://git.w7.local` |
| Webhook Listener | `http://webhook.w7.local` |
| Whoami (Test) | `http://whoami.w7.local` |

### Setting Up Local DNS
To route `.w7.local` domains on your machine, add them to your `/etc/hosts` file (or equivalent for your OS):

```text
127.0.0.1 logs.w7.local git.w7.local webhook.w7.local whoami.w7.local
```

### Adding Ingress to a Stack
When creating a new stack, ensure it connects to the `w7-ingress` external network and define Traefik labels in your `compose.yml`:

```yaml
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.myapp.rule=Host(`myapp.w7.local`)"
      - "traefik.http.services.myapp.loadbalancer.server.port=80"
    networks:
      - w7-ingress

networks:
  w7-ingress:
    external: true
```

---

## 🤖 CI/CD with Gitea Actions

W7-Base includes a local, integrated CI/CD pipeline powered by **Gitea Actions** and an isolated `act-runner` stack (`@ops/act-runner`). This allows you to run GitHub Actions-compatible workflows directly on your local infrastructure.

### 1. Enable Actions in Gitea
Actions are pre-configured in the `@ops/gitea` stack's `compose.yml`, but you may need to ensure it's enabled in your repository settings:
1. Navigate to your repository in Gitea (`http://git.w7.local`).
2. Go to **Settings > General**.
3. Check the **Enable Repository Actions** box.

### 2. The Act-Runner Layout
The `act-runner` stack is scaffolded identically to other W7 workloads:
```text
@ops/act-runner/
├── .w7-meta          # W7 routing metadata
├── compose.yml       # act_runner container configuration
├── data/             # Persistent storage for runner state
└── .env.example      # Required variables (URL, Token, Name)
```

### 3. Registering the Runner
To connect the runner to your local Gitea instance, you must provide a registration token.

1. In Gitea, navigate to **Site Administration > Actions > Runners** (for a global runner) or **Repository Settings > Actions > Runners** (for a repo-specific runner).
2. Click **Create new Runner** and copy the **Registration Token**.
3. Create an `.env` file in `@ops/act-runner/`:
   ```bash
   cp @ops/act-runner/.env.example @ops/act-runner/.env
   ```
4. Edit `@ops/act-runner/.env` and insert your token:
   ```ini
   GITEA_INSTANCE_URL=http://gitea-server:3000
   GITEA_RUNNER_REGISTRATION_TOKEN=your_token_here
   GITEA_RUNNER_NAME=w7-local-runner
   ```
5. Start the runner:
   ```bash
   w7 up @ops/act-runner
   ```
   *The runner will automatically register itself with Gitea on startup.*

### 4. Networking Assumptions
The `act-runner` container is attached to the `w7-ingress` Docker network. This allows it to resolve the `gitea-server` container directly via Docker's internal DNS without traversing the host network.

*   **`GITEA_INSTANCE_URL=http://gitea-server:3000`**: The runner communicates with Gitea over the internal Docker network on port `3000`. It does *not* use the external `git.w7.local` domain to register, avoiding DNS loopback issues on the host.
*   **Docker Socket**: The runner requires access to `/var/run/docker.sock` (configured in `compose.yml`) to spawn job containers.

### What is Scaffolded vs. Operator Input
*   **Scaffolded:** The W7 framework provides the `compose.yml`, the `w7-ingress` network attachment, and the `.env.example` template. The `act-runner` container is fully configured to read from these variables.
*   **Operator Input:** You must manually generate the registration token in the Gitea UI, create the `.env` file, and paste the token. (Tokens cannot be securely pre-provisioned via git).

---

## 📊 Observability & Monitoring

W7-Base provides a built-in observability stack powered by **Prometheus** and **Grafana**, with custom exporters to visualize platform health.

### 1. The Monitoring Stack
The observability layer is located in the `@ops` zone:
- **Prometheus** (`@ops/prometheus`): Scrapes metrics from platform services and exporters.
- **Grafana** (`@ops/grafana`): Provides visualization and alerting.
- **Node Exporter** (`@ops/node-exporter`): Exposes host-level hardware and OS metrics.
- **W7 Exporter** (`@ops/w7-exporter`): A custom bridge that transforms `w7 doctor --json` and `w7 stat` data into Prometheus metrics.

### 2. Accessing Dashboards
If you have local DNS configured, you can access the monitoring tools at:
- **Prometheus UI:** `http://prom.w7.local`
- **Grafana Dashboards:** `http://grafana.w7.local` (Default Login: `admin` / `admin`)

### 3. W7 Platform Metrics
The `w7-exporter` provides the following unique metrics for local orchestration:
- `w7_healthy`: Global system health (1 = Healthy, 0 = Unhealthy).
- `w7_error_count` / `w7_warning_count`: Totals from the latest `doctor` run.
- `w7_containers_up{zone="..."}`: Real-time container counts per deployment zone.
- `w7_policy_violation{zone="...", stack="...", policy="..."}`: Tracks automated policy enforcement failures.

### 4. Local Alerting
Prometheus is pre-configured with local alerting rules. Alerts will trigger if:
- The system remains in an "Unhealthy" state for more than 1 minute.
- A policy violation (e.g., privileged container in `@prod`) is detected.
