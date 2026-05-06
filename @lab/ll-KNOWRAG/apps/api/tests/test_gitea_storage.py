"""Tests for Gitea-backed storage (T5)."""
from __future__ import annotations

import base64
from typing import Any

import httpx
import pytest

from server.models.storage import Artifact, ArtifactRef, ArtifactSummary, FileDiff
from server.services.knowledge.frontmatter import Frontmatter, serialize as serialize_fm
from server.services.storage.gitea_storage import (
    ArtifactNotFoundError,
    ArtifactTooLargeError,
    ConcurrentModificationError,
    GiteaStorage,
    GiteaStorageError,
    InvalidPathError,
    VALID_CATEGORIES,
    validate_artifact_path,
)


# ── Path validation ────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "path",
    [
        "knowledge/example.md",
        "prompts/system-claude.md",
        "skills/test_skill.md",
        "knowledge/sub/nested.md",
        "mcp/01-server.md",
        "hooks/pre-commit.md",
        "commands/deploy.md",
    ],
)
def test_validate_path_accepts_canonical(path: str):
    validate_artifact_path(path)  # should not raise


@pytest.mark.parametrize(
    "path,reason",
    [
        ("", "empty"),
        ("/etc/passwd", "relative"),
        ("../etc/passwd", "traversal"),
        ("knowledge/../../etc/passwd", "traversal"),
        ("knowledge/test.txt", "must match"),
        ("random/file.md", "must match"),
        ("knowledge/", "must match"),
        ("knowledge/.gitkeep", "must match"),
        ("a" * 300 + ".md", "exceeds"),
    ],
)
def test_validate_path_rejects_unsafe(path: str, reason: str):
    with pytest.raises(InvalidPathError, match=reason):
        validate_artifact_path(path)


def test_validate_path_rejects_null_byte():
    with pytest.raises(InvalidPathError, match="null byte"):
        validate_artifact_path("knowledge/test\x00.md")


def test_validate_path_rejects_non_string():
    with pytest.raises(InvalidPathError, match="must be a string"):
        validate_artifact_path(None)  # type: ignore[arg-type]


# ── Fixtures ───────────────────────────────────────────────────────────────


class FakeRouter:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []
        self.bodies: list[Any] = []
        self._responses: dict[tuple[str, str], list[tuple[int, Any, str | None]]] = {}

    def queue(
        self,
        method: str,
        url_suffix: str,
        status: int,
        body: Any = None,
        text: str | None = None,
    ) -> None:
        self._responses.setdefault((method.upper(), url_suffix), []).append(
            (status, body, text)
        )

    def handler(self, request: httpx.Request) -> httpx.Response:
        method = request.method.upper()
        url = str(request.url).split("?", 1)[0]
        self.calls.append((method, url))
        if request.content:
            try:
                self.bodies.append(request.content.decode())
            except Exception:
                self.bodies.append(None)

        for (m, suffix), queue in self._responses.items():
            if m != method or not url.endswith(suffix) or not queue:
                continue
            status, body, text = queue.pop(0)
            if text is not None:
                return httpx.Response(status, text=text)
            return httpx.Response(status, json=body if body is not None else {})

        return httpx.Response(404, json={"error": f"unmatched {method} {url}"})


def _make_fm(**kwargs) -> Frontmatter:
    defaults = dict(id="x", owner="alice")
    defaults.update(kwargs)
    return Frontmatter(**defaults)


def _gitea_get_response(content: str, sha: str = "abc123") -> dict:
    encoded = base64.b64encode(content.encode("utf-8")).decode("ascii")
    return {
        "name": "example.md",
        "path": "knowledge/example.md",
        "type": "file",
        "encoding": "base64",
        "content": encoded,
        "sha": sha,
        "size": len(content),
    }


@pytest.fixture
def router() -> FakeRouter:
    return FakeRouter()


@pytest.fixture
def storage(router: FakeRouter) -> GiteaStorage:
    transport = httpx.MockTransport(router.handler)
    return GiteaStorage(
        base_url="http://gitea:3000",
        token="test-token",
        owner="knowrag",
        repo="kb-default",
        client=httpx.AsyncClient(transport=transport),
    )


# ── Construction ────────────────────────────────────────────────────────────


def test_construct_validates_required_fields():
    with pytest.raises(ValueError, match="base_url"):
        GiteaStorage(base_url="", token="t", owner="o", repo="r")
    with pytest.raises(ValueError, match="token"):
        GiteaStorage(base_url="x", token="", owner="o", repo="r")
    with pytest.raises(ValueError, match="owner and repo"):
        GiteaStorage(base_url="x", token="t", owner="", repo="r")


# ── get() ──────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_returns_parsed_artifact(storage: GiteaStorage, router: FakeRouter):
    fm = _make_fm(tags=["agents"], status="published")
    md = serialize_fm(fm, "Hello body")
    router.queue("GET", "/contents/knowledge/example.md", 200, _gitea_get_response(md))

    art = await storage.get("knowledge/example.md")
    assert isinstance(art, Artifact)
    assert art.path == "knowledge/example.md"
    assert art.frontmatter.tags == ["agents"]
    assert art.frontmatter.status == "published"
    assert "Hello body" in art.body
    assert art.commit_sha == "abc123"


