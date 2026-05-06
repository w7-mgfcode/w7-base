"""Tests for Qdrant search & similarity (T8)."""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from server.services.search.qdrant_search import (
    QdrantSearch,
    SearchFilters,
    SearchHit,
)


# ── Fixtures ───────────────────────────────────────────────────────────────


def _fake_collections(*names: str):
    return SimpleNamespace(collections=[SimpleNamespace(name=n) for n in names])


def _fake_point(
    *,
    artifact_path: str = "knowledge/x.md",
    chunk_index: int = 0,
    content: str = "chunk content",
    score: float = 0.9,
    section_title: str | None = None,
    commit_sha: str = "abc",
    extra: dict | None = None,
):
    payload = {
        "artifact_path": artifact_path,
        "chunk_index": chunk_index,
        "content": content,
        "section_title": section_title,
        "commit_sha": commit_sha,
        "tags": ["a"],
        "status": "published",
        "owner": "alice",
        **(extra or {}),
    }
    return SimpleNamespace(score=score, payload=payload)


def _fake_vector_point(
    *, vector: list[float], path: str = "knowledge/x.md"
):
    return SimpleNamespace(
        vector=vector, payload={"artifact_path": path}
    )


@pytest.fixture
def client_with_collection():
    client = MagicMock()
    client.get_collections.return_value = _fake_collections("kb_public", "kb_private")
    return client


# ── Construction ───────────────────────────────────────────────────────────


def test_construct_requires_client():
    with pytest.raises(ValueError, match="client required"):
        QdrantSearch(client=None)  # type: ignore[arg-type]


def test_construct_rejects_nonpositive_top_k():
    client = MagicMock()
    with pytest.raises(ValueError, match="default_top_k"):
        QdrantSearch(client=client, default_top_k=0)


# ── Filter construction ────────────────────────────────────────────────────


def test_build_filter_returns_none_when_no_filters():
    assert QdrantSearch._build_filter(None) is None
    assert QdrantSearch._build_filter(SearchFilters()) is None


def test_build_filter_includes_tags_as_match_any():
    flt = QdrantSearch._build_filter(SearchFilters(tags=["agents", "mcp"]))
    assert flt is not None
    assert any(c.key == "tags" for c in flt.must)


def test_build_filter_includes_owner_as_match_value():
    flt = QdrantSearch._build_filter(SearchFilters(owner="alice"))
    assert flt is not None
    assert any(c.key == "owner" for c in flt.must)


def test_build_filter_status_match_any():
    flt = QdrantSearch._build_filter(SearchFilters(status=["published", "review"]))
    assert flt is not None
    assert any(c.key == "status" for c in flt.must)


def test_build_filter_combines_all_fields():
    flt = QdrantSearch._build_filter(
        SearchFilters(
            tags=["agents"], status=["published"], owner="alice", fm_id="abc"
        )
    )
    assert flt is not None
    assert len(flt.must) == 4


# ── search ─────────────────────────────────────────────────────────────────


def test_search_returns_empty_when_collection_missing():
    client = MagicMock()
    client.get_collections.return_value = _fake_collections()  # no collections
    search = QdrantSearch(client=client)
    out = search.search(query_vector=[0.1, 0.2], visibility="public")
    assert out == []
    client.search.assert_not_called()


def test_search_passes_collection_and_top_k(client_with_collection):
    client_with_collection.search.return_value = [_fake_point()]
    search = QdrantSearch(client=client_with_collection, default_top_k=15)
    search.search(query_vector=[0.1, 0.2], visibility="public", top_k=7)
    args, kwargs = client_with_collection.search.call_args
    assert kwargs["collection_name"] == "kb_public"
    assert kwargs["limit"] == 7
    assert kwargs["query_vector"] == [0.1, 0.2]


def test_search_uses_default_top_k_when_unset(client_with_collection):
    client_with_collection.search.return_value = []
    search = QdrantSearch(client=client_with_collection, default_top_k=42)
    search.search(query_vector=[0.1], visibility="public")
    _, kwargs = client_with_collection.search.call_args
    assert kwargs["limit"] == 42


def test_search_parses_hits(client_with_collection):
    client_with_collection.search.return_value = [
        _fake_point(
            artifact_path="knowledge/a.md",
            chunk_index=2,
            content="alpha",
            score=0.95,
            section_title="Intro",
        ),
        _fake_point(
            artifact_path="prompts/b.md",
            chunk_index=0,
            content="beta",
            score=0.85,
        ),
    ]
    search = QdrantSearch(client=client_with_collection)
    hits = search.search(query_vector=[0.1, 0.2], visibility="public")
    assert len(hits) == 2
    assert hits[0].artifact_path == "knowledge/a.md"
    assert hits[0].score == 0.95
    assert hits[0].section_title == "Intro"
    assert hits[1].artifact_path == "prompts/b.md"


def test_search_rejects_empty_query_vector(client_with_collection):
    search = QdrantSearch(client=client_with_collection)
    with pytest.raises(ValueError, match="non-empty"):
        search.search(query_vector=[], visibility="public")


