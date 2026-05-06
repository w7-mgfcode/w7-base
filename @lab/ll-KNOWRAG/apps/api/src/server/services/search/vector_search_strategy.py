from typing import List
from supabase import Client
from server.services.search.base_search_strategy import BaseSearchStrategy
from server.models.search import SearchRequest, ChunkSearchResult

class VectorSearchStrategy(BaseSearchStrategy):
    """
    Semantic search using vector similarity (pgvector).
    """
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client

    async def search(self, request: SearchRequest, embedding: List[float]) -> List[ChunkSearchResult]:
        params = {
            "query_embedding": embedding,
            "match_threshold": request.match_threshold,
            "match_count": request.limit,
            "filter_source_id": request.filter_source_id
        }
        
        result = self.supabase.rpc("match_kb_chunks", params).execute()
        
        chunks = []
        for item in result.data:
            chunks.append(ChunkSearchResult(
                id=item["id"],
                source_id=item["source_id"],
                page_id=item["page_id"],
                content=item["content"],
                metadata=item["metadata"],
                similarity=item["similarity"]
            ))
        return chunks
