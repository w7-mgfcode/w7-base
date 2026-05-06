"""Qdrant search & similarity (Phase 8 — T8).

Two surfaces:

- :meth:`QdrantSearch.search` — straight vector kNN with frontmatter filters
  pushed down to Qdrant via payload conditions.
- :meth:`QdrantSearch.related_to_artifact` — centroid-based "find similar"
  starting from all chunks of a given artifact path.

Decoupled from the indexer: the writer (T7 :mod:`qdrant_indexer`) and the
reader live in different services so a deployment can scale them apart.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Iterable, Protocol, Sequence

from qdrant_client.models import (
    FieldCondition,
    Filter,
    MatchAny,
    MatchValue,
)

from server.services.search.qdrant_indexer import collection_name

logger = logging.getLogger(__name__)


# ── Models ─────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class SearchHit:
    """One Qdrant search result, decoded into our domain types."""

    artifact_path: str
    chunk_index: int
    content: str
    score: float
    section_title: str | None
    commit_sha: str
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SearchFilters:
    """Frontmatter filters pushed down to Qdrant via payload conditions."""

    tags: Sequence[str] | None = None
    status: Sequence[str] | None = None  # any-of
    owner: str | None = None
    fm_id: str | None = None


# ── Protocol ───────────────────────────────────────────────────────────────


class _QdrantClientProto(Protocol):
    def query_points(
        self,
        collection_name: str,
        query,
        limit: int,
        query_filter=None,
        with_payload: bool = True,
        **kwargs,
    ): ...

    def scroll(
        self,
        collection_name: str,
        scroll_filter=None,
        limit: int = 100,
        with_payload: bool = True,
        with_vectors: bool = False,
        offset=None,
        **kwargs,
    ): ...

    def get_collections(self): ...


# ── Search class ───────────────────────────────────────────────────────────


class QdrantSearch:
    """Reader-side Qdrant operations: kNN search + artifact centroid."""

    def __init__(
        self,
        client: _QdrantClientProto,
        *,
        default_top_k: int = 20,
        scroll_batch_size: int = 256,
    ) -> None:
        if client is None:
            raise ValueError("client required")
        if default_top_k <= 0:
            raise ValueError("default_top_k must be > 0")
        self.client = client
        self.default_top_k = default_top_k
        self.scroll_batch_size = scroll_batch_size

    # ── Filter construction ───────────────────────────────────────────────

    @staticmethod
    def _build_filter(filters: SearchFilters | None) -> Filter | None:
        if filters is None:
            return None
        must: list[FieldCondition] = []
        if filters.tags:
            must.append(
                FieldCondition(key="tags", match=MatchAny(any=list(filters.tags)))
            )
        if filters.status:
            must.append(
                FieldCondition(key="status", match=MatchAny(any=list(filters.status)))
            )
        if filters.owner:
            must.append(
                FieldCondition(key="owner", match=MatchValue(value=filters.owner))
            )
        if filters.fm_id:
            must.append(
                FieldCondition(key="fm_id", match=MatchValue(value=filters.fm_id))
            )
        if not must:
            return None
        return Filter(must=must)

    @staticmethod
    def _hit_from_point(point: Any) -> SearchHit:
        payload = dict(point.payload or {})
        return SearchHit(
            artifact_path=payload.get("artifact_path", ""),
            chunk_index=int(payload.get("chunk_index", 0)),
            content=payload.get("content", ""),
            score=float(getattr(point, "score", 0.0) or 0.0),
            section_title=payload.get("section_title"),
            commit_sha=payload.get("commit_sha", ""),
            payload=payload,
        )

    def _collection_exists(self, name: str) -> bool:
        return name in {c.name for c in self.client.get_collections().collections}

    # ── Search ────────────────────────────────────────────────────────────

    def search(
        self,
        *,
        query_vector: Sequence[float],
        visibility: str,
        filters: SearchFilters | None = None,
        top_k: int | None = None,
    ) -> list[SearchHit]:
        """Run a vector kNN with optional payload filters.

        Returns an empty list if the collection doesn't exist yet — fresh
        installs with no ingested data return [] rather than raising.
        """
        if not query_vector:
            raise ValueError("query_vector must be non-empty")
        if top_k is not None and top_k <= 0:
            raise ValueError("top_k must be > 0")
        k = top_k if top_k is not None else self.default_top_k
        name = collection_name(visibility)
        if not self._collection_exists(name):
            return []
        response = self.client.query_points(
            collection_name=name,
            query=list(query_vector),
            limit=k,
            query_filter=self._build_filter(filters),
            with_payload=True,
        )
        # qdrant-client 1.13+: query_points returns QueryResponse with .points;
        # tolerate either shape so adapter mocks can pass a list directly.
        points = getattr(response, "points", response)
        return [self._hit_from_point(p) for p in points]

    # ── Centroid / related ────────────────────────────────────────────────

    def get_artifact_centroid(
        self, *, artifact_path: str, visibility: str
    ) -> list[float] | None:
        """Average vector across every chunk of an artifact. ``None`` if no
        chunks exist for that path."""
        name = collection_name(visibility)
        if not self._collection_exists(name):
            return None

        flt = Filter(
            must=[
                FieldCondition(
                    key="artifact_path",
                    match=MatchValue(value=artifact_path),
                )
            ]
        )
        offset = None
        sum_vec: list[float] | None = None
        count = 0
        while True:
            points, offset = self.client.scroll(
                collection_name=name,
                scroll_filter=flt,
                limit=self.scroll_batch_size,
                with_payload=False,
                with_vectors=True,
                offset=offset,
            )
            if not points:
                break
            for p in points:
                vec = getattr(p, "vector", None)
                if not vec:
                    continue
                if sum_vec is None:
                    sum_vec = list(vec)
                else:
                    for i, v in enumerate(vec):
                        sum_vec[i] += float(v)
                count += 1
            if offset is None:
                break

        if count == 0 or sum_vec is None:
            return None
        return [v / count for v in sum_vec]

    def related_to_artifact(
        self,
        *,
        artifact_path: str,
        visibility: str,
        k: int = 5,
        exclude_self: bool = True,
        filters: SearchFilters | None = None,
    ) -> list[SearchHit]:
        """Find chunks similar to the centroid of an artifact's own chunks.

        Returns up to ``k`` hits, optionally excluding chunks belonging to
        the seed artifact itself."""
        if k <= 0:
            raise ValueError("k must be > 0")
        centroid = self.get_artifact_centroid(
            artifact_path=artifact_path, visibility=visibility
        )
        if centroid is None:
            return []
        # Over-fetch so exclude_self can drop self-hits and still return k.
        fetch = k * 4 if exclude_self else k
        hits = self.search(
            query_vector=centroid,
            visibility=visibility,
            filters=filters,
            top_k=fetch,
        )
        if exclude_self:
            hits = [h for h in hits if h.artifact_path != artifact_path]
        return hits[:k]


__all__ = ["QdrantSearch", "SearchFilters", "SearchHit"]