def test_search_rejects_nonpositive_top_k(client_with_collection):
    search = QdrantSearch(client=client_with_collection)
    with pytest.raises(ValueError, match="top_k"):
        search.search(query_vector=[0.1], visibility="public", top_k=0)


def test_search_passes_filter_when_supplied(client_with_collection):
    client_with_collection.search.return_value = []
    search = QdrantSearch(client=client_with_collection)
    search.search(
        query_vector=[0.1, 0.2],
        visibility="public",
        filters=SearchFilters(owner="alice"),
    )
    _, kwargs = client_with_collection.search.call_args
    assert kwargs["query_filter"] is not None


# ── Centroid / related_to_artifact ─────────────────────────────────────────


def test_centroid_returns_none_when_collection_missing():
    client = MagicMock()
    client.get_collections.return_value = _fake_collections()
    search = QdrantSearch(client=client)
    centroid = search.get_artifact_centroid(
        artifact_path="knowledge/x.md", visibility="public"
    )
    assert centroid is None


def test_centroid_returns_none_when_no_chunks(client_with_collection):
    client_with_collection.scroll.return_value = ([], None)
    search = QdrantSearch(client=client_with_collection)
    centroid = search.get_artifact_centroid(
        artifact_path="knowledge/missing.md", visibility="public"
    )
    assert centroid is None


def test_centroid_averages_vectors(client_with_collection):
    points = [
        _fake_vector_point(vector=[1.0, 2.0, 3.0]),
        _fake_vector_point(vector=[3.0, 4.0, 5.0]),
        _fake_vector_point(vector=[5.0, 6.0, 7.0]),
    ]
    client_with_collection.scroll.return_value = (points, None)
    search = QdrantSearch(client=client_with_collection)
    centroid = search.get_artifact_centroid(
        artifact_path="knowledge/x.md", visibility="public"
    )
    assert centroid == [3.0, 4.0, 5.0]  # mean of the three vectors


def test_centroid_paginates_via_scroll(client_with_collection):
    """Scroll returns ``(points, next_offset)`` repeatedly until ``None`` offset."""
    page1 = [_fake_vector_point(vector=[1.0, 1.0])]
    page2 = [_fake_vector_point(vector=[3.0, 3.0])]
    client_with_collection.scroll.side_effect = [
        (page1, "tok"),
        (page2, None),
    ]
    search = QdrantSearch(client=client_with_collection, scroll_batch_size=1)
    centroid = search.get_artifact_centroid(
        artifact_path="knowledge/x.md", visibility="public"
    )
    assert centroid == [2.0, 2.0]
    assert client_with_collection.scroll.call_count == 2


def test_related_returns_empty_when_no_centroid(client_with_collection):
    client_with_collection.scroll.return_value = ([], None)
    search = QdrantSearch(client=client_with_collection)
    out = search.related_to_artifact(
        artifact_path="knowledge/x.md", visibility="public", k=5
    )
    assert out == []


def test_related_excludes_self_by_default(client_with_collection):
    # Centroid available
    client_with_collection.scroll.return_value = (
        [_fake_vector_point(vector=[1.0, 1.0])],
        None,
    )
    # Search returns a mix of self + others
    client_with_collection.search.return_value = [
        _fake_point(artifact_path="knowledge/x.md", chunk_index=0, score=0.99),
        _fake_point(artifact_path="knowledge/y.md", chunk_index=0, score=0.95),
        _fake_point(artifact_path="knowledge/x.md", chunk_index=1, score=0.94),
        _fake_point(artifact_path="knowledge/z.md", chunk_index=0, score=0.92),
    ]
    search = QdrantSearch(client=client_with_collection)
    out = search.related_to_artifact(
        artifact_path="knowledge/x.md", visibility="public", k=5
    )
    paths = [h.artifact_path for h in out]
    assert "knowledge/x.md" not in paths
    assert paths == ["knowledge/y.md", "knowledge/z.md"]


def test_related_keeps_self_when_exclude_false(client_with_collection):
    client_with_collection.scroll.return_value = (
        [_fake_vector_point(vector=[1.0, 1.0])],
        None,
    )
    client_with_collection.search.return_value = [
        _fake_point(artifact_path="knowledge/x.md", score=0.99),
        _fake_point(artifact_path="knowledge/y.md", score=0.95),
    ]
    search = QdrantSearch(client=client_with_collection)
    out = search.related_to_artifact(
        artifact_path="knowledge/x.md",
        visibility="public",
        k=5,
        exclude_self=False,
    )
    paths = [h.artifact_path for h in out]
    assert "knowledge/x.md" in paths


def test_related_rejects_nonpositive_k(client_with_collection):
    search = QdrantSearch(client=client_with_collection)
    with pytest.raises(ValueError, match="k must be"):
        search.related_to_artifact(
            artifact_path="knowledge/x.md", visibility="public", k=0
        )
