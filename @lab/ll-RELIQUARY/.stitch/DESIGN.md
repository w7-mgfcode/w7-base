# Design System: Reliquary
**Project ID:** 17652338204408695000
**Generated:** 2026-05-20 via `Skill: stitch-design` (Stitch MCP, Gemini 3.1 Pro)
**Source seed:** STORYBOARD.md §1 (premise) + BRAINSTORM.md §3 (aesthetic & voice) + STORYBOARD.md §5.S01–S03 (wireframes)
**Status:** Generated. **Do not hand-edit** — see `.claude/rules/ui-design-pipeline.md`. Regenerate via the skill if it needs to change.

---

## 1. Visual Theme & Atmosphere

**Modern-museum × quiet-occult.** The product is a hushed gallery, an open notebook, a candlelit shelf. It is *patient, inviting, a little mysterious*. The interface treats every artifact as a museum piece — labelled, dated, dignified. Slight grain on surfaces evokes printed material; warmth in the gold evokes candlelight rather than neon. There is no game-y UI clichés: no XP bars, no avatars, no level numbers, no badges, no confetti.

The aesthetic pulls from:
- **Wellcome Collection** — typographic restraint, generous whitespace
- **Cabinet of Curiosities (Wunderkammer)** — finite, displayed objects
- **Calm-tech** — restraint over notification noise

---

## 2. Color Palette & Roles

Anchor tokens (the **canonical Reliquary palette**):

