# W7-Base

> **Local-first orchestration & GitOps platform** built on Docker Compose and a unified `w7` CLI. PaaS-grade ergonomics without leaving the terminal — designed for developers and homelab operators.

[![Platform](https://img.shields.io/badge/platform-linux%20%7C%20macOS-lightgrey)]()
[![Stack](https://img.shields.io/badge/stack-Docker%20Compose-2496ED?logo=docker)]()
[![CLI](https://img.shields.io/badge/CLI-bash-4EAA25?logo=gnubash)]()
[![GitOps](https://img.shields.io/badge/gitops-Gitea%20%2B%20Webhook-609926?logo=gitea)]()
[![Secrets](https://img.shields.io/badge/secrets-SOPS%20%2B%20AGE-blue)]()
[![Status](https://img.shields.io/badge/baseline-Phase%207%20sealed-success)]()
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![CI](https://github.com/w7-mgfcode/w7-base/actions/workflows/ci.yaml/badge.svg)](https://github.com/w7-mgfcode/w7-base/actions/workflows/ci.yaml)

---

## What is W7-Base?

W7-Base is a **directory-driven monorepo** that standardizes Docker Compose deployments across four isolated zones (`@ops`, `@dev`, `@prod`, `@lab`) and exposes them through a single ergonomic CLI: `w7`. It bundles GitOps automation, SOPS-encrypted secrets, Traefik ingress, observability, and policy enforcement — all running entirely on your local machine or a small VPS.

**Built for:**
- Developers running multiple compose stacks who are tired of typing `docker compose -f ... --env-file ...`.
- Homelab operators who want PaaS-style discoverability without Kubernetes.
- Teams that want GitOps discipline (push → deploy) on a single host, with no cloud dependency.

**Not built for:**
- Multi-host orchestration (use Kubernetes/Swarm).
- Production cloud deployments.
- Stateless ephemeral workloads (it's local-first, persistent-volume oriented).

---

## 🚦 Current Development State

| Area | Status | Notes |
|------|--------|-------|
| **Platform baseline** (zones, CLI, GitOps, secrets, observability) | ✅ **Sealed at Slice 21** | All 23 documentation slices verified |
| **`@ops` services** (9 stacks) | ✅ Operational | Gitea, Traefik, Webhook, Prometheus, Grafana, Node Exporter, W7 Exporter, Dozzle, Act-Runner |
| **`@dev/anythingllm`** (LLM workspace) | ✅ Deployed | Postgres + Qdrant + Gemini, SOPS-encrypted secrets |
| **`@lab/ll-KNOWRAG`** (KB/RAG sub-project) | 🔄 Phase 7 sealed → Phase 8 pivot in-flight | See [§ KNOWRAG](#-knowrag--knowledge-base--rag-sub-project) |
| **`@prod/whoami`** | ✅ Validation workload | Pre-prod gate verified |

> 📍 **Active focus:** `@lab/ll-KNOWRAG` is mid-pivot from Supabase/PostgREST to **Gitea + Qdrant** as the storage backend. Phase 7 (UI/Backend parity, recursive crawling, reranking) is sealed; Phase 8 (re-architecture) is the next planned slice.

---

## 🚀 Quick Start

**Prerequisites:** `bash` (or `zsh`), `docker`, `docker-compose-plugin`, `tar`. Optional: `age` and `sops` for encrypted secrets.

```bash
# 1. Clone
git clone https://github.com/w7-mgfcode/w7-base.git ~/w7-base
cd ~/w7-base

# 2. Activate shell integration (adds `w7` CLI, zone aliases, `w7 go` cwd-jump)
echo 'source ~/w7-base/.shared/w7.sh' >> ~/.bashrc
source ~/.bashrc

# 3. Verify
w7 stat        # Cross-zone health matrix
w7 doctor      # Validate host dependencies, DNS, contracts
```

You'll see the W7-Base health matrix showing all stacks across all zones.

---

## 🏗️ Architecture

```
~/w7-base/
├── @ops/             Core platform (Gitea, Traefik, Prometheus, Grafana, ...)
├── @dev/             Active development stacks
├── @prod/            Production-grade local stacks (gated)
├── @lab/             Sandboxes & experiments (only zone where `prune` is allowed)
├── .shared/          Global env bridge, policies, deploy templates
├── .bin/             Vendored CLI: w7, sops, age
└── docs/             Platform documentation
```

### The Strict Stack Contract

A **stack** is any directory exactly one level deep inside a zone that contains a `.w7-meta` file:

```
@dev/my-app/
├── .w7-meta          YAML — GitOps routing, dependencies, health checks
├── compose.yml       Standard Docker Compose definition
├── data/             Persistent volumes (target of `w7 backup`)
├── .env.example      Required-secret schema (committed)
├── .env              Real secrets (NEVER committed)
└── .env.sops         SOPS+AGE encrypted secrets (safe to commit)
```

The CLI auto-injects `COMPOSE_PROJECT_NAME="<zone>-<stack>"` (e.g., `dev-my-app`) before invoking Docker so identical stacks across zones don't collide.

### Zone Lifecycle Policy

| Zone | Trust | GitOps | `prune` allowed | `up` requires `--yes` |
|------|-------|--------|-----------------|----------------------|
| `@ops` | High | Webhook + Actions | ❌ | ❌ |
| `@dev` | Med  | Webhook (instant) | ❌ | ❌ |
| `@prod` | Highest | Actions only (approval-gated) | ❌ | ✅ |
| `@lab` | Low  | Webhook (instant) | ✅ | ❌ |

---

## 🛠️ The `w7` CLI

| Command | Description |
|---------|-------------|
| `w7 up <stack\|all>` | Start stack(s) — merges `.shared/global.env` and stack `.env`; `all` boots `@ops` first |
| `w7 down <stack\|all>` | Stop stack(s) — `all` stops application zones first, `@ops` last |
| `w7 init <@zone/stack>` | Scaffold a new stack with the standard contract |
| `w7 doctor [--json]` | Validate dependencies, DNS, secret coverage, policy compliance |
| `w7 stat` | O(1) cross-zone status matrix |
| `w7 top` / `stats` | Live per-zone resource visibility |
| `w7 logs <stack>` | Tail logs (preserves Docker ANSI colors) |
| `w7 go <stack>` | `cd` shell to stack path (requires `.shared/w7.sh` sourced) |
| `w7 net` | Port-mapping visibility |
| `w7 backup <stack>` | Tar.gz of `data/` (excludes `.env` to prevent secret leakage) |
| `w7 prune <stack>` | Destroy containers + networks + volumes — **`@lab` only** |
| `w7 verify <stack>` | Run stack-local end-to-end smoke (e.g. KNOWRAG: ingestion + search + `/related` + MCP) |
| `w7 secret <init\|edit\|decrypt> <stack>` | SOPS+AGE secret management |

---

## 🌍 Environment Bridge

W7-Base layers env files instead of duplicating them. CLI runs:

```bash
docker compose --env-file .shared/global.env --env-file .env up -d
```

**Precedence (highest wins):**
1. Host OS exported variables
2. Stack-local `.env`
3. Global bridge `.shared/global.env` (no secrets here — committed)

Use `${REQUIRED_KEY:?error msg}` in `compose.yml` for fail-fast on missing vars.

---

## 🔐 Secret Management — Three-File Model

| File | Committed? | Purpose |
|------|-----------|---------|
| `.env.example` | ✅ Yes | Schema (key names + placeholders) |
| `.env` | ❌ **Never** | Real values, runtime only |
| `.env.sops` | ✅ Yes (encrypted) | AGE-encrypted `.env`, GitOps-safe |

**Auto-decrypt:** `w7 up` decrypts `.env.sops` → `.env` automatically when the encrypted file is newer and `sops` is installed.

```bash
age-keygen -o ~/.config/sops/age/keys.txt    # Generate key
# Paste public key into root .sops.yaml
w7 secret init @ops/gitea                     # Encrypt existing .env
w7 secret edit @ops/gitea                     # Edit encrypted secrets
```

Full guide: [.shared/SECRETS.md](.shared/SECRETS.md)

---

## 🔄 GitOps — Hybrid Model

| Path | Trigger | Use For | Approvals |
|------|---------|---------|-----------|
| **Webhook** (`@ops/webhook`) | Instant push (HMAC-signed) | `@dev`, `@lab` | None — speed over ceremony |
| **Runner** (`@ops/act-runner`) | Gitea Actions (push, PR, schedule, manual) | `@ops`, `@prod` | Branch protection + required reviews |

The webhook flow: push → HMAC verify → `git pull` → `docker compose config` validation → `w7 up`. Failed validation rolls back the commit; the running stack stays untouched.

Full design: [.shared/GITOPS_DESIGN.md](.shared/GITOPS_DESIGN.md)

### Gitea Actions workflows

The repo ships with ready-to-run workflows for the local `@ops/act-runner`:

| File | Purpose |
|------|---------|
| `.gitea/workflows/validate.yaml` | `docker compose config` across every stack + run all `.shared/policy/*.sh` checks. Triggered on push/PR. |
| `.gitea/workflows/deploy.yaml` | Discovers stacks changed in the push, runs `w7 up` on each (skips `@prod` — that path requires manual approval). |
| `.shared/workflows/deploy-template.yaml` | Reference template for stacks that want their own per-repo deploy pipeline. |

GitHub Actions equivalents (`.github/workflows/ci.yaml`, `lint.yaml`) run the same compose + policy + ShellCheck/yamllint validation on PRs.

---

## 🌐 Ingress — Traefik

All HTTP services route through Traefik on the `w7-ingress` external Docker network. Default hostnames (add to `/etc/hosts`):

| Service | URL |
|---------|-----|
| Traefik dashboard | `http://localhost:8080` |
| Gitea | `http://git.w7.local` |
| Webhook listener | `http://webhook.w7.local` |
| Dozzle (logs) | `http://logs.w7.local` |
| Prometheus | `http://prom.w7.local` |
| Grafana | `http://grafana.w7.local` |

```bash
# /etc/hosts
127.0.0.1 git.w7.local webhook.w7.local logs.w7.local prom.w7.local grafana.w7.local
```

---

## 📊 Observability

Built-in Prometheus + Grafana + custom W7-aware exporter:

- **`@ops/prometheus`** — scrapes `node-exporter` + `w7-exporter`
- **`@ops/grafana`** — dashboards (default login: `admin` / `admin`)
- **`@ops/node-exporter`** — host metrics
- **`@ops/w7-exporter`** — translates `w7 doctor --json` + `w7 stat` into Prometheus metrics
- **`@ops/dozzle`** — real-time container log streaming

Custom metrics exposed:
- `w7_healthy` — global system health (1/0)
- `w7_error_count`, `w7_warning_count` — `doctor` results
- `w7_containers_up{zone}` — per-zone container counts
- `w7_policy_violation{zone, stack, policy}` — automated policy enforcement failures

---

## 🛡️ Policy Enforcement

Static checks under `.shared/policy/` run during `w7 doctor`:

- `prod-privileged.sh` — blocks `privileged: true` in `@prod`
- `prod-no-root-mount.sh` — blocks host `/` or `/etc` mounts in `@prod`
- `zone-ingress-naming.sh` — enforces `*.w7.local` naming convention

---

## 🧪 KNOWRAG — Knowledge Base & RAG sub-project

`@lab/ll-KNOWRAG` is an in-flight local-first KB+RAG system extracted from [Archon](https://github.com/coleam00/archon). It ingests websites/documents, chunks and embeds content, and exposes retrieval via FastAPI, FastMCP, and a React UI.

**Phase 7 (sealed):**
- ✅ Recursive crawling with depth limits
- ✅ `llms.txt` task expansion
- ✅ Crawl4AI integration with httpx fallback for JS-rendered pages
- ✅ Provider-based reranking with lexical fallback
- ✅ UI overhaul with backend parity
- ✅ 6 dogfood-found UI/API issues fixed

**Phase 8 (planned — re-architecture pivot):**
- 🔴 Replace Supabase/PostgREST with **Gitea + Qdrant** (Git as artifact source-of-truth, Qdrant for semantic search)
- 🔴 Markdown frontmatter parser (tags, status, version, owner)
- 🔴 Git-webhook-driven Qdrant ingestion pipeline
- 🔴 Tailwind-based card-grid catalog UI
- 🔴 Open WebUI + MCP integration

See `@lab/ll-KNOWRAG/.omg/state/taskboard.md` for the full Phase 8 task plan.

---

## 📁 Repository Layout

```
.
├── @ops/             Platform services (9 stacks)
│   ├── gitea/        Local Git server (mirror + Actions host)
│   ├── traefik/      Reverse proxy + ingress
│   ├── webhook/      GitOps deploy listener (HMAC-signed)
│   ├── act-runner/   Gitea Actions runner
│   ├── dozzle/       Real-time container logs
│   ├── prometheus/   Metrics server
│   ├── grafana/      Dashboards
│   ├── node-exporter/ Host metrics
│   └── w7-exporter/  Custom W7 → Prometheus bridge
├── @dev/             Development stacks
│   ├── anythingllm/  LLM workspace + PG + Qdrant + SOPS secrets
│   ├── skill-generator/ Claude skill builder (no compose stack)
│   └── test-scaffold/ Init template fixture
├── @prod/            Production-grade stacks
│   └── whoami/       Pre-prod validation workload
├── @lab/             Sandbox / experiments
│   ├── ll-KNOWRAG/   KB + RAG system (Archon-derived)
│   └── test-init/    Init template fixture
├── .bin/             w7, sops, age (vendored)
├── .shared/          Global env, policies, workflows, contract spec
├── .claude/          Claude Code rules + skills (project instructions)
└── docs/             Platform documentation
```

---

## 📚 Documentation Map

**Operator-facing:**
- [README.md](README.md) — this file
- [AGENTS.md](AGENTS.md) — agent/AI assistant guidance
- [llms.txt](llms.txt) — LLM discovery file

**Platform docs (`docs/`):**
- [README-LLM.md](docs/README-LLM.md) — concise LLM-optimized platform guide
- [KNOWLEDGE_BASE.md](docs/KNOWLEDGE_BASE.md) — operational reference + troubleshooting
- [ARCHITECTURE_DIAGRAM.md](docs/ARCHITECTURE_DIAGRAM.md) — network topology + request flow
- [API_REFERENCE.md](docs/API_REFERENCE.md) — CLI flags + `.w7-meta` schema
- [SECURITY_POLICY.md](docs/SECURITY_POLICY.md) — zone isolation + trust boundaries
- [CI_CD_EXAMPLES.md](docs/CI_CD_EXAMPLES.md) — Gitea Actions templates
- [OBSERVABILITY.md](docs/OBSERVABILITY.md) — Prometheus + Grafana setup
- [BACKUP_SCRIPTS.md](docs/BACKUP_SCRIPTS.md) — automated backup guide
- [DISASTER_RECOVERY.md](docs/DISASTER_RECOVERY.md) — full restoration steps
- [USER_ONBOARDING.md](docs/USER_ONBOARDING.md) — Day 1 operator guide
- [OMG_GEMINI_AI_WORKFRAME_KB.md](docs/OMG_GEMINI_AI_WORKFRAME_KB.md) — `oh-my-gemini-cli` orchestration framework KB

**Internal contracts (`.shared/`):**
- [W7-CONTRACT.md](.shared/W7-CONTRACT.md) — directory + `.w7-meta` spec
- [ENV_PRECEDENCE.md](.shared/ENV_PRECEDENCE.md) — env-file overlay rules
- [SECRETS.md](.shared/SECRETS.md) — SOPS+AGE operator guide
- [GITOPS_DESIGN.md](.shared/GITOPS_DESIGN.md) — webhook + runner design

---

## 🚑 Troubleshooting

| Symptom | Cause / Fix |
|---------|-------------|
| `w7 go` says "directory not found" | You're running `.bin/w7` directly. `source ~/w7-base/.shared/w7.sh` to activate the shell wrapper. |
| `w7 up @prod/...` fails | By design — `@prod` is gated. Use `--yes` to bypass interactively, or use the Gitea Actions path. |
| Webhook silently doesn't deploy | Check `w7 logs @ops/webhook`. `docker compose config` validation failure auto-rolls-back the commit. |
| `w7 doctor` warns about SOPS | Install `age` + `sops` and configure `~/.config/sops/age/keys.txt`. |
| `*.w7.local` doesn't resolve | Add the hostnames to `/etc/hosts` (see § Ingress). |

---

## 🤖 GitOps Attack Surface (read this)

The `@ops/webhook` and `@ops/act-runner` containers mount `/var/run/docker.sock` to execute `w7 up`. **If compromised, this gives root-equivalent host access.** Mitigations baked in:

- HMAC-SHA256 signature verification on webhook payloads.
- `docker compose config` pre-flight validation — rolls back the commit on failure.
- Hard-blocked `@prod` deploys via the webhook path; `@prod` requires the Actions path with branch protection.

**Never expose the webhook port (9000) or Gitea (3000) to the public internet** without zero-trust overlays (Tailscale, Cloudflare Tunnel, etc.).

---

## 🗺️ Roadmap

| Feature | Status |
|---------|--------|
| `w7 init` scaffolding engine | ✅ Implemented |
| `w7 doctor` system validation | ✅ Implemented |
| SOPS+AGE secret management | ✅ Implemented |
| Webhook GitOps + HMAC | ✅ Implemented |
| Gitea Actions / runner integration | ✅ Implemented |
| Traefik ingress + `*.w7.local` | ✅ Implemented |
| Prometheus + Grafana + W7 exporter | ✅ Implemented |
| Policy enforcement (privileged, root-mount, naming) | ✅ Implemented |
| Backup retention + restore | ✅ Implemented |
| Interactive `@prod` approvals | ✅ Implemented |
| KNOWRAG Phase 8 — Gitea+Qdrant pivot | 🔴 Planned (next slice) |
| Webhook audit logging | 📋 Planned |

---

## 🤝 Contributing

This is a personal homelab/operator framework first, but suggestions and patches are welcome. Conventions:

- **Commits:** `type(scope): description` — types: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`. See historical `git log`.
- **Stacks:** Must follow the contract in [.shared/W7-CONTRACT.md](.shared/W7-CONTRACT.md).
- **Secrets:** Never commit `.env`. Use `.env.example` for the schema and `.env.sops` for encrypted values.
- **Policy:** New `@prod` stacks must pass `.shared/policy/*.sh` checks.

---

## 📜 License

Released under the [MIT License](LICENSE).

---

## 🙏 Acknowledgements

- **[Archon](https://github.com/coleam00/archon)** — KB/RAG core reused and adapted in `@lab/ll-KNOWRAG`.
- **[Traefik](https://traefik.io/)**, **[Gitea](https://gitea.io/)**, **[Prometheus](https://prometheus.io/)**, **[Grafana](https://grafana.com/)** — the platform substrate.
- **[Mozilla SOPS](https://github.com/getsops/sops)** + **[AGE](https://github.com/FiloSottile/age)** — encrypted secrets.
- **[Crawl4AI](https://github.com/unclecode/crawl4ai)** — JS-rendered crawling in KNOWRAG.
