# UI Design Pipeline — MANDATORY for ll-CARDSHED

> **EPIC RULESET — load-bearing once `apps/ui/` exists.** The interface IS the game-feel layer. There is no hand-rolled UI escape hatch.

This rule strengthens the root `.claude/rules/ui-design.md`. Where they conflict, **this file wins** inside `@lab/ll-CARDSHED/`.

> Note: this rule has **no effect** until `apps/ui/` lands at PRP 3 M1. The bootstrap stub has no UI surface. From M1 onward, every UI change goes through the pipeline below.

---

## 1. The Pipeline (every UI change goes through it)

```
  ┌──────────────┐    ┌──────────────────┐    ┌─────────────────┐
  │  IDEA        │ →  │  STITCH          │ →  │  AGENT-BROWSER  │
  │  (PRP 3 §B   │    │  (skill + MCP    │    │  (Vercel-based  │
  │   screen spec)    │   generation)    │    │   validation)   │
  └──────────────┘    └──────────────────┘    └────────┬────────┘
                                                       │
                                                       ▼ if complex eval
                                              ┌─────────────────────┐
                                              │  PLAYWRIGHT MCP +   │
                                              │  SKILLS (deep e2e)  │
                                              └─────────────────────┘
```

You do **not** skip a stage. You do **not** reorder them. You do **not** invent UI without a Stitch artifact upstream.

---

## 2. STAGE 1 — STITCH (generation / transformation)

**Use one of these — nothing else:**

| Tool | When |
|------|------|
| `Skill: stitch-design` | Default entry-point for any new or modified screen. Wraps prompt-enhancement, design-system synthesis, and screen generation/edit. |
| `Skill: enhance-prompt` | When the input idea is vague — runs first, then hands off to `stitch-design`. |
| `Skill: design-md` | When the design system itself needs synthesis into `.stitch/DESIGN.md`. |
| `Skill: stitch-loop` | When iterating on multiple screens with consistent system (baton-pass loop). |
| `mcp__stitch__*` | Direct MCP calls when the skill abstraction is wrong fit (rare). |

**Mandatory inputs every Stitch invocation:**

1. The screen spec from `PRPs/cardshed-03-experience-prp.md` §B.
2. The relevant engine API contract (`apps/core/src/core/rules.ts` + `types.ts`) — the UI must not invent state the engine doesn't expose.
3. The pre-Stitch wireframe (PRP 3 §B per-screen ASCII layout).
4. The current `.stitch/DESIGN.md` (so output stays coherent).

**Output destination:**
- Screen mockups → `docs/SCREENS/<screen-slug>.md` (+ exported assets if Stitch returns them).
- Design system updates → `.stitch/DESIGN.md` (only `stitch-design` / `design-md` write here).

---

## 3. STAGE 2 — AGENT-BROWSER (validation / visualisation)

Default validator. Use for: dogfooding, screenshot capture, exploratory QA, click-through flows, simple regression smoke.

**Why agent-browser over Playwright MCP for the default case?** Per project memory: on Ubuntu 26.04, Playwright MCP can't install Chromium reliably; agent-browser ships a bundled browser. It also runs in Vercel-sandbox microVMs for clean-room runs.

**Use the `agent-browser` skill** for every UI-change verification. Output goes under `dogfood-output/<UTC-timestamp>/` as `report.md` + screenshots.

**Mandatory verification gates after every Stitch generation:**
- ✅ Screen renders without console errors.
- ✅ Screenshot captured at the canonical viewport (desktop 1440×900 minimum; add mobile when the storyboard demands it).
- ✅ At least one game-relevant action exercised (submit an attack, beat a card, stop defending) and its result captured.

---

## 4. STAGE 3 — PLAYWRIGHT MCP + SKILLS (complex eval)

Reach for Playwright **only** when the case demands what agent-browser can't cleanly do:

- Multi-tab / multi-context scenarios (hot-seat pass-and-play simulation across two viewports).
- Network interception / mock injection (testing the WebSocket reconnection path at PRP 3 M14+).
- Trace recording for performance analysis (card-flip animation budget).
- Programmatic accessibility-tree assertions.
- Long-running e2e suites with reporters.

**Tools:** `mcp__plugin_playwright_playwright__*` and the `webapp-testing` skill.

**Do NOT** use Playwright when agent-browser suffices — the heavier setup makes change loops slow.

---

## 5. Hard prohibitions

- ❌ **Hand-writing screens** — every screen has a Stitch origin in `docs/SCREENS/`.
- ❌ **Inventing design tokens** — read `.stitch/DESIGN.md` and apply via `mcp__stitch__apply_design_system`. If a token doesn't exist, regenerate the design system first.
- ❌ **Claiming a UI change is "done" without `agent-browser` evidence** under `dogfood-output/`. Type-check + unit-test passing ≠ UI works.
- ❌ **Re-implementing rules in the UI.** The UI must consume `@cardshed/core` for every legality check, legal-action enumeration, and view projection. If a UI helper duplicates a rule function, delete the helper and call the core.
- ❌ **Mixing UI frameworks.** React + Tailwind v4 + Radix + framer-motion + Zustand + TanStack Query + Immer. No Material UI, no shadcn-without-Stitch-mapping, no PixiJS (cards are DOM, not canvas).
- ❌ **Mocking the UI surface in screenshot tests** — capture from the running container.

---

## 6. Decision flow (when uncertain)

```
UI task arrives
   │
   ├─ Vague request ("make the table feel less cramped")
   │     → enhance-prompt → stitch-design
   │
   ├─ New screen needed
   │     → stitch-design (with all 4 mandatory inputs)
   │
   ├─ Design system feels incoherent across screens
   │     → design-md → mcp__stitch__create_design_system → apply across all screens
   │
   ├─ Many screens to evolve together
   │     → stitch-loop
   │
   ├─ Verify a change works in browser
   │     → agent-browser → capture screenshot → save under dogfood-output/
   │
   ├─ Need multi-tab / network mock / a11y tree / trace
   │     → playwright MCP + webapp-testing skill
   │
   └─ Just code, no visual change?
         → still verify with agent-browser; UI plumbing without proof = unverified
```

---

## 7. Acceptance checklist (every UI PR — applies from PRP 3 M1)

- [ ] Screen spec referenced from `PRPs/cardshed-03-experience-prp.md` §B
- [ ] Stitch mockup under `docs/SCREENS/<screen>.md` with provenance (which prompt, which design-system version)
- [ ] Screen built against the current `.stitch/DESIGN.md`
- [ ] UI consumes `@cardshed/core` for every rule (no rule re-implementation)
- [ ] `agent-browser` run under `dogfood-output/<timestamp>/` with `report.md` + screenshots
- [ ] If complex behaviour: Playwright trace under `dogfood-output/<timestamp>/traces/`
- [ ] No new design tokens introduced outside `.stitch/DESIGN.md`
- [ ] Lint, type-check, unit-tests green (core + ui both)

---

## 8. Why this rule exists

Three failure modes we explicitly prevent:

1. **Bespoke-UI drift** — once a developer hand-rolls one screen, the design system fractures. Every screen Stitch-touched stays coherent.
2. **Unverified-frontend claims** — "tests pass" doesn't mean the screen works. Real-browser evidence under `dogfood-output/` is the only proof we accept.
3. **Rule duplication** — the UI is *tempted* to re-implement "is this card legal?" for ergonomic reasons. That temptation is how clients and servers desync. The engine API is the single source of truth.

This is policy, not preference. If you find a real reason the pipeline can't apply, document it in `docs/DECISIONS/` and propose a rule amendment — don't bypass.
