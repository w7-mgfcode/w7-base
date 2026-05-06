# W7-Base Architecture Extensions & Roadmap

## Decision Criteria
1. **Operator Value:** Does it eliminate toil or prevent critical errors?
2. **Implementation Difficulty:** Can it be built cleanly within the bash/docker constraints?
3. **Maintenance Cost:** Will it require constant updates or break often?
4. **Security Risk:** Does it expose new attack surfaces (e.g., executing arbitrary code)?
5. **Phase Fit:** MVP (Immediate need), Phase 2 (Core enhancement), Plugin (Optional/Niche).

## Option Comparison Matrix

| Option | Value | Difficulty | Maint. Cost | Phase Fit | Notes |
| --- | --- | --- | --- | --- | --- |
| `w7 init` & Templates | High | Low | Low | **Phase 2** | Highest ROI for onboarding. Replaces manual `mkdir` and `.w7-meta` writing. |
| `w7 doctor` & `validate` | High | Med | Med | **Phase 2** | Prevents confusing failures by verifying `docker`, shell aliases, and schema syntax. |
| Encrypted Secrets (`sops`) | High | High | High | **Phase 2** | Solves the ".env cannot be committed" problem, making GitOps fully stateless. |
| Backup Retention / `restore` | Med | Med | Med | Phase 2 | Natural evolution of `w7 backup`. |
| Audit/Event Log for Webhooks | Med | Low | Low | Phase 2 | Critical for debugging GitOps automation failures locally. |
| Approval Gates (`@prod`) | Med | Low | Low | Phase 2 | Explicit interactive confirmation before running `up` in `@prod`. |
| Terminal TUI Status | Med | High | High | Plugin | `w7 stat` works well enough. TUI requires complex dependencies (Go/Python). |
| Stack Tags & Dependency Graph | Low | High | High | Plugin | Over-engineering for local-first. Use native Compose `depends_on` instead. |
| Zone Inheritance Rules | Low | High | High | Plugin | Complex logic. The simple `global.env -> .env` bridge is easier to reason about. |

## Recommended Phase 2 Roadmap

### 1. `w7 init` (Scaffold Engine)
**Why it matters:** The directory contract is strict (`.w7-meta`, `compose.yml`, `data/`). Forcing the operator to create this manually every time causes friction. `w7 init <zone>/<stack>` could generate standard templates (e.g., `postgres`, `node`, `static`).

### 2. Built-in `sops` Integration (Secret Management)
**Why it matters:** The current MVP relies on an out-of-band `.env` file because secrets cannot be committed to Gitea. Wrapping `sops` (Mozilla Secret OPerationS) into the `w7 up` command allows operators to safely commit encrypted secrets to Git, unlocking true GitOps for local deployments.

### 3. `w7 doctor` (System Health & Validation)
**Why it matters:** As W7-Base is moved between different local machines, shell environments and Docker installations vary. `w7 doctor` quickly validates that dependencies (`docker`, `tar`, `bash`), shell integrations, and all `.w7-meta` files are syntactically valid.

### 4. Interactive `@prod` Approvals & Webhook Audit Logging
**Why it matters:** The webhook currently blocks `@prod` silently. The CLI should introduce a `--force` flag or a `[y/N]` prompt for `@prod` deployments. Furthermore, the webhook should write an `audit.log` so operators can see exactly why a push did or didn't deploy.

## What Should NOT Be Added Yet (Deferred/Plugins)
- **Dependency Graphs across Stacks:** Trying to orchestrate boot order *across* different stacks (e.g., DB stack must boot before API stack) reinvents Kubernetes or Docker Swarm. Operators should rely on application-level retry logic.
- **Canary/Staged Rollouts:** Overkill for a local-first framework. Blue/Green deployments are best handled by an external load balancer (like Traefik) and advanced CI/CD, not a local bash orchestrator.
- **TUI Dashboards:** A custom TUI adds heavy binary dependencies. The MVP relies on Dozzle for UI and `w7 stat` for quick text checks. This is sufficient.

## Execution Handoff for Next Phase
If proceeding to Phase 2, the execution order should be:
1. Implement `w7 init` with basic templates.
2. Implement `w7 doctor` to validate the environment.
3. Design the `sops` integration architecture.