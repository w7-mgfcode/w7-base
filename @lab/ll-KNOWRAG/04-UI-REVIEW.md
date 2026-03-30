# Phase 4 — UI Review

**Audited:** 2026-03-29
**Baseline:** abstract standards
**Screenshots:** not captured (no dev server)

---

## Pillar Scores

| Pillar | Score | Key Finding |
|--------|-------|-------------|
| 1. Copywriting | 3/4 | Functional labels but generic in some areas. |
| 2. Visuals | 1/4 | Inline styles used for almost all layout and visual elements. |
| 3. Color | 1/4 | Hardcoded hex values (#007bff, #b42318) instead of design tokens. |
| 4. Typography | 1/4 | Hardcoded pixel values (12px, 14px) throughout components. |
| 5. Spacing | 1/4 | Inconsistent hardcoded spacing (1rem, 10px 20px, 8px). |
| 6. Experience Design | 3/4 | Strong handling of loading, error, and empty states. |

**Overall: 10/24**

---

## Top 3 Priority Fixes

1. **Adopt a CSS Framework/Design System** — The project currently relies on inline styles (64 occurrences vs 1 className). Replace these with Tailwind CSS or CSS Modules to ensure consistent visual language and maintainability.
2. **Centralize Design Tokens** — Hardcoded colors (e.g., `#007bff` for primary) and typography should be moved to a theme or CSS variables to avoid fragmentation and enable easier updates.
3. **Component Refactoring** — Extract repetitive styled elements like buttons, dialogs, and list items into reusable UI components to ensure visual consistency across features.

---

## Detailed Findings

### Pillar 1: Copywriting (3/4)
- **Strengths:** Clear action labels like "Crawl URL", "Upload File", "Search".
- **Findings:**
  - `apps/ui/src/features/knowledge/components/AddKnowledgeDialog.tsx:145`: "Cancel" is standard.
  - `apps/ui/src/features/search/components/SearchInterface.tsx:60`: "Searching..." and "Search" provides good interaction feedback.
  - Some error messages are generic: `loadError ? <p>Error loading sources</p>`.

### Pillar 2: Visuals (1/4)
- **Findings:**
  - Almost all visual styling is defined via `style={{ ... }}` blocks inside JSX.
  - `apps/ui/src/features/knowledge/views/KnowledgeView.tsx:81`: High-priority action button has inline backgroundColor `#007bff`.
  - Visual hierarchy is achieved through manual `fontSize` and `fontWeight` adjustments in styles rather than a unified system.

### Pillar 3: Color (1/4)
- **Findings:**
  - `backgroundColor: '#007bff'` is used as a primary action color in multiple files.
  - `color: '#b42318'` is hardcoded for errors.
  - `backgroundColor: '#f9f9f9'`, `#f6f9ff`, `#eef6ff` are used for backgrounds without a clear relationship to a palette.
  - Hardcoded borders like `1px solid #ddd` or `1px solid #eee` are frequent.

### Pillar 4: Typography (1/4)
- **Findings:**
  - `fontSize: '12px'`, `13px`, `14px` are hardcoded in inline styles.
  - `fontWeight: 'bold'` is used manually instead of semantic heading levels or scale-based classes.

### Pillar 5: Spacing (1/4)
- **Findings:**
  - `padding: '10px 20px'` (KnowledgeView:81)
  - `marginTop: '2rem'`, `paddingTop: '2rem'` (SearchInterface:33)
  - `padding: '1rem'` (SearchInterface:70)
  - Inconsistency between pixel-based and rem-based spacing.

### Pillar 6: Experience Design (3/4)
- **Strengths:** Excellent state coverage.
- **Findings:**
  - `KnowledgeView.tsx:105`: `{loading ? <p>Loading sources...</p> : ...}` handles initial load.
  - `KnowledgeView.tsx:161`: `{pages.length === 0 ? <p>No pages found.</p> : ...}` handles empty states.
  - `AddKnowledgeDialog.tsx:147`: Buttons reflect current loading state ("Starting...", "Uploading...").
  - `CrawlProgress.tsx:85`: Specific error display from progress state.

---

## Files Audited
- apps/ui/src/features/knowledge/views/KnowledgeView.tsx
- apps/ui/src/features/knowledge/components/AddKnowledgeDialog.tsx
- apps/ui/src/features/knowledge/components/CrawlProgress.tsx
- apps/ui/src/features/search/components/SearchInterface.tsx
- apps/ui/src/App.tsx
- apps/ui/src/main.tsx
