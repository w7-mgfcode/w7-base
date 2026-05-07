---
name: repo-visibility-audit
description: Audits the W7-Base public-facing surface — README.md, llms.txt, AGENTS.md, CLAUDE.md, BRANCHING.md, RELEASE.md, docs/, @lab/ll-KNOWRAG/{README,BLUEPRINT,PRD,CLAUDE,AGENTS}.md, runbook. Detects broken internal links, dead anchors, badge failures (HTTP probe), README↔llms.txt drift, stale docs (>90d unchanged), orphan docs, and outdated screenshots. Read-only — produces a scannable report. Triggers on "audit the README", "check the docs", "verify llms.txt", "find stale docs", "find orphan docs", "/repo-visibility-audit". Do NOT use for code review, dependency audits, security scanning, or rewriting docs.
---

# repo-visibility-audit

Read-only audit of the W7-Base public-facing surface. **You print a scannable report. You NEVER edit files.**

## Scope

Audit ONLY these paths:

- Root: `README.md`, `llms.txt`, `AGENTS.md`, `CLAUDE.md`, `BRANCHING.md`, `RELEASE.md`
- `docs/*.md` (all files)
- `@lab/ll-KNOWRAG/{README,BLUEPRINT,PRD,CLAUDE,AGENTS}.md`
- `@lab/ll-KNOWRAG/docs/runbook.md`

Anything else: skip.

## Procedure

1. Build the scope list with:
   ```bash
   find . -maxdepth 4 -type f \( -name 'README.md' -o -name 'llms.txt' -o -name 'AGENTS.md' \
     -o -name 'CLAUDE.md' -o -name 'BRANCHING.md' -o -name 'RELEASE.md' \
     -o -name 'BLUEPRINT.md' -o -name 'PRD.md' -o -name 'runbook.md' \
     -o -path './docs/*.md' \) 2>/dev/null
   ```
2. For each file, extract:
   - markdown links: `grep -nE '\]\([^)]+\)' "$f"`
   - headings: `grep -nE '^#+ ' "$f"`
   - image refs: `grep -nE '!\[[^]]*\]\(([^)]+)\)' "$f"`
   - badge URLs (README only): first 30 lines
3. Run checks 1–8 below.
4. Cap HTTP probes at 5s timeout. Use `xargs -P 8` for parallelism.
5. Use `git log -1 --format=%cs -- <file>` per scope file for freshness.

## Checks

1. **Broken internal links / anchors** — resolve every `](path)` and `](#anchor)` relative to the source file. Miss = ❌.
2. **Badge sanity** — README badges: probe via `curl -sI -o /dev/null -w "%{http_code}" --max-time 5 <url>`. 2xx/3xx = ✅, otherwise ❌ (transient 5xx may be ⚠️).
3. **Stale anchor list** — every `## Heading` produces a slug (lowercased, spaces→`-`, punctuation stripped). Cross-check incoming `#anchor` links against the slug list.
4. **`llms.txt` ↔ README drift** — README's "Key documents" / "Documentation Map" must appear in `llms.txt`. Missing → ❌. Orphan in `llms.txt` (not in README) → ⚠️.
5. **Stale docs** — `now - git-mtime > 90 days` → ⚠️ STALE.
6. **Orphans** — doc in `docs/` not referenced from README, llms.txt, CLAUDE.md, or any other in-scope doc → ⚠️ ORPHAN.
7. **30-second pitch** — extract README's first ~200 words. Subjective ✅ / ⚠️ on whether they answer "what does W7-Base do for me?".
8. **Screenshots** — any `![](path)` image referenced from README with local file mtime > 180 days → ⚠️.

## Report format

Use `.claude/rules/output-formatting.md` exactly:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🔍 Repo-Visibility Audit
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 Internal links & anchors
  ✅ README.md — 42/42 links resolve
  ❌ docs/USER_ONBOARDING.md:88 — link to ../missing/foo.md not found

📋 Badges (README)
  ✅ 7/8 badges return 2xx
  ⚠️ shields.io coverage badge — 503 (transient?)

📋 llms.txt ↔ README drift
  ❌ docs/OBSERVABILITY.md listed in README but missing from llms.txt

📋 Stale docs (>90 days, unchanged)
  ⚠️ docs/BACKUP_SCRIPTS.md — last touched 142 days ago

📋 Orphans
  ⏭️ docs/OMG_GEMINI_AI_WORKFRAME_KB.md — not referenced anywhere in scope

📋 30-second pitch
  ✅ README opens with a clear value statement

📋 Screenshots
  ✅ no images > 180 days old

────────────────────────────────────────────
  ❌ Result: NOT CLEAN — 2 errors, 3 warnings
────────────────────────────────────────────

👉 Next steps:
  1. Fix broken link at `docs/USER_ONBOARDING.md:88`
  2. Add `docs/OBSERVABILITY.md` to `llms.txt` (or remove from README)
  3. Review `docs/BACKUP_SCRIPTS.md` — re-validate or mark deprecated
```

## Constraints

- **Read-only.** If a check needs to write, ABORT with `❌ Tool restriction violated`.
- Cap output at 80 lines. If more findings, append `(+N more)` footer.
- Do NOT call the network for anything beyond the README badge probe list.
- Do NOT analyze code files — markdown only.
- Do NOT propose textual rewrites — that's the operator's call.
