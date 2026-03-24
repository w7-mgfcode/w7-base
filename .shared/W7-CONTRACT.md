# W7-Base Architecture Contract

## 1. Directory & Path Rules
- **Zones:** Must be prefixed with `@` (e.g., `@ops`, `@dev`, `@prod`, `@lab`).
- **Stack Discovery:** A stack is any directory exactly one level deep inside a zone that contains a `.w7-meta` file (e.g., `@dev/database/.w7-meta`).
- **Strict Layout:** Every stack must contain:
  - `.w7-meta` (YAML format)
  - `compose.yml`
  - `data/` (Directory for local persistent volumes)
  - `.env` (Ignored in Git, generated from `.env.example` if applicable)

## 2. Naming & Collision Prevention
- **Daemon Isolation:** The `w7` CLI **MUST** export `COMPOSE_PROJECT_NAME="<zone>-<stack>"` (e.g., `dev-database`) before executing any underlying `docker compose` commands. This prevents naming and network collisions when identical stacks run in different zones.

## 3. Metadata Schema (`.w7-meta`)
The `.w7-meta` file uses YAML and must include GitOps routing data so the webhook listener knows which stack to update when a repository pushes.

```yaml
version: "1.0"
description: "Description of the stack"
git_trigger:
  repository: "gitea_user/repo_name"
  branch: "main"  # The branch that triggers an update for this specific zone
health_checks:
  - type: "http"
    endpoint: "http://localhost:8080/health"
```

## 4. Environment Variables
- **Bridge Ordering:** The `w7` CLI must source `.shared/global.env` first, then source the stack's local `.env`, allowing the stack variables to override global defaults.