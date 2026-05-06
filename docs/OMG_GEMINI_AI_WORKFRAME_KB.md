# OmG Gemini AI-Workframe KB

## Purpose
This file is a working knowledge base for helping with tasks related to `oh-my-gemini-cli` (OmG), based on the upstream README:
https://github.com/Joonghyun-Lee-Frieren/oh-my-gemini-cli/blob/main/README.md

It is optimized for practical assistance: onboarding, command selection, workflow execution, debugging, and safe iteration.

## What OmG Is (Operational View)
- OmG is a Gemini CLI extension that turns single-session usage into a structured orchestration workflow.
- It introduces command-driven control (`/omg:*`), role-based agents, retained deep-work skills, and persistent state artifacts.
- Its core strength is staged execution with explicit verify/fix loops, not one-shot prompting.

## Core Runtime Building Blocks
- `gemini-extension.json`: extension delivery/registration contract.
- `GEMINI.md` + `context/omg-core.md`: core context and operating behavior.
- `commands/omg/*.toml`: slash-command control plane.
- `agents/*.md`: role prompts (planner, executor, verifier, debugger, director, etc.).
- `skills/*/SKILL.md`: retained deep-work skill pack.
- `.omg/state/*`: durable workflow state for lanes, taskboard, hooks, notify, and checkpoints.

## Primary Execution Flow
1. Intent routing:
   - `/omg:intent` classifies request and routes toward the correct staged workflow.
2. Workspace setup:
   - `/omg:workspace` sets/audits lane ownership and multi-root boundaries.
3. Team shaping:
   - `/omg:team-assemble` proposes dynamic roster and asks approval.
4. Planning and acceptance:
   - `/omg:team-plan` and `/omg:team-prd` produce dependency-aware tasks and measurable acceptance.
5. Implementation loop:
   - `/omg:team-exec` -> `/omg:team-verify` -> `/omg:team-fix` until done/blocker.
6. Lifecycle control:
   - `/omg:checkpoint`, `/omg:status`, `/omg:stop`, `/omg:cancel`.

## Logic Rules That Matter Most
- Smallest ready slice first, not broad multi-file guessing.
- Verification gates drive completion state (`done` vs `verified` are distinct).
- Taskboard/workspace are first-class memory; avoid replaying full chat history.
- Fallback routing exists when execution/review agents are unavailable.
- High-risk architecture-sensitive work should escalate to stronger judgment lanes (`omg-director` / `omg-architect`).

## State Files and Why They Matter
- `.omg/state/workspace.json`: lane roots, trust boundaries, ownership.
- `.omg/state/taskboard.md`: stable task IDs, priority (`p0`-`p3`), dependencies, evidence.
- `.omg/state/workflow.md`: lifecycle continuity and session posture.
- `.omg/state/notify.json`: alert policy routing.
- `.omg/state/hooks.json` and related hook outputs: continuation symmetry and automation behavior.
- `.omg/state/quota-watch.json`: token usage snapshots from after-agent monitor.
- `.omg/state/learn-watch.json`: dedupe/safety state for learn-signal hook.

## Command Selection Cheat-Sheet
- Need orientation now: `/omg:status`
- Need diagnosis before long run: `/omg:doctor`
- Need execution lane hygiene: `/omg:workspace audit`
- Need deterministic next task: `/omg:taskboard sync` then `/omg:taskboard next`
- Need full staged delivery: `/omg:team`
- Need custom team composition: `/omg:team-assemble`
- Need autonomous bounded loop: `/omg:autopilot`
- Need resume after interruption: `/omg:loop` or `/omg:checkpoint` + `/omg:status`
- Need prior rationale quickly: `/omg:recall "<query>" scope=state`

## Compatibility and Drift Checks
- README baseline says recommended Gemini CLI is `v0.36.0+`.
- OmG planning skill slash conflict: use `/omg-plan` (or `$omg-plan`) if native `/plan` collides.
- Policy migration note: legacy `--allowed-tools` should be replaced with policy profiles.

## Practical Failure Patterns and Recovery
- Symptom: command missing (`/omg:*` not found).
  - Check extension load with `gemini extensions list`, then restart session.
- Symptom: task selection unstable.
  - Run `/omg:taskboard sync` and ensure priorities are present (default drift can break `next` behavior).
- Symptom: parallel lanes keep conflicting.
  - Audit workspace and assign explicit lane/root ownership.
- Symptom: verify loop never closes.
  - Force evidence-based verification and check unresolved IDs in taskboard.

## Assistant Operating Defaults For OmG Requests
When asked to help with "omg gemini ai-workframe", prioritize this sequence:
1. Clarify current mode and goal (`/omg:status`, objective, done criteria).
2. Validate readiness (`/omg:doctor`, workspace/taskboard health).
3. Choose minimal correct command path (not maximal automation by default).
4. Keep verify/fix evidence explicit.
5. End with next safest command and fallback path if it fails.

## [NEEDS REPO CHECK] Items
- Exact current command definitions and flags in `commands/omg/*.toml`.
- Any README drift vs live extension internals (agents/skills/hook scripts).
- Latest release behavior beyond README-reviewed date.

