# W7-Base Taskboard

## Slice 1: Framework & CLI Core
| Task ID | Task | Owner | Dependency | Parallelizable | Worktree | Validation | Status |
|---|---|---|---|---|---|---|---|
| `W7-1.1` | Scaffold layout, `.shared` network init, & Shell integration | `omg-executor` | None | No | `ops`, `shared` | Dirs exist, PATH updated, `w7` reachable | completed |
| `W7-1.2` | Define `.w7-meta` schema & Env Bridge | `omg-architect` | None | Yes | `shared` | Schema JSON/YAML defined | completed |
| `W7-1.3` | Implement `w7` core routing, `up`, `stat`, `logs`, `prune` | `omg-executor` | W7-1.1, W7-1.2 | No | `ops` | CLI wraps compose natively across zones | completed |
| `W7-1.4` | Implement `w7 go` (discovery/routing) | `omg-executor` | W7-1.3 | No | `ops` | CLI routes to specific stack context | completed |

## Slice 2: Platform Services & GitOps
| Task ID | Task | Owner | Dependency | Parallelizable | Worktree | Validation | Status |
|---|---|---|---|---|---|---|---|
| `W7-2.1` | Deploy Gitea stack into `@ops/gitea` | `omg-executor` | W7-1.3 | No | `ops` | Gitea boots, accessible on localhost | completed |
| `W7-2.2` | GitOps Webhook Listener service | `omg-executor` | W7-2.1 | No | `ops` | Listener triggers `w7 up` on push | completed |
| `W7-2.3` | Implement `w7 backup` logic | `omg-executor` | W7-1.3 | Yes | `ops` | `data/` directory archived safely | completed |

## Slice 3: Workloads, Health & Automation
| Task ID | Task | Owner | Dependency | Parallelizable | Worktree | Validation | Status |
|---|---|---|---|---|---|---|---|
| `W7-3.1` | Health matrix & pre-prod validation | `omg-verifier` | W7-2.2 | No | `dev`, `prod` | `w7 stat` shows matrix health | completed |
| `W7-3.2` | Operator UX, Prompts, & Documentation | `omg-editor` | W7-3.1 | No | `shared` | README complete, Shell prompt clean | verified |

*Note: Architecture verified. Implementation pending.*
## Slice 4: Phase 2 - Scaffolding & Security
| Task ID | Task | Owner | Dependency | Parallelizable | Worktree | Validation | Status |
|---|---|---|---|---|---|---|---|
| `W7-4.1` | Implement `w7 init` scaffolding engine | `omg-executor` | W7-1.3 | No | `bin` | `w7 init` creates strict layout | completed |
| `W7-4.2` | Implement `w7 doctor` validation | `omg-executor` | W7-1.3 | No | `bin` | `w7 doctor` validates system | completed |

## Slice 5: Phase 2 - Secret Management Foundation
| Task ID | Task | Owner | Dependency | Parallelizable | Worktree | Validation | Status |
|---|---|---|---|---|---|---|---|
| `W7-5.1` | Root `.gitignore` preventing secret leakage | `omg-executor` | W7-4.2 | Yes | `root` | `.env` excluded, `.env.example`/`.env.sops` allowed | completed |
| `W7-5.2` | `.sops.yaml` configuration for AGE encryption | `omg-executor` | W7-5.1 | Yes | `root` | SOPS discovers config from any stack dir | completed |
| `W7-5.3` | `.env` key validation in `w7 doctor` | `omg-executor` | W7-4.2 | No | `bin` | Doctor warns on missing keys vs `.env.example` | completed |
| `W7-5.4` | Secret management doctor checks (gitignore, sops config) | `omg-executor` | W7-5.1, W7-5.2 | No | `bin` | Doctor validates secret infrastructure | completed |
| `W7-5.5` | Webhook `.env.example` & improved `w7 init` templates | `omg-executor` | W7-5.1 | Yes | `ops`, `bin` | Templates guide operator toward safe secret setup | completed |
| `W7-5.6` | Operator guide (`SECRETS.md`) | `omg-editor` | W7-5.1 thru W7-5.5 | No | `shared` | Zone-specific guidance, SOPS setup documented | completed |
| `W7-5.7` | Update `ENV_PRECEDENCE.md`, `README.md`, taskboard, checkpoint | `omg-editor` | W7-5.6 | No | `shared`, `omg` | Docs consistent with implementation | completed |

