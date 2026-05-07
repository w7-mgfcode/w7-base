# UI Design Workflow

> **Rule:** When the task involves UI/frontend design, generation, iteration, or visual review, you **MUST** use the dedicated skills and MCP tools. Do not hand-write UI code from scratch when these tools apply.

## Required Toolchain (in order of typical use)

1. **Skills** — invoke via the `Skill` tool:
   - `enhance-prompt` — turn vague UI ideas into Stitch-optimized prompts (specificity, UI/UX keywords, design system context).
   - `stitch-design` — unified entry point for Stitch work (prompt enhancement → design system synthesis → screen generation/edit).
   - `design-md` — analyze Stitch projects and synthesize a `.stitch/DESIGN.md` semantic design system.
   - `stitch-loop` — iterative baton-passing loop for autonomous Stitch builds.
   - `frontend-design` — distinctive, production-grade frontend code (avoids generic AI aesthetics).
   - `shadcn-ui` — when the target uses shadcn/ui components.
   - `webapp-testing` — Playwright-based local app verification (frontend behavior, screenshots, browser logs).

2. **MCP servers** — call via the `mcp__*` tools:
   - `mcp__stitch__*` — `create_project`, `generate_screen_from_text`, `edit_screens`, `generate_variants`, `apply_design_system`, `create_design_system`, etc.
   - `mcp__plugin_playwright_playwright__*` — browser automation for verification (`browser_navigate`, `browser_snapshot`, `browser_take_screenshot`, `browser_click`, `browser_fill_form`, ...).
   - `mcp__claude_ai_Excalidraw__*` — when wireframes or visual diagrams are needed.

3. **Stitch** — the design-system-aware screen generator. Drive it through `stitch-design` (skill) or `mcp__stitch__*` (direct MCP). Use it for:
   - Initial screen generation from text prompts.
   - Editing existing screens.
   - Generating variants.
   - Applying a unified design system across screens.

4. **agent-browser** (skill) — browser automation CLI for AI agents. Use for:
   - Dogfooding / exploratory QA on the running UI.
   - Form-fill, click-through, and login flows.
   - Capturing screenshots and console logs to verify a change works in a real browser.
   - Preferred over any built-in browser tooling.

## Decision Flow

```
UI task arrives
   │
   ├─ Vague idea / one-line request?
   │     → enhance-prompt → stitch-design
   │
   ├─ Need new screens or visual variants?
   │     → stitch-design (or mcp__stitch__generate_screen_from_text)
   │
   ├─ Need a coherent design system (.stitch/DESIGN.md)?
   │     → design-md → mcp__stitch__create_design_system
   │
   ├─ Implementing the actual frontend code?
   │     → frontend-design (+ shadcn-ui if applicable)
   │
   └─ Verifying the running UI?
         → webapp-testing (local, scripted)
         → agent-browser (exploratory, real-browser)
         → mcp__plugin_playwright_playwright__* (low-level steps)
```

## Hard Requirements

- **Never** hand-roll UI code without first checking whether `stitch-design` or `frontend-design` applies.
- **Never** claim a UI change is complete without exercising it in a real browser via `agent-browser`, `webapp-testing`, or Playwright MCP. Type-check + tests passing ≠ UI works.
- **Never** invent design tokens, spacing, or component patterns when a `.stitch/DESIGN.md` exists — read it first and apply it via `mcp__stitch__apply_design_system`.

## What Counts as "UI Designing"

Any of:
- Creating or editing pages, components, layouts, or screens.
- Designing visual hierarchy, typography, spacing, color systems.
- Building or modifying a frontend (React, Vue, Svelte, plain HTML/CSS).
- Iterating on look-and-feel based on user feedback.
- Producing wireframes, mockups, or design specs.

If the task is *only* backend or non-visual logic, this rule does not apply.