@pytest.mark.asyncio
async def test_get_raises_when_missing(storage: GiteaStorage, router: FakeRouter):
    router.queue("GET", "/contents/knowledge/missing.md", 404)
    with pytest.raises(ArtifactNotFoundError):
        await storage.get("knowledge/missing.md")


@pytest.mark.asyncio
async def test_get_validates_path(storage: GiteaStorage):
    with pytest.raises(InvalidPathError):
        await storage.get("../etc/passwd")


@pytest.mark.asyncio
async def test_get_raises_on_unexpected_status(storage: GiteaStorage, router: FakeRouter):
    router.queue("GET", "/contents/knowledge/example.md", 500, {"error": "oops"})
    with pytest.raises(GiteaStorageError, match="500"):
        await storage.get("knowledge/example.md")


@pytest.mark.asyncio
async def test_get_raises_on_unexpected_encoding(
    storage: GiteaStorage, router: FakeRouter
):
    router.queue(
        "GET",
        "/contents/knowledge/example.md",
        200,
        {"encoding": "utf-8", "content": "hi", "sha": "x"},
    )
    with pytest.raises(GiteaStorageError, match="unexpected encoding"):
        await storage.get("knowledge/example.md")


@pytest.mark.asyncio
async def test_get_raises_on_invalid_frontmatter(
    storage: GiteaStorage, router: FakeRouter
):
    bad = "no frontmatter here"
    router.queue("GET", "/contents/knowledge/example.md", 200, _gitea_get_response(bad))
    with pytest.raises(GiteaStorageError, match="frontmatter error"):
        await storage.get("knowledge/example.md")


# ── create() ───────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_succeeds(storage: GiteaStorage, router: FakeRouter):
    router.queue(
        "POST",
        "/contents/knowledge/new.md",
        201,
        {"content": {"sha": "newsha"}, "commit": {"sha": "commitsha"}},
    )
    ref = await storage.create("knowledge/new.md", _make_fm(), "body content")
    assert ref.path == "knowledge/new.md"
    assert ref.commit_sha == "newsha"


@pytest.mark.asyncio
async def test_create_rejects_existing(storage: GiteaStorage, router: FakeRouter):
    router.queue(
        "POST",
        "/contents/knowledge/dup.md",
        422,
        text='{"error":"file already exists"}',
    )
    with pytest.raises(GiteaStorageError, match="already exists"):
        await storage.create("knowledge/dup.md", _make_fm(), "body")


@pytest.mark.asyncio
async def test_create_validates_path(storage: GiteaStorage):
    with pytest.raises(InvalidPathError):
        await storage.create("../escape.md", _make_fm(), "body")


@pytest.mark.asyncio
async def test_create_rejects_oversized_body(storage: GiteaStorage):
    huge = "x" * (storage.max_body_bytes + 1)
    with pytest.raises(ArtifactTooLargeError):
        await storage.create("knowledge/huge.md", _make_fm(), huge)


@pytest.mark.asyncio
async def test_create_uses_custom_message(storage: GiteaStorage, router: FakeRouter):
    router.queue("POST", "/contents/knowledge/m.md", 201, {"content": {"sha": "s"}})
    await storage.create("knowledge/m.md", _make_fm(), "body", message="custom msg")
    body = router.bodies[0]
    assert "custom msg" in body


# ── update() ───────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_update_succeeds(storage: GiteaStorage, router: FakeRouter):
    router.queue(
        "PUT",
        "/contents/knowledge/x.md",
        200,
        {"content": {"sha": "newsha"}},
    )
    ref = await storage.update(
        "knowledge/x.md", _make_fm(status="published"), "new body", sha="oldsha"
    )
    assert ref.commit_sha == "newsha"
    body = router.bodies[0]
    assert "oldsha" in body  # sha sent for optimistic concurrency


@pytest.mark.asyncio
async def test_update_raises_on_stale_sha(storage: GiteaStorage, router: FakeRouter):
    router.queue("PUT", "/contents/knowledge/x.md", 409, {"error": "sha mismatch"})
    with pytest.raises(ConcurrentModificationError):
        await storage.update("knowledge/x.md", _make_fm(), "body", sha="stale")


@pytest.mark.asyncio
async def test_update_raises_on_missing(storage: GiteaStorage, router: FakeRouter):
    router.queue("PUT", "/contents/knowledge/x.md", 404)
    with pytest.raises(ArtifactNotFoundError):
        await storage.update("knowledge/x.md", _make_fm(), "body", sha="anysha")


@pytest.mark.asyncio
async def test_update_requires_sha(storage: GiteaStorage):
    with pytest.raises(ValueError, match="sha required"):
        await storage.update("knowledge/x.md", _make_fm(), "body", sha="")


