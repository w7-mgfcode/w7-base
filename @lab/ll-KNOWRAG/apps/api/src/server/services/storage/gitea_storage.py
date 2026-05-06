"""Gitea-backed artifact storage (T5 — Phase 8).

Replaces the Phase-7 PostgREST storage layer for KB artifacts. Each artifact
is one ``.md`` file under a canonical category directory in the Gitea repo;
mutations are commits, audit log is the git history.

Public surface:

- ``GiteaStorage.get(path, ref?) -> Artifact``
- ``GiteaStorage.create(path, frontmatter, body, message?) -> ArtifactRef``
- ``GiteaStorage.update(path, frontmatter, body, sha, message?) -> ArtifactRef``
- ``GiteaStorage.delete(path, sha, message?) -> None``
- ``GiteaStorage.list(category?) -> list[ArtifactSummary]``
- ``GiteaStorage.diff(base, head) -> list[FileDiff]``

Path safety, file-size limits, optimistic concurrency, and clear exception
typing for the caller. All HTTP is via httpx — pass a ``MockTransport``
client in tests.

The legacy ``StorageOperations`` (PostgREST) class is kept until T7 migrates
all callers. Do not extend it.
"""
from __future__ import annotations

import base64
import logging
import re
from typing import Iterable

import httpx

from server.models.storage import (
    Artifact,
    ArtifactRef,
    ArtifactSummary,
    FileDiff,
)
from server.services.knowledge.frontmatter import (
    Frontmatter,
    FrontmatterError,
    parse as parse_frontmatter,
    serialize as serialize_frontmatter,
)

logger = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────────────────────────

VALID_CATEGORIES: tuple[str, ...] = (
    "prompts",
    "commands",
    "mcp",
    "hooks",
    "skills",
    "knowledge",
)

# Path: <category>/<segment>(/<segment>)*.md, segments are url-safe.
_SEGMENT = r"[A-Za-z0-9][A-Za-z0-9_\-.]*"
PATH_RE = re.compile(
    r"^(" + "|".join(VALID_CATEGORIES) + r")/" + _SEGMENT + r"(?:/" + _SEGMENT + r")*\.md$"
)

MAX_PATH_LENGTH = 256
MAX_BODY_BYTES = 10 * 1024 * 1024  # 10 MiB


# ── Exceptions ─────────────────────────────────────────────────────────────


class GiteaStorageError(RuntimeError):
    """Base class for storage failures."""


class InvalidPathError(GiteaStorageError, ValueError):
    """Path is not safe or violates the canonical category contract."""


class ArtifactNotFoundError(GiteaStorageError, KeyError):
    """No artifact at the given path/ref."""


class ConcurrentModificationError(GiteaStorageError):
    """The provided commit SHA is stale — another writer changed the file."""


class ArtifactTooLargeError(GiteaStorageError, ValueError):
    """Artifact body exceeds the configured size cap."""


# ── Path validation ────────────────────────────────────────────────────────


def validate_artifact_path(path: str) -> None:
    """Reject empty, traversal, non-canonical, non-markdown paths.

    Raises ``InvalidPathError`` if the path is unsafe or non-conforming.
    """
    if not isinstance(path, str):
        raise InvalidPathError("path must be a string")
    if not path:
        raise InvalidPathError("path is empty")
    if len(path) > MAX_PATH_LENGTH:
        raise InvalidPathError(f"path exceeds {MAX_PATH_LENGTH} chars")
    if path.startswith("/"):
        raise InvalidPathError(f"path must be relative: {path!r}")
    if ".." in path.split("/"):
        raise InvalidPathError(f"path traversal detected: {path!r}")
    if "\x00" in path:
        raise InvalidPathError("path contains null byte")
    if not PATH_RE.match(path):
        raise InvalidPathError(
            f"path must match <category>/<name>.md where category is one of "
            f"{VALID_CATEGORIES}: got {path!r}"
        )


# ── Storage class ──────────────────────────────────────────────────────────