## Slice 6: Phase 3 - Core Workloads & Observability
| Task ID | Task | Owner | Dependency | Parallelizable | Worktree | Validation | Status |
|---|---|---|---|---|---|---|---|
| `W7-6.1` | Deploy Dozzle logging stack | `omg-executor` | None | Yes | `ops` | Logs available at Dozzle port | completed |
| `W7-6.2` | Pre-prod stack deployment | `omg-executor` | None | Yes | `prod` | Initial compose setup validates | completed |
| `W7-6.3` | Test full GitOps push pipeline | `omg-verifier` | W7-6.1, W7-6.2 | No | `ops`, `prod` | Push triggers auto-deployment via Webhook | completed |


## Slice 7: Pipeline Stabilization & Security Hardening
| Task ID | Task | Owner | Dependency | Parallelizable | Worktree | Validation | Status |
|---|---|---|---|---|---|---|---|
| `W7-7.1` | Secure workspace (`.gitignore` update) | `omg-executor` | None | Yes | `root` | `.specstory/` ignored | completed |
| `W7-7.2` | Finalize webhook & meta configs | `omg-executor` | None | No | `ops`, `prod` | Clean working tree | completed |
| `W7-7.3` | End-to-End System Validation | `omg-verifier` | W7-7.1, 7.2 | No | `all` | `w7 stat` runs successfully | completed |

## Slice 8: Phase 4 - Network Routing & Ingress (Traefik)
| Task ID | Task | Owner | Dependency | Parallelizable | Worktree | Validation | Status |
|---|---|---|---|---|---|---|---|
| `W7-8.1` | Deploy Traefik reverse proxy | `omg-executor` | None | No | `ops` | Traefik dashboard accessible | verified |
| `W7-8.2` | Migrate Gitea & Dozzle to Ingress | `omg-executor` | W7-8.1 | Yes | `ops` | Services accessible via domain | verified |
| `W7-8.3` | Document Local Routing & DNS | `omg-editor` | W7-8.2 | No | `shared` | README updated with ingress details | verified |

## Slice 9: Backup Resiliency & Stabilization
| Task ID | Task | Owner | Dependency | Parallelizable | Worktree | Validation | Status |
|---|---|---|---|---|---|---|---|
| `W7-9.1` | Context-aware `.env` validation | `omg-executor` | None | Yes | `bin` | `backup`/`logs` warn instead of exit | completed |
| `W7-9.2` | Privilege boundary pre-check | `omg-executor` | None | Yes | `bin` | `backup` halts on unreadable `data/` | completed |
| `W7-9.3` | Test and Seal Fix | `omg-verifier` | W7-9.1, W7-9.2 | No | `root` | Fix committed, Git tree clean | verified |

## Slice 10: Phase 5 - Gitea Actions Base Configuration
| Task ID | Task | Owner | Dependency | Parallelizable | Worktree | Validation | Status |
|---|---|---|---|---|---|---|---|
| `W7-10.1` | Enable Actions in Gitea config | `omg-executor` | None | No | `ops` | Gitea UI shows Actions tab | completed |
| `W7-10.2` | Scaffold `@ops/act-runner` | `omg-executor` | None | No | `ops` | Runner dir structure matches W7 standard | completed |
| `W7-10.3` | Connect act-runner to Gitea | `omg-executor` | W7-10.1, 10.2 | No | `ops` | Runner registers successfully in Gitea UI | completed |
| `W7-10.4` | Document CI/CD Usage | `omg-editor` | W7-10.3 | No | `shared` | README details local pipeline steps | completed |