# ── delete() ───────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_delete_succeeds(storage: GiteaStorage, router: FakeRouter):
    router.queue("DELETE", "/contents/knowledge/x.md", 200)
    await storage.delete("knowledge/x.md", sha="cur")


@pytest.mark.asyncio
async def test_delete_raises_on_missing(storage: GiteaStorage, router: FakeRouter):
    router.queue("DELETE", "/contents/knowledge/missing.md", 404)
    with pytest.raises(ArtifactNotFoundError):
        await storage.delete("knowledge/missing.md", sha="any")


@pytest.mark.asyncio
async def test_delete_raises_on_stale_sha(storage: GiteaStorage, router: FakeRouter):
    router.queue("DELETE", "/contents/knowledge/x.md", 409, {"error": "sha"})
    with pytest.raises(ConcurrentModificationError):
        await storage.delete("knowledge/x.md", sha="stale")


# ── list() ─────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_returns_summaries_for_category(
    storage: GiteaStorage, router: FakeRouter
):
    fm1 = _make_fm(id="one")
    fm2 = _make_fm(id="two")
    router.queue(
        "GET",
        "/contents/knowledge",
        200,
        [
            {"name": "one.md", "type": "file", "path": "knowledge/one.md"},
            {"name": "two.md", "type": "file", "path": "knowledge/two.md"},
            {"name": ".gitkeep", "type": "file", "path": "knowledge/.gitkeep"},
            {"name": "subdir", "type": "dir", "path": "knowledge/subdir"},
        ],
    )
    router.queue(
        "GET",
        "/contents/knowledge/one.md",
        200,
        _gitea_get_response(serialize_fm(fm1, "B1"), sha="s1"),
    )
    router.queue(
        "GET",
        "/contents/knowledge/two.md",
        200,
        _gitea_get_response(serialize_fm(fm2, "B2"), sha="s2"),
    )
    summaries = await storage.list(category="knowledge")
    assert len(summaries) == 2
    paths = {s.path for s in summaries}
    assert paths == {"knowledge/one.md", "knowledge/two.md"}


@pytest.mark.asyncio
async def test_list_rejects_unknown_category(storage: GiteaStorage):
    with pytest.raises(InvalidPathError, match="unknown category"):
        await storage.list(category="not-a-real-category")


@pytest.mark.asyncio
async def test_list_returns_empty_for_missing_category(
    storage: GiteaStorage, router: FakeRouter
):
    router.queue("GET", "/contents/knowledge", 404)
    out = await storage.list(category="knowledge")
    assert out == []


@pytest.mark.asyncio
async def test_list_all_iterates_every_category(
    storage: GiteaStorage, router: FakeRouter
):
    for cat in VALID_CATEGORIES:
        router.queue("GET", f"/contents/{cat}", 404)  # all empty
    out = await storage.list()
    assert out == []
    # 6 GET calls expected, one per category
    list_calls = [c for c in router.calls if c[0] == "GET" and "/contents/" in c[1]]
    assert len(list_calls) == len(VALID_CATEGORIES)


# ── diff() ─────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_diff_filters_to_canonical_categories(
    storage: GiteaStorage, router: FakeRouter
):
    router.queue(
        "GET",
        "/compare/old...new",
        200,
        {
            "files": [
                {"filename": "knowledge/a.md", "status": "added", "sha": "n1"},
                {"filename": "knowledge/b.md", "status": "modified", "sha": "n2", "previous_sha": "p2"},
                {"filename": "README.md", "status": "modified"},  # filtered out
                {"filename": ".gitignore", "status": "modified"},  # filtered out
                {"filename": "skills/c.md", "status": "removed", "previous_sha": "p3"},
            ]
        },
    )
    diffs = await storage.diff("old", "new")
    paths = [d.path for d in diffs]
    assert paths == ["knowledge/a.md", "knowledge/b.md", "skills/c.md"]
    assert diffs[0].status == "added"
    assert diffs[2].status == "removed"


@pytest.mark.asyncio
async def test_diff_returns_empty_when_no_changes(
    storage: GiteaStorage, router: FakeRouter
):
    router.queue("GET", "/compare/x...y", 200, {"files": []})
    diffs = await storage.diff("x", "y")
    assert diffs == []


@pytest.mark.asyncio
async def test_diff_raises_on_unknown_compare(
    storage: GiteaStorage, router: FakeRouter
):
    router.queue("GET", "/compare/x...y", 404)
    with pytest.raises(GiteaStorageError, match="not found"):
        await storage.diff("x", "y")


# ── Auth header propagation ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_auth_header_sent_on_every_call(storage: GiteaStorage):
    captured: list[str] = []

    def transport(request: httpx.Request) -> httpx.Response:
        captured.append(request.headers.get("authorization", ""))
        return httpx.Response(404)

    storage._client = httpx.AsyncClient(transport=httpx.MockTransport(transport))
    with pytest.raises(ArtifactNotFoundError):
        await storage.get("knowledge/x.md")
    assert captured == ["token test-token"]
