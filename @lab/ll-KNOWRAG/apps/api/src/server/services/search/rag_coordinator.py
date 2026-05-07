"""RAG retrieval coordinator.

Composes embed → search (vector or hybrid) → optional rerank → optional
page grouping. Drives the ``/api/artifacts/search`` and
``/api/artifacts/{path}/related`` routes.
"""
from __future__ import annotations

import logging
from collections import OrderedDict
from typing import Awaitable, Callable, Literal, Protocol, Sequence

from server.services.knowledge.ingest_pipeline import Embedder
from server.services.search.hybrid_search import HybridSearch
from server.services.search.qdrant_search import (
    QdrantSearch,
    SearchFilters,
    SearchHit,
)

logger = logging.getLogger(__name__)

ReturnMode = Literal["chunk", "page"]


class _Reranker(Protocol):
    """Minimal reranker interface — synchronous or async, takes hits + query."""

    def rerank(
        self, query: str, hits: list[SearchHit], top_n: int | None = None
    ) -> list[SearchHit]: ...


class RagCoordinator:
    """Orchestrates the embed → search → rerank → group flow."""

    def __init__(
        self,
        *,
        embedder: Embedder,
        vector_search: QdrantSearch,
        hybrid_search: HybridSearch | None = None,
        reranker: _Reranker | None = None,
    ) -> None:
        self.embedder = embedder
        self.vector_search = vector_search
        self.hybrid_search = hybrid_search
        self.reranker = reranker

    async def query(
        self,
        *,
        query: str,
        visibility: str = "public",
        filters: SearchFilters | None = None,
        top_k: int = 20,
        mode: ReturnMode = "chunk",
        use_hybrid: bool = False,
        use_rerank: bool = False,
    ) -> dict:
        """Run a RAG query. Returns ``{hits, pages?, query_time_ms?}``."""
        if not query or not query.strip():
            raise ValueError("query must be non-empty")
        if top_k <= 0:
            raise ValueError("top_k must be > 0")

        embeddings = await self.embedder.embed_batch([query])
        if not embeddings or not embeddings[0]:
            raise RuntimeError("embedder returned empty result for query")
        query_vector = embeddings[0]

        if use_hybrid and self.hybrid_search is not None:
            hits = self.hybrid_search.search(
                query=query,
                query_vector=query_vector,
                visibility=visibility,
                filters=filters,
                top_k=top_k,
            )
        else:
            hits = self.vector_search.search(
                query_vector=query_vector,
                visibility=visibility,
                filters=filters,
                top_k=top_k,
            )

        if use_rerank and self.reranker is not None and hits:
            try:
                hits = self.reranker.rerank(query, hits, top_n=top_k)
            except Exception as exc:  # noqa: BLE001 — reranker is best-effort
                logger.warning("reranker failed, falling back to raw hits: %s", exc)

        out: dict = {"hits": [self._hit_to_dict(h) for h in hits]}
        if mode == "page":
            out["pages"] = self._group_by_page(hits)
        return out

    async def related(
        self,
        *,
        artifact_path: str,
        visibility: str = "public",
        k: int = 5,
        filters: SearchFilters | None = None,
    ) -> list[dict]:
        """Find ``k`` artifacts similar to ``artifact_path``."""
        hits = self.vector_search.related_to_artifact(
            artifact_path=artifact_path,
            visibility=visibility,
            k=k * 4,  # over-fetch so we can dedupe by artifact_path
            exclude_self=True,
            filters=filters,
        )
        # Dedupe by artifact_path so we return one entry per related artifact.
        seen: set[str] = set()
        unique: list[SearchHit] = []
        for h in hits:
            if h.artifact_path in seen:
                continue
            seen.add(h.artifact_path)
            unique.append(h)
            if len(unique) >= k:
                break
        return [self._hit_to_dict(h) for h in unique]

    # ── Internals ─────────────────────────────────────────────────────────

    @staticmethod
    def _hit_to_dict(h: SearchHit) -> dict:
        return {
            "artifact_path": h.artifact_path,
            "chunk_index": h.chunk_index,
            "content": h.content,
            "score": h.score,
            "section_title": h.section_title,
            "commit_sha": h.commit_sha,
            "tags": h.payload.get("tags", []),
            "status": h.payload.get("status"),
            "owner": h.payload.get("owner"),
        }

    @staticmethod
    def _group_by_page(hits: list[SearchHit]) -> list[dict]:
        """Group chunks by ``artifact_path``. Each page entry carries the
        top chunk's score (already sorted by score upstream)."""
        groups: "OrderedDict[str, dict]" = OrderedDict()
        for h in hits:
            entry = groups.get(h.artifact_path)
            if entry is None:
                groups[h.artifact_path] = {
                    "artifact_path": h.artifact_path,
                    "top_score": h.score,
                    "top_chunk_index": h.chunk_index,
                    "section_titles": (
                        [h.section_title] if h.section_title else []
                    ),
                    "chunk_count": 1,
                    "owner": h.payload.get("owner"),
                    "tags": h.payload.get("tags", []),
                }
            else:
                entry["chunk_count"] += 1
                if h.section_title and h.section_title not in entry["section_titles"]:
                    entry["section_titles"].append(h.section_title)
        return list(groups.values())


__all__ = ["RagCoordinator", "ReturnMode"]
