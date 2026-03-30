from typing import List
from supabase import Client
from server.services.search.base_search_strategy import BaseSearchStrategy
from server.models.search import SearchRequest, ChunkSearchResult

class HybridSearchStrategy(BaseSearchStrategy):
    """
    Combines vector search and full-text search.
    """
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client

    async def search(self, request: SearchRequest, embedding: List[float]) -> List[ChunkSearchResult]:
        params = {
            "query_text": request.query,
            "query_embedding": embedding,
            "match_threshold": request.match_threshold,
            "match_count": request.limit,
            "full_text_weight": request.metadata.get("full_text_weight", 1.0),
            "vector_weight": request.metadata.get("vector_weight", 1.0)
        }
        
        # Note: RPC logic for filter_source_id in hybrid might need adjustment in SQL 
        # if not already handled in migration 006.
        result = self.supabase.rpc("hybrid_search_kb_chunks", params).execute()
        
        chunks = []
        for item in result.data:
            chunks.append(ChunkSearchResult(
                id=item["id"],
                source_id=item.get("source_id", "unknown"), # depends on RPC return shape
                page_id=item.get("page_id"),
                content=item["content"],
                metadata=item["metadata"],
                similarity=item.get("combined_score", 0.0)
            ))
        return chunks
