# S03 — Account Claim (passwordless, skippable)

**Journey:** A · beat 3 (soft retention — "keep your shelf?")
**Status:** 🟡 **Stitch-pending.** Wireframe + prompt are locked; the `generate_screen_from_text` call timed out during the 2026-05-20 session. **Action**: re-run `Skill: stitch-design` against this doc.

---

## Mockup

> 🟡 _No Stitch mockup committed yet._
> The wireframe in `STORYBOARD.md §5` and the prompt below define the screen exactly; once Stitch returns the screen, save assets under `.stitch/designs/S03-account-claim.{html,png}`.

**When generated, asset paths:**
- HTML: `.stitch/designs/S03-account-claim.html`
- Screenshot: `.stitch/designs/S03-account-claim.png`

---

## Wireframe provenance

Derived from **`STORYBOARD.md` §5 → S03** (Account Claim wireframe, dated 2026-05-20).

Source inputs for Stitch:
- Premise: `STORYBOARD.md` §1
- Aesthetic anchor: `BRAINSTORM.md` §3
- Retention design: `BRAINSTORM.md` §3 ("Daily relic is the heartbeat. No streaks. Opt-in retention.")
- Account strategy: `ARCHITECTURE.md` §3 (device-key first, email optional later)

---

## What it must contain

(authoritative spec — reproduce on re-generation)

### Background
Shelf with the first relic now visible in slot #3, dimmed 50% with warm-tinted scrim.

### Modal (centered, ~720px × ~540px — slightly shorter than S02)
- Surface: `--color-surface-raised` (#15130f)
- Border: 1px `--color-accent` at 40% opacity
- Radius: `--radius-card` (14px)
- Padding: 48px internal

### Inside the modal (vertical stack, center-aligned, generous breathing room)

1. Small gold ✦ glyph (24px), `--color-accent`.

2. **12px gap.**

3. **Headline** (Cormorant Garamond, `--color-ink`, 40px, centered):
   - *"Keep your shelf?"* — a question, not a command.

4. Thin gold rule (40px wide, `--color-accent`).

5. **24px gap.**

6. **Reassurance copy** (Inter, `--color-ink`, 16px, centered, 2 lines):
   - *"This shelf is yours."*
   - *"Save it to this device, or carry it across sessions."*

7. **40px gap.**

8. **Primary CTA (full-width pill)**:
   - `--color-accent` fill, `--color-surface` text.
   - Label: *"Keep on this device"* — Cormorant Garamond small-caps + 2px letter-spacing.
   - Tail: *"(default)"* in Space Mono italic, smaller, lower contrast, right-aligned within the button.

9. **12px gap.**

10. **Secondary CTA (full-width pill)**:
    - Transparent fill. 1.5px hairline `--color-ink` outline at 70% opacity. `--color-ink` text.
    - Label: *"Add an email  (optional)"* — Inter, normal weight.

11. **24px gap with "─ or ─" divider** (Space Mono, `--color-ink-muted` at 60% opacity).

12. **Tertiary action — text link only** (centered):
    - `--color-ink-muted`, Inter italic, 15px.
    - *"[ Skip — I'll decide later ]"*

13. **40px gap.**

14. **Trust hint footer** (Space Mono, `--color-ink-muted` at 60% opacity, 12px, centered, 2 lines):
    - *"no passwords. no tracking."*
    - *"we use a device key stored only in your browser."*

---

## Hard prohibitions (this screen specifically)

These tokens must **not** appear anywhere in S03:
- The words *"Sign up"*, *"Register"*, *"Create an account"*
- Checkmark icons
- *"Already have an account?"* link
- Security padlock icons
- *"or sign in with Google / Apple / GitHub"* social-auth row

The frame is *"keep what you have"*, never *"join a service"*.

---

## Motion (animation spec)

| Phase | Token | Duration | Notes |
|-------|-------|----------|-------|
| Scrim fade-in | `--motion-fast` | 160ms | After S02 dismisses |
| Modal slide-up | `--motion-modal` | 220ms | cubic-bezier(0.2, 0.8, 0.2, 1) |
| Email field expand (when secondary clicked) | `--motion-base` | 240ms | height-grow + cross-fade |
| `prefers-reduced-motion` fallback | `--motion-cross-fade` | 240ms | modal cross-fades, no slide |

---

## Interactive contract (when implemented)

| Element | Behavior |
|---------|----------|
| `[ Keep on this device (default) ]` | Primary. Generates device-key UUIDv4 client-side, `POST /session`, sets long-lived session cookie. Modal closes. No email required. |
| `[ Add an email (optional) ]` | Secondary. Expands inline into an email field + magic-link send. Does **not** block the primary path. |
| `[ Skip — I'll decide later ]` | Tertiary. Closes modal. Relic persists locally only; next visit shows a subtle banner *"your shelf is on this device only"*. |
| Esc | Maps to Skip (matches tertiary). |
| Focus order | Primary → Secondary → Tertiary → Close. |
| Trust hint | Announced via `aria-describedby` at modal open. |

---

## Acceptance gates for implementation

- [ ] Stitch mockup committed (currently `🟡 pending`).
- [ ] Built against `.stitch/DESIGN.md` tokens only.
- [ ] WCAG AA verified.
- [ ] **Hard-prohibition tokens absent** — review the prohibition list above before merging.
- [ ] Email path does not block the primary "keep on this device" path.
- [ ] agent-browser screenshot saved under `dogfood-output/<UTC>/S03-rendered.png`.

---

## Re-generation prompt

When Stitch is responsive:

```
Modal overlay for "Reliquary" — the soft account-claim moment. Continuation of the
existing Reliquary landing-page and reveal-modal styling: surface #0b0a08, raised
#15130f, ink parchment #f4ead5, ink-muted #c2b893, antique gold #c89f3c. Cormorant
Garamond display + Inter body + Space Mono labels. Museum × quiet-occult.

BACKGROUND: shelf with first relic in slot #3 visible, dimmed 50%, warm scrim.

MODAL (centered ~720×540, surface-raised, 14px radius, hairline gold border, 48px
padding) — stack:
  1. Gold ✦ glyph (24px).
  2. 12px gap.
  3. Headline "Keep your shelf?" — Cormorant Garamond, parchment, 40px, centered.
     A QUESTION not a command.
  4. 40px gold rule.
  5. 24px gap.
  6. Reassurance, Inter parchment 16px, 2 lines:
     "This shelf is yours."
     "Save it to this device, or carry it across sessions."
  7. 40px gap.
  8. Primary CTA — full-width gold pill: "Keep on this device" (Cormorant
     small-caps) + " (default)" in Space Mono italic at lower contrast.
  9. 12px gap.
  10. Secondary CTA — full-width transparent pill, hairline parchment outline:
      "Add an email  (optional)" (Inter).
  11. 24px gap, "─ or ─" divider in Space Mono worn parchment.
  12. Tertiary text link: "[ Skip — I'll decide later ]" (Inter italic muted).
  13. 40px gap.
  14. Trust hint, Space Mono worn parchment 60% opacity, 2 lines:
      "no passwords. no tracking."
      "we use a device key stored only in your browser."

MUST AVOID: "Sign up", "Register", "Create an account", checkmark icons,
"Already have an account?", security padlock icons, social-auth rows.

TONE: Generous, not pushy. Email offered, not required. "Skip" is dignified —
no red, no warning, no guilt-trip. The trust hint is literal plain language.
WCAG AA throughout.
```
