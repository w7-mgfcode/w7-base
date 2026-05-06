"""Phase 8 artifact endpoints — Gitea-backed CRUD + Qdrant retrieval.

Additive to the legacy ``knowledge_api`` and ``pages_api`` routers. Powers
the T10 catalog UI: list with frontmatter, detail view, related pane, and
filter-pushed-down semantic search.
"""
from __future__ import annotations

from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from server.dependencies import (
    get_gitea_storage,
    get_rag_coordinator,
)
from server.models.storage import Artifact, ArtifactSummary
from server.services.search.qdrant_search import SearchFilters
from server.services.search.rag_coordinator import RagCoordinator
from server.services.storage.gitea_storage import (
    ArtifactNotFoundError,
    GiteaStorage,
    GiteaStorageError,
    InvalidPathError,
    VALID_CATEGORIES,
)

router = APIRouter(prefix="/api/artifacts", tags=["Artifacts"])


# ── Models ─────────────────────────────────────────────────────────────────


class RelatedArtifact(BaseModel):
    """One related-artifact entry returned from the kNN endpoint."""

    artifact_path: str
    score: float
    section_title: Optional[str] = None
    snippet: str
    tags: List[str] = []
    status: Optional[str] = None
    owner: Optional[str] = None
    shared_tags: List[str] = []


class SearchRequest(BaseModel):
    query: str
    visibility: str = "public"
    tags: Optional[List[str]] = None
    status: Optional[List[str]] = None
    owner: Optional[str] = None
    top_k: int = 20
    use_hybrid: bool = False
    use_rerank: bool = False


# ── Routes ─────────────────────────────────────────────────────────────────


@router.get("", response_model=List[ArtifactSummary])
async def list_artifacts(
    storage: Annotated[GiteaStorage, Depends(get_gitea_storage)],
    category: Optional[str] = Query(
        None,
        description=f"Restrict to one category. Valid values: {', '.join(VALID_CATEGORIES)}",
    ),
):
    """List all artifacts (optionally filtered by category) with their parsed
    frontmatter metadata. Body is omitted — use ``GET /api/artifacts/{path}``
    for full content."""
    try:
        async with storage:
            return await storage.list(category=category)
    except InvalidPathError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except GiteaStorageError as exc:
        raise HTTPException(status_code=502, detail=f"Gitea storage error: {exc}")


@router.get("/{path:path}/related", response_model=List[RelatedArtifact])
async def get_related_artifacts(
    path: str,
    coordinator: Annotated[RagCoordinator, Depends(get_rag_coordinator)],
    visibility: str = Query("public", description="public or private"),
    k: int = Query(5, ge=1, le=20, description="Number of related artifacts to return"),
):
    """Find ``k`` artifacts semantically similar to the given one.

    The endpoint computes the centroid of the seed artifact's chunks and
    runs a kNN on Qdrant, deduplicating by ``artifact_path`` so the result
    is one entry per related artifact (not per chunk)."""
    if visibility not in ("public", "private"):
        raise HTTPException(status_code=400, detail="visibility must be public or private")

    seed_tags: set[str] = set()
    try:
        async with get_gitea_storage() as storage:
            seed = await storage.get(path)
            seed_tags = set(seed.frontmatter.tags)
    except ArtifactNotFoundError:
        # Seed artifact missing — Qdrant may still have stale chunks; return [] cleanly.
        return []
    except (InvalidPathError, GiteaStorageError):
        # Soft-fail: still attempt the centroid lookup; missing seed_tags just
        # means the "shared_tags" signal won't be populated for these results.
        seed_tags = set()

    hits = await coordinator.related(
        artifact_path=path,
        visibility=visibility,
        k=k,
    )

    out: List[RelatedArtifact] = []
    for h in hits:
        hit_tags = h.get("tags") or []
        shared = sorted(seed_tags.intersection(hit_tags)) if seed_tags else []
        snippet = (h.get("content") or "").strip()
        if len(snippet) > 180:
            snippet = snippet[:177].rstrip() + "..."
        out.append(
            RelatedArtifact(
                artifact_path=h["artifact_path"],
                score=float(h.get("score", 0.0)),
                section_title=h.get("section_title"),
                snippet=snippet,
                tags=list(hit_tags),
                status=h.get("status"),
                owner=h.get("owner"),
                shared_tags=shared,
            )
        )
    return out


@router.get("/{path:path}", response_model=Artifact)
async def get_artifact(
    path: str,
    storage: Annotated[GiteaStorage, Depends(get_gitea_storage)],
    ref: Optional[str] = Query(None, description="Read at a specific commit/branch/tag"),
):
    """Fetch one artifact (frontmatter + body + commit_sha) for the detail view."""
    try:
        async with storage:
            return await storage.get(path, ref=ref)
    except ArtifactNotFoundError:
        raise HTTPException(status_code=404, detail=f"artifact not found: {path}")
    except InvalidPathError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except GiteaStorageError as exc:
        raise HTTPException(status_code=502, detail=f"Gitea storage error: {exc}")


@router.post("/search")
async def search_artifacts(
    request: SearchRequest,
    coordinator: Annotated[RagCoordinator, Depends(get_rag_coordinator)],
):
    """Semantic search with frontmatter filters pushed down to Qdrant."""
    if request.visibility not in ("public", "private"):
        raise HTTPException(status_code=400, detail="visibility must be public or private")
    filters = SearchFilters(
        tags=request.tags,
        status=request.status,
        owner=request.owner,
    )
    try:
        result = await coordinator.query(
            query=request.query,
            visibility=request.visibility,
            filters=filters,
            top_k=request.top_k,
            mode="page",
            use_hybrid=request.use_hybrid,
            use_rerank=request.use_rerank,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=f"search error: {exc}")
    return result
