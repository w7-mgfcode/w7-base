---
id: verify-related-a
owner: w7-mgfcode
tags: [verify, retrieval, related, kb-smoke]
status: published
version: 0.1.0
visibility: public
---

# Verify related A — semantic similarity anchor

This fixture is one of three artifacts intentionally similar to `verify-baseline.md`. It exists so that the verify harness's `related.api_returns_3_plus` check has a deterministic floor: at least three artifacts should appear when `/api/artifacts/knowledge/verify-baseline.md/related?k=5` is queried after this verify run's seed commits.

The body shares vocabulary with the baseline by design — "retrieval", "KB", "verify", "smoke", "fixture", "ingestion", "Qdrant", "chunk", "embedding". Semantic similarity should land this artifact near the baseline in the embedding space without requiring identical text.

## Specific overlap

The baseline talks about the contract "git push → searchable in 30 seconds, end-to-end." This fixture talks about the **same contract** from a different angle: the operator perspective. From the operator's seat, the verify harness is the proof that a committed markdown file becomes a retrievable artifact, with metadata-aware filters and a related-pane that surfaces topical neighbors without requiring the operator to manage a vector database directly.

This is the value proposition Phase 8 commits to. The verify harness's job is to keep that commitment honest after every change to the ingestion pipeline, the chunker, the embedder, or the Qdrant client.

## Why three related fixtures

`/api/artifacts/{path}/related?k=5` is configured with a default `k=5` upper bound and a deduplication step that returns one entry per `artifact_path`, not per chunk. To assert "≥3 results" we need at least three other artifacts in the same visibility scope (`kb_public`) that share enough semantic mass with the baseline to outrank random noise. This fixture, plus `verify-related-b` and `verify-related-c`, gives the harness a stable floor.

If the related endpoint ever returns fewer than three results during verify, that is a real signal that ingestion is partial, embeddings are degenerate, or the Qdrant collection is mis-scoped — all conditions worth failing the harness on.
