<!--
PR title MUST follow `type(scope): description (#issue)` — see .claude/rules/commit-format.md
-->

## Summary

<!-- 1-3 bullets on what this PR does and why -->
-

Closes #

## Zone(s) touched

<!-- Tick all that apply -->
- [ ] `@ops`
- [ ] `@dev`
- [ ] `@prod`
- [ ] `@lab`
- [ ] `.shared` / `.bin` / root platform
- [ ] `repo` (CI, hygiene, tooling)

## Test plan

<!-- Bullets, not prose. Cite commands the reviewer can run. -->
-

### `w7 verify` result

<!-- For changes touching @lab/ll-KNOWRAG, paste the verify output. Otherwise: "n/a — <reason>" -->

```
```

## Checklist

- [ ] Commit messages follow `type(scope): description (#issue)`
- [ ] No AI co-author trailers (`Co-Authored-By: Claude …` / `Generated with [Claude Code]`)
- [ ] Issue is referenced in every commit
- [ ] CI is green (compose validate, policy, lint, tests, security, dependency-review)
- [ ] No new `privileged: true` outside `@lab/`
- [ ] No new host `/` or `/etc` mounts outside `@lab/`

## Secrets touched?

- [ ] No secrets touched
- [ ] Secrets touched — confirm:
  - SOPS file path: `<path/to/.env.sops>`
  - No plaintext value leaked into git history, logs, or CI output
  - `.env.example` updated if a new key was introduced

## Backwards compatibility (KNOWRAG)

<!-- Required if this PR changes apps/api or apps/mcp public contracts -->
- [ ] N/A
- [ ] Compatible — no contract change
- [ ] Breaking — described below + version bump planned

<details>
<summary>Breaking-change details</summary>

<!-- What breaks, who's affected, migration path -->

</details>

## Vision review

<!-- Per .claude/rules/product-vision.md -->
- [ ] Aligns with single-host / Compose-only / zone-first principles
- [ ] Tension noted — `vision-review` label applied + tension described above