class GiteaStorage:
    """High-level CRUD over a Gitea-hosted KB repo."""

    def __init__(
        self,
        *,
        base_url: str,
        token: str,
        owner: str,
        repo: str,
        branch: str = "main",
        timeout: float = 30.0,
        max_body_bytes: int = MAX_BODY_BYTES,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        if not base_url:
            raise ValueError("base_url required")
        if not token:
            raise ValueError("token required")
        if not owner or not repo:
            raise ValueError("owner and repo required")
        self.base_url = base_url.rstrip("/")
        self.owner = owner
        self.repo = repo
        self.branch = branch
        self.timeout = timeout
        self.max_body_bytes = max_body_bytes
        self._client = client
        self._owns_client = client is None
        self._headers = {
            "Authorization": f"token {token}",
            "Accept": "application/json",
        }

    async def __aenter__(self) -> "GiteaStorage":
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self

    async def __aexit__(self, *exc_info) -> None:
        if self._owns_client and self._client is not None:
            await self._client.aclose()
            self._client = None

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            raise GiteaStorageError("client not initialised — use as async context manager")
        return self._client

    def _repo_url(self, suffix: str) -> str:
        return f"{self.base_url}/api/v1/repos/{self.owner}/{self.repo}{suffix}"

    # ── CRUD ───────────────────────────────────────────────────────────────

    async def get(self, path: str, ref: str | None = None) -> Artifact:
        """Fetch an artifact. Raises ``ArtifactNotFoundError`` on 404.

        Pass ``ref`` to read at a specific commit/branch/tag (default: branch).
        """
        validate_artifact_path(path)
        url = self._repo_url(f"/contents/{path}")
        params = {"ref": ref or self.branch}
        resp = await self.client.get(url, headers=self._headers, params=params)
        if resp.status_code == 404:
            raise ArtifactNotFoundError(path)
        if resp.status_code != 200:
            raise GiteaStorageError(
                f"GET {path} failed ({resp.status_code}): {resp.text[:300]}"
            )

        data = resp.json()
        encoding = data.get("encoding")
        if encoding != "base64":
            raise GiteaStorageError(f"unexpected encoding {encoding!r} for {path}")
        try:
            raw = base64.b64decode(data["content"])
            content = raw.decode("utf-8")
        except (KeyError, ValueError, UnicodeDecodeError) as exc:
            raise GiteaStorageError(f"failed to decode {path}: {exc}") from exc

        try:
            fm, body = parse_frontmatter(content)
        except FrontmatterError as exc:
            raise GiteaStorageError(f"frontmatter error in {path}: {exc}") from exc

        return Artifact(
            path=path,
            frontmatter=fm,
            body=body,
            commit_sha=data.get("sha", ""),
            size=int(data.get("size", len(raw))),
        )

    async def create(
        self,
        path: str,
        frontmatter: Frontmatter,
        body: str,
        message: str | None = None,
    ) -> ArtifactRef:
        """Create a new artifact. Raises if the path already exists."""
        validate_artifact_path(path)
        content = serialize_frontmatter(frontmatter, body)
        encoded = self._encode_body(content)

        url = self._repo_url(f"/contents/{path}")
        payload = {
            "message": message or f"feat(kb): create {path}",
            "content": encoded,
            "branch": self.branch,
        }
        resp = await self.client.post(url, headers=self._headers, json=payload)
        if resp.status_code == 422 and "already exists" in resp.text.lower():
            raise GiteaStorageError(f"artifact already exists: {path}")
        if resp.status_code not in (200, 201):
            raise GiteaStorageError(
                f"create {path} failed ({resp.status_code}): {resp.text[:300]}"
            )
        sha = self._extract_sha(resp.json())
        return ArtifactRef(path=path, commit_sha=sha)

    async def update(
        self,
        path: str,
        frontmatter: Frontmatter,
        body: str,
        sha: str,
        message: str | None = None,
    ) -> ArtifactRef:
        """Update an existing artifact. ``sha`` must be the current SHA
        (optimistic concurrency) — supply the value returned by ``get()``.

        Raises ``ConcurrentModificationError`` if the SHA is stale.
        """
        validate_artifact_path(path)
        if not sha:
            raise ValueError("sha required for update (optimistic concurrency)")
        content = serialize_frontmatter(frontmatter, body)
        encoded = self._encode_body(content)

        url = self._repo_url(f"/contents/{path}")
        payload = {
            "message": message or f"chore(kb): update {path}",
            "content": encoded,
            "sha": sha,
            "branch": self.branch,
        }
        resp = await self.client.put(url, headers=self._headers, json=payload)
        if resp.status_code == 404:
            raise ArtifactNotFoundError(path)
        if resp.status_code == 409 or (
            resp.status_code == 422 and "sha" in resp.text.lower()
        ):
            raise ConcurrentModificationError(
                f"stale sha for {path}: {resp.text[:200]}"
            )
        if resp.status_code not in (200, 201):
            raise GiteaStorageError(
                f"update {path} failed ({resp.status_code}): {resp.text[:300]}"
            )
        new_sha = self._extract_sha(resp.json())
        return ArtifactRef(path=path, commit_sha=new_sha)

    async def delete(self, path: str, sha: str, message: str | None = None) -> None:
        """Delete an artifact. ``sha`` must be the current SHA."""
        validate_artifact_path(path)
        if not sha:
            raise ValueError("sha required for delete")
        url = self._repo_url(f"/contents/{path}")
        payload = {
            "message": message or f"chore(kb): delete {path}",
            "sha": sha,
            "branch": self.branch,
        }
        resp = await self.client.request(
            "DELETE", url, headers=self._headers, json=payload
        )
        if resp.status_code == 404:
            raise ArtifactNotFoundError(path)
        if resp.status_code == 409 or (
            resp.status_code == 422 and "sha" in resp.text.lower()
        ):
            raise ConcurrentModificationError(
                f"stale sha for {path}: {resp.text[:200]}"
            )
        if resp.status_code not in (200, 204):
            raise GiteaStorageError(
                f"delete {path} failed ({resp.status_code}): {resp.text[:300]}"
            )

    async def list(self, category: str | None = None) -> list[ArtifactSummary]:
        """List artifacts in one category (or all if ``category`` is None)."""
        if category is not None and category not in VALID_CATEGORIES:
            raise InvalidPathError(f"unknown category: {category!r}")

        categories = [category] if category else list(VALID_CATEGORIES)
        out: list[ArtifactSummary] = []
        for cat in categories:
            out.extend(await self._list_category(cat))
        return out

    async def _list_category(self, category: str) -> list[ArtifactSummary]:
        url = self._repo_url(f"/contents/{category}")
        resp = await self.client.get(
            url, headers=self._headers, params={"ref": self.branch}
        )
        if resp.status_code == 404:
            return []
        if resp.status_code != 200:
            raise GiteaStorageError(
                f"list {category}/ failed ({resp.status_code}): {resp.text[:300]}"
            )
        items = resp.json()
        if not isinstance(items, list):
            return []  # single-file response — empty category

        summaries: list[ArtifactSummary] = []
        for item in items:
            name = item.get("name", "")
            if not name.endswith(".md") or item.get("type") != "file":
                continue
            path = f"{category}/{name}"
            try:
                artifact = await self.get(path)
            except (ArtifactNotFoundError, GiteaStorageError) as exc:
                logger.warning("skipping %s during list: %s", path, exc)
                continue
            summaries.append(
                ArtifactSummary(
                    path=path,
                    frontmatter=artifact.frontmatter,
                    commit_sha=artifact.commit_sha,
                    size=artifact.size,
                )
            )
        return summaries

    async def diff(self, base: str, head: str) -> list[FileDiff]:
        """Compare two commits and return the files that changed (under any
        canonical category — non-canonical paths are skipped silently)."""
        url = self._repo_url(f"/compare/{base}...{head}")
        resp = await self.client.get(url, headers=self._headers)
        if resp.status_code == 404:
            raise GiteaStorageError(f"compare {base}...{head} not found")
        if resp.status_code != 200:
            raise GiteaStorageError(
                f"compare failed ({resp.status_code}): {resp.text[:300]}"
            )

        data = resp.json()
        files = data.get("files") or []
        out: list[FileDiff] = []
        for f in files:
            path = f.get("filename") or ""
            status = f.get("status") or "modified"
            if not _is_under_canonical_category(path):
                continue
            out.append(
                FileDiff(
                    path=path,
                    status=status,
                    old_sha=f.get("previous_sha"),
                    new_sha=f.get("sha"),
                    previous_path=f.get("previous_filename"),
                )
            )
        return out

    # ── Internal ───────────────────────────────────────────────────────────

    def _encode_body(self, content: str) -> str:
        raw = content.encode("utf-8")
        if len(raw) > self.max_body_bytes:
            raise ArtifactTooLargeError(
                f"body exceeds {self.max_body_bytes} bytes ({len(raw)} given)"
            )
        return base64.b64encode(raw).decode("ascii")

    @staticmethod
    def _extract_sha(payload: dict) -> str:
        # Gitea returns either {"content": {"sha": ...}} or {"sha": ...}
        if isinstance(payload.get("content"), dict):
            return str(payload["content"].get("sha") or "")
        return str(payload.get("sha") or "")


def _is_under_canonical_category(path: str) -> bool:
    if not path or "/" not in path:
        return False
    head = path.split("/", 1)[0]
    return head in VALID_CATEGORIES


__all__ = [
    "GiteaStorage",
    "GiteaStorageError",
    "InvalidPathError",
    "ArtifactNotFoundError",
    "ConcurrentModificationError",
    "ArtifactTooLargeError",
    "VALID_CATEGORIES",
    "validate_artifact_path",
]
