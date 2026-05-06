"""Tests for hybrid search (T8)."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from server.services.search.hybrid_search import (
    HybridSearch,
    _bm25_lite,
    _normalize,
    _tokenize,
)
from server.services.search.qdrant_search import (
    QdrantSearch,
    SearchFilters,
    SearchHit,
)


# ── Helpers ────────────────────────────────────────────────────────────────


def test_tokenize_lowercases_alphanumeric():
    assert _tokenize("Hello, World! 42") == ["hello", "world", "42"]


def test_tokenize_handles_empty():
    assert _tokenize("") == []
    assert _tokenize(None) == []  # type: ignore[arg-type]


def test_normalize_handles_empty():
    assert _normalize([]) == []


def test_normalize_handles_uniform():
    assert _normalize([0.5, 0.5, 0.5]) == [1.0, 1.0, 1.0]


def test_normalize_scales_to_zero_one():
    out = _normalize([1.0, 2.0, 3.0])
    assert out == pytest.approx([0.0, 0.5, 1.0])


def test_bm25_zero_when_no_overlap():
    assert _bm25_lite(["foo"], ["bar", "baz"]) == 0.0


def test_bm25_increases_with_overlap():
    score_one = _bm25_lite(["foo"], ["foo", "bar"])
    score_three = _bm25_lite(["foo"], ["foo", "foo", "foo"])
    # Saturation: 3 occurrences scores higher but not 3x
    assert 0 < score_one < score_three < 3 * score_one


def test_bm25_dedupes_query_tokens():
    s1 = _bm25_lite(["foo"], ["foo", "bar"])
    s2 = _bm25_lite(["foo", "foo"], ["foo", "bar"])
    assert s1 == s2


# ── Construction ───────────────────────────────────────────────────────────


def test_construct_rejects_alpha_out_of_range():
    vs = MagicMock(spec=QdrantSearch)
    with pytest.raises(ValueError, match="alpha"):
        HybridSearch(vs, alpha=-0.1)
    with pytest.raises(ValueError, match="alpha"):
        HybridSearch(vs, alpha=1.5)


def test_construct_rejects_low_candidate_multiplier():
    vs = MagicMock(spec=QdrantSearch)
    with pytest.raises(ValueError, match="candidate_multiplier"):
        HybridSearch(vs, candidate_multiplier=0)


# ── Search behaviour ───────────────────────────────────────────────────────


def _hit(path: str, content: str, score: float, idx: int = 0) -> SearchHit:
    return SearchHit(
        artifact_path=path,
        chunk_index=idx,
        content=content,
        score=score,
        section_title=None,
        commit_sha="sha",
        payload={"content": content},
    )


def test_search_returns_empty_when_vector_returns_empty():
    vs = MagicMock(spec=QdrantSearch)
    vs.search.return_value = []
    h = HybridSearch(vs)
    out = h.search(
        query="hello", query_vector=[0.1], visibility="public", top_k=5
    )
    assert out == []


def test_search_overfetches_then_blends():
    """alpha=0.5 → blend of vector score and lexical score."""
    candidates = [
        _hit("a.md", "lots of agents and mcp content here", 0.50),  # high lex
        _hit("b.md", "totally unrelated text content", 0.95),  # high vec
        _hit("c.md", "mcp agents agents agents", 0.30),  # mid both
    ]
    vs = MagicMock(spec=QdrantSearch)
    vs.search.return_value = candidates
    h = HybridSearch(vs, alpha=0.5, candidate_multiplier=2)
    out = h.search(
        query="agents mcp",
        query_vector=[0.1],
        visibility="public",
        top_k=3,
    )
    assert len(out) == 3
    # Vector score is captured per-hit in `score` after blending — sorted desc.
    scores = [hit.score for hit in out]
    assert scores == sorted(scores, reverse=True)


def test_search_pure_vector_when_alpha_one():
    candidates = [
        _hit("a.md", "matching agents content", 0.50),
        _hit("b.md", "unrelated text", 0.95),
    ]
    vs = MagicMock(spec=QdrantSearch)
    vs.search.return_value = candidates
    h = HybridSearch(vs, alpha=1.0)
    out = h.search(
        query="agents", query_vector=[0.1], visibility="public", top_k=2
    )
    # alpha=1 → vector only → b.md (0.95) ranks first
    assert out[0].artifact_path == "b.md"


def test_search_pure_lexical_when_alpha_zero():
    candidates = [
        _hit("a.md", "agents agents agents", 0.10),
        _hit("b.md", "unrelated text", 0.99),
    ]
    vs = MagicMock(spec=QdrantSearch)
    vs.search.return_value = candidates
    h = HybridSearch(vs, alpha=0.0)
    out = h.search(
        query="agents", query_vector=[0.1], visibility="public", top_k=2
    )
    # alpha=0 → lexical only → a.md (heavy lexical match) ranks first
    assert out[0].artifact_path == "a.md"


def test_search_falls_back_to_vector_for_empty_query_tokens():
    """Punctuation-only query has no alphanumeric tokens."""
    candidates = [
        _hit("a.md", "ax", 0.5),
        _hit("b.md", "bx", 0.9),
    ]
    vs = MagicMock(spec=QdrantSearch)
    vs.search.return_value = candidates
    h = HybridSearch(vs)
    out = h.search(
        query="!!! ???", query_vector=[0.1], visibility="public", top_k=2
    )
    # Falls back to vector ordering — b first
    assert out[0].artifact_path == "b.md"


def test_search_passes_filters_through_to_vector_layer():
    vs = MagicMock(spec=QdrantSearch)
    vs.search.return_value = []
    h = HybridSearch(vs, candidate_multiplier=4)
    filters = SearchFilters(owner="alice")
    h.search(
        query="hi",
        query_vector=[0.1],
        visibility="public",
        filters=filters,
        top_k=10,
    )
    _, kwargs = vs.search.call_args
    assert kwargs["filters"] is filters
    assert kwargs["top_k"] == 40  # top_k * multiplier


def test_search_rejects_nonpositive_top_k():
    vs = MagicMock(spec=QdrantSearch)
    h = HybridSearch(vs)
    with pytest.raises(ValueError, match="top_k"):
        h.search(
            query="hi", query_vector=[0.1], visibility="public", top_k=0
        )
