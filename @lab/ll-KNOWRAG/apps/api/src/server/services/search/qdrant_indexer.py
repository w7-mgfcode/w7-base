"""Qdrant indexer (Phase 8) — collection management + chunk upsert/delete.

Each *visibility scope* maps to a separate Qdrant collection
(``kb_public`` / ``kb_private``) so a public-vs-private filter is
a collection switch rather than a payload filter.

Point IDs are deterministic UUIDv5 derived from
``(artifact_path, commit_sha, chunk_index)`` so re-ingesting the same
``(path, sha)`` produces the same IDs (idempotent upserts).
"""
from __future__ import annotations

import logging
import uuid
from typing import Protocol

from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    FilterSelector,
    MatchValue,
    PointStruct,
    VectorParams,
)

from server.services.knowledge.chunker import Chunk
from server.services.knowledge.frontmatter import Frontmatter

logger = logging.getLogger(__name__)

POINT_ID_NAMESPACE = uuid.UUID("d2c1b9b1-1b1b-4b1b-8b1b-1b1b1b1b1b1b")


def collection_name(visibility: str) -> str:
    """``public`` → ``kb_public``, ``private`` → ``kb_private``."""
    if visibility not in ("public", "private"):
        raise ValueError(f"unsupported visibility: {visibility!r}")
    return f"kb_{visibility}"


def stable_point_id(artifact_path: str, commit_sha: str, chunk_index: int) -> str:
    """Deterministic UUIDv5 for one chunk identity."""
    name = f"{artifact_path}@{commit_sha}#{chunk_index}"
    return str(uuid.uuid5(POINT_ID_NAMESPACE, name))


class _QdrantClientProto(Protocol):
    """Subset of ``qdrant_client.QdrantClient`` we depend on (lets tests use a mock)."""

    def get_collections(self): ...
    def create_collection(self, collection_name: str, vectors_config): ...
    def upsert(self, collection_name: str, points): ...
    def delete(self, collection_name: str, points_selector): ...
    def count(self, collection_name: str, count_filter=None, exact: bool = True): ...


class QdrantIndexer:
    """High-level Qdrant operations for the KB chunk index."""

    def __init__(
        self,
        client: _QdrantClientProto,
        *,
        default_dim: int = 768,
        distance: Distance = Distance.COSINE,
    ) -> None:
        if client is None:
            raise ValueError("client required")
        if default_dim <= 0:
            raise ValueError("default_dim must be > 0")
        self.client = client
        self.default_dim = default_dim
        self.distance = distance

    # ── Collection management ─────────────────────────────────────────────

    def ensure_collection(self, visibility: str, *, dim: int | None = None) -> bool:
        """Idempotently create the collection. Returns True if created."""
        name = collection_name(visibility)
        existing = {c.name for c in self.client.get_collections().collections}
        if name in existing:
            return False
        size = dim or self.default_dim
        self.client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(size=size, distance=self.distance),
        )
        logger.info("created Qdrant collection %s (dim=%d)", name, size)
        return True

    # ── Upsert ────────────────────────────────────────────────────────────

    def upsert(
        self,
        *,
        artifact_path: str,
        commit_sha: str,
        frontmatter: Frontmatter,
        chunks: list[Chunk],
        embeddings: list[list[float]],
    ) -> int:
        """Upsert all chunks for one artifact. Returns the number of points
        upserted. No-op (returns 0) on empty inputs."""
        if not chunks:
            return 0
        if len(chunks) != len(embeddings):
            raise ValueError(
                f"chunks/embeddings length mismatch: {len(chunks)} vs {len(embeddings)}"
            )
        for i, vec in enumerate(embeddings):
            if not vec:
                raise ValueError(f"empty embedding at index {i}")

        dim = len(embeddings[0])
        for i, vec in enumerate(embeddings):
            if len(vec) != dim:
                raise ValueError(
                    f"embedding dim mismatch at index {i}: {len(vec)} vs {dim}"
                )

        self.ensure_collection(frontmatter.visibility, dim=dim)
        name = collection_name(frontmatter.visibility)

        points = []
        for chunk, vector in zip(chunks, embeddings):
            payload = {
                "artifact_path": artifact_path,
                "commit_sha": commit_sha,
                "chunk_index": chunk.index,
                "section_title": chunk.section_title,
                "content": chunk.content,
                "char_count": chunk.char_count,
                # Denormalized frontmatter for filtering
                "fm_id": frontmatter.id,
                "tags": list(frontmatter.tags),
                "status": frontmatter.status,
                "owner": frontmatter.owner,
                "version": frontmatter.version,
            }
            points.append(
                PointStruct(
                    id=stable_point_id(artifact_path, commit_sha, chunk.index),
                    vector=list(vector),
                    payload=payload,
                )
            )

        self.client.upsert(collection_name=name, points=points)
        return len(points)

    # ── Deletion ──────────────────────────────────────────────────────────

    def delete_artifact(self, *, artifact_path: str, visibility: str) -> None:
        """Remove every chunk for the given path in this visibility scope."""
        name = collection_name(visibility)
        existing = {c.name for c in self.client.get_collections().collections}
        if name not in existing:
            return
        self.client.delete(
            collection_name=name,
            points_selector=FilterSelector(
                filter=Filter(
                    must=[
                        FieldCondition(
                            key="artifact_path",
                            match=MatchValue(value=artifact_path),
                        ),
                    ]
                )
            ),
        )

    def delete_stale_chunks(
        self,
        *,
        artifact_path: str,
        visibility: str,
        current_commit_sha: str,
    ) -> None:
        """Remove chunks whose ``commit_sha`` is **not** the current one.

        Used after re-ingestion to garbage-collect chunks from older commits
        that were superseded by the new content."""
        name = collection_name(visibility)
        existing = {c.name for c in self.client.get_collections().collections}
        if name not in existing:
            return
        self.client.delete(
            collection_name=name,
            points_selector=FilterSelector(
                filter=Filter(
                    must=[
                        FieldCondition(
                            key="artifact_path",
                            match=MatchValue(value=artifact_path),
                        ),
                    ],
                    must_not=[
                        FieldCondition(
                            key="commit_sha",
                            match=MatchValue(value=current_commit_sha),
                        ),
                    ],
                )
            ),
        )


__all__ = [
    "QdrantIndexer",
    "POINT_ID_NAMESPACE",
    "collection_name",
    "stable_point_id",
]
