"""Pydantic models for the Phase 8 Gitea-backed storage layer."""
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from server.services.knowledge.frontmatter import Frontmatter


class ArtifactRef(BaseModel):
    """Lightweight reference to an artifact (path + commit identity)."""

    model_config = ConfigDict(frozen=True)

    path: str
    commit_sha: str


class Artifact(BaseModel):
    """Full artifact: frontmatter, body, and the commit at which it was read."""

    path: str
    frontmatter: Frontmatter
    body: str
    commit_sha: str
    size: int = 0


class ArtifactSummary(BaseModel):
    """Listing-friendly artifact view (no body, just metadata)."""

    path: str
    frontmatter: Frontmatter
    commit_sha: str
    size: int


FileStatus = Literal["added", "modified", "removed", "renamed"]


class FileDiff(BaseModel):
    """One file changed between two commits — used by the webhook receiver."""

    path: str
    status: FileStatus
    old_sha: str | None = None
    new_sha: str | None = None
    previous_path: str | None = None  # populated for renames


__all__ = ["Artifact", "ArtifactRef", "ArtifactSummary", "FileDiff", "FileStatus"]
