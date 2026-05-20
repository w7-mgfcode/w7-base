# UI Design Pipeline — MANDATORY for ll-RELIQUARY

> **EPIC RULESET — load-bearing.** Reliquary is a design-driven product. The interface IS the game. There is no hand-rolled UI escape hatch.

This rule strengthens the root `.claude/rules/ui-design.md`. Where they conflict, **this file wins** inside `@lab/ll-RELIQUARY/`.

---

## 1. The Pipeline (every UI change goes through it)

```
  ┌──────────────┐    ┌──────────────────┐    ┌─────────────────┐
  │  IDEA        │ →  │  STITCH          │ →  │  AGENT-BROWSER  │
  │  (storyboard │    │  (skill + MCP    │    │  (Vercel-based  │
  │   wireframe) │    │   generation)    │    │   validation)   │
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

1. Premise (`STORYBOARD.md` §1).
2. The relevant user journey (`STORYBOARD.md` §2.A / §2.B / §2.C).
3. The pre-Stitch wireframe (`STORYBOARD.md` §5).
4. The current `.stitch/DESIGN.md` (so output stays coherent).

**Output destination:**
- Screen mockups → `docs/SCREENS/<screen-slug>.md` (+ exported assets if Stitch returns them).
- Design system updates → `.stitch/DESIGN.md` (only `stitch-design` / `design-md` write here).

---

## 3. STAGE 2 — AGENT-BROWSER (validation / visualisation)

Default validator. Use for: dogfooding, screenshot capture, exploratory QA, login/click-through flows, simple regression smoke.

**Why agent-browser over Playwright MCP for the default case?** Per project memory: on Ubuntu 26.04, Playwright MCP can't install Chromium reliably; agent-browser ships a bundled browser. It also runs in Vercel-sandbox microVMs for clean-room runs.

**Use the `agent-browser` skill** for every UI-change verification. Output goes under `dogfood-output/<UTC-timestamp>/` as `report.md` + screenshots.

**Mandatory verification gates after every Stitch generation:**
- ✅ Screen renders without console errors.
- ✅ Screenshot captured at the canonical viewport (desktop 1440×900 minimum; add mobile when the storyboard demands it).
- ✅ At least one user-action exercised (click, type, drag) and its result captured.

---

## 4. STAGE 3 — PLAYWRIGHT MCP + SKILLS (complex eval)

Reach for Playwright **only** when the case demands what agent-browser can't cleanly do:

- Multi-tab / multi-context scenarios.
- Network interception / mock injection.
- Trace recording for performance analysis.
- Programmatic accessibility-tree assertions.
- Long-running e2e suites with reporters.

**Tools:** `mcp__plugin_playwright_playwright__*` and the `webapp-testing` skill.

**Do NOT** use Playwright when agent-browser suffices — the heavier setup makes change loops slow.

---

## 5. Hard prohibitions

- ❌ **Hand-writing screens** — every screen has a Stitch origin in `docs/SCREENS/`.
- ❌ **Inventing design tokens** — read `.stitch/DESIGN.md` and apply via `mcp__stitch__apply_design_system`. If a token doesn't exist, regenerate the design system first.
- ❌ **Claiming a UI change is "done" without `agent-browser` evidence** under `dogfood-output/`. Type-check + unit-test passing ≠ UI works.
- ❌ **Mixing UI frameworks** — React + Tailwind v4 + Radix + framer-motion + PixiJS. No Material UI, no shadcn-without-Stitch-mapping, no Phaser.
- ❌ **Mocking the UI surface in screenshot tests** — capture from the running container.

---

## 6. Decision flow (when uncertain)

```
UI task arrives
   │
   ├─ Vague request ("make a card detail page nicer")
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

## 7. Acceptance checklist (every UI PR)

- [ ] Wireframe in `STORYBOARD.md` §5
- [ ] Stitch mockup under `docs/SCREENS/<screen>.md` with provenance (which prompt, which design-system version)
- [ ] Screen built against the current `.stitch/DESIGN.md`
- [ ] `agent-browser` run under `dogfood-output/<timestamp>/` with `report.md` + screenshots
- [ ] If complex behaviour: Playwright trace under `dogfood-output/<timestamp>/traces/`
- [ ] No new design tokens introduced outside `.stitch/DESIGN.md`
- [ ] Lint, type-check, unit-tests green

---

## 8. Why this rule exists

Two failure modes we explicitly prevent:

1. **Bespoke-UI drift** — once a developer hand-rolls one screen, the design system fractures. Every screen Stitch-touched stays coherent.
2. **Unverified-frontend claims** — "tests pass" doesn't mean the screen works. Real-browser evidence under `dogfood-output/` is the only proof we accept.

This is policy, not preference. If you find a real reason the pipeline can't apply, document it in `BRAINSTORM.md` §7 (decision log) and propose a rule amendment — don't bypass.
