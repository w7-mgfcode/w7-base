# AGENTS.md — ll-CARDSHED

> Agent-side overview for this stack. For full project rules read `CLAUDE.md`; for the platform rules see the repo root `AGENTS.md` and `.claude/rules/`.

## What this stack is

ll-CARDSHED is a browser implementation of the CARD SHED card game in `@lab`. **Phase: Core Sealed.** The pure-logic rules engine ships at `apps/core/`; the UI/server/AI layers are PRP 3 work (17 milestones).

## The non-negotiables

1. **Core purity.** No `Math.random`, no time calls, no I/O inside `apps/core/`. ESLint enforces — see `.claude/rules/core-determinism.md`.
2. **UI pipeline.** Once `apps/ui/` exists, every UI change goes Stitch → agent-browser → (Playwright if needed). See `.claude/rules/ui-design-pipeline.md`.
3. **No rule variants.** CARD SHED v2.0 is frozen in PRP 2. Variants belong in PRP 3's simulation harness behind an explicit flag.
4. **Replay is law.** Every match is reproducible from `(matchSeed, actions[])`. Any change that breaks this is a bug.

## Specialist tools for this stack

| Surface | First-choice tool |
|---------|-------------------|
| Rules engine change | direct edit in `apps/core/src/core/*.ts` + add a test before touching `rules.ts` |
| New / edited screen (PRP 3 M1+) | `Skill: stitch-design` |
| Vague UI prompt | `Skill: enhance-prompt` → `stitch-design` |
| Multi-screen iteration | `Skill: stitch-loop` |
| Design system synthesis | `Skill: design-md` |
| Visual verification | `Skill: agent-browser` |
| Complex e2e / network mocks | `mcp__plugin_playwright_playwright__*` + `Skill: webapp-testing` |
| Stitch direct calls | `mcp__stitch__*` |

## Useful root agents

| Agent | When |
|-------|------|
| `policy-gatekeeper` | Before risky bash; before cross-zone changes |
| `repo-visibility-manager` | If you touch this stack's README / PRP index at release time |
| `Plan` | When breaking a PRP 3 milestone into atomic sub-issues before execution |
| `Explore` | Fast lookups within `@lab/ll-CARDSHED/` |

## Daily commands

```bash
# Core (library) — no container
cd @lab/ll-CARDSHED/apps/core
npm test               # 82/82 green; conservation property ≥200 iters
npm run sim-smoke      # 1000-game smoke

# Stack (stub until PRP 3 M1)
w7 up @lab/ll-CARDSHED
w7 logs @lab/ll-CARDSHED
w7 down @lab/ll-CARDSHED
w7 prune @lab/ll-CARDSHED   # destroy (allowed only in @lab)
```

## Conventions

- **Commits**: `type(scope): description (#issue)`. Scope `cardshed` is already in the allow-list.
- **Branches**: `feat/cardshed-*`, `fix/cardshed-*`, `chore/cardshed-*`, kebab-case ≤50 chars.
- **Issue first**: every commit references `#N`. PRP 3 milestones map 1:1 to atomic issues.
- **No `:latest`**: image pins always.
- **No invented tokens**: once `.stitch/DESIGN.md` is generated, it's the source of truth.
- **Tests stay green on master**: `npm test` AND `npm run sim-smoke` AND `npm run lint` AND `npm run typecheck` all clean before push.

## Bootstrap-phase acceptance checklist

- [x] `.w7-meta`, `compose.yml`, `.env.example`, `.gitignore` written
- [x] `README.md`, `CLAUDE.md`, `AGENTS.md`, `BLUEPRINT.md` written
- [x] Local rules: `.claude/rules/ui-design-pipeline.md`, `.claude/rules/core-determinism.md`
- [x] `.stitch/DESIGN.md` placeholder (generation deferred to PRP 3 M1)
- [x] Stack discoverable via `w7 stat` (`.w7-meta` present)
- [ ] `w7 up @lab/ll-CARDSHED` boots the placeholder container
- [ ] Policy scripts (`prod-privileged`, `prod-no-root-mount`, `zone-ingress-naming`) exit 0
- [ ] PRP 3 M1 umbrella issue opened with sub-issues

When the boxes are ticked, the stack is ready for PRP 3 M1 execution.
