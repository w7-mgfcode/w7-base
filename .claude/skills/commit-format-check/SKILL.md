---
name: commit-format-check
description: Validates a staged commit message against W7-Base's commit-format rule (`type(scope): description (#issue)`). Triggers on "check this commit", "validate commit message", "is this commit format ok", "/commit-format-check", or before invoking `git commit` programmatically. Re-used by the PreToolUse hook at .claude/hooks/check-commit-format.sh. Validates type, scope (against the W7-Base allow-list), description style (lowercase, no trailing period), issue reference, and absence of AI co-author trailers. Does NOT modify files.
---

# commit-format-check

Validate a commit message against `.claude/rules/commit-format.md`. Read-only.

## What you check

A valid message matches:

```
^(feat|fix|docs|refactor|test|chore|release)(\(([a-z]+)(,([a-z]+))?\))?: [a-z][^\.]*[^\.]( \(#\d+\))$
```

Plus these constraints:

- **Type** ∈ `{feat, fix, docs, refactor, test, chore, release}`
- **Scope** (when present) ∈ `{knowrag, api, ui, mcp, ingest, repo, platform, stacks, state, ops, ci, docs, release}`
  - Comma-pairs allowed (e.g., `ui,api`); both halves must be in the allow-list
- **Description**: lowercase first letter, no trailing period
- **Issue ref**: `(#N)` where `N` is a positive integer; required for every commit
- **No AI trailer**: rejects any line matching:
  - `Co-Authored-By: Claude.*<noreply@anthropic.com>` (any version)
  - `Generated with \[Claude Code\]`
  - `🤖 Generated with`

## Inputs

- A commit message string (passed by the user or read from `.git/COMMIT_EDITMSG`)
- OR the path to a commit-message file

## Output

Emit one of three verdicts (per `.claude/rules/output-formatting.md`):

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✅ Commit format OK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Subject: feat(api): wire /related endpoint (#42)
  Type: feat | Scope: api | Issue: #42 | AI trailer: none
```

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ❌ Commit format invalid
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Subject: <subject>
  ❌ scope `misc` not in allow-list
  ❌ description ends with `.`
  ❌ AI co-author trailer detected
  
👉 Suggested rewrite:
  feat(api): wire /related endpoint (#42)
  
  See .claude/rules/commit-format.md
```

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ⚠️ Commit format borderline
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ⚠️ scope inferred from path; was not specified in the message
  ✅ everything else is fine
```

## Issue existence check (optional second pass)

If `gh` is available and the user has authenticated:

```bash
gh issue view <N> --json state,title 2>/dev/null
```

- If the issue doesn't exist → escalate verdict to ❌
- If the issue is closed and the commit is `feat`/`fix` → ⚠️ "issue is closed; reopen or pick a different issue"
- If `gh` is not available → silently skip this check (do not fail)

## Procedure

1. Read the message (string or file).
2. Strip leading/trailing whitespace.
3. Apply the regex above to the subject line.
4. For each captured group, check the constraints (type, scope, description, issue).
5. Walk every line of the body; flag AI trailers.
6. (Optional) `gh issue view <N>` to confirm existence.
7. Emit one of the three verdicts.

## Constraints

- **Read-only.** Never edit `.git/COMMIT_EDITMSG` or any other file.
- Hook integration: when called from `.claude/hooks/check-commit-format.sh`, exit codes are `0=ok`, `2=invalid`. Do not change those exit codes — the hook depends on them.
- Be terse. The verdict is one block; no preamble, no follow-up suggestions beyond "Suggested rewrite".
