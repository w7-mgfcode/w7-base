from typing import List, Dict, Any
import logging
import time
import re
from server.models.search import ChunkSearchResult

logger = logging.getLogger(__name__)

class RerankingService:
    """
    Second-pass reranking for retrieval results.
    Simplest viable approach for local-first: Normalized Similarity + Lexical Boost.
    """
    
    def __init__(self, use_llm_as_fallback: bool = False):
        self.use_llm = use_llm_as_fallback

    async def rerank(self, query: str, chunks: List[ChunkSearchResult]) -> List[ChunkSearchResult]:
        if not chunks:
            return []

        start_time = time.time()
        query_words = set(re.findall(r'\w+', query.lower()))
        
        # 1. Calculate lexical overlap score (simple substitute for a model-based reranker)
        for chunk in chunks:
            chunk_words = set(re.findall(r'\w+', chunk.content.lower()))
            overlap = len(query_words.intersection(chunk_words))
            lexical_score = overlap / len(query_words) if query_words else 0.0
            
            # Combine original similarity (vector/hybrid) with lexical overlap
            # We give 70% weight to original, 30% to lexical refinement
            chunk.similarity = (chunk.similarity * 0.7) + (lexical_score * 0.3)
            
        # 2. Re-sort by updated similarity
        chunks.sort(key=lambda x: x.similarity, reverse=True)
        
        duration = (time.time() - start_time) * 1000
        logger.info(f"Reranked {len(chunks)} results in {duration:.2f}ms")
        return chunks
