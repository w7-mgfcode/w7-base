# CARD SHED PRP Bundle — Option B (Layered Concern Split)

> Generated 2026-05-20. Three input briefs for `/base_prp:generate-prp` to consume in parallel.

## The split

A monolithic master prompt + 8 follow-ups for the **CARD SHED** card game design were sliced into **3 layered concerns** so the work can run in parallel against three separate PRP-generation sessions.

| # | Layer | Brief | What it produces | Touches |
|---|-------|-------|------------------|---------|
| 1 | **Strategy & Blueprint** | `01-strategy-blueprint.md` | Decisions document — tech-stack choice, architecture diagrams, deliverables outline. **No code.** | Master §1 + §9 + Additional Instruction |
| 2 | **Deterministic Core** | `02-deterministic-core.md` | TypeScript data models + pure rules engine + Vitest suite. **No UI, no network, no I/O.** | Master §7 + §8 + FU1 + FU2 + FU8 |
| 3 | **Experience & Distribution** | `03-experience-distribution.md` | MVP build plan + UI/UX spec + WebSocket protocol + analytics taxonomy + AI bot design. **Wraps the core, no rules logic.** | Master §2 + §3 + §4 + §5 + §6 + FU3, FU4, FU5, FU6, FU7 |

## Why parallel works here

Each brief embeds the **complete CARD SHED v2.0 rule set** as its source of truth. None of the briefs reads the others' output — they share a frozen spec (the rules + the data-model contract written into PRP 2's brief), so PRP 1 / 2 / 3 are independent.

The only coupling: **PRP 2's brief pre-commits the `Card`/`Suit`/`Rank` enum encoding** so PRP 3 can be written against the same vocabulary without consuming PRP 2's output. The contract is in each brief's "Shared Contract" section verbatim — if you edit it in one, edit it in all three.

## Next-session protocol

```bash
# Run three parallel agents in a single message, each invoking the skill
# against one of the briefs:
#
#   Agent A: /base_prp:generate-prp on PRPs/01-strategy-blueprint.md
#   Agent B: /base_prp:generate-prp on PRPs/02-deterministic-core.md
#   Agent C: /base_prp:generate-prp on PRPs/03-experience-distribution.md
#
# Each agent will emit a PRP under PRPs/ following templates/prp_base.md.
# Output names suggested:
#   PRPs/cardshed-01-strategy-prp.md
#   PRPs/cardshed-02-core-prp.md
#   PRPs/cardshed-03-experience-prp.md
```

## What "done" looks like

- ✅ Three PRP documents under `PRPs/` matching the `prp_base.md` shape.
- ✅ PRP 1 contains the locked tech-stack decision + the implementation roadmap.
- ✅ PRP 2 contains exact pseudocode for every rules-engine function + test cases.
- ✅ PRP 3 contains the MVP feature checklist + the WebSocket message catalogue + the UI screen inventory.
- ✅ No PRP invents rule variants not marked `(optional)` in the brief.

## What to do if the briefs disagree

If during PRP generation an agent finds a contradiction between briefs (e.g., a function name in PRP 2 doesn't match a message field in PRP 3), **flag it in the PRP — do not silently reconcile**. Reconciliation belongs to the human-in-the-loop review step before any code is written.
