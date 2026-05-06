"""Tests for the ingestion pipeline orchestrator (T7)."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from server.models.storage import Artifact, FileDiff
from server.services.knowledge.frontmatter import Frontmatter
from server.services.knowledge.ingest_pipeline import IngestionPipeline
from server.services.storage.gitea_storage import ArtifactNotFoundError


# ── Helpers ────────────────────────────────────────────────────────────────


def _make_fm(**kwargs) -> Frontmatter:
    defaults = dict(id="x", owner="alice")
    defaults.update(kwargs)
    return Frontmatter(**defaults)


def _make_artifact(
    *,
    path: str = "knowledge/x.md",
    body: str = "# Title\n\nBody content here.",
    sha: str = "abc",
    visibility: str = "public",
) -> Artifact:
    return Artifact(
        path=path,
        frontmatter=_make_fm(visibility=visibility),
        body=body,
        commit_sha=sha,
        size=len(body),
    )


def _make_pipeline(
    *,
    storage_get=None,
    embedder_batch=None,
):
    storage = MagicMock()
    storage.get = AsyncMock(side_effect=storage_get)
    indexer = MagicMock()
    indexer.upsert = MagicMock(return_value=2)
    embedder = MagicMock()
    embedder.embed_batch = AsyncMock(side_effect=embedder_batch)
    return IngestionPipeline(
        storage=storage, indexer=indexer, embedder=embedder
    ), storage, indexer, embedder


# ── ingest_artifact ────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_ingest_artifact_happy_path():
    artifact = _make_artifact(body="x" * 2500)
    pipeline, storage, indexer, embedder = _make_pipeline(
        storage_get=lambda *a, **kw: artifact,
        embedder_batch=lambda texts: [[0.1, 0.2, 0.3] for _ in texts],
    )
    result = await pipeline.ingest_artifact("knowledge/x.md")
    assert result["action"] == "ingested"
    assert result["chunks"] >= 1
    assert result["commit_sha"] == "abc"
    assert result["visibility"] == "public"
    storage.get.assert_awaited_once()
    embedder.embed_batch.assert_awaited_once()
    indexer.upsert.assert_called_once()
    indexer.delete_stale_chunks.assert_called_once()


@pytest.mark.asyncio
async def test_ingest_artifact_empty_body_skipped():
    artifact = _make_artifact(body="")
    pipeline, _, indexer, embedder = _make_pipeline(
        storage_get=lambda *a, **kw: artifact,
        embedder_batch=lambda texts: [],
    )
    result = await pipeline.ingest_artifact("knowledge/x.md")
    assert result["action"] == "skipped"
    assert result["reason"] == "empty"
    embedder.embed_batch.assert_not_awaited()
    indexer.upsert.assert_not_called()


@pytest.mark.asyncio
async def test_ingest_artifact_propagates_not_found():
    pipeline, _, _, _ = _make_pipeline(
        storage_get=lambda *a, **kw: (_ for _ in ()).throw(
            ArtifactNotFoundError("knowledge/x.md")
        ),
    )
    with pytest.raises(ArtifactNotFoundError):
        await pipeline.ingest_artifact("knowledge/x.md")


@pytest.mark.asyncio
async def test_ingest_artifact_embedder_count_mismatch_raises():
    artifact = _make_artifact(body="content")
    pipeline, _, _, _ = _make_pipeline(
        storage_get=lambda *a, **kw: artifact,
        embedder_batch=lambda texts: [],  # zero embeddings for 1 chunk
    )
    with pytest.raises(RuntimeError, match="returned"):
        await pipeline.ingest_artifact("knowledge/x.md")


@pytest.mark.asyncio
async def test_ingest_artifact_passes_ref_to_storage():
    artifact = _make_artifact()
    pipeline, storage, _, _ = _make_pipeline(
        storage_get=lambda path, ref=None: artifact,
        embedder_batch=lambda texts: [[0.0]],
    )
    await pipeline.ingest_artifact("knowledge/x.md", ref="some-sha")
    storage.get.assert_awaited_once_with("knowledge/x.md", ref="some-sha")


# ── remove_artifact ────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_remove_artifact_calls_indexer():
    pipeline, _, indexer, _ = _make_pipeline(storage_get=lambda *a, **kw: None)
    result = await pipeline.remove_artifact("knowledge/x.md", "public")
    assert result["action"] == "removed"
    indexer.delete_artifact.assert_called_once_with(
        artifact_path="knowledge/x.md", visibility="public"
    )


# ── process_diff ───────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_process_diff_added_triggers_ingest():
    artifact = _make_artifact()
    pipeline, _, indexer, embedder = _make_pipeline(
        storage_get=lambda *a, **kw: artifact,
        embedder_batch=lambda texts: [[0.0] for _ in texts],
    )
    diffs = [FileDiff(path="knowledge/x.md", status="added", new_sha="abc")]
    results = await pipeline.process_diff(diffs)
    assert len(results) == 1
    assert results[0]["action"] == "ingested"


@pytest.mark.asyncio
async def test_process_diff_removed_calls_delete_in_both_visibilities():
    pipeline, _, indexer, _ = _make_pipeline(storage_get=lambda *a, **kw: None)
    diffs = [FileDiff(path="knowledge/x.md", status="removed")]
    results = await pipeline.process_diff(diffs)
    assert results[0]["action"] == "removed"
    # Called once for public, once for private.
    assert indexer.delete_artifact.call_count == 2
    visibilities = {
        c.kwargs["visibility"]
        for c in indexer.delete_artifact.call_args_list
    }
    assert visibilities == {"public", "private"}


@pytest.mark.asyncio
async def test_process_diff_handles_vanished_file_gracefully():
    pipeline, _, _, _ = _make_pipeline(
        storage_get=lambda *a, **kw: (_ for _ in ()).throw(
            ArtifactNotFoundError("vanished")
        ),
    )
    diffs = [FileDiff(path="knowledge/v.md", status="modified")]
    results = await pipeline.process_diff(diffs)
    assert results[0]["action"] == "skipped"
    assert results[0]["reason"] == "vanished"


@pytest.mark.asyncio
async def test_process_diff_per_item_error_isolation():
    """One failing file does not fail the whole batch."""
    artifact = _make_artifact()

    def storage_side(path, ref=None):
        if path == "knowledge/bad.md":
            raise RuntimeError("backend exploded")
        return artifact

    pipeline, _, _, _ = _make_pipeline(
        storage_get=storage_side,
        embedder_batch=lambda texts: [[0.0] for _ in texts],
    )
    diffs = [
        FileDiff(path="knowledge/good.md", status="added"),
        FileDiff(path="knowledge/bad.md", status="modified"),
        FileDiff(path="knowledge/another.md", status="modified"),
    ]
    results = await pipeline.process_diff(diffs)
    actions = [r["action"] for r in results]
    assert actions == ["ingested", "failed", "ingested"]
    assert "backend exploded" in results[1]["error"]


@pytest.mark.asyncio
async def test_process_diff_renamed_treated_as_ingest():
    artifact = _make_artifact()
    pipeline, _, _, _ = _make_pipeline(
        storage_get=lambda *a, **kw: artifact,
        embedder_batch=lambda texts: [[0.0] for _ in texts],
    )
    diffs = [FileDiff(path="knowledge/new.md", status="renamed", previous_path="knowledge/old.md")]
    results = await pipeline.process_diff(diffs)
    assert results[0]["action"] == "ingested"


@pytest.mark.asyncio
async def test_process_diff_empty_returns_empty():
    pipeline, _, _, _ = _make_pipeline(storage_get=lambda *a, **kw: None)
    results = await pipeline.process_diff([])
    assert results == []
