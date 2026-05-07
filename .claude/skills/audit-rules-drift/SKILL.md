---
name: audit-rules-drift
description: Detects drift between W7-Base policy artifacts and the codebase. Compares .claude/rules/*.md against CLAUDE.md references, AGENTS.md references, and actual repo paths/commands they cite. Surfaces rules that no doc cites (orphan rules), CLAUDE.md sections that reference missing rules, scopes/types in commit-format.md that no commit ever uses (and vice versa), and policy scripts in .shared/policy/ that no rule cites. Read-only — produces a scannable diff report. Triggers on "audit rules", "find rule drift", "are the rules current", "/audit-rules-drift", or before a docs-refresh PR. Do NOT use for code review, security audits, or rewriting rules.
---

# audit-rules-drift

Detect drift between `.claude/rules/`, `CLAUDE.md`, `AGENTS.md`, and the repo state they describe. Read-only.

## Scope

- `.claude/rules/*.md` (root)
- `@lab/ll-KNOWRAG/.claude/rules/*.md`
- Root `CLAUDE.md`
- `@lab/ll-KNOWRAG/CLAUDE.md`
- Root `AGENTS.md`
- `.shared/policy/*.sh`

## Procedure

1. **List rule files**: `find .claude/rules @lab/*/​.claude/rules -name '*.md' 2>/dev/null`.
2. **List policy scripts**: `ls .shared/policy/*.sh`.
3. For each rule file, extract:
   - The frontmatter `paths:` patterns (KNOWRAG-style) if any.
   - Every concrete file path and command it mentions.
   - Every scope/type/keyword it constrains (`scope` allow-list in `commit-format.md`, branch prefixes in `branch-naming.md`, …).
4. For each `CLAUDE.md`, extract every rule path it references.
5. For each `AGENTS.md`, extract every rule path it references.
6. Run the four checks below.

## Checks

1. **Orphan rules** — a `.claude/rules/<name>.md` that is referenced from NEITHER `CLAUDE.md` NOR `AGENTS.md`. Flag `⚠️ ORPHAN`.
2. **Dangling references** — `CLAUDE.md` cites a rule file (or section heading) that does not exist. Flag `❌ DANGLING`.
3. **Path / command drift** — a rule cites a concrete path (e.g., `devsync/cli/main.py`, `.shared/policy/foo.sh`, `compose.yml`) that does not exist on disk. Flag `❌ PATH-DRIFT`.
4. **Empirical-vs-declared scope drift** (commit-format.md only) —
   - Run: `git log --pretty=%s -200 master | grep -oE '^[a-z]+\(([a-z,]+)\)' | sed 's/.*(\([a-z,]\+\))/\1/' | tr ',' '\n' | sort -u`
   - Diff vs. the scope allow-list in `commit-format.md`.
   - Scopes used but not declared → ❌ `UNDECLARED`.
   - Scopes declared but never used → ⚠️ `UNUSED` (low-value to fix; report only).
5. **Policy scripts not cited** — a `.shared/policy/*.sh` that no rule mentions. Flag `⚠️ ORPHAN-POLICY`.

## Report format

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🧭 Rules Drift Audit
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 Rules inventory
  ✅ 8 rule files discovered (root: 8, KNOWRAG: 5)

📋 Orphan rules
  ⚠️ .claude/rules/foo-rule.md — not referenced from CLAUDE.md or AGENTS.md

📋 Dangling references
  ❌ CLAUDE.md:12 — references `.claude/rules/missing.md` (not found)

📋 Path / command drift
  ❌ .claude/rules/test-requirements.md:9 — cites `devsync/` (not in repo)

📋 Commit-format scope drift
  ❌ UNDECLARED scopes used in last 200 commits: misc, foo
  ⚠️ UNUSED scopes declared: bar, baz

📋 Policy scripts not cited
  ⚠️ .shared/policy/legacy-foo.sh — referenced by no rule

────────────────────────────────────────────
  ❌ Result: 2 errors, 3 warnings
────────────────────────────────────────────

👉 Next steps:
  1. Fix dangling reference in CLAUDE.md:12
  2. Add `misc`, `foo` to commit-format scope allow-list (or rewrite the offending commits)
  3. Triage orphan rule(s) — link from CLAUDE.md or delete
```

## Constraints

- **Read-only.**
- Cap report at 80 lines.
- Do NOT propose textual rewrites — list findings, the main session decides.
- The 200-commit window for empirical scope analysis is a deliberate limit: longer windows are noisy. Adjust if the user explicitly asks.
- If a rule has `paths:` frontmatter (KNOWRAG-style), respect it: don't flag `PATH-DRIFT` for a path that the rule explicitly scopes.
