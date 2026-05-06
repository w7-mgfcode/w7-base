"""Gitea KB-repo bootstrap (T4).

Idempotent first-boot provisioning for the KB Git repo:

1. Wait until Gitea is reachable.
2. Ensure the KB repo exists (create if missing, owned by ``owner``).
3. Ensure the canonical directory shape exists by committing a ``.gitkeep``
   into each missing directory.

Designed to be called from the API ``lifespan`` startup hook **and** runnable
as a standalone script (``python -m server.services.storage.gitea_bootstrap``)
for an init-container deployment pattern.

Security:
- Token is loaded from env at instantiation time and never logged.
- HTTP client honours the ``timeout`` argument to avoid wedging on a stuck
  Gitea instance.
- All file paths are validated against the canonical directory list to
  prevent accidental writes outside the intended structure.
"""
from __future__ import annotations

import asyncio
import base64
import logging
from typing import Iterable, Sequence

import httpx

logger = logging.getLogger(__name__)

KB_DIRECTORIES: tuple[str, ...] = (
    "prompts",
    "commands",
    "mcp",
    "hooks",
    "skills",
    "knowledge",
)

DEFAULT_README = b"""# KnowRAG KB

This repository is the source-of-truth for ll-KNOWRAG knowledge artifacts.

Directory layout:

- `prompts/` - System prompts, prompt templates
- `commands/` - Slash commands, CLI invocations
- `mcp/` - MCP server configs and notes
- `hooks/` - Hook scripts and triggers
- `skills/` - Agent skills, capabilities
- `knowledge/` - General knowledge articles

Each artifact is a single `.md` file with YAML frontmatter.
Pushes to this repo trigger ingestion into the Qdrant vector index.
"""


class GiteaBootstrapError(RuntimeError):
    """Raised when the bootstrap cannot complete."""


