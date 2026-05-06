# W7-Base Monorepo

This repository is a local-first Docker Compose orchestration monorepo for managing W7 stacks across `@ops`, `@dev`, `@prod`, and `@lab` zones.

## Scope

This root `AGENTS.md` applies to the entire repository. Prefer nested `AGENTS.md` files inside specific stacks when a subproject has different workflows or tooling.

## Repo Shape

```text
w7-localbase/
├── @ops/    <- platform and infrastructure services
├── @dev/    <- active development stacks
├── @prod/   <- production-grade local stacks
├── @lab/    <- sandboxes and experiments
├── docs/    <- stable platform documentation
├── README.md
└── AGENTS.md
```

## Working Model

- Treat this repository as a multi-zone monorepo, not as a single application.
- Use the zone model before making assumptions about lifecycle, safety, or deployment behavior.
- Prefer the `w7` workflow for operating existing stacks.
- Read stack-local documentation before making stack-specific changes.

## Stable Concepts

- A stack is a directory managed under one of the zone roots.
- `@ops` contains shared platform services.
- `@dev` is for active development and integration work.
- `@prod` is higher-trust and should be treated conservatively.
- `@lab` is for disposable experiments and prototyping.

## Operator Guidance

- Use `README.md` for the main platform overview and CLI behavior.
- Use `docs/README-LLM.md` for concise LLM/operator guidance.
- Use `docs/KNOWLEDGE_BASE.md` for stable platform concepts and terminology.
- Use nested `AGENTS.md` files when entering a stack with specialized workflows.

## Safety

- Never store secrets in committed code or docs; use environment files and the repo's secret-management flow.
- Do not assume a workflow from one stack applies to another stack.
- Do not document unstable file-level details here when a stack-local file is a better fit.
- Keep root guidance small; push stack-specific rules downward.

## UI Design Work

When the task involves UI / frontend design, generation, or visual review, you **MUST** use the dedicated toolchain — skills (`stitch-design`, `enhance-prompt`, `frontend-design`, `design-md`, `webapp-testing`, `agent-browser`), the Stitch MCP (`mcp__stitch__*`), and Playwright MCP (`mcp__plugin_playwright_playwright__*`) — and verify changes in a real browser before claiming completion. Full rule: `.claude/rules/ui-design.md`.
