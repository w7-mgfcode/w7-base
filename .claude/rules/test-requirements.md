# Test Requirements

> Vision principle: **"Lean over sprawling."** W7-Base is a Compose-shaped platform — its primary "test" is `w7 verify`, plus per-stack smoke. Sub-projects (KNOWRAG) carry richer unit-test floors; the platform itself does not.

## What "tests" mean here

Three layers, applied differently per zone/stack:

| Layer | Where | What it asserts |
|-------|-------|-----------------|
| **Compose contract** | every stack | `docker compose config` parses; `.w7-meta` + `compose.yml` exist; `.env.example` covers required vars |
| **Policy** | every stack | `.shared/policy/*.sh` checks pass (no privileged, no root mounts in `@prod`, ingress naming) |
| **Smoke** | per-stack | A stack-local script that asserts the running stack's contract (e.g., `@lab/ll-KNOWRAG/scripts/verify.sh`) |
| **Unit / integration** | sub-projects only | KNOWRAG `apps/api/tests/` (pytest), `apps/ui/*.test.ts` (vitest) |

## When new tests are required

### Platform stacks (`@ops`, `@dev`, `@prod`)
- New stack → MUST ship a `compose.yml`, `.w7-meta`, and `.env.example`
- New stack → SHOULD ship a healthcheck in `compose.yml`
- New `.shared/policy/*.sh` → MUST be idempotent and exit 0 on a clean repo

### KNOWRAG sub-project (`@lab/ll-KNOWRAG/`)
- **New Python module under `apps/api/src/server/`** → MUST have a test file under `apps/api/tests/test_<module>.py`
- **New public function/method** → MUST have at least one happy-path test
- **Bug fix** → MUST include a regression test that would have caught the bug
- **New TypeScript component** → SHOULD have a vitest test if it owns non-trivial state (forms, queries, derivations)
- KNOWRAG end-to-end → `w7 verify @lab/ll-KNOWRAG` MUST stay 6/6 green on master

## Conventions

### KNOWRAG api (`apps/api/tests/`)
- Files: `test_<module>.py`
- Functions: `test_<function>_<scenario>()`
- Mock external dependencies (Gitea, Qdrant, Ollama) in unit tests
- Use `conftest.py` fixtures, not setUp/tearDown
- Integration tests may hit real services (the live stack); the verify harness owns these

### KNOWRAG ui (`apps/ui/`)
- Vitest, colocated `*.test.ts(x)` next to source

### Platform smoke
- Shell scripts under `<stack>/scripts/` or stack-local `scripts/`
- Idempotent, exit-coded, no interactive prompts

## What doesn't need tests

- `.shared/global.env` value tweaks
- `compose.yml` label-only changes (Traefik routing, etc.)
- Documentation
- `.claude/rules/` policy files (the rule IS the test)
- Configuration constants
- `__init__.py` re-exports

## Before committing

- Platform: `bash .shared/policy/prod-privileged.sh && bash .shared/policy/prod-no-root-mount.sh && bash .shared/policy/zone-ingress-naming.sh` — all must exit 0
- KNOWRAG api change: `cd @lab/ll-KNOWRAG/apps/api && PYTHONPATH=src python -m pytest tests/ -q`
- KNOWRAG ui change: `cd @lab/ll-KNOWRAG/apps/ui && npm test -- --run`
- KNOWRAG end-to-end: `w7 verify @lab/ll-KNOWRAG` (live stack required)

CI runs these for you — but a local run before push avoids round-trips. Do not commit on red.
