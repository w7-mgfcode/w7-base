"""Tests for the Phase 8 ingestion webhook route (#19).

Validates HMAC verification, payload diffing, and dispatch to the
``IngestionPipeline``. The pipeline itself is tested separately in
`test_ingest_pipeline.py`; here we exercise only the FastAPI surface.
"""
from __future__ import annotations

import hashlib
import hmac
import json
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from server.api_routes import ingest_api
from server.api_routes.ingest_api import _diffs_from_push, _is_kb_artifact


SECRET = "test-secret-not-real"


def _sign(body: bytes, secret: str = SECRET) -> str:
    return hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()


def _push_payload(
    *,
    ref: str = "refs/heads/main",
    after: str = "deadbeef",
    commits: list[dict] | None = None,
) -> dict:
    return {
        "ref": ref,
        "before": "0" * 40,
        "after": after,
        "commits": commits or [],
    }


@pytest.fixture
def app(monkeypatch):
    """Build a minimal FastAPI app with the ingest router and a fake pipeline."""
    pipeline = MagicMock()
    pipeline.process_diff = AsyncMock(return_value=[])
    pipeline.storage = MagicMock()
    pipeline.storage.list = AsyncMock(return_value=[])

    async def _fake_pipeline():
        yield pipeline

    # Stub out the secret + branch so verification uses our test values.
    from server.config.config import settings
    monkeypatch.setattr(settings, "gitea_webhook_secret", SECRET)
    monkeypatch.setattr(settings, "gitea_kb_branch", "main")

    app = FastAPI()
    app.include_router(ingest_api.router)
    app.dependency_overrides[ingest_api.get_ingestion_pipeline] = _fake_pipeline
    app.state.pipeline_mock = pipeline
    return app


@pytest.fixture
def client(app):
    return TestClient(app)


# ── _is_kb_artifact ────────────────────────────────────────────────────────


def test_is_kb_artifact_accepts_canonical_md():
    assert _is_kb_artifact("knowledge/foo.md")
    assert _is_kb_artifact("prompts/bar.md")


def test_is_kb_artifact_rejects_non_md():
    assert not _is_kb_artifact("knowledge/foo.txt")
    assert not _is_kb_artifact("knowledge/foo")


def test_is_kb_artifact_rejects_root_files():
    assert not _is_kb_artifact("README.md")


def test_is_kb_artifact_rejects_unknown_category():
    assert not _is_kb_artifact("evil/foo.md")
    assert not _is_kb_artifact("../../etc/passwd.md")


def test_is_kb_artifact_rejects_gitkeep_at_dir_root():
    # .gitkeep is technically not .md but worth being explicit
    assert not _is_kb_artifact("knowledge/.gitkeep")


# ── _diffs_from_push ───────────────────────────────────────────────────────


def test_diffs_from_push_handles_added_modified_removed():
    payload = _push_payload(commits=[{
        "added": ["knowledge/a.md"],
        "modified": ["prompts/b.md"],
        "removed": ["skills/c.md"],
    }])
    diffs = {d.path: d.status for d in _diffs_from_push(payload)}
    assert diffs == {
        "knowledge/a.md": "added",
        "prompts/b.md": "modified",
        "skills/c.md": "removed",
    }


def test_diffs_from_push_collapses_added_then_removed_to_noop():
    payload = _push_payload(commits=[
        {"added": ["knowledge/x.md"]},
        {"removed": ["knowledge/x.md"]},
    ])
    diffs = _diffs_from_push(payload)
    assert diffs == []


def test_diffs_from_push_filters_non_canonical_paths():
    payload = _push_payload(commits=[{
        "added": ["knowledge/keep.md", "evil/skip.md", "knowledge/.gitkeep", "README.md"],
    }])
    paths = [d.path for d in _diffs_from_push(payload)]
    assert paths == ["knowledge/keep.md"]


def test_diffs_from_push_attaches_after_sha():
    payload = _push_payload(after="abc123", commits=[{
        "added": ["knowledge/a.md"],
    }])
    [diff] = _diffs_from_push(payload)
    assert diff.new_sha == "abc123"


# ── HTTP: signature verification ───────────────────────────────────────────


def test_webhook_rejects_missing_signature(client):
    body = json.dumps(_push_payload()).encode()
    resp = client.post("/api/ingest/webhook", content=body)
    assert resp.status_code == 401


def test_webhook_rejects_bad_signature(client):
    body = json.dumps(_push_payload()).encode()
    resp = client.post(
        "/api/ingest/webhook",
        content=body,
        headers={"X-Gitea-Signature": "f00ba1" * 10},
    )
    assert resp.status_code == 401


def test_webhook_accepts_valid_signature_no_changes(client, app):
    body = json.dumps(_push_payload()).encode()
    resp = client.post(
        "/api/ingest/webhook",
        content=body,
        headers={
            "X-Gitea-Signature": _sign(body),
            "X-Gitea-Event": "push",
        },
    )
    assert resp.status_code == 200
    assert resp.json()["action"] == "no-op"
    app.state.pipeline_mock.process_diff.assert_not_awaited()


def test_webhook_skips_non_default_branch(client, app):
    body = json.dumps(_push_payload(ref="refs/heads/feature-x")).encode()
    resp = client.post(
        "/api/ingest/webhook",
        content=body,
        headers={"X-Gitea-Signature": _sign(body), "X-Gitea-Event": "push"},
    )
    assert resp.status_code == 200
    assert resp.json()["action"] == "skipped"
    app.state.pipeline_mock.process_diff.assert_not_awaited()


def test_webhook_ignores_non_push_events(client, app):
    body = json.dumps({"action": "opened"}).encode()
    resp = client.post(
        "/api/ingest/webhook",
        content=body,
        headers={"X-Gitea-Signature": _sign(body), "X-Gitea-Event": "issues"},
    )
    assert resp.status_code == 200
    assert resp.json()["action"] == "ignored"
    app.state.pipeline_mock.process_diff.assert_not_awaited()


def test_webhook_dispatches_diffs_to_pipeline(client, app):
    body = json.dumps(_push_payload(commits=[{
        "added": ["knowledge/new.md"],
        "modified": ["prompts/edit.md"],
    }])).encode()
    resp = client.post(
        "/api/ingest/webhook",
        content=body,
        headers={"X-Gitea-Signature": _sign(body), "X-Gitea-Event": "push"},
    )
    assert resp.status_code == 200
    assert resp.json()["action"] == "ingested"
    app.state.pipeline_mock.process_diff.assert_awaited_once()
    diffs = app.state.pipeline_mock.process_diff.call_args.args[0]
    assert {d.path for d in diffs} == {"knowledge/new.md", "prompts/edit.md"}


def test_webhook_rejects_invalid_json(client):
    body = b"not json {"
    resp = client.post(
        "/api/ingest/webhook",
        content=body,
        headers={"X-Gitea-Signature": _sign(body), "X-Gitea-Event": "push"},
    )
    assert resp.status_code == 400
    assert "invalid JSON" in resp.json()["detail"]


# ── reconcile ─────────────────────────────────────────────────────────────


def test_reconcile_walks_repo_and_processes(client, app):
    summary = MagicMock()
    summary.path = "knowledge/seed.md"
    app.state.pipeline_mock.storage.list = AsyncMock(return_value=[summary])
    resp = client.post("/api/ingest/reconcile")
    assert resp.status_code == 200
    body = resp.json()
    assert body["action"] == "reconciled"
    assert body["scanned"] == 1
    app.state.pipeline_mock.process_diff.assert_awaited_once()
