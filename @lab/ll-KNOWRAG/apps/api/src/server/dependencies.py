"""Application-wide service singletons + FastAPI dependency providers.

Phase 8 (Gitea + Qdrant + Ollama) is the only backend. Phase 7 (Supabase +
PostgREST + pgvector) was retired in #23.
"""
from __future__ import annotations

from qdrant_client import QdrantClient

from server.config.config import settings
from server.services.storage.gitea_storage import GiteaStorage
from server.services.knowledge.ingest_pipeline import IngestionPipeline
from server.services.embeddings.llm_provider_service import LLMProviderService
from server.services.embeddings.embedding_service import EmbeddingService
from server.services.search.qdrant_search import QdrantSearch
from server.services.search.qdrant_indexer import QdrantIndexer
from server.services.search.rag_coordinator import RagCoordinator
from server.services.search.reranker import RerankingService

# ── Embedding + reranking singletons (shared by ingest + retrieval) ────────
provider_svc = LLMProviderService(settings.embedding_provider_url)
embedding_svc = EmbeddingService(provider_svc, settings.embedding_model, settings.embedding_dimension)
reranking_svc = RerankingService(
    provider=settings.reranking_provider,
    model=settings.reranking_model,
    base_url=settings.reranking_provider_url,
    api_key=settings.reranking_api_key,
    top_n=settings.reranking_top_n,
)

# ── Qdrant singletons ──────────────────────────────────────────────────────
qdrant_client: QdrantClient = QdrantClient(
    host=settings.qdrant_host,
    port=settings.qdrant_port,
)
qdrant_search = QdrantSearch(client=qdrant_client)
qdrant_indexer = QdrantIndexer(
    client=qdrant_client,
    default_dim=settings.embedding_dimension,
)
rag_coordinator = RagCoordinator(
    embedder=embedding_svc,
    vector_search=qdrant_search,
    hybrid_search=None,  # Phase 8 hybrid_search wired separately when ready
    reranker=reranking_svc if settings.use_reranking else None,
)


def get_gitea_storage() -> GiteaStorage:
    """Construct a Gitea storage adapter per request.

    GiteaStorage owns an httpx.AsyncClient that must be closed; callers use
    it as an ``async with`` context manager. FastAPI does not pool async
    clients across requests, so a fresh instance per dependency call is
    intentional.
    """
    return GiteaStorage(
        base_url=settings.gitea_base_url,
        token=settings.gitea_token,
        owner=settings.gitea_kb_owner,
        repo=settings.gitea_kb_repo,
        branch=settings.gitea_kb_branch,
    )


# ── Factory functions for FastAPI Depends ──────────────────────────────────

def get_qdrant_search() -> QdrantSearch:
    return qdrant_search


def get_qdrant_indexer() -> QdrantIndexer:
    return qdrant_indexer


def get_rag_coordinator() -> RagCoordinator:
    return rag_coordinator


def get_embedding_svc() -> EmbeddingService:
    return embedding_svc


async def get_ingestion_pipeline():
    """Yield an `IngestionPipeline` bound to a per-request `GiteaStorage`.

    The Gitea HTTP client is owned by `GiteaStorage` and must be closed
    after the request completes — we use a generator dependency so FastAPI
    runs the teardown.
    """
    storage = GiteaStorage(
        base_url=settings.gitea_base_url,
        token=settings.gitea_token,
        owner=settings.gitea_kb_owner,
        repo=settings.gitea_kb_repo,
        branch=settings.gitea_kb_branch,
    )
    async with storage:
        yield IngestionPipeline(
            storage=storage,
            indexer=qdrant_indexer,
            embedder=embedding_svc,
        )


def get_settings():
    return settings