## Slice 11: Phase 5 - CI/CD Integration Testing
| Task ID | Task | Owner | Dependency | Parallelizable | Worktree | Validation | Status |
|---|---|---|---|---|---|---|---|
| `W7-11.1` | Setup Gitea Admin & Runner Token | `omg-executor` | None | No | `ops` | CLI configures auth and token | verified |
| `W7-11.2` | Start and register `@ops/act-runner` | `omg-executor` | W7-11.1 | No | `ops` | Runner online, connected to `w7-ingress` | verified |
| `W7-11.3` | Create test repository & workflow | `omg-executor` | W7-11.2 | No | `ops` | `test-repo` created via API, pushed workflow | verified |
| `W7-11.4` | Verify CI execution & Docker socket | `omg-verifier` | W7-11.3 | No | `ops` | `docker info` runs successfully in job | verified |

## Slice 12: Phase 5 - Deployment Handoff
| Task ID | Task | Owner | Dependency | Parallelizable | Worktree | Validation | Status |
|---|---|---|---|---|---|---|---|
| `W7-12.1` | Hybrid GitOps model documentation | `omg-architect` | None | Yes | `shared` | `GITOPS_DESIGN.md` updated with Webhook vs Runner | verified |
| `W7-12.2` | Reusable Deployment Action template | `omg-executor` | W7-11.4 | Yes | `shared` | `.shared/workflows/deploy-template.yaml` exists | verified |
| `W7-12.3` | Risk & Trust boundary mapping | `omg-architect` | None | Yes | `shared` | Security trade-offs documented | verified |

## Slice 13: Phase 6 - Interactive @prod Protection
| Task ID | Task | Owner | Dependency | Parallelizable | Worktree | Validation | Status |
|---|---|---|---|---|---|---|---|
| `W7-13.1` | Interactive confirmation prompt for `w7 up` on `@prod` | `omg-executor` | None | No | `bin` | `w7 up @prod/stack` prompts for [y/N] | verified |
| `W7-13.2` | Non-interactive bypass for CI (`--yes`) | `omg-executor` | W7-13.1 | No | `bin` | `w7 up @prod/stack --yes` skips prompt | verified |
| `W7-13.3` | `.w7-lock` based production deployment lock | `omg-executor` | W7-13.1 | No | `bin` | `w7 up` fails if `.w7-lock` exists in `@prod` | verified |

## Slice 14: Phase 6 - GitOps-Aware Diagnostics (w7 doctor v2)
| Task ID | Task | Owner | Dependency | Parallelizable | Worktree | Validation | Status |
|---|---|---|---|---|---|---|---|
| `W7-14.1` | Webhook HMAC parity check | `omg-executor` | None | No | `bin` | `doctor` compares HMAC secrets | verified |
| `W7-14.2` | act-runner heartbeat/status check | `omg-executor` | None | No | `bin` | `doctor` checks if runner is online | verified |
| `W7-14.3` | Traefik ingress connectivity checks | `omg-executor` | None | No | `bin` | `doctor` pings internal domains | verified |
| `W7-14.4` | Secret sealing validation for `@prod` | `omg-executor` | None | No | `bin` | `doctor` warns on unsealed prod secrets | verified |

## Slice 15: Phase 6 - Approval-Gated CI/CD Workflows
| Task ID | Task | Owner | Dependency | Parallelizable | Worktree | Validation | Status |
|---|---|---|---|---|---|---|---|
| `W7-15.1` | Protected branch / approval documentation | `omg-editor` | None | Yes | `shared` | `GITOPS_DESIGN.md` updated | verified |
| `W7-15.2` | `w7-preflight` CI action for prod validation | `omg-executor` | W7-14.4 | No | `shared` | Action runs pre-checks before deploy | verified |
| `W7-15.3` | deploy-template refinement with review gate | `omg-editor` | W7-15.1 | No | `shared` | Template includes `preflight` gate | verified |

## Slice 16: Phase 7 - Policy Enforcement Foundations
| Task ID | Task | Owner | Dependency | Parallelizable | Worktree | Validation | Status |
|---|---|---|---|---|---|---|---|
| `W7-16.1` | Policy engine discovery & scaffolding | `omg-executor` | None | No | `shared` | `.shared/policy` exists, tool detected | verified |
| `W7-16.2` | Define "No Privileged @prod" policy | `omg-architect` | W7-16.1 | No | `shared` | Rego/Shell policy defines constraint | verified |
| `W7-16.3` | Integrate policy audit into `w7 doctor` | `omg-executor` | W7-16.2 | No | `bin` | `doctor` reports policy violations | verified |

