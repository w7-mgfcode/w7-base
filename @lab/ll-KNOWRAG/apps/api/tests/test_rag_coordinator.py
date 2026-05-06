"""Tests for the RAG coordinator (T8)."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from server.services.search.qdrant_search import SearchHit
from server.services.search.rag_coordinator import RagCoordinator


# ── Fixtures ───────────────────────────────────────────────────────────────


def _hit(
    path: str = "knowledge/x.md",
    chunk_index: int = 0,
    score: float = 0.9,
    section_title: str | None = None,
    tags=None,
    owner: str = "alice",
) -> SearchHit:
    return SearchHit(
        artifact_path=path,
        chunk_index=chunk_index,
        content=f"content of {path}#{chunk_index}",
        score=score,
        section_title=section_title,
        commit_sha="sha",
        payload={"tags": tags or [], "status": "published", "owner": owner},
    )


def _make_coord(*, vector_hits=None, hybrid_hits=None, related_hits=None):
    embedder = MagicMock()
    embedder.embed_batch = AsyncMock(return_value=[[0.1, 0.2, 0.3]])
    vs = MagicMock()
    vs.search = MagicMock(return_value=vector_hits or [])
    vs.related_to_artifact = MagicMock(return_value=related_hits or [])
    hs = None
    if hybrid_hits is not None:
        hs = MagicMock()
        hs.search = MagicMock(return_value=hybrid_hits)
    rr = MagicMock()
    rr.rerank = MagicMock(side_effect=lambda q, h, top_n=None: h[::-1])
    coord = RagCoordinator(
        embedder=embedder, vector_search=vs, hybrid_search=hs, reranker=rr
    )
    return coord, embedder, vs, hs, rr


# ── Validation ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_query_rejects_empty_query():
    coord, *_ = _make_coord()
    with pytest.raises(ValueError, match="non-empty"):
        await coord.query(query="")


@pytest.mark.asyncio
async def test_query_rejects_whitespace_query():
    coord, *_ = _make_coord()
    with pytest.raises(ValueError, match="non-empty"):
        await coord.query(query="   ")


@pytest.mark.asyncio
async def test_query_rejects_nonpositive_top_k():
    coord, *_ = _make_coord()
    with pytest.raises(ValueError, match="top_k"):
        await coord.query(query="hi", top_k=0)


@pytest.mark.asyncio
async def test_query_raises_on_empty_embedding():
    coord, embedder, *_ = _make_coord()
    embedder.embed_batch = AsyncMock(return_value=[[]])
    with pytest.raises(RuntimeError, match="embedder returned"):
        await coord.query(query="hi")


# ── Search routing ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_query_uses_vector_search_by_default():
    coord, _, vs, hs, _ = _make_coord(vector_hits=[_hit()])
    result = await coord.query(query="hello", top_k=10)
    vs.search.assert_called_once()
    assert hs is None  # no hybrid configured
    assert len(result["hits"]) == 1


@pytest.mark.asyncio
async def test_query_uses_hybrid_when_requested_and_configured():
    coord, _, vs, hs, _ = _make_coord(
        vector_hits=[_hit("a.md")],
        hybrid_hits=[_hit("b.md", score=0.95)],
    )
    result = await coord.query(query="hello", use_hybrid=True)
    hs.search.assert_called_once()
    vs.search.assert_not_called()
    assert result["hits"][0]["artifact_path"] == "b.md"


@pytest.mark.asyncio
async def test_query_falls_back_to_vector_when_hybrid_requested_but_unconfigured():
    coord, _, vs, _, _ = _make_coord(vector_hits=[_hit()])
    # No hybrid_search supplied
    result = await coord.query(query="hello", use_hybrid=True)
    vs.search.assert_called_once()
    assert len(result["hits"]) == 1


# ── Rerank ─────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_query_applies_rerank_when_requested():
    hits = [_hit(path="a.md", score=0.99), _hit(path="b.md", score=0.50)]
    coord, _, _, _, rr = _make_coord(vector_hits=hits)
    result = await coord.query(query="hello", use_rerank=True)
    rr.rerank.assert_called_once()
    # Our mock reverses — so b.md should now come first
    assert result["hits"][0]["artifact_path"] == "b.md"


@pytest.mark.asyncio
async def test_query_falls_back_when_reranker_raises():
    hits = [_hit(path="a.md"), _hit(path="b.md")]
    coord, _, _, _, rr = _make_coord(vector_hits=hits)
    rr.rerank = MagicMock(side_effect=RuntimeError("rerank exploded"))
    result = await coord.query(query="hello", use_rerank=True)
    # Original order preserved
    paths = [h["artifact_path"] for h in result["hits"]]
    assert paths == ["a.md", "b.md"]


@pytest.mark.asyncio
async def test_rerank_skipped_when_no_hits():
    coord, _, _, _, rr = _make_coord(vector_hits=[])
    await coord.query(query="hello", use_rerank=True)
    rr.rerank.assert_not_called()


# ── Page-mode grouping ─────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_chunk_mode_omits_pages_field():
    coord, *_ = _make_coord(vector_hits=[_hit()])
    result = await coord.query(query="hello", mode="chunk")
    assert "pages" not in result


@pytest.mark.asyncio
async def test_page_mode_groups_chunks_by_artifact():
    hits = [
        _hit(path="a.md", chunk_index=0, score=0.99, section_title="Intro"),
        _hit(path="a.md", chunk_index=1, score=0.95, section_title="Body"),
        _hit(path="b.md", chunk_index=0, score=0.80),
        _hit(path="a.md", chunk_index=2, score=0.70, section_title="Body"),
    ]
    coord, *_ = _make_coord(vector_hits=hits)
    result = await coord.query(query="hello", mode="page")
    pages = result["pages"]
    paths = [p["artifact_path"] for p in pages]
    assert paths == ["a.md", "b.md"]
    a_page = pages[0]
    assert a_page["chunk_count"] == 3
    assert a_page["top_score"] == 0.99
    assert "Intro" in a_page["section_titles"]
    assert "Body" in a_page["section_titles"]
    assert len(a_page["section_titles"]) == 2  # deduped


@pytest.mark.asyncio
async def test_page_mode_with_no_hits_returns_empty_pages():
    coord, *_ = _make_coord(vector_hits=[])
    result = await coord.query(query="hello", mode="page")
    assert result["pages"] == []


# ── Related ────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_related_returns_unique_artifacts():
    hits = [
        _hit(path="b.md", chunk_index=0, score=0.99),
        _hit(path="b.md", chunk_index=1, score=0.95),
        _hit(path="c.md", chunk_index=0, score=0.85),
        _hit(path="d.md", chunk_index=0, score=0.80),
    ]
    coord, _, vs, _, _ = _make_coord(related_hits=hits)
    out = await coord.related(artifact_path="a.md", k=3)
    paths = [h["artifact_path"] for h in out]
    assert paths == ["b.md", "c.md", "d.md"]


@pytest.mark.asyncio
async def test_related_returns_empty_when_no_hits():
    coord, *_ = _make_coord(related_hits=[])
    out = await coord.related(artifact_path="a.md", k=5)
    assert out == []


@pytest.mark.asyncio
async def test_related_respects_k_limit():
    hits = [_hit(path=f"x{i}.md", chunk_index=0) for i in range(20)]
    coord, *_ = _make_coord(related_hits=hits)
    out = await coord.related(artifact_path="seed.md", k=3)
    assert len(out) == 3


# ── Hit-to-dict shape ──────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_hit_dict_contains_expected_fields():
    hits = [_hit(path="a.md", section_title="Section", tags=["x"])]
    coord, *_ = _make_coord(vector_hits=hits)
    result = await coord.query(query="hello")
    h = result["hits"][0]
    assert set(h.keys()) >= {
        "artifact_path",
        "chunk_index",
        "content",
        "score",
        "section_title",
        "commit_sha",
        "tags",
        "status",
        "owner",
    }
    assert h["section_title"] == "Section"
    assert h["tags"] == ["x"]
