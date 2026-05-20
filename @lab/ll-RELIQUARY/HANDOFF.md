# Session Handoff — 2026-05-20 (ll-RELIQUARY Phase 0 boilerplate + Phase 1 design seed)

> **Date:** 2026-05-20
> **Workspace:** `/home/w7-hector/w7-localbase/@lab/ll-RELIQUARY/`
> **Session focus:** Bootstrap a new `@lab` stack for a browser-based collectable-artifact game, encode a mandatory Stitch + agent-browser + Playwright design pipeline, and run the first design-system generation pass through to baseline.
> **Status:** `partial` — Phase 0 (boilerplate) fully shipped + verified; Phase 1 first-pass `stitch-design` generated S01 cleanly but S02/S03 jobs failed to land server-side after 3+ attempts. All wireframes/specs are locked-and-loaded for a re-run.

---

## What Was Done

### 1. New stack scaffolded: `@lab/ll-RELIQUARY/`

30+ files, all currently **untracked** (git status: `?? @lab/ll-RELIQUARY/`). W7 contract compliant, policy-clean.

| Layer | Files | Notes |
|-------|-------|-------|
| W7 contract | `.w7-meta`, `compose.yml`, `.env.example`, `.gitignore`, `data/` | `docker compose --env-file .env.example config -q` passes |
| Local rules | `.claude/rules/ui-design-pipeline.md`, `.claude/rules/docker-infra.md` | Mandatory Stitch + agent-browser + Playwright workflow encoded |
| Top-level docs | `README.md`, `CLAUDE.md`, `AGENTS.md` | |
| Planning trio | `BRAINSTORM.md`, `STORYBOARD.md`, `ARCHITECTURE.md` | Substantive — see §3 below |
| Stitch | `.stitch/DESIGN.md` (generated), `.stitch/designs/S01-empty-shelf.{html,png}` | DESIGN.md is the canonical token source |
| Screens | `docs/SCREENS/S01-empty-shelf.md`, `S02-first-reveal.md`, `S03-account-claim.md` | S01 is mockup-backed; S02/S03 are spec-only (Stitch-pending) |
| API stub | `apps/api/{Dockerfile,requirements.txt,src/server/main.py}` | FastAPI /health + /version |
| UI stub | `apps/ui/{Dockerfile,nginx.conf,package.json,vite.config.ts,tsconfig.json,index.html,src/{App.tsx,main.tsx,index.css}}` | React 18 + Vite 5 + Tailwind v4 + Radix + framer-motion + PixiJS |
| Baseline | `dogfood-output/baseline-20260520T190943Z/{01-boilerplate-landing.png,report.md}` | agent-browser, 1440×900, no console errors |

### 2. Stack booted via `w7 up @lab/ll-RELIQUARY` and verified

Generated `.env` with `openssl rand -hex 24` secrets (mode 600, gitignored). All four containers came up healthcheck-gated:

| Container | Image | Host port | Status at session end |
|-----------|-------|-----------|----------------------|
| `lab-ll-reliquary-db` | `postgres:16.6-alpine` | 5454 | ✅ healthy |
| `lab-ll-reliquary-cache` | `redis:7.4.1-alpine` | 6464 | ✅ healthy |
| `lab-ll-reliquary-api` | `reliquary-api:latest` (FastAPI) | 8282 | ✅ healthy — `/health` returns `{"status":"ok"}` |
| `lab-ll-reliquary-ui` | `reliquary-ui:latest` (nginx) | 4242 | ⚠️ container marked **unhealthy** by Docker, but **HTTP 200 from host curl** — see "Known issues" below |

### 3. Planning trio filled with reasoned defaults (BRAINSTORM.md §3)

Eight locked product decisions, all logged with rationale in `BRAINSTORM.md` §7:

- Single-player v0 (curator experience, no PvP)
- 30-second core session beat (anti-slot-machine)
- Core verb: **COLLECT** (anti-adversarial)
- Finite editions (`Print N of M`) over hidden rarity tiers — anti-gacha
- Daily relic, **no streaks** (opt-in retention, anti-Duolingo-shame)
- Aesthetic: **modern-museum × quiet-occult** (Wellcome × Wunderkammer × calm-tech)
- Desktop-first, mobile-readable
- WCAG AA from day one

### 4. Storyboard wireframes locked for Journey A

`STORYBOARD.md` §5 now has full ASCII wireframes + interactive contracts + motion specs + accessibility notes for **S01 (Empty Shelf)**, **S02 (First Reveal)**, **S03 (Account Claim)**. Screen inventory updated to `🟡 wireframe ready` for the three.

