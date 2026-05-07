# Branch Naming

Branch names mirror the `type` field of `commit-format.md`. This rule applies to every `git checkout -b` / `git switch -c` Claude runs.

## Format

```
<type>/<scope-slug>
```

- **type** — one of: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `release`, `hotfix`, `keep`
- **scope-slug** — kebab-case, ≤ 50 chars, no issue number (the issue lives in commit + PR)
- The slug should hint at the scope from `commit-format.md` so a glance reveals intent (`feat/knowrag-…`, `fix/ops-…`).

## Examples

Good:
- `feat/knowrag-webhook-route`
- `fix/api-30x-redirect`
- `chore/repo-prune-stale-stacks`
- `docs/branching-md`
- `release/knowrag-v0.4.0`
- `hotfix/prod-tls-renew`
- `keep/qdrant-reranker-spike`

Bad:
- `add-feature` — no type prefix
- `feat/issue-42` — embeds the issue number
- `feat/My_Feature_Branch` — not kebab-case, capitalized
- `feature/foo` — wrong type prefix (use `feat/`)
- `feat/` — empty slug

## Rules

- Branch off `master` (never off another feature branch).
- One branch per issue. If a single issue grows beyond one branch, split the issue.
- `release/*` branches are ephemeral — delete after the tag is pushed.
- `keep/*` branches are excluded from the stale-branch cleaner.
- Don't reuse a branch name after it's been merged and deleted.

## Before creating a branch

1. There is an issue (`gh issue list --search "<topic>"`) — if not, open one first.
2. Pick the right `type` for the work.
3. Pick a kebab-case slug ≤ 50 chars.
4. `git switch -c <type>/<slug>` from an up-to-date `master`.

If the user asks for a branch that doesn't fit this format, propose a corrected name and explain why.
