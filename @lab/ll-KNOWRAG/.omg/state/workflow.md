# ll-KNOWRAG Workflow

- **Mode**: autopilot
- **Cycle**: 1
- **Current Step**: Done
- **Acceptance Criteria (Slice 7.5)**:
    - [x] Settings config updated with RERANKING_PROVIDER and others.
    - [x] SearchResponse updated with `reranking_applied`.
    - [x] Reranker refactored to support `lexical`, `ollama`, `cohere`.
    - [x] Default fallback to `lexical` maintained.
    - [x] RagService uses `reranking_applied`.
    - [x] Dependency injection updated without breaking existing API requests.
    - [x] Verified via pytest and code check.
