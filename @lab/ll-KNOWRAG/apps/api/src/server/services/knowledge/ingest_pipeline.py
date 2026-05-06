"""Ingestion pipeline orchestrator (Phase 8).

Ties together :class:`GiteaStorage` (T5), :func:`chunk_markdown` (T7),
the embedder, and :class:`QdrantIndexer` (T7) into a single
``ingest_artifact`` / ``process_diff`` flow.

Decoupled from any concrete embedder via the ``Embedder`` Protocol —
the existing ``EmbeddingService`` from Phase 7 satisfies it after a
small adapter shim, and tests use a fake.
"""
from __future__ import annotations

import logging
from typing import Awaitable, Callable, Protocol

from server.models.storage import FileDiff
from server.services.knowledge.chunker import chunk_markdown
from server.services.knowledge.frontmatter import Frontmatter
from server.services.search.qdrant_indexer import QdrantIndexer
from server.services.storage.gitea_storage import (
    ArtifactNotFoundError,
    GiteaStorage,
)

logger = logging.getLogger(__name__)


class Embedder(Protocol):
    """Minimal embedder interface — async, batched."""

    async def embed_batch(self, texts: list[str]) -> list[list[float]]: ...


class IngestResult(dict):
    """Light dict subclass for nicer logging."""


class IngestionPipeline:
    """Orchestrates the read → chunk → embed → upsert flow."""

    def __init__(
        self,
        *,
        storage: GiteaStorage,
        indexer: QdrantIndexer,
        embedder: Embedder,
        target_chunk_size: int = 1500,
        overlap: int = 200,
    ) -> None:
        self.storage = storage
        self.indexer = indexer
        self.embedder = embedder
        self.target_chunk_size = target_chunk_size
        self.overlap = overlap

    # ── One-artifact paths ────────────────────────────────────────────────

    async def ingest_artifact(self, path: str, ref: str | None = None) -> IngestResult:
        """Re-ingest one artifact end-to-end. Idempotent on the same
        ``(path, commit_sha)`` thanks to deterministic point IDs."""
        artifact = await self.storage.get(path, ref=ref)
        chunks = chunk_markdown(
            artifact.body,
            target_size=self.target_chunk_size,
            overlap=self.overlap,
        )
        if not chunks:
            logger.info("no chunks emitted for %s — skipping", path)
            return IngestResult(
                path=path,
                action="skipped",
                reason="empty",
                commit_sha=artifact.commit_sha,
            )

        embeddings = await self.embedder.embed_batch([c.content for c in chunks])
        if len(embeddings) != len(chunks):
            raise RuntimeError(
                f"embedder returned {len(embeddings)} vectors for {len(chunks)} chunks"
            )

        n = self.indexer.upsert(
            artifact_path=path,
            commit_sha=artifact.commit_sha,
            frontmatter=artifact.frontmatter,
            chunks=chunks,
            embeddings=embeddings,
        )
        # Garbage-collect chunks from older commits at this path.
        self.indexer.delete_stale_chunks(
            artifact_path=path,
            visibility=artifact.frontmatter.visibility,
            current_commit_sha=artifact.commit_sha,
        )
        return IngestResult(
            path=path,
            action="ingested",
            chunks=n,
            commit_sha=artifact.commit_sha,
            visibility=artifact.frontmatter.visibility,
        )

    async def remove_artifact(self, path: str, visibility: str) -> IngestResult:
        """Remove every chunk for a deleted artifact."""
        self.indexer.delete_artifact(artifact_path=path, visibility=visibility)
        return IngestResult(path=path, action="removed", visibility=visibility)

    # ── Diff-driven path (webhook entry point) ────────────────────────────

    async def process_diff(self, diffs: list[FileDiff]) -> list[IngestResult]:
        """Apply a list of file changes (from a Gitea push compare)."""
        results: list[IngestResult] = []
        for diff in diffs:
            try:
                if diff.status == "removed":
                    # We can't read the file — try both visibility scopes.
                    for vis in ("public", "private"):
                        self.indexer.delete_artifact(
                            artifact_path=diff.path, visibility=vis
                        )
                    results.append(
                        IngestResult(path=diff.path, action="removed")
                    )
                else:  # added | modified | renamed
                    results.append(await self.ingest_artifact(diff.path))
            except ArtifactNotFoundError:
                logger.warning("file %s vanished during ingestion", diff.path)
                results.append(
                    IngestResult(
                        path=diff.path, action="skipped", reason="vanished"
                    )
                )
            except Exception as exc:  # noqa: BLE001 — orchestrator catches per-item
                logger.exception("ingestion failed for %s", diff.path)
                results.append(
                    IngestResult(
                        path=diff.path, action="failed", error=str(exc)
                    )
                )
        return results


__all__ = ["Embedder", "IngestionPipeline", "IngestResult"]
