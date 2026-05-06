"""Hybrid search — vector candidates re-scored with lexical signal (Phase 8).

Phase 7 used Postgres ``tsvector`` for the lexical half of hybrid search.
Qdrant has no equivalent built-in, so we approximate: over-fetch from vector
search, score each candidate by client-side BM25-lite token overlap with the
query, then blend the two signals.

This trades a small amount of recall for zero new infrastructure. To upgrade
later, wire FastEmbed sparse-vectors at ingest time and replace the lexical
path with a Qdrant sparse-vector query (no consumer-side change required).
"""
from __future__ import annotations

import logging
import math
import re
from collections import Counter
from typing import Sequence

from server.services.search.qdrant_search import (
    QdrantSearch,
    SearchFilters,
    SearchHit,
)

logger = logging.getLogger(__name__)

_TOKEN_RE = re.compile(r"[A-Za-z0-9]+")


def _tokenize(text: str) -> list[str]:
    return [t.lower() for t in _TOKEN_RE.findall(text or "")]


def _bm25_lite(query_tokens: list[str], doc_tokens: list[str]) -> float:
    """A small BM25-flavoured score, no IDF (single-doc context).

    Uses the BM25 saturation curve (k1=1.5, b=0.75) over a normalized doc
    length. No corpus-level IDF — we're scoring *within* the candidate set
    that vector search returned, so relative scores are what matters.
    """
    if not query_tokens or not doc_tokens:
        return 0.0
    k1 = 1.5
    b = 0.75
    avg_dl = 1500  # a sensible default given our chunk size target
    dl = len(doc_tokens)
    counts = Counter(doc_tokens)
    score = 0.0
    seen = set()
    for q in query_tokens:
        if q in seen:
            continue
        seen.add(q)
        f = counts.get(q, 0)
        if f == 0:
            continue
        denom = f + k1 * (1 - b + b * dl / avg_dl)
        score += (f * (k1 + 1)) / denom
    return score


def _normalize(values: Sequence[float]) -> list[float]:
    if not values:
        return []
    lo = min(values)
    hi = max(values)
    if math.isclose(hi, lo):
        return [1.0] * len(values)
    span = hi - lo
    return [(v - lo) / span for v in values]


class HybridSearch:
    """Vector kNN candidates re-scored by lexical BM25-lite."""

    def __init__(
        self,
        vector_search: QdrantSearch,
        *,
        alpha: float = 0.5,
        candidate_multiplier: int = 3,
    ) -> None:
        if not 0.0 <= alpha <= 1.0:
            raise ValueError("alpha must be in [0, 1]")
        if candidate_multiplier < 1:
            raise ValueError("candidate_multiplier must be >= 1")
        self.vector_search = vector_search
        self.alpha = alpha
        self.candidate_multiplier = candidate_multiplier

    def search(
        self,
        *,
        query: str,
        query_vector: Sequence[float],
        visibility: str,
        filters: SearchFilters | None = None,
        top_k: int = 20,
    ) -> list[SearchHit]:
        """Return ``top_k`` results re-ranked by ``alpha * vector + (1-alpha) * lexical``."""
        if top_k <= 0:
            raise ValueError("top_k must be > 0")
        candidates = self.vector_search.search(
            query_vector=query_vector,
            visibility=visibility,
            filters=filters,
            top_k=top_k * self.candidate_multiplier,
        )
        if not candidates:
            return []

        query_tokens = _tokenize(query)
        if not query_tokens:
            # No alphanumeric query — fall back to pure vector ordering.
            return sorted(candidates, key=lambda h: h.score, reverse=True)[:top_k]

        vector_scores = [h.score for h in candidates]
        lexical_scores = [
            _bm25_lite(query_tokens, _tokenize(h.content)) for h in candidates
        ]
        norm_vec = _normalize(vector_scores)
        norm_lex = _normalize(lexical_scores)

        merged: list[tuple[float, SearchHit]] = []
        for hit, v, l in zip(candidates, norm_vec, norm_lex):
            blended = self.alpha * v + (1.0 - self.alpha) * l
            merged.append((blended, hit))
        merged.sort(key=lambda pair: pair[0], reverse=True)

        # Replace each hit's score with the blended score for downstream
        # consumers (page grouping, reranking, UI display).
        out: list[SearchHit] = []
        for blended, hit in merged[:top_k]:
            out.append(
                SearchHit(
                    artifact_path=hit.artifact_path,
                    chunk_index=hit.chunk_index,
                    content=hit.content,
                    score=blended,
                    section_title=hit.section_title,
                    commit_sha=hit.commit_sha,
                    payload=hit.payload,
                )
            )
        return out


__all__ = ["HybridSearch"]