### 5. Stitch design system generated (first pass)

- **Stitch project**: `Reliquary — Collectable Artifact Game (ll-RELIQUARY)`, ID `17652338204408695000` (PRIVATE)
- **S01 generated, downloaded, verified**: Stitch produced a beautiful museum × quiet-occult interpretation — gold "Reliquary" wordmark, dark warm surface with wave-grain texture, 4-slot horizontal shelf, slot #3 glowing with ✦ glyph, gold pill CTA, italic footer hint. **Matches the wireframe faithfully.**
- **`.stitch/DESIGN.md` written**: anchor token set, typography scale (Cormorant Garamond / Inter / Space Mono), motion vocabulary, Tailwind v4 `@theme` mapping, WCAG contrast verification table, full provenance footer.
- **`docs/SCREENS/S01-empty-shelf.md`** carries the design-system mapping and interactive contract.

### 6. agent-browser baseline captured

`dogfood-output/baseline-20260520T190943Z/`:
- `01-boilerplate-landing.png` — 1440×900 screenshot, gold wordmark, live API health probe `✓ reliquary-api — ok (boilerplate)`
- `report.md` — observation log, snapshot tree, intentional gaps vs. Phase 1 spec, stack health table
- Browser launched with `--no-sandbox --disable-dev-shm-usage` (Ubuntu 26.04 user-namespace sandbox restriction)

---

## Decisions Made (with rationale)

