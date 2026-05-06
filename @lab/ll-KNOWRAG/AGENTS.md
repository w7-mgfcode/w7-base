# Archon RAG Workflow

This stack follows a strict **RESEARCH -> BRAINSTORM -> VALIDATE** workflow. Retrieve relevant documentation and code examples first, synthesize project-specific options second, and validate those options before recommending or implementing anything.

## Stack Scope

This file applies to `@lab/ll-KNOWRAG`. It supplements the root [`AGENTS.md`](/home/w7-hector/w7-localbase/AGENTS.md) with stack-specific research and validation rules.

## Architecture At A Glance

```text
@lab/ll-KNOWRAG/
├── apps/      <- api, mcp, and ui services
├── docs/      <- architecture and runbook docs
├── _kb/       <- project knowledge files for agents
├── db/        <- migrations and seeds
├── compose.yml
├── README.md
├── CLAUDE.md
└── AGENTS.md
```

## Workflow

```text
Task
  ↓
RESEARCH
  ↓
BRAINSTORM
  ↓
VALIDATE
  ↓
Recommendation / Implementation Plan
```

If results are weak, loop back to broader search terms, adjacent concepts, or source browsing.

## Component Responsibilities

| Component | Boundary | Does NOT |
|-----------|----------|----------|
| `research` | Searches documentation and knowledge sources | Does not make final decisions |
| `brainstorm` | Turns findings into candidate approaches | Does not invent unsupported claims |
| `validate` | Confirms recency, fit, and evidence quality | Does not skip source checks |
| `source_selection` | Chooses the correct `source_id` for targeted search | Does not filter by URL or domain |
| `code_example_search` | Finds example implementations before coding | Does not copy examples blindly |

## Design Principles

- Research first; do not implement from scratch before searching.
- Evidence over intuition; ground recommendations in retrieved material.
- Adapt, do not copy; reuse patterns only after tailoring them to this stack.
- Validate before commit; check fit, limitations, and evidence quality before finalizing.
- Use focused retrieval; keep `match_count` low for precise results.
- Use `source_id` for source-targeted retrieval.

## Key Interfaces

| Interface | Type | Purpose |
|-----------|------|---------|
| `rag_search_knowledge_base` | retrieval API | Find technical guidance and documentation |
| `rag_search_code_examples` | retrieval API | Find implementation patterns |
| `rag_get_available_sources` | source registry | List available source IDs |
| `rag_list_pages_for_source` | source navigation | Browse source structure |
| `rag_read_full_page` | source reader | Read full page context |

## Operational Flow

### Research

```bash
rag_search_knowledge_base(query="microservices vs monolith pros cons", match_count=5)
rag_search_knowledge_base(query="OAuth 2.0 PKCE flow implementation", match_count=3)
rag_search_knowledge_base(query="React useEffect cleanup function", match_count=2)
rag_search_code_examples(query="React custom hook data fetching", match_count=3)
rag_search_code_examples(query="PostgreSQL connection pooling Node.js", match_count=2)
```

### Brainstorm

- Synthesize results into candidate approaches.
- Adapt patterns to stack requirements.
- Prefer conservative solutions when evidence is incomplete.

### Validate

- Cross-check multiple sources when possible.
- Confirm project fit.
- Record assumptions and limitations.

## Source-Targeted Search

1. Run `rag_get_available_sources()`.
2. Find the matching source title.
3. Search with `source_id`.

```bash
rag_get_available_sources()
rag_search_knowledge_base(query="vector functions", source_id="src_abc123")
rag_search_code_examples(query="authentication", source_id="src_def456")
```

## Safety Constraints

- Never store secrets in code; environment variables only.
- Never use URLs or domain names for source filtering; always use `source_id`.
- Never treat one example as production-ready without validation.
- Never skip applicability checks.
- Never present assumptions as verified facts.

## Project References

- `README.md` for stack overview and startup flow.
- `CLAUDE.md` for project-specific implementation guidance.
- `docs/archon-porting-map.md` for what was reused or intentionally excluded.
- `docs/runbook.md` for operational procedures.
- `_kb/` for stack-local knowledge files when they are relevant to the task.