## Slice 17: Phase 7 - Advanced Compliance & Reporting
| Task ID | Task | Owner | Dependency | Parallelizable | Worktree | Validation | Status |
|---|---|---|---|---|---|---|---|
| `W7-17.1` | "No Root Volume Mounts in @prod" policy | `omg-executor` | W7-16.3 | Yes | `shared` | Prevents mounting / or /etc in @prod | verified |
| `W7-17.2` | "Zone-Aware Ingress naming" policy | `omg-architect` | W7-16.3 | Yes | `shared` | Ensures prod uses standard domains | verified |
| `W7-17.3` | JSON output for policy violations in `doctor` | `omg-executor` | W7-16.3 | No | `bin` | `doctor --json` prints violations | verified |

## Slice 18: Phase 8 - Observability Foundation
| Task ID | Task | Owner | Dependency | Parallelizable | Worktree | Validation | Status |
|---|---|---|---|---|---|---|---|
| `W7-18.1` | Scaffold and deploy `@ops/prometheus` | `omg-executor` | None | No | `ops` | Prometheus accessible at `prom.w7.local` | verified |
| `W7-18.2` | Scaffold and deploy `@ops/grafana` | `omg-executor` | W7-18.1 | No | `ops` | Grafana accessible at `grafana.w7.local` | verified |
| `W7-18.3` | Deploy `node-exporter` for host visibility | `omg-executor` | None | Yes | `ops` | Metrics available in Prometheus | verified |

## Slice 19: Phase 8 - W7 Platform Exporter (JSON to Metrics)
| Task ID | Task | Owner | Dependency | Parallelizable | Worktree | Validation | Status |
|---|---|---|---|---|---|---|---|
| `W7-19.1` | Implement `w7-exporter` script/container | `omg-executor` | W7-17.3 | No | `bin`, `ops` | Exporter runs `w7 doctor --json` | verified |
| `W7-19.2` | Map JSON output to Prometheus metrics | `omg-architect` | W7-19.1 | No | `ops` | Metrics visible in `/metrics` endpoint | verified |
| `W7-19.3` | Integrate `w7 stat` zone/stack visibility | `omg-executor` | W7-19.2 | Yes | `ops` | Container counts visible as metrics | verified |

## Slice 20: Phase 8 - Cross-Zone Dashboards & Local Alerting
| Task ID | Task | Owner | Dependency | Parallelizable | Worktree | Validation | Status |
|---|---|---|---|---|---|---|---|
| `W7-20.1` | Create Grafana dashboards for global W7 health | `omg-editor` | W7-18.2, 19.3 | No | `ops` | Dashboard shows cross-zone status | verified |
| `W7-20.2` | Add local alerting rules for failures/policies | `omg-architect` | W7-20.1 | No | `ops` | Alerts trigger on policy violations | verified |
| `W7-20.3` | Document observability-driven operations | `omg-editor` | W7-20.2 | No | `shared` | README updated with observability ops | verified |

## Slice 21: Final Platform Audit & Completion
| Task ID | Task | Owner | Dependency | Parallelizable | Worktree | Validation | Status |
|---|---|---|---|---|---|---|---|
| `W7-21.1` | Workspace sanitization & cleanup | `omg-executor` | None | Yes | `root` | Helpers removed, git tree clean | verified |
| `W7-21.2` | Full system health & compliance audit | `omg-verifier` | W7-21.1 | No | `all` | `doctor` passes 100%, stats consistent | planned |
| `W7-21.3` | Final documentation polish | `omg-editor` | W7-21.2 | Yes | `shared` | README reflect total Phase 1-8 scope | planned |
| `W7-21.4` | Platform handoff & state freeze | `omg-director` | W7-21.3 | No | `omg` | State files locked as completed | planned |
