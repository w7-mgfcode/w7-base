# Session Handoff — 2026-05-21 (CARD SHED stack contract bootstrapped + PRP 3 MVP umbrella opened)

> **Date:** 2026-05-21
> **Workspace:** `/home/w7-hector/w7-localbase/` (focus on `@lab/ll-CARDSHED/`)
> **Session focus:** Scaffolded the `@lab/ll-CARDSHED/` stack-contract root that was missing after PRP 2's core landed, fixed a latent commit-format hook scope-drift along the way, then decomposed PRP 3 §A into an 8-sub-issue MVP umbrella ready for execution.
> **Status:** `completed`
> **Previous handoff archived (local only — gitignored):** repo-root `.handoffs/2026-05-21-cardshed-prp02-merged.md`
> **This file's location:** `@lab/ll-CARDSHED/HANDOFF.md` — stack-local, committed (force-added past root `.gitignore`'s `HANDOFF.md` rule, mirroring `@lab/ll-RELIQUARY/HANDOFF.md` convention).

> This is the **cardshed stack-local** handoff. RELIQUARY has its own active handoff at `@lab/ll-RELIQUARY/HANDOFF.md` (still locally modified — not from this session) and is not superseded by this one.

---

## What Was Done

- **PR #145** opened, reviewed, **merged** to `master` (`cb780cc`). Two atomic commits on `chore/cardshed-stack-bootstrap`:
  - `bd3cedb` — `chore(repo): sync commit-format hook scope allow-list (#144)`
  - `3021b93` — `chore(cardshed): bootstrap @lab/ll-CARDSHED stack contract (#143)`