- **Working name `ll-RELIQUARY`** — because *reliquary* (treasure-keeper) carries the artifact+retention metaphor at the brand level; user reserved rebrand option via `git mv`.
- **4-container topology over the user's 3-container minimum** — because Redis is the natural home for sessions, daily-relic counters, and (later) pub/sub for shelf-update fan-out; postponing it would force a retrofit during Phase 2.
- **FastAPI (Python) for the backend** — because consistency with `@lab/ll-KNOWRAG` keeps the operator-zone toolchain to one language; rejected Node/Fastify (would add a second runtime to the lab zone).
- **React 18 + Vite 5 + Tailwind v4 + Radix + framer-motion + PixiJS** — because Tailwind v4 + Radix is already validated in KNOWRAG (proven Stitch-compatible per memory), PixiJS is reserved for canvas-heavy screens only (reveal, lineage). Rejected Phaser/Godot — engine-creep risk.
- **Mandatory Stitch + agent-browser + Playwright pipeline encoded in stack-local `.claude/rules/ui-design-pipeline.md`** — because the user's instructions made this an EPIC RULESET; encoding it locally (not just globally) raises the bar inside this stack specifically and prevents drift if the root rule weakens.
- **Postgres + Redis split over single-DB design** — because Postgres for persistent identity/lineage, Redis for hot-path counters and pub/sub; trade-off: two ops surfaces, but avoids retrofit cost later.
- **Postgres `16.6-alpine`, Redis `7.4.1-alpine`** — version-pinned per `.claude/rules/docker-infra.md`; no `:latest`.
- **Non-root containers across api + ui** — because the platform pattern (memorialized in recent KNOWRAG fixes #115/#117/#119) is to run as low-privilege users; api uses uid 10001, ui uses nginx user.
- **`.stitch/DESIGN.md` is generated, not hand-authored** — because the `ui-design-pipeline.md` rule forbids hand-rolled tokens; first generation came from Stitch S01 and was post-processed into Tailwind v4 `@theme` syntax.
- **Space Mono accepted as the mono font** (Stitch swap for the proposed IBM Plex Mono) — because Stitch resolved to Space Mono during S01 generation and the result reads true to the museum-card register; locked in DESIGN.md.

---

## Dead Ends / Failed Approaches

- **Tried:** `mcp__stitch__generate_screen_from_text` for S02 and S03 with detailed ~3500-char prompts → **Failed because:** the MCP call timed out at the ~2-min mark, and the jobs never appeared in `list_screens` over the following ~10 minutes (S01, by contrast, landed cleanly within ~2 min of its call). **Pattern:** the first generation in the project succeeds; subsequent calls in the same session appear to silently drop.
- **Tried:** retrying S02 with a shorter (~1500-char) prompt → **Failed because:** same symptom; job did not register. Skill docs explicitly warn against retries ("If the tool fails with a timeout, don't retry").
- **Tried:** opening `agent-browser` without `--no-sandbox` → **Failed because:** Ubuntu 26.04 restricts unprivileged user namespaces via AppArmor; Chrome exits before DevTools URL is written. Workaround: `--args "--no-sandbox,--disable-dev-shm-usage"` (also noted in project memory for future).
- **Tried:** `--viewport` as a top-level flag → **Failed because:** not a recognized agent-browser command. Correct path: `agent-browser set viewport 1440 900` after `open`.

---

## Known Issues

1. **UI container shows `unhealthy` even though `http://localhost:4242/` serves HTTP 200** — the `HEALTHCHECK` in `apps/ui/Dockerfile` uses `wget -qO- http://localhost:8080/`, and inside the container `wget` can't connect (logs: `wget: can't connect to remote host: Connection refused`). External curl from the host works fine. Likely cause: nginx is binding only to one interface, or the non-root nginx user can't reach localhost the way BusyBox wget expects. **Does not block traffic** but breaks `w7 stat` health rollup and Docker's `depends_on: condition: service_healthy` for any future child container.

2. **Stitch session is "warm" — S02/S03 jobs may resurrect later** — the user's Stitch account may still receive completed jobs for the timed-out S02/S03 generations after this session ends. If new screens appear in `list_screens` for project `17652338204408695000`, download them as `S02-first-reveal.{html,png}` / `S03-account-claim.{html,png}` and update the mockup docs.

3. **All work is uncommitted on the wrong branch** — current branch is `chore/knowrag-ollama-version-bump` (unrelated to Reliquary). Switching branches without committing will lose everything. See Next Steps for the recovery move.

---

## Open Questions (for the next session)

- [ ] Does the stack name `RELIQUARY` survive user review, or rebrand before commit? (User reserved this option.)
- [ ] Should `reliquary` be added to the commit-format scope allow-list (`.claude/rules/commit-format.md`), or fall back to scope `stacks` for the first commit?
- [ ] Should the new stack live under its own branch (`feat/reliquary-bootstrap`) off `master`, or remain on the current `chore/knowrag-ollama-version-bump` branch (NOT recommended)?
- [ ] When Stitch is responsive again, should S02 + S03 be re-generated with the saved prompts, or should new screens be added to the queue (S04 daily relic, S05 codex)?
- [ ] Are there any aesthetic adjustments needed to S01 before it gets implemented in code? (e.g., the wave-grain texture, slot count of 4 vs. 5, the ✦-inside-slot decision Stitch made.)
- [ ] What's the card-art pipeline for the first 7 artifacts in the `Ember of First Light` lineage? (AI-gen baseline + hand-touchup, or commission?)

---

## Next Steps

### 1. ⭐ Verify Stitch S02/S03 status, then re-trigger with the saved prompts.

Run from any directory:

```bash
# Check if the timed-out jobs resurrected post-session
# (Stitch sometimes finishes jobs after the MCP timeout — list_screens will reveal new ones)
```

Then in Claude Code:

```
Invoke Skill: stitch-design
Project ID: 17652338204408695000
Paste verbatim: the "## Re-generation prompt" block from
  @lab/ll-RELIQUARY/docs/SCREENS/S02-first-reveal.md
Wait for completion (~3 min). Download HTML+PNG to
  @lab/ll-RELIQUARY/.stitch/designs/S02-first-reveal.{html,png}
Update docs/SCREENS/S02-first-reveal.md status from 🟡 to ✅ and fill the "What Stitch produced" + "How it consumes the design system" sections.
Repeat for S03.
```

**Expected outcome**: `docs/SCREENS/S02-first-reveal.md` and `S03-account-claim.md` both transition from 🟡 Stitch-pending to ✅ Stitch-generated, mockup screenshots committed under `.stitch/designs/`.

### 2. Secure the work — branch hygiene + first commit

The current branch (`chore/knowrag-ollama-version-bump`) is wrong for this feature. Options:

```bash
# 2a. Open a GitHub issue first (per .claude/rules/commit-format.md — issue-before-commit)
gh issue create --title "feat(reliquary): bootstrap @lab/ll-RELIQUARY browser game stack" --label "stack:reliquary"

# 2b. Add `reliquary` to the commit-format scope allow-list
#     Edit .claude/rules/commit-format.md and append `reliquary` to the table around line 21

# 2c. Create the right branch off master
git switch master
git pull --rebase origin master
git switch -c feat/reliquary-bootstrap

# 2d. Stage + commit (NEVER use `git add .` — list paths explicitly per security-patterns.md)
git add @lab/ll-RELIQUARY/.w7-meta @lab/ll-RELIQUARY/compose.yml @lab/ll-RELIQUARY/.env.example \
        @lab/ll-RELIQUARY/.gitignore @lab/ll-RELIQUARY/README.md @lab/ll-RELIQUARY/CLAUDE.md \
        @lab/ll-RELIQUARY/AGENTS.md @lab/ll-RELIQUARY/BRAINSTORM.md @lab/ll-RELIQUARY/STORYBOARD.md \
        @lab/ll-RELIQUARY/ARCHITECTURE.md @lab/ll-RELIQUARY/HANDOFF.md \
        @lab/ll-RELIQUARY/.claude/ @lab/ll-RELIQUARY/.stitch/ @lab/ll-RELIQUARY/docs/ \
        @lab/ll-RELIQUARY/apps/ @lab/ll-RELIQUARY/data/.gitkeep @lab/ll-RELIQUARY/dogfood-output/.gitkeep \
        @lab/ll-RELIQUARY/dogfood-output/baseline-20260520T190943Z/

git commit -m "feat(reliquary): bootstrap @lab/ll-RELIQUARY browser game stack (#<issue>)"
```

### 3. Fix the UI healthcheck

Replace `wget` with `curl` in `@lab/ll-RELIQUARY/apps/ui/Dockerfile`:

```dockerfile
# Add to runtime stage, before USER nginx:
RUN apk add --no-cache curl

# Replace HEALTHCHECK:
HEALTHCHECK --interval=15s --timeout=5s --retries=4 --start-period=10s \
  CMD curl -fsS http://127.0.0.1:8080/ >/dev/null || exit 1
```

Rebuild: `w7 down @lab/ll-RELIQUARY && w7 up @lab/ll-RELIQUARY`. Verify with `docker ps --filter "name=lab-ll-reliquary-ui"`.

### 4. Implement S01 in code against the generated DESIGN.md

Replace `@lab/ll-RELIQUARY/apps/ui/src/index.css` `@theme` block with the canonical version from `.stitch/DESIGN.md` §9. Replace `apps/ui/src/App.tsx` with the S01 layout (header + headline + 4-slot shelf with active slot #3 + gold CTA + footer hint). Run `agent-browser` again at 1440×900 and diff against `.stitch/designs/S01-empty-shelf.png`.

---

## Context for the next session

**Stack is currently running.** Do NOT `w7 prune` or `w7 down -v` before verifying you don't need the captured state. Postgres has no data of value yet, but the `.env` file (gitignored, mode 600) contains the running session's secrets — regenerating is fine but optional.

**The Stitch project is the source of truth for the design system, not this repo.** The link is the project ID `17652338204408695000`. Future Stitch invocations should reuse this ID, not create new projects.

**The user's preferred workflow is PLAN → 3× parallel research → CONTEXT → REVIEW → EXECUTE** (per project memory). Auto-mode was active this session; the user did not interject with corrections, so all defaults stuck. Confirm before committing on a different branch or renaming the stack.

**Memory-relevant facts captured this session** (not yet written to `~/.claude/.../memory/`):
- agent-browser on Ubuntu 26.04 needs `--args "--no-sandbox,--disable-dev-shm-usage"` (already in memory as `reference_agent_browser_ubuntu26`)
- Stitch first generation in a project succeeds; subsequent calls in the same session may silently drop — **this is new; consider capturing as a reference memory** if it reproduces.

---

## Files Touched / Created This Session

All under `@lab/ll-RELIQUARY/`, all currently untracked:

```
.w7-meta                          .gitignore                .env.example
compose.yml                       README.md                 CLAUDE.md               AGENTS.md
BRAINSTORM.md                     STORYBOARD.md             ARCHITECTURE.md         HANDOFF.md
.claude/rules/ui-design-pipeline.md
.claude/rules/docker-infra.md
.stitch/DESIGN.md                 .stitch/designs/S01-empty-shelf.html
                                  .stitch/designs/S01-empty-shelf.png
docs/SCREENS/.gitkeep             docs/SCREENS/S01-empty-shelf.md
                                  docs/SCREENS/S02-first-reveal.md
                                  docs/SCREENS/S03-account-claim.md
docs/DECISIONS/.gitkeep
apps/api/Dockerfile               apps/api/requirements.txt
apps/api/src/server/__init__.py   apps/api/src/server/main.py
apps/ui/Dockerfile                apps/ui/nginx.conf        apps/ui/package.json
apps/ui/vite.config.ts            apps/ui/tsconfig.json     apps/ui/index.html
apps/ui/src/App.tsx               apps/ui/src/main.tsx      apps/ui/src/index.css
data/.gitkeep
dogfood-output/.gitkeep
dogfood-output/baseline-20260520T190943Z/01-boilerplate-landing.png
dogfood-output/baseline-20260520T190943Z/report.md
```

Outside the stack: **no other files were modified.** The previous root `HANDOFF.md` (2026-05-12, code-scanning loop) is untouched and unrelated.
