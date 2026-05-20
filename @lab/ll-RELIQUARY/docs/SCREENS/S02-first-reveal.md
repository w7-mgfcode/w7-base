# S02 — First Reveal

**Journey:** A · beat 2 (the wonder moment — first artifact flips into existence)
**Status:** 🟡 **Stitch-pending.** Wireframe + prompt are locked; the `generate_screen_from_text` call timed out twice during the 2026-05-20 session (S01 generated normally; S02/S03 jobs appear not to have queued). **Action**: re-run `Skill: stitch-design` against this doc in a future session.

---

## Mockup

> 🟡 _No Stitch mockup committed yet._
> The wireframe in `STORYBOARD.md §5` and the prompt below define the screen exactly; once Stitch returns the screen, save assets under `.stitch/designs/S02-first-reveal.{html,png}` and replace this placeholder.

**When generated, asset paths:**
- HTML: `.stitch/designs/S02-first-reveal.html`
- Screenshot: `.stitch/designs/S02-first-reveal.png`

---

## Wireframe provenance

Derived from **`STORYBOARD.md` §5 → S02** (First Reveal wireframe, dated 2026-05-20).

Source inputs for Stitch:
- Premise: `STORYBOARD.md` §1
- Aesthetic anchor: `BRAINSTORM.md` §3 ("modern-museum × quiet-occult")
- Voice: `BRAINSTORM.md` §3 (curatorial-mythic — "Print 1 of 7", "one of seven. always remembered.")
- Design system: `.stitch/DESIGN.md` (anchor tokens)

---

## What it must contain

(authoritative spec — reproduce on re-generation)

### Background
Shelf from S01 visible but dimmed to 60% with a warm-tinted scrim (`#0b0a08` at 60% opacity + 2% amber bias). **Not** pure black scrim.

### Modal (centered, ~720px × ~640px)
- Surface: `--color-surface-raised` (#15130f)
- Border: 1px `--color-accent` at 40% opacity
- Radius: `--radius-card` (14px)
- Padding: 48px internal
- Halo: 4–8px outside, `--color-accent` at 8%

### Inside the modal (vertical stack, center-aligned)

1. **Artifact card** ~280×392px (5:7 portrait):
   - 14px radius, 1.5px `--color-accent` border, parchment-tinted inner wash.
   - **Top 70%**: illustrated warm-ember-glow on parchment (ink-and-wash style; **never** photo-real, **never** pixel art).
   - Hairline gold divider.
   - **Bottom 30%**:
     - Title: *"EMBER OF FIRST LIGHT"* — Cormorant Garamond small-caps, +2px letter-spacing, `--color-accent`, centered.
     - 40px gold rule.
     - Edition: *"Print 1 of 7"* — Space Mono italic, small-caps, `--color-ink-muted`.
   - Tilt: card sits at ~6° on Y-axis suggesting mid-3D-flip motion.

2. **32px gap.**

3. **Lore line**: Inter italic, `--color-ink-muted`, 18px, centered, 5–9 words:
   - *"one of seven. always remembered."*

4. **40px gap.**

5. **Primary CTA**: pill button, `--color-accent` fill, `--color-surface` text:
   - Label: *"Place on shelf  →"* — Cormorant Garamond small-caps + right-arrow icon.

6. **12px gap.**

7. **Dismiss hint**: Space Mono italic, `--color-ink-muted` at 50% opacity, 13px, centered:
   - *"(esc to dismiss)"*

---

## Motion (animation spec for implementation)

| Phase | Token | Duration | Notes |
|-------|-------|----------|-------|
| Scrim fade-in | `--motion-fast` | 160ms | ease-out |
| Modal entry (slide-up) | `--motion-modal` | 220ms | cubic-bezier(0.2, 0.8, 0.2, 1) |
| Card 3D flip | `--motion-reveal` | 720ms | cubic-bezier(0.2, 0.8, 0.2, 1) |
| Place-on-shelf (card scales into slot #3) | `--motion-modal` × 1.5 | 320ms | glow transfers from slot #3 to slot #4 |
| `prefers-reduced-motion` fallback | `--motion-cross-fade` | 240ms | flat card, cross-fade modal |

---

## Interactive contract (when implemented)

| Element | Behavior |
|---------|----------|
| `[ Place on shelf → ]` | Closes modal; card animates into slot #3; slot's active glow transfers to slot #4. Opens S03 after a 320ms beat. |
| `Esc` / click outside | Defers placement; relic is stored client-side ("pending placement") and reappears on next visit. |
| Initial focus | Auto-set on the CTA, not the card. |
| `aria-labelledby` | Points to the artifact title. |
| `aria-live` | Polite — announces "Ember of First Light. Print 1 of 7. Place on shelf." on open. |

---

## Acceptance gates for implementation

- [ ] Stitch mockup committed (currently `🟡 pending`).
- [ ] Built against `.stitch/DESIGN.md` tokens only.
- [ ] WCAG AA verified.
- [ ] 720ms flip uses CSS `transform: rotateY()` + `backface-visibility: hidden` (not a video, not a sprite).
- [ ] `prefers-reduced-motion` fallback uses cross-fade.
- [ ] agent-browser screenshot saved under `dogfood-output/<UTC>/S02-rendered.png`.

---

## Re-generation prompt

When Stitch is responsive, re-invoke `Skill: stitch-design` with the prompt below (or the longer version preserved in this session's chat history):

```
Modal overlay for "Reliquary" — the first-artifact reveal. Same museum × quiet-occult
palette as the Reliquary landing page in this project: surface #0b0a08, raised #15130f,
ink parchment #f4ead5, ink muted #c2b893, antique gold #c89f3c. Cormorant Garamond
display + Inter body + Space Mono labels.

BACKGROUND: shelf from the landing page, dimmed 60% behind a warm-tinted scrim
(not pure black).

MODAL (centered ~720×640, surface-raised #15130f, 14px radius, hairline gold border,
48px padding, faint outer warm halo) — stack:
  1. Artifact card 280×392 (5:7): parchment inner, 1.5px gold border. Top 70% is a
     stylized ink-and-wash ember-glow illustration on parchment. Hairline gold divider.
     Bottom 30%: title "EMBER OF FIRST LIGHT" (Cormorant Garamond small-caps, gold),
     40px gold rule, edition "Print 1 of 7" (Space Mono italic). Card tilted ~6° on Y axis.
  2. 32px gap.
  3. Lore line, Inter italic worn parchment 18px: "one of seven. always remembered."
  4. 40px gap.
  5. Primary CTA: gold pill "Place on shelf →" (Cormorant small-caps).
  6. 12px gap.
  7. Dismiss hint, Space Mono italic at 50% opacity: "(esc to dismiss)"

TONE: a reveal in a hushed room. Patient. Dignified. No fanfare, no glow-bomb.
The card feels printed, not generated. WCAG AA.
```
