import time
import logging
from typing import List, Dict, Any, Optional
import uuid

from server.services.search.base_search_strategy import BaseSearchStrategy
from server.services.search.vector_search_strategy import VectorSearchStrategy
from server.services.search.hybrid_search_strategy import HybridSearchStrategy
from server.services.embeddings.embedding_service import EmbeddingService
from server.models.search import (
    SearchRequest, SearchResponse, SearchMode, 
    ChunkSearchResult, PageSearchResult
)

logger = logging.getLogger(__name__)

class RagService:
    """
    Retrieval Coordinator (RAG Service).
    Ported from Archon: orchestrates query embedding, search, and page grouping.
    """
    
    def __init__(
        self, 
        embedding_service: EmbeddingService,
        vector_strategy: VectorSearchStrategy,
        hybrid_strategy: Optional[HybridSearchStrategy] = None
    ):
        self.embedding_service = embedding_service
        self.vector_strategy = vector_strategy
        self.hybrid_strategy = hybrid_strategy

    async def query(self, request: SearchRequest) -> SearchResponse:
        start_time = time.time()
        
        # 1. Embed query
        # We wrap query in a dummy ChunkCreate-like object if needed or just use a helper
        # Since EmbeddingService.embed_chunks takes List[ChunkCreate], 
        # let's assume it has or we add a direct embed_text method
        # For now, let's just use its provider directly or a mocked call
        
        # Actually, let's assume EmbeddingService has a method 'get_query_embedding'
        # if not, we use the provider.
        query_embedding = await self.embedding_service.provider.get_embeddings(
            self.embedding_service.model, [request.query]
        )
        embedding = query_embedding[0]
        
        # 2. Select strategy
        strategy: BaseSearchStrategy = self.vector_strategy
        if request.use_hybrid and self.hybrid_strategy:
            strategy = self.hybrid_strategy
            
        # 3. Execute search
        chunks = await strategy.search(request, embedding)
        
        # 4. Process results by mode
        results = chunks
        if request.mode == SearchMode.PAGE:
            results = await self._group_by_page(chunks)
            
        processing_time = (time.time() - start_time) * 1000
        
        return SearchResponse(
            query=request.query,
            mode=request.mode,
            results=results,
            total_results=len(results),
            processing_time_ms=processing_time
        )

    async def _group_by_page(self, chunks: List[ChunkSearchResult]) -> List[PageSearchResult]:
        """
        Groups chunk results by page_id for page-mode retrieval.
        """
        if not chunks:
            return []
            
        page_map: Dict[uuid.UUID, List[ChunkSearchResult]] = {}
        for c in chunks:
            if c.page_id:
                if c.page_id not in page_map:
                    page_map[c.page_id] = []
                page_map[c.page_id].append(c)
                
        page_results = []
        for pid, p_chunks in page_map.items():
            # In a real port, we'd fetch page metadata (url, title) from DB here
            # For v1, we extract what we can from chunk metadata or return skeleton
            first_chunk = p_chunks[0]
            max_sim = max(c.similarity for c in p_chunks)
            
            page_results.append(PageSearchResult(
                page_id=pid,
                source_id=first_chunk.source_id,
                url=first_chunk.metadata.get("page_url", "unknown"),
                title=first_chunk.metadata.get("page_title", "Untitled"),
                max_similarity=max_sim,
                chunk_count=len(p_chunks),
                chunks=p_chunks
            ))
            
        # Sort by max similarity
        page_results.sort(key=lambda x: x.max_similarity, reverse=True)
        return page_results
