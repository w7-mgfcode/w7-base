"""RAG generation endpoint — retrieve + answer.

POST /api/rag/query runs vector retrieval via ``RagCoordinator`` then asks
the configured chat-completions provider to answer the user's question
grounded in the retrieved chunks. When the chat provider is unreachable or
the configured model isn't available, returns a structured 503 with the
retrieved hits intact so the caller can fall back to a retrieval-only view.
"""
from __future__ import annotations

import logging
from typing import Annotated, List, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from server.config.config import settings
from server.dependencies import (
    get_chat_provider_svc,
    get_rag_coordinator,
)
from server.services.embeddings.llm_provider_service import LLMProviderService
from server.services.search.qdrant_search import SearchFilters
from server.services.search.rag_coordinator import RagCoordinator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/rag", tags=["RAG"])


# ── Models ─────────────────────────────────────────────────────────────────


class RagQueryRequest(BaseModel):
    query: str = Field(..., min_length=1)
    visibility: str = "public"
    tags: Optional[List[str]] = None
    status: Optional[List[str]] = None
    owner: Optional[str] = None
    match_count: int = Field(default=5, ge=1, le=50)
    use_hybrid: bool = False
    use_rerank: bool = False


class RagQueryHit(BaseModel):
    artifact_path: str
    chunk_index: int
    content: str
    score: float
    section_title: Optional[str] = None
    tags: List[str] = []


class RagQueryResponse(BaseModel):
    query: str
    answer: str
    hits: List[RagQueryHit]
    chat_provider: str
    chat_model: str


# ── Helpers ────────────────────────────────────────────────────────────────


SYSTEM_PROMPT = (
    "You are a knowledge-base assistant. Answer the user's question using "
    "ONLY the supplied context. If the context does not contain the answer, "
    "say so explicitly. Reference artifact paths inline when relevant."
)


def _build_prompt(query: str, hits: List[dict]) -> str:
    if not hits:
        return (
            f"Question: {query}\n\n"
            "Context: (no relevant artifacts were retrieved)\n\n"
            "Answer:"
        )
    blocks = []
    for i, h in enumerate(hits, 1):
        blocks.append(f"[{i}] {h['artifact_path']}\n{h['content']}")
    return f"Context:\n" + "\n\n".join(blocks) + f"\n\nQuestion: {query}\n\nAnswer:"


def _hits_to_response(hits: List[dict]) -> List[RagQueryHit]:
    return [
        RagQueryHit(
            artifact_path=h["artifact_path"],
            chunk_index=h["chunk_index"],
            content=h["content"],
            score=float(h["score"]),
            section_title=h.get("section_title"),
            tags=list(h.get("tags") or []),
        )
        for h in hits
    ]


# ── Routes ─────────────────────────────────────────────────────────────────


@router.post("/query", response_model=RagQueryResponse)
async def rag_query(
    request: RagQueryRequest,
    coordinator: Annotated[RagCoordinator, Depends(get_rag_coordinator)],
    chat: Annotated[LLMProviderService, Depends(get_chat_provider_svc)],
):
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
            top_k=request.match_count,
            mode="chunk",
            use_hybrid=request.use_hybrid,
            use_rerank=request.use_rerank,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=f"retrieval error: {exc}")

    hits: List[dict] = result.get("hits", [])
    prompt = _build_prompt(request.query, hits)

    try:
        answer = await chat.generate_text(
            model=settings.chat_model,
            prompt=prompt,
            system=SYSTEM_PROMPT,
        )
    except (httpx.ConnectError, httpx.ConnectTimeout, httpx.ReadTimeout, httpx.NetworkError) as exc:
        logger.warning("chat provider unreachable at %s: %s", chat.base_url, exc)
        raise HTTPException(
            status_code=503,
            detail={
                "error_code": "chat_provider_unavailable",
                "message": (
                    f"Chat provider at {chat.base_url} is unreachable. "
                    f"Set CHAT_BASE_URL/CHAT_MODEL or ensure Ollama is running. "
                    f"See docs/runbook.md#configuring-rag-generation."
                ),
                "retrieved_context": [h.model_dump() for h in _hits_to_response(hits)],
            },
        )
    except httpx.HTTPStatusError as exc:
        body = exc.response.text[:200] if exc.response is not None else ""
        status = exc.response.status_code if exc.response is not None else "?"
        logger.warning(
            "chat provider returned %s for model %s: %s",
            status, settings.chat_model, body,
        )
        raise HTTPException(
            status_code=503,
            detail={
                "error_code": "chat_model_unavailable",
                "message": (
                    f"Chat model '{settings.chat_model}' is not available at "
                    f"{chat.base_url}. Pull it with: "
                    f"docker exec -it knowrag-ollama ollama pull {settings.chat_model}. "
                    f"See docs/runbook.md#configuring-rag-generation."
                ),
                "retrieved_context": [h.model_dump() for h in _hits_to_response(hits)],
            },
        )

    return RagQueryResponse(
        query=request.query,
        answer=answer,
        hits=_hits_to_response(hits),
        chat_provider=settings.chat_provider,
        chat_model=settings.chat_model,
    )
