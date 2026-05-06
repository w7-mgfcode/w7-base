---
id: verify-baseline
owner: w7-mgfcode
tags: [verify, baseline, retrieval, kb-smoke]
status: published
version: 0.1.0
visibility: public
---

# Verify baseline — KB end-to-end smoke fixture

This fixture exists to anchor `w7 verify @lab/ll-KNOWRAG`'s assertion chain. It is the seed artifact whose successful ingestion proves that a markdown commit to the Gitea KB repo flows through the webhook, the chunker, the Ollama embedder, and lands as searchable points in the Qdrant `kb_public` collection.

The fixture is intentionally generic: short paragraphs, technical vocabulary that overlaps with the related fixtures, and no external links. Embeddings live or die by lexical and semantic overlap — the baseline shares the tokens "retrieval", "KB", "smoke", "verify", "ingestion", and "fixture" with the three related fixtures so that `/api/artifacts/{path}/related` returns each of them with a non-trivial cosine score.

The fixture must be at least 1500 bytes to ensure the chunker (1200–1800 char window with 150–250 char overlap) emits at least one chunk. Padding with realistic prose, not lorem ipsum, keeps the embedding semantically clean.

## What this fixture asserts

When the verify harness commits this file under `knowledge/verify-baseline.md` on a temp branch, four things must follow within the verify timeout window:

1. The Gitea webhook fires and the API receives a verified HMAC payload.
2. The frontmatter parser accepts the YAML block and emits a `Frontmatter` instance.
3. The chunker produces at least one chunk; the Ollama embedder produces at least one embedding vector.
4. The Qdrant indexer upserts at least one point into the `kb_public` collection with payload `artifact_path = "knowledge/verify-baseline.md"`.

Once those steps complete, `POST /api/artifacts/search` with the query "verify baseline" must return this artifact among the top-5 hits, and `GET /api/artifacts/knowledge/verify-baseline.md/related?k=5` must return three or more sibling artifacts that were committed in the same verify run.

## Why this matters

Phase 8's contract is "git push → searchable in 30 seconds, end-to-end, on real running infrastructure." Mocked unit tests cover the seams. This fixture and its three companions cover the seam crossings.