- **`.claude/hooks/check-commit-format.sh:77`** — extended `SCOPE_ALLOW` regex from `knowrag|api|ui|mcp|ingest|repo|platform|stacks|state|ops|ci|docs|release` to include `reliquary|cardshed` (closes #144). The rule MD already listed both scopes; the hook was stale because the introducing PRs (#135 + #139) landed via GitHub squash-merge, which bypasses local hooks.

- **`@lab/ll-CARDSHED/` stack root** scaffolded — 15 new files, modelled on `@lab/ll-RELIQUARY/`:
  - **Contract:** `.w7-meta`, `compose.yml` (alpine sleep stub for now), `.env.example` (UI_PORT=4343 placeholder), `.gitignore`
  - **Root docs:** `README.md` (162 lines), `CLAUDE.md` (109 lines), `AGENTS.md` (73 lines), `BLUEPRINT.md` (80 lines)
  - **Stack-local rules:** `.claude/rules/ui-design-pipeline.md` (148 lines, adapted from reliquary), `.claude/rules/core-determinism.md` (166 lines, codifies PRP 2's purity guarantees)
  - **Placeholders:** `.stitch/DESIGN.md` (explicit "do not hand-author — run `stitch-design` at PRP 3 M1"), `data/.gitkeep`, `dogfood-output/.gitkeep`, `docs/SCREENS/.gitkeep`, `docs/DECISIONS/.gitkeep`
  - Force-added `.w7-meta` + `.claude/` + `data/` + `dogfood-output/` because root `.gitignore` blanket-ignores those paths (same convention as reliquary — memory `reference_w7_sh_gitignore_convention`).

- **Issue #143** (cardshed stack contract) and **#144** (hook scope drift) opened with full scope/acceptance bodies; both closed by PR #145.

- **Umbrella #146** opened — `epic(cardshed): MVP — hot-seat browser (PRP 3 §A, M1–M17)`. Decomposed PRP 3 §A's 17 milestones into **8 grouped sub-issues** (preserves M-order while keeping the checklist scannable):

  | Issue # | Title | Milestones |
  |---------|-------|-----------|
  | #148 | scaffold apps/ui + design system | M1 + M2 |
  | #149 | pre-match screens — MainMenu + PlayerSetup | M3 + M4 |
  | #147 | table render + privacy splash | M5 + M6 |
  | #152 | attack + defense + phase transitions | M7 + M8 + M9 |
  | #150 | round/match results + settings + rules help | M10 + M11 |
  | #154 | a11y + responsive + juice | M12 + M13 + M14 |
  | #151 | analytics + Level-0 bot | M15 + M16 |
  | #153 | MVP shipping gate | M17 |

  Issue numbers are scrambled (parallel-creation race); the native sub-issue chain on #146 preserves M1→M17 sequence. Confirmed via GraphQL `subIssuesSummary { total }` = 8.

- **Memory saved:** `reference_commit_format_hook_drift.md` — flags the foot-gun that scopes added to `.claude/rules/commit-format.md` need a corresponding edit in `.claude/hooks/check-commit-format.sh:77`; GitHub squash-merge hides the drift. MEMORY.md index updated.

### Files Changed

```
Committed (in PR #145 → master cb780cc):
  M .claude/hooks/check-commit-format.sh                              (+1 / -1)
  A @lab/ll-CARDSHED/.claude/rules/core-determinism.md                (+166)
  A @lab/ll-CARDSHED/.claude/rules/ui-design-pipeline.md              (+148)
  A @lab/ll-CARDSHED/.env.example                                     (+16)
  A @lab/ll-CARDSHED/.gitignore                                       (+23)
  A @lab/ll-CARDSHED/.stitch/DESIGN.md                                (+38)
  A @lab/ll-CARDSHED/.w7-meta                                         (+8)
  A @lab/ll-CARDSHED/AGENTS.md                                        (+73)
  A @lab/ll-CARDSHED/BLUEPRINT.md                                     (+80)
  A @lab/ll-CARDSHED/CLAUDE.md                                        (+109)
  A @lab/ll-CARDSHED/README.md                                        (+162)
  A @lab/ll-CARDSHED/compose.yml                                      (+26)
  A @lab/ll-CARDSHED/data/.gitkeep                                    (empty)
  A @lab/ll-CARDSHED/docs/DECISIONS/.gitkeep                          (empty)
  A @lab/ll-CARDSHED/docs/SCREENS/.gitkeep                            (empty)
  A @lab/ll-CARDSHED/dogfood-output/.gitkeep                          (empty)

Memory updates (~/.claude/projects/-home-w7-hector-w7-localbase/memory/):
  A reference_commit_format_hook_drift.md
  M MEMORY.md                                                         (+1 line)

Issues opened/closed this session:
  #143 (closed via #145)  chore(cardshed): bootstrap @lab/ll-CARDSHED stack contract
  #144 (closed via #145)  chore(repo): sync commit-format hook scope allow-list
  #145 (MERGED)            PR for #143 + #144
  #146 (open, umbrella)    epic(cardshed): MVP — hot-seat browser (PRP 3 §A, M1–M17)
  #147–#154 (open, chained under #146)  the 8 MVP sub-issues
```

---

## Decisions Made

- **Picked Option A "Bootstrap stack root"** over Option B "PRP 3 M1 UI" or Option C "Decompose PRP 3 into sub-issues only" — because the W7-Base contract (`.shared/W7-CONTRACT.md`) requires `.w7-meta` for every stack; PRP 3 work would have landed in orphan paths otherwise. Low-risk, foundational, unblocks everything downstream.

- **Two atomic commits on the same branch** (hook fix first, then cardshed) rather than a single combined commit — because the cardshed scope was hook-blocked, and a two-commit shape gives cleaner audit trail + easier per-commit revert if the hook fix surfaces an unexpected interaction.

- **Decomposed PRP 3 §A into 8 grouped sub-issues (not 17 individual)** — because grouping logically-coupled milestones (e.g. M7+M8+M9 = attack/defense/phase as one PR-sized slice) preserves M-order while keeping the umbrella checklist scannable. Per-Mn acceptance criteria still live verbatim in sub-issue bodies. User can split further if PR sizes balloon.

- **Used GitHub native sub-issues (GraphQL `addSubIssue`)** over body-checkbox tracking — because KNOWRAG #55 precedent + the `subIssuesSummary` GraphQL field gives auto-progress on the umbrella. The native chain also preserves M-order even when raw issue numbers race.

- **`@lab/ll-CARDSHED/.stitch/DESIGN.md` written as an explicit placeholder** with content warning "do NOT hand-author; do NOT copy reliquary's tokens" — because reliquary's "modern-museum × quiet-occult" aesthetic does not fit a card game, and a future Stitch generation seeded from the wrong file would mislead the design synthesis.

- **`compose.yml` shipped as a bootable `alpine:3.20.3 + tail -f /dev/null` stub** rather than omitted — because `.shared/W7-CONTRACT.md` says every stack must have `compose.yml`, and `w7 stat` / discovery expect it. The stub becomes `cardshed-ui` (real React+nginx) at PRP 3 M1. Pattern mirrors `@lab/test-init/compose.yml`.

- **Used `chore(cardshed)` and `chore(repo)` scopes** rather than bundling under `chore(stacks)` — because the allow-list now contains both (after the hook fix landed in the same branch); more precise blame + closer to the PRP-2 precedent (`feat(cardshed)` in #139).

---

## Dead Ends

- **Tried:** Committing `chore(cardshed): bootstrap @lab/ll-CARDSHED stack contract (#143)` locally → **Failed because:** `.claude/hooks/check-commit-format.sh:77`'s `SCOPE_ALLOW` regex was missing `reliquary` and `cardshed`. Both scopes had been added to `.claude/rules/commit-format.md` (in #135 + #139), but the rule MD and the hook script are independent artifacts maintained by hand — and both introducing PRs landed via GitHub squash-merge, which bypasses local hooks entirely. The drift went undetected since #135/#139. I am the first one to trip it. Resolved by extending the regex (#144) as a separate atomic commit on the same branch. Memorialized as `reference_commit_format_hook_drift.md`.

- **Tried:** `git add '@lab/ll-CARDSHED/'` to stage everything in the new stack root → **Failed because:** root `.gitignore` blanket-ignores `.w7-meta`, `.claude/`, `data/`, `dogfood-output/`. Five files weren't staged. Resolved by `git add -f` for the ignored paths — same convention as reliquary scaffolding (per existing memory `reference_w7_sh_gitignore_convention`).

- **Tried:** Opening 8 sub-issues in parallel via backgrounded `gh issue create &` → **Worked but** the returned issue numbers were out of M-order (race condition: #147 went to "M5+M6 table" instead of "M1+M2 scaffold"). The native sub-issue chain saved the day — I mapped titles → numbers via `gh issue list` and chained via GraphQL `addSubIssue` in explicit M1→M17 order. Worth noting: future parallel issue creation should either accept the scrambled order, or serialize the calls.

---

## Open Questions

- [ ] **Reliquary leftovers** in working tree (`M @lab/ll-RELIQUARY/HANDOFF.md`, `?? @lab/hermes-ollama-gemma4-e2b/`, `?? @lab/ll-RELIQUARY/docs/DECISIONS/PALETTE_REVIEW.md`, `?? @lab/ll-RELIQUARY/landing/`) — block a clean `git status`. Pre-existing, not from this session. See `@lab/ll-RELIQUARY/HANDOFF.md` for the documented landing plan. Should they ship before #148 starts, or in parallel?

- [ ] **PRP 3's NEW #6 / #7 / #8 / #9 / #10 contradictions** (in `PRPs/cardshed-03-experience-prp.md` §"Cross-PRP Contradictions Flagged") — resolutions are "proposed" pending human review. Several are load-bearing for M1+M2 (e.g. NEW #6 = `shuffleDeck(seed)` required everywhere; NEW #9 = MVP treats single round as match). Should they be locked in a doc-only PR before #148, or addressed inside #148's PR?

- [ ] **Root `README.md` active-stacks table** — currently lists only KNOWRAG and a few stacks. Doesn't list cardshed or reliquary. Same gap exists for reliquary. Worth a follow-up PR.

- [ ] **GitHub labels `stack:cardshed` and `stack:reliquary`** — neither exists. Scope-prefixed issue titles work for discoverability but labels make filtered queries easier. Worth adding? (Reliquary handoff mentions using `stack:reliquary` label but it doesn't exist.)

- [ ] **Versioning trains** — `.claude/rules/versioning.md` mentions `platform-vX.Y.Z` + `knowrag-vX.Y.Z` only. When does cardshed get its own train (`cardshed-vX.Y.Z`)? Likely after M17 ships, but worth deciding the criterion.

- [ ] **Cardshed `apps/core/` workspace layout** — package.json says `"name": "@cardshed/core"` but there's no root workspace declaration. PRP 3 §M15 references `packages/analytics/` and `packages/ai/` as workspaces. Is this a yarn / npm / pnpm workspace, and where does the root `package.json` live? (Not at `@lab/ll-CARDSHED/` root yet.)

---

## Next Steps

> **VALIDATION GATE applied:** Step #1 names exact file paths, lists explicit dep changes, and references the PRP 3 line range. Could be executed by a fresh session without reading the rest of this handoff.

1. **Immediate (start #148, M1):** Open `PRPs/cardshed-03-experience-prp.md` at line 716 (M1 SCAFFOLD apps/ui yaml block). Create branch:
   ```bash
   git switch -c feat/cardshed-ui-scaffold
   ```
   Then mirror `@lab/ll-RELIQUARY/apps/ui/package.json` to `@lab/ll-CARDSHED/apps/ui/package.json` with these explicit changes:
   - **REMOVE** `dependencies`: `pixi.js`, `react-router-dom`
   - **ADD** `dependencies`: `partysocket`, `zod`, `immer`, `zustand`, `framer-motion`, `@radix-ui/react-dialog`, `@radix-ui/react-tooltip`, `@radix-ui/react-tabs`, `tailwind-merge`, `clsx`
   - **ADD** `dependencies`: `@cardshed/core` via `file:../core` workspace link
   - **KEEP** the existing `vitest ^2.1.x` + `typescript ^5.7.x` + Vite 5.4 pins (memory `project_knowrag_phase8_ui_stack` confirms Vite 6 is deferred)

2. **Scaffold the rest of M1:** Create `apps/ui/{tsconfig.json, vite.config.ts (port 4343, base "/"), index.html, src/{main.tsx, App.tsx, index.css}}` mirroring reliquary's UI tree. App.tsx renders `<h1>CARD SHED — MVP M1</h1>`. Verify `npm install && npm run dev` boots at `http://localhost:4343`, `npm run build` + `npm run lint` green.

3. **Capture M1 evidence:** Run `Skill: agent-browser` against the running dev server with viewport 1440×900. Save screenshot under `dogfood-output/<UTC>/m1-boot/` + auto-generated `report.md`. Per `.claude/rules/ui-design-pipeline.md` §3 — non-negotiable before closing #148.

4. **Start M2 (same #148 branch):** Write `docs/STORYBOARD.md` (§1 premise from PRP 3 §B + §2 user journey + §5 wireframes for all 9 MVP screens). Then run `Skill: stitch-design` with the storyboard + the engine API (`apps/core/src/core/types.ts` + `rules.ts`) as inputs. Replaces `.stitch/DESIGN.md` placeholder with the real generated design system. Record provenance in `docs/DECISIONS/<date>-stitch-run-1.md`.

5. **Open PR for #148:** Commit grammar `feat(cardshed): scaffold apps/ui + design system (#148)`. Body checklist mirrors #148's acceptance criteria. Link dogfood evidence + Stitch provenance.

6. **Resolve open question** about PRP 3 NEW #6–#10 contradictions before #149 starts — they're load-bearing for the next slice (matchStore wiring, win-on-defender semantics, etc.).

7. **Out-of-band** (any time, separate PRs): triage reliquary leftovers per `@lab/ll-RELIQUARY/HANDOFF.md`'s plan. Don't block cardshed MVP track on it.

---

## Context for Next Session

**Branch state:** `master` is fully up-to-date with `origin/master` at `cb780cc`. PR #145 squash-merged. Working tree has 4 uncommitted reliquary items pre-existing this session — they will NOT affect cardshed work; do NOT stage them on a cardshed branch.

**Cardshed shipped surface (post-#145):**
- Pure-logic core at `@lab/ll-CARDSHED/apps/core/` — 82/82 tests + sim-smoke green (PRP 2, #139)
- Stack contract root at `@lab/ll-CARDSHED/` — README, CLAUDE.md, AGENTS.md, BLUEPRINT.md, .w7-meta, .compose.yml stub, .claude/rules/, .stitch/DESIGN.md placeholder
- No `apps/ui/`, no `apps/server/`, no bots, no analytics — those land in #148–#154

**Commit-format hook scope allow-list (post-#145):** `knowrag, reliquary, cardshed, api, ui, mcp, ingest, repo, platform, stacks, state, ops, ci, docs, release`. Rule MD + hook regex are in sync. **Next session: if you add another scope, edit BOTH files in the same PR** (memory `reference_commit_format_hook_drift`).

**W7 stack-contract gotcha:** Root `.gitignore` blanket-ignores `.w7-meta`, `.claude/`, `data/`, `dogfood-output/`. When committing new stack-internal files of those types, use `git add -f`. Memory `reference_w7_sh_gitignore_convention`.

**Port allocation so far:**
- reliquary-ui: 4242, reliquary-api: 8282, reliquary-db: 5454, reliquary-cache: 6464
- **cardshed-ui: 4343** (declared in `@lab/ll-CARDSHED/.env.example` + `.w7-meta` health_check)
- Reserved (PRP 3 M3+): cardshed-server probably 8383, cardshed-db probably 5555 — not yet locked

**Stitch invariants** (from prior memories + reliquary's experience):
- Warm-session silent-drop: first Stitch generation in a Claude Code session succeeds; calls #2+ in the SAME session time out at ~2 min and never appear in `mcp__stitch__list_screens`. **Restart Claude Code between Stitch generations.**
- Harvest existing screens first via `mcp__stitch__list_screens` before generating new ones.
- Cardshed has NO existing Stitch project yet — first generation in M2 will create it.

**agent-browser invariants (Ubuntu 26.04):** Launch with `--args "--no-sandbox,--disable-dev-shm-usage"`. Set viewport AFTER `open`, not as a top-level flag (`agent-browser set viewport 1440 900`). Output goes to `dogfood-output/<UTC>/` with `report.md` + screenshots. Memory `reference_agent_browser_ubuntu26`.

**PRP 3 navigation cheatsheet** (`PRPs/cardshed-03-experience-prp.md`, 2026 lines):
| Section | Line range |
|---------|-----------|
| Cross-PRP contradictions (read first — NEW #6–#10 are load-bearing) | 22–128 |
| Shared Contract (frozen, byte-identical to PRP 2 types.ts) | 361–388 |
| Rules Engine API consumed by this layer | 389–406 |
| W7 Design-System Pipeline (mandatory) | 407–431 |
| Known Gotchas | 488–553 |
| Sub-deliverable A — MVP plan (17 milestones) | 694–1074 |
| Sub-deliverable B — UI/UX spec (screen inventory) | 1076–1169 |
| Sub-deliverable C — WebSocket protocol | 1170–1374 |
| Sub-deliverable D — Analytics & simulation | 1375–1477 |
| Sub-deliverable E — AI bot ladder | 1478–1661 |

**Memory updates this session:**
- Added: `reference_commit_format_hook_drift.md` — pointer to the rule-MD ↔ hook-regex drift gotcha
- Updated: `MEMORY.md` index

**Issues active:**
- #146 (umbrella, OPEN) → 8/8 sub-issues OPEN, 0/8 complete
- First sub-issue to execute: **#148** (M1+M2)
- All other sub-issues (#147, #149–#154) are dependency-ordered behind #148 — see umbrella body for M1→M17 sequence

**No PR is currently in-flight.** Branch `chore/cardshed-stack-bootstrap` was merged + can be deleted locally (`git branch -d chore/cardshed-stack-bootstrap`) — it still exists locally because I haven't cleaned it up.
