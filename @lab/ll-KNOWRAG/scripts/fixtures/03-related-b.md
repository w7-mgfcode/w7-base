---
id: verify-related-b
owner: w7-mgfcode
tags: [verify, retrieval, related, kb-smoke, hybrid-search]
status: published
version: 0.1.0
visibility: public
---

# Verify related B — hybrid search anchor

This fixture is the second of three artifacts seeded to anchor the `related.api_returns_3_plus` check in `w7 verify @lab/ll-KNOWRAG`. It re-uses the baseline's vocabulary while introducing additional terms relevant to the hybrid-search code path: "BM25", "sparse vector", "lexical overlap", and "rerank".

When `USE_HYBRID_SEARCH=true` is set on the API, the search strategy combines dense vector cosine similarity with a sparse-vector BM25 score. The verify harness does NOT toggle hybrid mode — it asserts the dense-only path because that is the lowest common denominator. This fixture's hybrid-flavored content does not change the dense-only assertion; it simply makes the related-pane more colorful in manual inspection.

## Why this content

The plan calls out that fixtures should be substantive enough to chunk, semantically aligned enough to outrank noise in the related-pane, and topically distinct enough that operators reading the artifacts directly find them informative rather than padding. This fixture does that by talking about real Phase 8 wiring decisions — chunking targets of 1200–1800 characters, overlap of 150–250 characters, sparse-vector BM25 over Postgres `tsvector` (the Phase 7 path that no longer exists in the running stack), and visibility-scoped collections.

The verify harness commits this fixture to a temporary branch in the KB Gitea repo, waits for the webhook to fire, polls Qdrant for the resulting points, and then runs the related query against the baseline path. If this fixture's embedding is semantically similar enough to the baseline, it will be one of the three results that satisfy the assertion. If it is not, the embedder is broken or the index is stale.

## Cleanup

After the verify run exits, this fixture (along with its temp branch and corresponding Qdrant points) is deleted by the harness's cleanup hook unless `--keep` was passed. The KB repo's `main` branch is never touched by the harness.
