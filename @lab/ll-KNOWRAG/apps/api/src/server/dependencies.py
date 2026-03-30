from supabase import create_client, Client
from server.config.config import settings
from server.services.crawling.discovery_service import DiscoveryService
from server.services.crawling.crawler_manager import CrawlerManager
from server.services.crawling.crawling_service import CrawlingService
from server.services.storage.storage_operations import StorageOperations
from server.services.knowledge.ingestion_service import IngestionService
from server.services.embeddings.llm_provider_service import LLMProviderService
from server.services.embeddings.embedding_service import EmbeddingService
from server.services.search.vector_search_strategy import VectorSearchStrategy
from server.services.search.hybrid_search_strategy import HybridSearchStrategy
from server.services.search.reranker import RerankingService
from server.services.search.rag_service import RagService

# Global instances (initialized once)
supabase: Client = create_client(settings.supabase_url, settings.supabase_service_key)
discovery_svc = DiscoveryService()
crawler_mgr = CrawlerManager()
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

# Factory functions for dependency injection
def get_storage_ops() -> StorageOperations:
    return storage_ops

def get_crawling_svc() -> CrawlingService:
    return crawling_svc

def get_ingestion_svc() -> IngestionService:
    return ingestion_svc

def get_rag_svc() -> RagService:
    return rag_svc

def get_settings():
    return settings
