"""Tests for Qdrant indexer (T7)."""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from server.services.knowledge.chunker import Chunk
from server.services.knowledge.frontmatter import Frontmatter
from server.services.search.qdrant_indexer import (
    QdrantIndexer,
    collection_name,
    stable_point_id,
)


# ── Helpers ────────────────────────────────────────────────────────────────


def _fake_client(existing_collections: list[str] | None = None) -> MagicMock:
    """Build a MagicMock that satisfies the protocol."""
    client = MagicMock()
    cols = existing_collections or []
    client.get_collections.return_value = SimpleNamespace(
        collections=[SimpleNamespace(name=n) for n in cols]
    )
    return client


def _make_fm(visibility: str = "public", **kwargs) -> Frontmatter:
    defaults = dict(id="x", owner="alice", visibility=visibility)
    defaults.update(kwargs)
    return Frontmatter(**defaults)


def _make_chunks(n: int) -> list[Chunk]:
    return [
        Chunk(index=i, content=f"chunk {i} content", char_count=15, section_title=None)
        for i in range(n)
    ]


def _make_embeddings(n: int, dim: int = 4) -> list[list[float]]:
    return [[float(i + j) for j in range(dim)] for i in range(n)]


# ── Helpers (collection_name, stable_point_id) ────────────────────────────


def test_collection_name_public():
    assert collection_name("public") == "kb_public"


def test_collection_name_private():
    assert collection_name("private") == "kb_private"


def test_collection_name_invalid_raises():
    with pytest.raises(ValueError, match="unsupported visibility"):
        collection_name("secret")


def test_stable_point_id_is_deterministic():
    a = stable_point_id("knowledge/x.md", "abc", 0)
    b = stable_point_id("knowledge/x.md", "abc", 0)
    assert a == b


def test_stable_point_id_changes_on_chunk_index():
    a = stable_point_id("knowledge/x.md", "abc", 0)
    b = stable_point_id("knowledge/x.md", "abc", 1)
    assert a != b


def test_stable_point_id_changes_on_commit():
    a = stable_point_id("knowledge/x.md", "abc", 0)
    b = stable_point_id("knowledge/x.md", "def", 0)
    assert a != b


def test_stable_point_id_is_uuid_format():
    pid = stable_point_id("knowledge/x.md", "abc", 0)
    # UUID has 36 chars including hyphens
    assert len(pid) == 36
    assert pid.count("-") == 4


# ── Construction ───────────────────────────────────────────────────────────


def test_construct_requires_client():
    with pytest.raises(ValueError, match="client required"):
        QdrantIndexer(client=None)  # type: ignore[arg-type]


def test_construct_rejects_zero_dim():
    with pytest.raises(ValueError, match="default_dim"):
        QdrantIndexer(client=_fake_client(), default_dim=0)


# ── ensure_collection ──────────────────────────────────────────────────────


def test_ensure_collection_creates_when_missing():
    client = _fake_client(existing_collections=[])
    indexer = QdrantIndexer(client=client, default_dim=4)
    created = indexer.ensure_collection("public")
    assert created is True
    client.create_collection.assert_called_once()
    args, kwargs = client.create_collection.call_args
    assert kwargs["collection_name"] == "kb_public"


def test_ensure_collection_skips_when_existing():
    client = _fake_client(existing_collections=["kb_public"])
    indexer = QdrantIndexer(client=client, default_dim=4)
    created = indexer.ensure_collection("public")
    assert created is False
    client.create_collection.assert_not_called()


def test_ensure_collection_uses_explicit_dim():
    client = _fake_client(existing_collections=[])
    indexer = QdrantIndexer(client=client, default_dim=4)
    indexer.ensure_collection("public", dim=1024)
    _, kwargs = client.create_collection.call_args
    assert kwargs["vectors_config"].size == 1024


def test_ensure_collection_creates_payload_indexes_for_filter_fields():
    from server.services.search.qdrant_indexer import FILTER_PAYLOAD_FIELDS
    from qdrant_client.models import PayloadSchemaType
    client = _fake_client(existing_collections=[])
    indexer = QdrantIndexer(client=client, default_dim=4)
    indexer.ensure_collection("public")
    indexed = {
        c.kwargs["field_name"]: c.kwargs["field_schema"]
        for c in client.create_payload_index.call_args_list
    }
    assert set(indexed) == set(FILTER_PAYLOAD_FIELDS)
    assert all(s == PayloadSchemaType.KEYWORD for s in indexed.values())


def test_ensure_collection_skips_payload_indexes_when_collection_exists():
    client = _fake_client(existing_collections=["kb_public"])
    indexer = QdrantIndexer(client=client, default_dim=4)
    indexer.ensure_collection("public")
    client.create_payload_index.assert_not_called()


# ── upsert ─────────────────────────────────────────────────────────────────


def test_upsert_empty_chunks_is_noop():
    client = _fake_client()
    indexer = QdrantIndexer(client=client)
    n = indexer.upsert(
        artifact_path="knowledge/x.md",
        commit_sha="abc",
        frontmatter=_make_fm(),
        chunks=[],
        embeddings=[],
    )
    assert n == 0
    client.upsert.assert_not_called()


