"""Phase 8 ingestion webhook receiver.

Closes the gap surfaced by the first live `w7 verify` run: the Gitea push
event was firing into the void because no FastAPI route consumed it. This
module wires `POST /api/ingest/webhook` to the existing `IngestionPipeline`
and exposes `POST /api/ingest/reconcile` as an admin-triggered full-repo
re-sync.

Security:
- Every webhook call is HMAC-verified against `GITEA_WEBHOOK_SECRET` before
  the body is parsed, per `.claude/rules/security-patterns.md`.
- Reconcile is open by default — gate via reverse proxy in shared deployments.

Idempotency:
- The pipeline's deterministic point IDs (`stable_point_id` over
  `(artifact_path, commit_sha, chunk_index)`) make webhook re-deliveries safe.
"""
from __future__ import annotations

import json
import logging
from typing import Annotated, Iterable

from fastapi import APIRouter, Depends, Header, HTTPException, Request

from server.config.config import settings
from server.dependencies import get_ingestion_pipeline
from server.models.storage import FileDiff
from server.services.knowledge.ingest_pipeline import IngestionPipeline
from server.services.knowledge.webhook_security import (
    WebhookVerificationError,
    verify_gitea_signature,
)
from server.services.storage.gitea_storage import GiteaStorage, VALID_CATEGORIES

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ingest", tags=["Ingestion"])


def _is_kb_artifact(path: str) -> bool:
    """Only ingest .md files under canonical category dirs (skip .gitkeep,
    README.md at root, etc.)."""
    if not path.endswith(".md"):
        return False
    parts = path.split("/", 1)
    return len(parts) == 2 and parts[0] in VALID_CATEGORIES


def _diffs_from_push(payload: dict) -> list[FileDiff]:
    """Compute per-path effective diff from a Gitea push event payload.

    Walks every commit in order and folds into a path→status map. A path
    that's added then later removed in the same push is dropped (net no-op).
    Modifications win over earlier adds (the pipeline re-ingests at the
    push's tip commit anyway).
    """
    state: dict[str, str] = {}
    for commit in payload.get("commits", []) or []:
        for p in commit.get("added", []) or []:
            state[p] = "added"
        for p in commit.get("modified", []) or []:
            # Preserve "added" if this path was newly added in this push;
            # at re-ingest time the result is identical.
            if state.get(p) != "added":
                state[p] = "modified"
        for p in commit.get("removed", []) or []:
            if state.get(p) == "added":
                state.pop(p, None)
            else:
                state[p] = "removed"

    after = payload.get("after")
    diffs: list[FileDiff] = []
    for path, status in state.items():
        if not _is_kb_artifact(path):
            continue
        diffs.append(FileDiff(path=path, status=status, new_sha=after))
    return diffs


@router.post("/webhook")
async def gitea_webhook(
    request: Request,
    pipeline: Annotated[IngestionPipeline, Depends(get_ingestion_pipeline)],
    x_gitea_signature: Annotated[str | None, Header()] = None,
    x_gitea_event: Annotated[str | None, Header()] = None,
):
    """Receive an HMAC-signed Gitea push event and trigger ingestion."""
    body = await request.body()
    try:
        verify_gitea_signature(
            secret=settings.gitea_webhook_secret,
            payload=body,
            signature_header=x_gitea_signature,
        )
    except WebhookVerificationError as exc:
        logger.warning("rejected webhook: %s", exc)
        raise HTTPException(status_code=401, detail=str(exc))

    if x_gitea_event and x_gitea_event != "push":
        # Other Gitea events (issue, pull_request, ...) are accepted but ignored.
        return {"action": "ignored", "reason": f"event={x_gitea_event}"}

    try:
        payload = json.loads(body)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail=f"invalid JSON: {exc}")
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="payload must be a JSON object")

    expected_ref = f"refs/heads/{settings.gitea_kb_branch}"
    ref = payload.get("ref")
    if ref != expected_ref:
        return {"action": "skipped", "reason": f"ref {ref!r} != {expected_ref!r}"}

    diffs = _diffs_from_push(payload)
    if not diffs:
        return {"action": "no-op", "reason": "no markdown changes under canonical dirs"}

    results = await pipeline.process_diff(diffs)
    return {
        "action": "ingested",
        "count": len(results),
        "results": [dict(r) for r in results],
    }


@router.post("/reconcile")
async def reconcile_kb(
    pipeline: Annotated[IngestionPipeline, Depends(get_ingestion_pipeline)],
):
    """Walk the KB repo's canonical directories and re-ingest every artifact.

    Use after a webhook delivery loss, after a Qdrant reset, or as a periodic
    sweep. Idempotent — re-ingesting the same `(path, commit_sha)` is a
    no-op via stable point IDs.
    """
    storage: GiteaStorage = pipeline.storage  # already entered as async ctx
    summaries = await storage.list()
    paths: list[str] = [s.path for s in summaries if _is_kb_artifact(s.path)]

    diffs = [FileDiff(path=p, status="modified") for p in paths]
    results = await pipeline.process_diff(diffs)
    return {
        "action": "reconciled",
        "scanned": len(paths),
        "results": [dict(r) for r in results],
    }
