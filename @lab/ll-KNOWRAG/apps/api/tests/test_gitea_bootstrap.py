"""Tests for the Gitea KB-repo bootstrap (T4)."""
from __future__ import annotations

import base64
from typing import Any

import httpx
import pytest

from server.services.storage.gitea_bootstrap import (
    GiteaBootstrap,
    GiteaBootstrapError,
    KB_DIRECTORIES,
)


# ── Fixtures ────────────────────────────────────────────────────────────────


class FakeRouter:
    """Tiny router that lets each test queue (status, body) responses per URL."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []  # (method, url)
        self.bodies: list[Any] = []  # list of bodies posted
        # url -> list of (status_code, json_body) consumed in order
        self._responses: dict[tuple[str, str], list[tuple[int, Any]]] = {}

    def queue(self, method: str, url_suffix: str, status: int, body: Any = None) -> None:
        self._responses.setdefault((method.upper(), url_suffix), []).append(
            (status, body)
        )

    def handler(self, request: httpx.Request) -> httpx.Response:
        method = request.method.upper()
        # Strip query string for suffix matching — `?ref=branch` is auth-only.
        url = str(request.url).split("?", 1)[0]
        self.calls.append((method, url))
        if method == "POST" and request.content:
            try:
                self.bodies.append(request.content.decode())
            except Exception:
                self.bodies.append(None)

        # Match by suffix — allows tests to register short paths.
        for (m, suffix), queue in self._responses.items():
            if m != method:
                continue
            if not url.endswith(suffix):
                continue
            if not queue:
                continue
            status, body = queue.pop(0)
            return httpx.Response(status, json=body if body is not None else {})

        return httpx.Response(404, json={"error": f"unmatched {method} {url}"})


@pytest.fixture
def router() -> FakeRouter:
    return FakeRouter()


@pytest.fixture
def client(router: FakeRouter) -> httpx.AsyncClient:
    transport = httpx.MockTransport(router.handler)
    return httpx.AsyncClient(transport=transport)


@pytest.fixture
def bs(client: httpx.AsyncClient) -> GiteaBootstrap:
    return GiteaBootstrap(
        base_url="http://gitea:3000",
        token="test-token",
        owner="knowrag",
        repo="kb-default",
        client=client,
    )


# ── Construction validation ─────────────────────────────────────────────────


def test_construct_requires_base_url():
    with pytest.raises(ValueError, match="base_url"):
        GiteaBootstrap(base_url="", token="t", owner="o", repo="r")


def test_construct_requires_token():
    with pytest.raises(ValueError, match="token"):
        GiteaBootstrap(base_url="http://x", token="", owner="o", repo="r")


def test_construct_requires_owner_and_repo():
    with pytest.raises(ValueError, match="owner and repo"):
        GiteaBootstrap(base_url="http://x", token="t", owner="", repo="r")


def test_strips_trailing_slash():
    inst = GiteaBootstrap(
        base_url="http://gitea:3000/", token="t", owner="o", repo="r"
    )
    assert inst.base_url == "http://gitea:3000"


# ── wait_for_ready ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_wait_for_ready_succeeds(bs: GiteaBootstrap, router: FakeRouter):
    router.queue("GET", "/api/healthz", 200)
    await bs.wait_for_ready(max_retries=2, delay=0)


@pytest.mark.asyncio
async def test_wait_for_ready_retries_then_fails(
    bs: GiteaBootstrap, router: FakeRouter
):
    router.queue("GET", "/api/healthz", 503)
    router.queue("GET", "/api/healthz", 503)
    with pytest.raises(GiteaBootstrapError, match="did not become ready"):
        await bs.wait_for_ready(max_retries=2, delay=0)


# ── ensure_repo ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_ensure_repo_existing(bs: GiteaBootstrap, router: FakeRouter):
    router.queue("GET", "/api/v1/repos/knowrag/kb-default", 200, {"name": "kb-default"})
    created = await bs.ensure_repo()
    assert created is False


@pytest.mark.asyncio
async def test_ensure_repo_creates_when_missing(
    bs: GiteaBootstrap, router: FakeRouter
):
    router.queue("GET", "/api/v1/repos/knowrag/kb-default", 404)
    router.queue("POST", "/api/v1/user/repos", 201, {"name": "kb-default"})
    created = await bs.ensure_repo()
    assert created is True
    # Verify the create body included the right fields.
    create_body = router.bodies[0]
    assert "kb-default" in create_body
    assert "auto_init" in create_body


@pytest.mark.asyncio
async def test_ensure_repo_handles_concurrent_creation(
    bs: GiteaBootstrap, router: FakeRouter
):
    router.queue("GET", "/api/v1/repos/knowrag/kb-default", 404)
    router.queue("POST", "/api/v1/user/repos", 409)
    created = await bs.ensure_repo()
    assert created is False


@pytest.mark.asyncio
async def test_ensure_repo_raises_on_unexpected_probe_status(
    bs: GiteaBootstrap, router: FakeRouter
):
    router.queue("GET", "/api/v1/repos/knowrag/kb-default", 500, {"error": "oops"})
    with pytest.raises(GiteaBootstrapError, match="500"):
        await bs.ensure_repo()


@pytest.mark.asyncio
async def test_ensure_repo_raises_on_create_failure(
    bs: GiteaBootstrap, router: FakeRouter
):
    router.queue("GET", "/api/v1/repos/knowrag/kb-default", 404)
    router.queue("POST", "/api/v1/user/repos", 422, {"error": "validation"})
    with pytest.raises(GiteaBootstrapError, match="failed to create"):
        await bs.ensure_repo()


# ── ensure_directory_shape ──────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_ensure_directory_shape_seeds_all_when_missing(
    bs: GiteaBootstrap, router: FakeRouter
):
    for d in KB_DIRECTORIES:
        router.queue("GET", f"/contents/{d}/.gitkeep", 404)
        router.queue("POST", f"/contents/{d}/.gitkeep", 201)
    seeded = await bs.ensure_directory_shape()
    assert sorted(seeded) == sorted(KB_DIRECTORIES)


@pytest.mark.asyncio
async def test_ensure_directory_shape_skips_existing(
    bs: GiteaBootstrap, router: FakeRouter
):
    # All exist
    for d in KB_DIRECTORIES:
        router.queue("GET", f"/contents/{d}/.gitkeep", 200, {"path": f"{d}/.gitkeep"})
    seeded = await bs.ensure_directory_shape()
    assert seeded == []


@pytest.mark.asyncio
async def test_ensure_directory_shape_seeds_only_missing(
    bs: GiteaBootstrap, router: FakeRouter
):
    # First 3 exist, last 3 missing
    for d in KB_DIRECTORIES[:3]:
        router.queue("GET", f"/contents/{d}/.gitkeep", 200, {"path": f"{d}/.gitkeep"})
    for d in KB_DIRECTORIES[3:]:
        router.queue("GET", f"/contents/{d}/.gitkeep", 404)
        router.queue("POST", f"/contents/{d}/.gitkeep", 201)
    seeded = await bs.ensure_directory_shape()
    assert sorted(seeded) == sorted(KB_DIRECTORIES[3:])


@pytest.mark.asyncio
async def test_ensure_directory_shape_rejects_non_canonical_dir(
    bs: GiteaBootstrap,
):
    with pytest.raises(GiteaBootstrapError, match="non-canonical"):
        await bs.ensure_directory_shape(["arbitrary"])


@pytest.mark.asyncio
async def test_ensure_directory_shape_rejects_path_traversal(
    bs: GiteaBootstrap,
):
    with pytest.raises(GiteaBootstrapError, match="non-canonical|unsafe"):
        await bs.ensure_directory_shape(["../etc/passwd"])


@pytest.mark.asyncio
async def test_ensure_directory_shape_handles_already_exists_race(
    bs: GiteaBootstrap, router: FakeRouter
):
    # Probe says missing, but PUT returns 422 "already exists" (race condition).
    d = KB_DIRECTORIES[0]
    router.queue("GET", f"/contents/{d}/.gitkeep", 404)
    router.queue("POST", f"/contents/{d}/.gitkeep", 422, {"error": "file already exists"})
    seeded = await bs.ensure_directory_shape([d])
    # We treat the race as success — the file is there now even if not by us.
    assert seeded == [d]


# ── Auth header verification ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_token_is_sent_in_auth_header(bs: GiteaBootstrap, router: FakeRouter):
    """Capture the Authorization header from a probe and verify the token."""
    captured: dict[str, str] = {}

    def transport(request: httpx.Request) -> httpx.Response:
        captured["auth"] = request.headers.get("authorization", "")
        return httpx.Response(200, json={"name": "kb-default"})

    bs._client = httpx.AsyncClient(transport=httpx.MockTransport(transport))
    await bs.ensure_repo()
    assert captured["auth"] == "token test-token"


# ── Integration: run() ──────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_run_full_bootstrap_fresh_install(bs: GiteaBootstrap, router: FakeRouter):
    # Healthz ready
    router.queue("GET", "/api/healthz", 200)
    # Repo missing → create
    router.queue("GET", "/api/v1/repos/knowrag/kb-default", 404)
    router.queue("POST", "/api/v1/user/repos", 201, {"name": "kb-default"})
    # All dirs missing → seed all
    for d in KB_DIRECTORIES:
        router.queue("GET", f"/contents/{d}/.gitkeep", 404)
        router.queue("POST", f"/contents/{d}/.gitkeep", 201)

    summary = await bs.run()
    assert summary["repo"] == "knowrag/kb-default"
    assert summary["created_repo"] is True
    assert sorted(summary["seeded_directories"]) == sorted(KB_DIRECTORIES)


@pytest.mark.asyncio
async def test_run_idempotent_on_existing_install(
    bs: GiteaBootstrap, router: FakeRouter
):
    router.queue("GET", "/api/healthz", 200)
    router.queue("GET", "/api/v1/repos/knowrag/kb-default", 200, {"name": "kb-default"})
    for d in KB_DIRECTORIES:
        router.queue("GET", f"/contents/{d}/.gitkeep", 200, {"path": f"{d}/.gitkeep"})
    summary = await bs.run()
    assert summary["created_repo"] is False
    assert summary["seeded_directories"] == []