def test_upsert_length_mismatch_raises():
    client = _fake_client(existing_collections=["kb_public"])
    indexer = QdrantIndexer(client=client)
    with pytest.raises(ValueError, match="length mismatch"):
        indexer.upsert(
            artifact_path="knowledge/x.md",
            commit_sha="a",
            frontmatter=_make_fm(),
            chunks=_make_chunks(2),
            embeddings=_make_embeddings(3),
        )


def test_upsert_dim_mismatch_raises():
    client = _fake_client(existing_collections=["kb_public"])
    indexer = QdrantIndexer(client=client)
    chunks = _make_chunks(2)
    embeddings = [[1.0, 2.0, 3.0], [1.0, 2.0]]  # different dims
    with pytest.raises(ValueError, match="dim mismatch"):
        indexer.upsert(
            artifact_path="knowledge/x.md",
            commit_sha="a",
            frontmatter=_make_fm(),
            chunks=chunks,
            embeddings=embeddings,
        )


def test_upsert_empty_embedding_raises():
    client = _fake_client(existing_collections=["kb_public"])
    indexer = QdrantIndexer(client=client)
    with pytest.raises(ValueError, match="empty embedding"):
        indexer.upsert(
            artifact_path="knowledge/x.md",
            commit_sha="a",
            frontmatter=_make_fm(),
            chunks=_make_chunks(1),
            embeddings=[[]],
        )


def test_upsert_creates_collection_if_missing():
    client = _fake_client(existing_collections=[])
    indexer = QdrantIndexer(client=client, default_dim=4)
    indexer.upsert(
        artifact_path="knowledge/x.md",
        commit_sha="a",
        frontmatter=_make_fm(),
        chunks=_make_chunks(2),
        embeddings=_make_embeddings(2, dim=4),
    )
    client.create_collection.assert_called_once()


def test_upsert_uses_visibility_collection():
    client = _fake_client(existing_collections=["kb_private"])
    indexer = QdrantIndexer(client=client)
    indexer.upsert(
        artifact_path="knowledge/x.md",
        commit_sha="a",
        frontmatter=_make_fm(visibility="private"),
        chunks=_make_chunks(1),
        embeddings=_make_embeddings(1, dim=4),
    )
    _, kwargs = client.upsert.call_args
    assert kwargs["collection_name"] == "kb_private"


def test_upsert_payload_includes_denormalized_frontmatter():
    client = _fake_client(existing_collections=["kb_public"])
    indexer = QdrantIndexer(client=client)
    fm = _make_fm(tags=["a", "b"], status="published", version="1.0.0")
    indexer.upsert(
        artifact_path="knowledge/x.md",
        commit_sha="abc",
        frontmatter=fm,
        chunks=_make_chunks(1),
        embeddings=_make_embeddings(1, dim=4),
    )
    _, kwargs = client.upsert.call_args
    points = kwargs["points"]
    assert len(points) == 1
    payload = points[0].payload
    assert payload["artifact_path"] == "knowledge/x.md"
    assert payload["commit_sha"] == "abc"
    assert payload["chunk_index"] == 0
    assert payload["tags"] == ["a", "b"]
    assert payload["status"] == "published"
    assert payload["owner"] == "alice"
    assert payload["fm_id"] == "x"


def test_upsert_uses_deterministic_point_ids():
    client = _fake_client(existing_collections=["kb_public"])
    indexer = QdrantIndexer(client=client)
    indexer.upsert(
        artifact_path="knowledge/x.md",
        commit_sha="abc",
        frontmatter=_make_fm(),
        chunks=_make_chunks(2),
        embeddings=_make_embeddings(2, dim=4),
    )
    _, kwargs = client.upsert.call_args
    ids = [p.id for p in kwargs["points"]]
    assert ids == [
        stable_point_id("knowledge/x.md", "abc", 0),
        stable_point_id("knowledge/x.md", "abc", 1),
    ]


# ── delete_artifact ────────────────────────────────────────────────────────


def test_delete_artifact_when_collection_exists():
    client = _fake_client(existing_collections=["kb_public"])
    indexer = QdrantIndexer(client=client)
    indexer.delete_artifact(artifact_path="knowledge/x.md", visibility="public")
    client.delete.assert_called_once()


def test_delete_artifact_no_op_when_collection_missing():
    client = _fake_client(existing_collections=[])
    indexer = QdrantIndexer(client=client)
    indexer.delete_artifact(artifact_path="knowledge/x.md", visibility="public")
    client.delete.assert_not_called()


# ── delete_stale_chunks ────────────────────────────────────────────────────


def test_delete_stale_chunks_when_collection_exists():
    client = _fake_client(existing_collections=["kb_public"])
    indexer = QdrantIndexer(client=client)
    indexer.delete_stale_chunks(
        artifact_path="knowledge/x.md",
        visibility="public",
        current_commit_sha="abc",
    )
    client.delete.assert_called_once()
    _, kwargs = client.delete.call_args
    selector = kwargs["points_selector"]
    flt = selector.filter
    # must = artifact_path filter
    assert any(c.key == "artifact_path" for c in flt.must)
    # must_not = current commit filter
    assert any(c.key == "commit_sha" for c in flt.must_not)


def test_delete_stale_chunks_no_op_when_collection_missing():
    client = _fake_client(existing_collections=[])
    indexer = QdrantIndexer(client=client)
    indexer.delete_stale_chunks(
        artifact_path="knowledge/x.md",
        visibility="public",
        current_commit_sha="abc",
    )
    client.delete.assert_not_called()
