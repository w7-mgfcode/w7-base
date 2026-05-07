# Product Vision Alignment

Before creating issues, planning features, or starting work, check that the proposed work aligns with W7-Base's core identity.

## Core Principles

1. **Local-first.** Everything must run on a single host (developer laptop or small VPS). No cloud dependency, no SaaS tier, no external accounts required.
2. **Zone-first.** All work belongs to a zone — `@ops` (high-trust platform), `@dev` (active dev), `@prod` (gated production-grade), `@lab` (disposable). Cross-zone leakage is a smell.
3. **Compose-only.** Docker Compose is the deployment substrate. Stacks must follow the contract in `.shared/W7-CONTRACT.md` (one `.w7-meta` per stack, `compose.yml`, optional `.env.example` / `.env.sops`).
4. **Hybrid GitOps.** Webhook (instant, `@dev`/`@lab`) + Gitea Actions (gated, `@ops`/`@prod`). `@prod` deploys are interactive — never auto.
5. **SOPS-only secrets.** Three-file model: `.env.example` (committed), `.env` (never committed), `.env.sops` (AGE-encrypted, GitOps-safe). Plaintext secrets in `.env` files are the only acceptable runtime form, and they never leave the host.
6. **Lean CLI.** A single `bash` CLI (`.bin/w7`) wraps Docker Compose. No daemons, no background processes, no Python/Node rewrites of `w7`.
7. **Observability-as-default.** Every new stack must be visible in `w7 stat` and `w7 doctor`; production-grade stacks must expose Prometheus metrics where reasonable.
8. **Operator ergonomics.** Two humans should be able to operate the entire platform from `bash` + `w7` + a browser at `*.w7.local`.

## What W7-Base Is Not (Negative Guardrails)

Identity-level constraints. If a feature pushes W7-Base toward any of these, flag it.

- **Not a multi-host orchestrator** — use Kubernetes/Swarm/Nomad if you need that. W7-Base is single-host by design.
- **Not a cloud / SaaS product** — no hosted registry, no accounts, no managed control plane.
- **Not a PaaS replacement** — it gives you PaaS-shaped ergonomics, not PaaS feature parity.
- **Not an AI / LLM platform** — KNOWRAG is a guest workload in `@lab`, not a core platform feature. Don't build platform-level AI affordances.
- **Not stateless** — W7-Base is persistent-volume oriented. Ephemeral workloads should run elsewhere.
- **Not a destructive tool** — `w7 prune` is allowed only in `@lab`; `@prod` is gated; `git push --force` is forbidden by safety guardrails.

## Out of Scope (Hard No)

Do not propose or build:
- Multi-host clustering / leader election
- A hosted backend or web account system
- Auto-syncing daemons or file watchers (the webhook is enough)
- Replacing the Bash CLI with another language
- A vendored fork of Docker Compose
- Anything that requires `privileged: true` outside of `@lab`
- Anything that mounts host `/` or `/etc` outside of `@lab` (policy-enforced)

## The Litmus Test

When evaluating an idea, ask:
1. Does it run on a single host?
2. Is it Compose-shaped?
3. Does it respect the zone trust ladder (`@ops` > `@prod` > `@dev` > `@lab`)?
4. Does it use the existing CLI / GitOps / observability surface, or build a parallel one?
5. Is it lean enough that two operators can maintain it?
6. Are secrets handled via SOPS+AGE?

If any answer is "no" or "unclear", flag the concern before proceeding.

## When Ideas Don't Align

- Don't silently proceed — raise the concern directly
- Cite the specific principle it conflicts with
- Suggest an alternative that fits the zone model
- If the user wants to proceed despite the concern: go ahead, but:
  1. Add the `vision-review` label to the issue/PR
  2. Note the specific vision tension in the description
  3. This lets the project owner batch-review vision-flagged work

## When Ideas Are Ambiguous

- Ask which zone owns the work
- Ask whether the workload is single-host
- Check if the feature adds external service dependencies
- Default to deferring rather than guessing
