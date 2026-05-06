---
version: alpha
name: KnowRAG Operator
description: >
  Local-first knowledge-base + RAG operator console. Dark-only, dense-data tooling
  aesthetic. Single emerald accent. Hairline borders. Tabular numerics. JetBrains Mono
  for IDs and code-like strings.

colors:
  surface-0: "#0a0a0f"
  surface-1: "#111118"
  surface-2: "#1a1a24"
  fg: "#e4e4ed"
  fg-muted: "#8888a0"
  fg-subtle: "#555570"
  hairline: "#2a2a3a"
  hairline-strong: "#3a3a50"
  accent: "#10b981"
  accent-strong: "#059669"
  status-ok: "#10b981"
  status-warn: "#f59e0b"
  status-err: "#ef4444"
  status-info: "#3b82f6"

typography:
  display:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: -0.01em
  h1:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: 600
    lineHeight: 1.3
  h2:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: 600
    lineHeight: 1.4
  body:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.5
  body-sm:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: 400
    lineHeight: 1.45
  caption:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: 400
    lineHeight: 1.4
  mono:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: 400
    lineHeight: 1.5

rounded:
  control: 0.375rem
  card: 0.5rem
  modal: 0.75rem
  full: 9999px

spacing:
  xs: 4px
  sm: 8px
  md: 12px
  lg: 16px
  xl: 24px
  2xl: 32px

components:
  button-primary:
    backgroundColor: "{colors.accent}"
    textColor: "#ffffff"
    typography: "{typography.body-sm}"
    rounded: "{rounded.control}"
  button-secondary:
    backgroundColor: "{colors.surface-2}"
    textColor: "{colors.fg}"
    typography: "{typography.body-sm}"
    rounded: "{rounded.control}"
  button-ghost:
    backgroundColor: "{colors.surface-0}"
    textColor: "{colors.fg-muted}"
    typography: "{typography.body-sm}"
    rounded: "{rounded.control}"
  card:
    backgroundColor: "{colors.surface-1}"
    textColor: "{colors.fg}"
    rounded: "{rounded.card}"
  card-selected:
    backgroundColor: "{colors.surface-1}"
    textColor: "{colors.fg}"
    rounded: "{rounded.card}"
  badge:
    backgroundColor: "{colors.surface-2}"
    textColor: "{colors.fg-muted}"
    typography: "{typography.caption}"
    rounded: "{rounded.full}"
  input:
    backgroundColor: "{colors.surface-2}"
    textColor: "{colors.fg}"
    typography: "{typography.body}"
    rounded: "{rounded.control}"
  dialog:
    backgroundColor: "{colors.surface-1}"
    textColor: "{colors.fg}"
    rounded: "{rounded.modal}"
---

# KnowRAG Operator Design System

## Overview

KnowRAG is an **operator console**, not a consumer app. Every visual decision favors
information density, scannability, and unambiguous status communication over
playfulness or whitespace. The aesthetic borrows from terminal multiplexers and
network operations dashboards: dark surfaces, single bright accent, monospace for
identifiers, hairline borders that delineate structure without competing with content.

The single user is a power operator who cares about: how many sources are healthy,
which crawls failed, what was searched, what got returned. The UI should feel like
a tool you live inside, not a brochure you visit.

## Colors

A flat dark palette with three surface tiers and a single emerald accent.

- **Surface 0 (#0a0a0f):** the page background, behind everything.
- **Surface 1 (#111118):** card and panel background; the substrate for grouped content.
- **Surface 2 (#1a1a24):** elevated background; hover states, input fields, selected rows.
- **Foreground (#e4e4ed):** primary text. Reserved for content the operator reads to make decisions.
- **Foreground muted (#8888a0):** metadata, captions, secondary labels.
- **Foreground subtle (#555570):** placeholders, disabled text, inactive icons.
- **Hairline (#2a2a3a):** the default 1px border. Used for card edges and dividers.
- **Hairline strong (#3a3a50):** hover/active border state.
- **Accent (#10b981):** the only chromatic color in the system. Used for primary
  actions, active states, and OK status. Never decorative.
- **Status warn / err / info:** reserved for genuine alerts. Borders and text
  colors over a tinted background — never full-fill, which fights scannability.

Contrast: foreground over surface-0 is ~14:1 (well above WCAG AA 4.5:1).
Accent over surface-0 passes 3:1 for UI components.

## Typography

Two fonts: **Inter** for UI, **JetBrains Mono** for identifiers, hashes, URLs, and
log-like content. Display sizes are kept small — operator UIs reward density.
Tabular numerics (`tnum`) are enabled globally so columns of numbers align.

## Layout & Spacing

8px base scale. Cards pad 16px (`lg`). List rows are tight (28-32px). Section
gutters are 16px. Avoid 24px+ gutters — they signal "marketing site," not "tool."

## Shapes

Three radii — control (small, for buttons/inputs), card (medium, for panels),
modal (large, for dialogs). No hard corners, no fully-rounded cards. Pill-shape
(`full`) reserved for filter chips and badges.

## Components

Every primitive composes the tokens above. Specific component → token mapping is
in the YAML front matter. Notable conventions:

- **Buttons** have variant (primary/secondary/ghost/destructive) and size (sm/md/lg).
  Primary uses solid accent. Ghost uses transparent surface-0.
- **Cards** have a `selected` state that applies a 5%-tinted accent background and
  accent-colored border.
- **Dialogs** use Radix Dialog primitive under the hood for focus trap, ARIA, and
  Esc handling. Custom skin via tokens.
- **Tabs** use Radix Tabs for arrow-key navigation between triggers.

## Do's and Don'ts

**Do**

- Use `font-mono` for source IDs, URLs, hashes, and command snippets.
- Use `tabular-nums` for any numeric column.
- Use the accent color for *one* primary action per view.
- Keep card padding consistent at 16px (`lg`).

**Don't**

- Use shadows for elevation. Use the surface tier system instead.
- Introduce a second chromatic color for "category." Use `surface-2` borders or
  monospace prefixes instead.
- Add gradients, glassmorphism, or "glow" effects.
- Use full-color status fills (`bg-status-err` solid). Use tinted bg + colored
  text + colored border instead.
