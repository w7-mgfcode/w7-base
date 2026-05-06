"""Application-wide service singletons + FastAPI dependency providers.

Phase 7 (Supabase + PostgREST) wiring is preserved for crawl/ingest paths
that have not yet migrated. Phase 8 (Gitea + Qdrant) wiring is **additive**:
the new factories return the new services without disturbing the legacy
ones, so T10 routes can opt in incrementally.
"""
from __future__ import annotations

from supabase import create_client, Client
from qdrant_client import QdrantClient

from server.config.config import settings
from server.services.crawling.discovery_service import DiscoveryService
from server.services.crawling.crawler_manager import CrawlerManager
from server.services.crawling.crawling_service import CrawlingService
from server.services.storage.storage_operations import StorageOperations
from server.services.storage.gitea_storage import GiteaStorage
from server.services.knowledge.ingestion_service import IngestionService
from server.services.embeddings.llm_provider_service import LLMProviderService
from server.services.embeddings.embedding_service import EmbeddingService
from server.services.search.vector_search_strategy import VectorSearchStrategy
from server.services.search.hybrid_search_strategy import HybridSearchStrategy
from server.services.search.qdrant_search import QdrantSearch
from server.services.search.qdrant_indexer import QdrantIndexer
from server.services.search.rag_coordinator import RagCoordinator
from server.services.search.reranker import RerankingService
from server.services.search.rag_service import RagService

# ── Phase 7 — Supabase singletons (legacy) ─────────────────────────────────
supabase: Client = create_client(settings.supabase_url, settings.supabase_service_key)
discovery_svc = DiscoveryService()
crawler_mgr = CrawlerManager(
    timeout=settings.crawl_page_timeout,
    use_crawl4ai=settings.use_crawl4ai,
    headless=settings.crawl4ai_headless,
    viewport_width=settings.crawl4ai_viewport_width,
    viewport_height=settings.crawl4ai_viewport_height,
    wait_strategy=settings.crawl_wait_strategy,
    delay_before_return=settings.crawl4ai_delay_before_return,
    scan_full_page=settings.crawl4ai_scan_full_page,
)
storage_ops = StorageOperations(supabase)
provider_svc = LLMProviderService(settings.embedding_provider_url)
embedding_svc = EmbeddingService(provider_svc, settings.embedding_model, settings.embedding_dimension)
ingestion_svc = IngestionService(storage_ops, embedding_svc, settings.use_contextual_embeddings, settings.chat_model)
crawling_svc = CrawlingService(discovery_svc, crawler_mgr, ingestion_svc)
vector_strategy = VectorSearchStrategy(supabase)
hybrid_strategy = HybridSearchStrategy(supabase) if settings.use_hybrid_search else None
reranking_svc = RerankingService(
    provider=settings.reranking_provider,
    model=settings.reranking_model,
    base_url=settings.reranking_provider_url,
    api_key=settings.reranking_api_key,
    top_n=settings.reranking_top_n
)
rag_svc = RagService(embedding_svc, vector_strategy, hybrid_strategy, reranking_svc)


# ── Phase 8 — Gitea + Qdrant singletons ────────────────────────────────────

# Qdrant client — shared by indexer, search, and reconcile paths.
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

def get_storage_ops() -> StorageOperations:
    return storage_ops


def get_crawling_svc() -> CrawlingService:
    return crawling_svc


def get_ingestion_svc() -> IngestionService:
    return ingestion_svc


def get_rag_svc() -> RagService:
    return rag_svc


def get_qdrant_search() -> QdrantSearch:
    return qdrant_search


def get_qdrant_indexer() -> QdrantIndexer:
    return qdrant_indexer


def get_rag_coordinator() -> RagCoordinator:
    return rag_coordinator


def get_embedding_svc() -> EmbeddingService:
    return embedding_svc


def get_settings():
    return settings
