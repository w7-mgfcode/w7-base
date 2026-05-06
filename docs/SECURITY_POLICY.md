# Security Policy & Trust Model

This document outlines the security architecture, trust boundaries, and isolation policies of the W7-Base platform.

## 1. Zone Isolation Model
The directory-based zone model is the primary security boundary:
- **@ops (Critical):** Trusted infrastructure. Managed via Runners or manual operator input.
- **@prod (High Trust):** Production-grade services. Protected by interactive `--yes` gates and policy enforcement.
- **@dev (Low Trust):** Active development. Webhook-based auto-sync enabled.
- **@lab (Zero Trust):** Disposable experiments. No persistent guarantees; pruning is permitted.

## 2. Trust Boundaries
- **Host Socket:** Services requiring Docker access (Traefik, Webhook, Act-Runner) mount `/var/run/docker.sock`. If these containers are compromised, the attacker gains root-level access to the host.
- **Network Segmentation:** All stacks are isolated by default. Ingress is managed strictly via Traefik and the external `w7-ingress` network.
- **External Exposure:** The platform is designed for **LOCAL-ONLY** use. Never expose Traefik (80/443), Gitea (3000), or Webhook (9000) to the public internet without a VPN or authenticated tunnel.

## 3. Secret Management (SOPS Sealing)
W7-Base uses SOPS/AGE for secret-at-rest encryption:
- **.env.example:** Committed to Git; defines the schema.
- **.env:** Never committed; contains real secrets at runtime.
- **.env.sops:** Committed to Git; encrypted version of `.env`.
- **Decryption:** The `w7 up` command handles decryption using the host's AGE private key.

## 4. Policy Enforcement
The `w7 doctor` command performs static analysis on stack configurations:
- **Privileged Containers:** Forbidden in `@prod` and `@ops` unless explicitly allowed.
- **Host Mounts:** Restricted in higher-trust zones to prevent container escape.
- **Root User:** Non-root users (`USER_UID=1000`) are preferred in all stacks.

## 5. Compliance Audits
Regularly run `w7 doctor --audit` to ensure all stacks comply with the latest platform policies. Violations will be tracked in the `w7_policy_violation` Prometheus metric.