class GiteaBootstrap:
    """Idempotent bootstrap for the KB repo on a fresh Gitea instance."""

    def __init__(
        self,
        *,
        base_url: str,
        token: str,
        owner: str,
        repo: str,
        branch: str = "main",
        timeout: float = 30.0,
        client: httpx.AsyncClient | None = None,
    ):
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
        self._client = client
        self._owns_client = client is None
        self._headers = {
            "Authorization": f"token {token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    async def __aenter__(self) -> "GiteaBootstrap":
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
            raise GiteaBootstrapError("client not initialised — use as async context manager")
        return self._client

    # ── Steps ─────────────────────────────────────────────────────────────

    async def wait_for_ready(self, max_retries: int = 30, delay: float = 2.0) -> None:
        """Poll the Gitea healthz endpoint until it succeeds or we give up."""
        url = f"{self.base_url}/api/healthz"
        last_err: Exception | None = None
        for attempt in range(1, max_retries + 1):
            try:
                resp = await self.client.get(url, timeout=5.0)
                if resp.status_code == 200:
                    logger.info("Gitea ready (healthz pass) after %d attempt(s)", attempt)
                    return
                last_err = GiteaBootstrapError(f"healthz returned {resp.status_code}")
            except httpx.HTTPError as exc:
                last_err = exc
            await asyncio.sleep(delay)
        raise GiteaBootstrapError(
            f"Gitea did not become ready after {max_retries} attempts: {last_err}"
        )

    async def ensure_repo(self) -> bool:
        """Create the KB repo if missing. Returns True if created, False if existed."""
        get_url = f"{self.base_url}/api/v1/repos/{self.owner}/{self.repo}"
        resp = await self.client.get(get_url, headers=self._headers)
        if resp.status_code == 200:
            logger.info("KB repo %s/%s already exists", self.owner, self.repo)
            return False
        if resp.status_code != 404:
            raise GiteaBootstrapError(
                f"unexpected status {resp.status_code} probing repo: {resp.text[:200]}"
            )

        # Create via /user/repos (owner = the authenticated user) or /orgs/{owner}/repos.
        # We try the current-user path first — operators own the KB repo by default.
        create_url = f"{self.base_url}/api/v1/user/repos"
        body = {
            "name": self.repo,
            "description": "ll-KNOWRAG knowledge artifacts (managed)",
            "private": True,
            "auto_init": True,
            "default_branch": self.branch,
            "readme": "Default",
        }
        create = await self.client.post(create_url, headers=self._headers, json=body)
        if create.status_code == 409:
            # Race — another worker created it. Treat as success.
            logger.info("KB repo created concurrently — treating as existing")
            return False
        if create.status_code not in (200, 201):
            raise GiteaBootstrapError(
                f"failed to create repo ({create.status_code}): {create.text[:300]}"
            )
        logger.info("KB repo %s/%s created", self.owner, self.repo)
        return True

    async def _file_exists(self, path: str) -> bool:
        url = f"{self.base_url}/api/v1/repos/{self.owner}/{self.repo}/contents/{path}"
        resp = await self.client.get(
            url, headers=self._headers, params={"ref": self.branch}
        )
        return resp.status_code == 200

    async def _put_file(self, path: str, content: bytes, message: str) -> None:
        url = f"{self.base_url}/api/v1/repos/{self.owner}/{self.repo}/contents/{path}"
        body = {
            "message": message,
            "content": base64.b64encode(content).decode("ascii"),
            "branch": self.branch,
        }
        resp = await self.client.post(url, headers=self._headers, json=body)
        if resp.status_code == 422 and "already exists" in resp.text.lower():
            logger.debug("File %s already exists — skipping", path)
            return
        if resp.status_code not in (200, 201):
            raise GiteaBootstrapError(
                f"failed to create {path} ({resp.status_code}): {resp.text[:300]}"
            )
        logger.info("Committed %s", path)

    async def ensure_directory_shape(
        self, directories: Sequence[str] = KB_DIRECTORIES
    ) -> list[str]:
        """Ensure every named directory has a ``.gitkeep``. Returns the list
        of directories that needed seeding."""
        # Validate against the canonical list — refuse arbitrary paths.
        for d in directories:
            if d not in KB_DIRECTORIES:
                raise GiteaBootstrapError(
                    f"refusing to seed non-canonical directory: {d!r}"
                )
            if "/" in d or ".." in d:
                raise GiteaBootstrapError(f"refusing to seed unsafe path: {d!r}")

        seeded: list[str] = []
        for d in directories:
            keep_path = f"{d}/.gitkeep"
            if await self._file_exists(keep_path):
                continue
            await self._put_file(
                keep_path,
                b"",
                f"chore(bootstrap): seed {d}/ directory",
            )
            seeded.append(d)
        return seeded

    async def ensure_webhook(self, *, target_url: str, secret: str) -> bool:
        """Idempotently ensure a Gitea push webhook exists pointing at
        ``target_url``. Returns True if newly created, False if already
        present (matched by config.url).

        Skips silently when ``target_url`` or ``secret`` is empty.
        """
        if not target_url or not secret:
            logger.info("ensure_webhook: target_url or secret missing — skipping")
            return False
        list_url = f"{self.base_url}/api/v1/repos/{self.owner}/{self.repo}/hooks"
        resp = await self.client.get(list_url, headers=self._headers)
        if resp.status_code != 200:
            raise GiteaBootstrapError(
                f"failed to list hooks ({resp.status_code}): {resp.text[:200]}"
            )
        try:
            existing: Iterable[dict] = resp.json() or []
        except ValueError:
            existing = []
        for hook in existing:
            url = (hook.get("config") or {}).get("url")
            if url == target_url:
                logger.debug("Webhook already present on %s/%s", self.owner, self.repo)
                return False
        body = {
            "type": "gitea",
            "active": True,
            "events": ["push"],
            "config": {
                "url": target_url,
                "content_type": "json",
                "secret": secret,
                "http_method": "POST",
            },
        }
        create = await self.client.post(list_url, headers=self._headers, json=body)
        if create.status_code not in (200, 201):
            raise GiteaBootstrapError(
                f"failed to create webhook ({create.status_code}): {create.text[:300]}"
            )
        logger.info("Created push webhook on %s/%s -> %s", self.owner, self.repo, target_url)
        return True

    async def run(
        self,
        *,
        wait: bool = True,
        webhook_url: str | None = None,
        webhook_secret: str | None = None,
    ) -> dict:
        """Execute the full bootstrap and return a summary dict.

        When ``webhook_url`` and ``webhook_secret`` are both provided, a
        push webhook is also ensured idempotently.
        """
        if wait:
            await self.wait_for_ready()
        created_repo = await self.ensure_repo()
        seeded = await self.ensure_directory_shape()
        webhook_created: bool | None = None
        if webhook_url and webhook_secret:
            webhook_created = await self.ensure_webhook(
                target_url=webhook_url, secret=webhook_secret
            )
        return {
            "repo": f"{self.owner}/{self.repo}",
            "branch": self.branch,
            "created_repo": created_repo,
            "seeded_directories": seeded,
            "webhook_created": webhook_created,
        }


async def bootstrap_from_env() -> dict:
    """Convenience entry point that pulls config from env via Pydantic settings."""
    from server.config.config import settings  # local import — heavy

    base_url = getattr(settings, "gitea_base_url", None)
    token = getattr(settings, "gitea_token", None)
    owner = getattr(settings, "gitea_kb_owner", "knowrag")
    repo = getattr(settings, "gitea_kb_repo", "kb-default")
    branch = getattr(settings, "gitea_kb_branch", "main")

    if not (base_url and token):
        raise GiteaBootstrapError(
            "GITEA_BASE_URL and GITEA_TOKEN must be set in env to run bootstrap"
        )

    async with GiteaBootstrap(
        base_url=base_url, token=token, owner=owner, repo=repo, branch=branch
    ) as bs:
        return await bs.run()


__all__ = [
    "GiteaBootstrap",
    "GiteaBootstrapError",
    "KB_DIRECTORIES",
    "bootstrap_from_env",
]
