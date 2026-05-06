# W7-Base Taskboard - FINALIZED

## Slice 1 thru 20: Implementation & Verification
| Task ID | Task | Owner | Status |
|---|---|---|---|
| W7-1 thru 4 | Core CLI & Scaffolding | `omg-executor` | verified |
| W7-5 | Secret Management (SOPS) | `omg-executor` | verified |
| W7-6 thru 7 | GitOps & Webhook | `omg-verifier` | verified |
| W7-8 thru 9 | Ingress & Backup | `omg-executor` | verified |
| W7-10 thru 12 | CI/CD & Handoff | `omg-editor` | verified |
| W7-13 thru 15 | Hardening & Approvals | `omg-executor` | verified |
| W7-16 thru 17 | Policy Enforcement | `omg-architect` | verified |
| W7-18 thru 20 | Observability & Monitoring | `omg-editor` | verified |

## Slice 21: Final Platform Audit & Completion
| Task ID | Task | Owner | Dependency | Parallelizable | Worktree | Validation | Status |
|---|---|---|---|---|---|---|---|
| `W7-21.1` | Workspace sanitization & cleanup | `omg-executor` | None | Yes | `root` | Helpers removed, git tree clean | verified |
| `W7-21.2` | Full system health & compliance audit | `omg-verifier` | W7-21.1 | No | `all` | `doctor` passes 100%, stats consistent | verified |
| `W7-21.3` | Final documentation polish | `omg-editor` | W7-21.2 | Yes | `shared` | README reflect total Phase 1-8 scope | verified |
| `W7-21.4` | Platform handoff & state freeze | `omg-director` | W7-21.3 | No | `omg` | State files locked as completed | verified |

## Slice 22: Documentation Actualization & Expansion
| Task ID | Task | Owner | Dependency | Parallelizable | Worktree | Validation | Status |
|---|---|---|---|---|---|---|---|
| `W7-22.1` | Audit & Update Root (README, AGENTS, llms.txt) | `omg-editor` | None | Yes | `root` | Root docs accurately reflect all @ops services and CI/CD state | todo |
| `W7-22.2` | Update & Standardize `docs/` and `.shared/` | `omg-editor` | None | Yes | `docs`, `.shared` | `KNOWLEDGE_BASE.md`, `README-LLM.md`, `GITOPS_DESIGN.md` are synced | todo |
| `W7-22.3` | Add Stack-Level `README.md` & `AGENTS.md` for `@ops` | `omg-editor` | None | Yes | `@ops` | Every `@ops/*` directory has documented purpose and configs | todo |
| `W7-22.4` | Audit and actualize `@dev`, `@prod`, `@lab` metadata & docs | `omg-editor` | None | Yes | `@dev`, `@prod`, `@lab` | Existing stacks follow the `W7-CONTRACT` | todo |
| `W7-22.5` | Draft Missing: `docs/DISASTER_RECOVERY.md` | `omg-architect` | W7-22.1 | No | `docs` | DR procedures (volumes, DBs, SOPS keys) documented | todo |
| `W7-22.6` | Draft Missing: `docs/USER_ONBOARDING.md` | `omg-architect` | W7-22.1 | No | `docs` | Day 1 developer setup is explicitly detailed | todo |
| `W7-22.7` | Draft Missing: `docs/API_REFERENCE.md` | `omg-architect` | W7-22.1 | No | `docs` | `w7` CLI options, `.w7-meta` schemas, webhook specs defined | todo |

## Slice 22: Documentation Actualization & Brainstorming
| Task ID | Task | Owner | Dependency | Parallelizable | Worktree | Validation | Status |
|---|---|---|---|---|---|---|---|
| `W7-22.1` | Root documentation update (README, AGENTS, llms) | `omg-editor` | None | Yes | `root` | Accuracy vs verified state | verified |
| `W7-22.2` | Global & Shared doc standardization | `omg-editor` | W7-22.1 | Yes | `shared` | Cross-ref check | verified |
| `W7-22.3` | @ops stack-level READMEs & AGENTS creation | `omg-editor` | None | Yes | `ops` | All @ops folders have docs | verified |
| `W7-22.4` | @dev, @prod, @lab zone audit | `omg-editor` | None | Yes | `all` | W7-CONTRACT compliance | verified |
| `W7-22.5` | Draft DISASTER_RECOVERY.md | `omg-architect` | None | Yes | `docs` | Backup/Recovery steps covered | verified |
| `W7-22.6` | Draft USER_ONBOARDING.md | `omg-consultant` | None | Yes | `docs` | Day 1 guide complete | verified |
| `W7-22.7` | Draft API_REFERENCE.md | `omg-director` | None | Yes | `docs` | CLI flags & schema defined | verified |
| `W7-22.8` | Final Brainstorming & Missing Doc Gap Analysis | `omg-director` | All W7-22 | No | `root` | Gap list identified | verified |

## Slice 23: High-Value Documentation Expansion
| Task ID | Task | Owner | Dependency | Parallelizable | Worktree | Validation | Status |
|---|---|---|---|---|---|---|---|
| `W7-23.1` | Draft docs/OBSERVABILITY.md | `omg-architect` | None | Yes | `docs` | Content complete & coherent | verified |
| `W7-23.2` | Draft docs/SECURITY_POLICY.md | `omg-architect` | None | Yes | `docs` | Content complete & coherent | verified |
| `W7-23.3` | Draft docs/CI_CD_EXAMPLES.md | `omg-editor` | None | Yes | `docs` | Workflow examples included | verified |
| `W7-23.4` | Draft docs/ARCHITECTURE_DIAGRAM.md | `omg-architect` | None | Yes | `docs` | Topology diagram included | verified |
| `W7-23.5` | Draft docs/BACKUP_SCRIPTS.md | `omg-executor` | None | Yes | `docs` | Automation scripts included | verified |
| `W7-23.6` | Platform Coherence & Cross-Referencing | `omg-editor` | All W7-23.1-5 | No | `all` | All links verified | verified |

## Slice 24: KNOWRAG Infrastructure & Architecture Pivot
| Task ID | Task | Owner | Dependency | Parallelizable | Worktree | Validation | Status |
|---|---|---|---|---|---|---|---|
| `KNOWRAG-1.1` | Update BLUEPRINT.md and PRD for Gitea+Qdrant pivot | `omg-architect` | None | Yes | `@lab/ll-KNOWRAG` | Docs reflect new architecture | pending |
| `KNOWRAG-1.2` | Rewrite `compose.yml` to replace Postgres with Qdrant + Gitea | `omg-executor` | KNOWRAG-1.1 | No | `@lab/ll-KNOWRAG` | `docker compose config` passes | pending |
