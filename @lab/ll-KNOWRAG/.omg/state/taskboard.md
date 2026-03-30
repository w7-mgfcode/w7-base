# ll-KNOWRAG Taskboard

## Phase 1: Foundation & Infrastructure
| Task ID | Task | Owner | Status |
|---|---|---|---|
| `KB-1.1` | Repo scaffolding & structure | `omg-executor` | verified |
| `KB-1.2` | Docker Compose & Env setup | `omg-executor` | verified |
| `KB-1.3` | Service entrypoints (API, MCP, UI) | `omg-executor` | verified |
| `KB-1.4` | Documentation skeletons | `omg-executor` | verified |

## Phase 2: Schema & Database
| Task ID | Task | Owner | Status |
|---|---|---|---|
| `KB-2.1` | SQL Migrations (Sources, Pages, Chunks) | `omg-executor` | verified |
| `KB-2.2` | Vector search RPC functions | `omg-executor` | verified |
| `KB-2.3` | Database seed data | `omg-planner` | verified |

## Phase 3: Core Porting (Archon)
| Task ID | Task | Owner | Status |
|---|---|---|---|
| `KB-3.1` | Discovery & Crawling port | `omg-executor` | verified |
| `KB-3.2` | Ingestion & Storage port | `omg-executor` | verified |
| `KB-3.3` | Embedding layer port | `omg-executor` | verified |
| `KB-3.4` | Retrieval & Search port | `omg-executor` | verified |

## Phase 4: Integration & UI
| Task ID | Task | Owner | Status |
|---|---|---|---|
| `KB-4.1` | MCP Tool integration | `omg-executor` | verified |
| `KB-4.2` | UI Knowledge views port | `omg-executor` | verified |
| `KB-4.3` | UI Search interface port | `omg-executor` | verified |

## Phase 5: Stabilization (Final)
| Task ID | Task | Owner | Status |
|---|---|---|---|
| `ST-5.1` | Fix RemoteProtocolError (PostgREST Stack) | `omg-executor` | verified |
| `ST-5.2` | E2E Loop Verification (Crawl->Ingest->Search) | `omg-executor` | verified |
| `ST-5.3` | Production Pinning (requirements.txt) | `omg-executor` | verified |
