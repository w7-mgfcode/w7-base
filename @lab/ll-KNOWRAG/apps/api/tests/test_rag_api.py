"""Tests for /api/rag/query — RAG generation endpoint (#43)."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
from fastapi.testclient import TestClient

from server.dependencies import (
    get_chat_provider_svc,
    get_rag_coordinator,
)
from server.main import app


@pytest.fixture
def fake_hits() -> list[dict]:
    return [
        {
            "artifact_path": "knowledge/auth.md",
            "chunk_index": 0,
            "content": "OAuth2 uses bearer tokens.",
            "score": 0.92,
            "section_title": "OAuth2",
            "tags": ["auth", "security"],
            "status": "published",
            "owner": "alice",
        },
        {
            "artifact_path": "knowledge/auth.md",
            "chunk_index": 1,
            "content": "Tokens should be rotated.",
            "score": 0.81,
            "section_title": "Rotation",
            "tags": ["auth"],
            "status": "published",
            "owner": "alice",
        },
    ]


def _async_mock(value):
    """Return an AsyncMock that raises if `value` is an Exception, else returns it."""
    if isinstance(value, BaseException):
        return AsyncMock(side_effect=value)
    return AsyncMock(return_value=value)


def _override_deps(coord_query=None, chat_generate=None):
    coord = MagicMock()
    coord.query = _async_mock(coord_query)
    chat = MagicMock()
    chat.base_url = "http://ollama:11434"
    chat.generate_text = _async_mock(chat_generate)
    app.dependency_overrides[get_rag_coordinator] = lambda: coord
    app.dependency_overrides[get_chat_provider_svc] = lambda: chat
    return coord, chat


@pytest.fixture(autouse=True)
def _clear_overrides():
    yield
    app.dependency_overrides.clear()


def test_rag_query_success(fake_hits):
    coord, chat = _override_deps(
        coord_query={"hits": fake_hits},
        chat_generate="Bearer tokens (knowledge/auth.md). Rotate them regularly.",
    )
    with TestClient(app) as client:
        resp = client.post(
            "/api/rag/query",
            json={"query": "How do I auth?", "match_count": 5},
        )
    assert resp.status_code == 200
    body = resp.json()
    assert body["query"] == "How do I auth?"
    assert body["answer"].startswith("Bearer tokens")
    assert len(body["hits"]) == 2
    assert body["hits"][0]["artifact_path"] == "knowledge/auth.md"
    assert body["hits"][0]["tags"] == ["auth", "security"]
    assert body["chat_model"]
    coord.query.assert_awaited_once()
    chat.generate_text.assert_awaited_once()


def test_rag_query_chat_provider_unavailable(fake_hits):
    coord, chat = _override_deps(
        coord_query={"hits": fake_hits},
        chat_generate=httpx.ConnectError("connection refused"),
    )
    with TestClient(app) as client:
        resp = client.post(
            "/api/rag/query",
            json={"query": "How do I auth?", "match_count": 5},
        )
    assert resp.status_code == 503
    detail = resp.json()["detail"]
    assert detail["error_code"] == "chat_provider_unavailable"
    assert "ollama:11434" in detail["message"]
    # Retrieval hits must survive the failure so the UI can render fallback.
    assert len(detail["retrieved_context"]) == 2
    assert detail["retrieved_context"][0]["artifact_path"] == "knowledge/auth.md"


def test_rag_query_embedding_provider_unavailable():
    coord, chat = _override_deps(
        coord_query=httpx.ConnectError("name resolution failed"),
        chat_generate="unused",
    )
    with TestClient(app) as client:
        resp = client.post(
            "/api/rag/query",
            json={"query": "How do I auth?", "match_count": 5},
        )
    assert resp.status_code == 503
    detail = resp.json()["detail"]
    assert detail["error_code"] == "chat_provider_unavailable"
    assert "ollama:11434" in detail["message"]
    assert detail["retrieved_context"] == []
    chat.generate_text.assert_not_awaited()


def test_rag_query_chat_model_unavailable(fake_hits):
    request = httpx.Request("POST", "http://ollama:11434/api/generate")
    response = httpx.Response(404, text='{"error":"model not found"}', request=request)
    coord, chat = _override_deps(
        coord_query={"hits": fake_hits},
        chat_generate=httpx.HTTPStatusError("404", request=request, response=response),
    )
    with TestClient(app) as client:
        resp = client.post(
            "/api/rag/query",
            json={"query": "How do I auth?", "match_count": 5},
        )
    assert resp.status_code == 503
    detail = resp.json()["detail"]
    assert detail["error_code"] == "chat_model_unavailable"
    assert "ollama pull" in detail["message"]
    assert len(detail["retrieved_context"]) == 2


def test_rag_query_no_hits_still_calls_chat():
    coord, chat = _override_deps(
        coord_query={"hits": []},
        chat_generate="I don't have enough context to answer.",
    )
    with TestClient(app) as client:
        resp = client.post(
            "/api/rag/query",
            json={"query": "What is X?", "match_count": 5},
        )
    assert resp.status_code == 200
    body = resp.json()
    assert body["hits"] == []
    assert body["answer"]
    chat.generate_text.assert_awaited_once()


def test_rag_query_rejects_empty_query():
    _override_deps()
    with TestClient(app) as client:
        resp = client.post("/api/rag/query", json={"query": "", "match_count": 5})
    assert resp.status_code == 422


def test_rag_query_rejects_invalid_visibility():
    _override_deps(coord_query={"hits": []}, chat_generate="ok")
    with TestClient(app) as client:
        resp = client.post(
            "/api/rag/query",
            json={"query": "x", "visibility": "secret", "match_count": 5},
        )
    assert resp.status_code == 400
    assert "visibility" in resp.json()["detail"]


def test_rag_query_propagates_retrieval_value_error():
    coord, chat = _override_deps(
        coord_query=ValueError("query must be non-empty"),
        chat_generate="unused",
    )
    with TestClient(app) as client:
        resp = client.post(
            "/api/rag/query",
            json={"query": "x", "match_count": 5},
        )
    assert resp.status_code == 400
    chat.generate_text.assert_not_awaited()