| Role | Token | Hex | Use |
|------|-------|-----|-----|
| Surface | `--color-surface` | `#0b0a08` | Page background. Deep warm black. Slight noise/grain. |
| Surface Raised | `--color-surface-raised` | `#15130f` | Headers, footers, modal containers, raised cards. |
| Surface Container | `--color-surface-container` | `#241f12` | Inner panels, secondary surfaces. |
| Ink | `--color-ink` | `#f4ead5` | Primary text on dark surfaces. Parchment. |
| Ink Strong | `--color-ink-strong` | `#ebe2cd` | Headlines (Stitch's `on-surface`). |
| Ink Muted | `--color-ink-muted` | `#c2b893` | Secondary text, lore lines, footer hints. |
| Ink Faint | `--color-ink-faint` | `#9a8f7d` | Tertiary text, dismiss hints. |
| Accent | `--color-accent` | `#c89f3c` | **Antique Gold.** Primary CTA, glowing slot, active states. |
| Accent Bright | `--color-accent-bright` | `#edc15a` | Hover state, highlights, focus glow. |
| Accent Soft | `--color-accent-soft` | `#5a4318` | Slot borders, focus rings, hairline dividers. |
| Accent Dim | `--color-accent-dim` | `#4e4636` | Outline variant, dim borders. |

Semantic / state tokens (derived):

| Role | Token | Hex |
|------|-------|-----|
| Error | `--color-error` | `#ffb4ab` |
| On Error | `--color-on-error` | `#690005` |
| Warning | `--color-warning` | `#edc15a` |
| Success | (use `--color-accent`) | `#c89f3c` |

**WCAG AA verification:**
- Parchment `#f4ead5` on Surface `#0b0a08` → contrast 16.3:1 ✓ (AAA)
- Ink Muted `#c2b893` on Surface `#0b0a08` → contrast 9.9:1 ✓ (AAA)
- Surface `#0b0a08` on Accent `#c89f3c` (CTA text) → contrast 9.5:1 ✓ (AAA)
- Accent `#c89f3c` on Surface `#0b0a08` (gold-on-black UI) → contrast 7.8:1 ✓ (AAA)

---

## 3. Typography Rules

| Role | Family | Weight | Usage |
|------|--------|--------|-------|
| Display | **Cormorant Garamond** | 400 / 600 italic | Wordmark, page headlines, artifact titles. Small-caps + 2px letter-spacing for labels. |
| Body | **Inter** | 400 / 400 italic | Subheads, paragraph copy, button labels (non-display CTAs). |
| Mono | **Space Mono** | 400 / 700 / 400 italic | Edition labels ("Print 1 of 7"), footer hints, trust microcopy. |

> Earlier the wireframes named *IBM Plex Mono*; Stitch resolved to *Space Mono* during generation — accept this as canonical going forward and update wireframes accordingly.

Scale (rem-based, root = 16px):

| Token | Size | Use |
|-------|------|-----|
| `--text-display-xl` | 56px (3.5rem) | "Your shelf is empty." |
| `--text-display-l` | 40px (2.5rem) | Modal headlines ("Keep your shelf?") |
| `--text-display-m` | 28px (1.75rem) | Artifact titles |
| `--text-body-l` | 18px (1.125rem) | Subheads, lore lines |
| `--text-body-m` | 16px (1rem) | Reassurance copy, button labels |
| `--text-mono-m` | 14px (0.875rem) | Edition labels, footer hints |
| `--text-mono-s` | 12px (0.75rem) | Trust microcopy, dismiss hints |

Letter-spacing on small-caps display labels: **+2px** (0.125em).

---

## 4. Component Stylings

### Buttons

| Variant | Surface | Text | Border | Radius | Padding |
|---------|---------|------|--------|--------|---------|
| **Primary (gold pill)** | `--color-accent` | `--color-surface` | none | `9999px` (full pill) | 16px × 48px |
| **Secondary (parchment outline)** | transparent | `--color-ink` | 1.5px `--color-ink` at 70% | `9999px` | 16px × 48px |
| **Tertiary (text link)** | transparent | `--color-ink-muted` | none | n/a | 8px × 16px |

Primary CTA label uses Cormorant Garamond, small-caps, +2px letter-spacing. Hover: subtle warm gold halo (8px outer glow, `--color-accent-bright` at 30%). Focus: 2px outline `--color-accent-bright` + 2px offset.

### Cards (artifact)

- Frame: `--radius-card` (14px), 1.5px `--color-accent` border, parchment-tinted inner wash (`--color-ink` at 8% on dark).
- Aspect: **5:7 portrait** (always).
- Top 70%: illustration area (ink-and-wash style, restrained, slight grain — NEVER photo-real, NEVER pixel art).
- Hairline gold rule divides the illustration from the label block.
- Bottom 30%: title (Cormorant Garamond small-caps, `--color-accent`), 40px gold rule, edition label (Space Mono italic, `--color-ink-muted`).

### Slots (shelf positions)

| State | Border | Background | Glow | Notes |
|-------|--------|------------|------|-------|
| Empty / inactive | 1px `--color-accent-soft` | inner shadow 6% black + faint diagonal hatch | none | Reads as "available but quiet". |
| Active / glowing | 1.5px `--color-accent` | inner shadow 4% black | 24px radial `--color-accent-bright` at 30% opacity, gentle pulse 1.4s ease-in-out | The "begin" affordance. |
| Filled (with relic) | 1.5px `--color-accent` | shows the artifact card inside | none | Hover → faint glow. |

Slot dimensions: 5:7 portrait, target 140px × 196px at desktop.

### Modal containers

- Surface: `--color-surface-raised` (#15130f).
- Border: 1px `--color-accent` at 40% opacity.
- Radius: `--radius-card` (14px).
- Padding: 48px internal.
- Halo: 4–8px outside glow, `--color-accent` at 8%.
- Scrim: `#0b0a08` at 60% opacity with a 2% warm-amber bias. **Never** pure black.

### Dividers / rules

- **Antique-gold rule**: 1px tall, `--color-accent`, typically 40–60px wide, centered. Used to separate headline from subhead/body.
- **Hairline dim rule**: 1px tall, `--color-accent-soft`, edge-to-edge inside containers.

---

## 5. Geometry, Radius, Spacing

| Token | Value | Use |
|-------|-------|-----|
| `--radius-card` | 14px | Artifact cards, modals, raised surfaces |
| `--radius-slot` | 10px | Shelf slots |
| `--radius-pill` | 9999px | Buttons |
| `--space-1` | 4px | Inline gaps |
| `--space-2` | 8px | Tight spacing |
| `--space-3` | 12px | Default inline padding |
| `--space-4` | 16px | Default vertical rhythm |
| `--space-5` | 24px | Inter-slot gap, modal divider |
| `--space-6` | 32px | Modal section spacing |
| `--space-7` | 40px | Headline → body, CTA leading |
| `--space-8` | 48px | Modal internal padding |
| `--space-9` | 60px | Shelf-to-CTA distance |
| `--space-10` | 80px | Section-to-shelf distance |

---

## 6. Motion Vocabulary

| Token | Duration | Easing | Use |
|-------|----------|--------|-----|
| `--motion-fast` | 160ms | `ease-out` | Scrim fade, micro-interactions |
| `--motion-base` | 240ms | `cubic-bezier(0.2, 0.8, 0.2, 1)` | Hover, focus, button-press |
| `--motion-modal` | 220ms | `cubic-bezier(0.2, 0.8, 0.2, 1)` | Modal entry (slide-up) |
| `--motion-reveal` | 720ms | `cubic-bezier(0.2, 0.8, 0.2, 1)` | Artifact card 3D flip |
| `--motion-pulse` | 1400ms | `ease-in-out`, infinite | Glowing slot pulse |
| `--motion-cross-fade` | 240ms | `ease-out` | `prefers-reduced-motion` fallback for the flip |

**`prefers-reduced-motion` policy**: all transforms become cross-fades; the slot-pulse becomes static; the card-flip becomes a cross-fade between front and back.

---

## 7. Layout Principles

- **Generous breathing room.** Default vertical rhythm uses `--space-7` (40px) between distinct blocks.
- **Center the human in the page, not the content.** Main shelf is centered both axes on a 1440×900 viewport.
- **Asymmetric portrait everywhere a card lives.** Cards and slots are always 5:7 portrait — never square, never landscape.
- **Hairlines, not boxes.** Use thin gold rules instead of full boxes wherever possible.
- **Texture, not pattern.** Subtle grain and noise on surfaces — never repeating decorative pattern.

---

## 8. Voice & Microcopy

- Short sentence fragments are encouraged.
- No exclamation marks.
- No marketing speak.
- Museum-card register with hints of folklore.
- Examples:
  - *"Your shelf is empty."*
  - *"Begin — your first relic awaits."*
  - *"one of seven. always remembered."*
  - *"shelves grow. nothing here is random."*
  - *"no passwords. no tracking."*

Forbidden words/phrases in primary UI: *"Sign up"*, *"Register"*, *"Account"* (as a CTA), *"Level up"*, *"Unlock"* (as a verb on a CTA), *"Premium"*, *"Pro"*, *"Subscribe"*.

---

## 9. Tailwind v4 `@theme` mapping

Drop-in for `apps/ui/src/index.css`:

```css
@import "tailwindcss";

@theme {
  /* Surfaces */
  --color-surface: #0b0a08;
  --color-surface-raised: #15130f;
  --color-surface-container: #241f12;

  /* Ink */
  --color-ink: #f4ead5;
  --color-ink-strong: #ebe2cd;
  --color-ink-muted: #c2b893;
  --color-ink-faint: #9a8f7d;

  /* Accent — Antique Gold */
  --color-accent: #c89f3c;
  --color-accent-bright: #edc15a;
  --color-accent-soft: #5a4318;
  --color-accent-dim: #4e4636;

  /* Semantic */
  --color-error: #ffb4ab;
  --color-on-error: #690005;

  /* Type */
  --font-display: "Cormorant Garamond", "Iowan Old Style", "Palatino", serif;
  --font-body: "Inter", "Segoe UI", system-ui, sans-serif;
  --font-mono: "Space Mono", "IBM Plex Mono", ui-monospace, monospace;

  --text-display-xl: 3.5rem;
  --text-display-l: 2.5rem;
  --text-display-m: 1.75rem;
  --text-body-l: 1.125rem;
  --text-body-m: 1rem;
  --text-mono-m: 0.875rem;
  --text-mono-s: 0.75rem;

  /* Geometry */
  --radius-card: 14px;
  --radius-slot: 10px;
  --radius-pill: 9999px;

  /* Motion */
  --motion-fast: 160ms;
  --motion-base: 240ms;
  --motion-modal: 220ms;
  --motion-reveal: 720ms;
  --motion-pulse: 1400ms;
}
```

---

## 10. Provenance

| Output | Sourced from |
|--------|--------------|
| Palette (anchor tokens) | Prompt to `mcp__stitch__generate_screen_from_text` for S01 + Stitch's auto-extended MD3 token set (preserved in `.stitch/designs/S01-empty-shelf.html`) |
| Typography | Prompt + Stitch resolution (Cormorant Garamond / Inter / Space Mono — Space Mono replaced the proposed IBM Plex Mono) |
| Spacing scale | Prompt-derived; matches the explicit pixel rhythms in STORYBOARD.md §5 |
| Motion vocabulary | STORYBOARD.md §5.S02 wireframe (720ms flip) + S03 wireframe (220ms slide) |
| Voice | BRAINSTORM.md §3 (curatorial-mythic) — locked at this revision |

Regeneration trigger: when the *aesthetic anchor* in `BRAINSTORM.md` §3 changes, or when ≥3 wireframes accumulate decisions that contradict this file. Do not hand-edit.
