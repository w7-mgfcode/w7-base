import logging
import time
import re
import httpx
from typing import List
from server.models.search import ChunkSearchResult

logger = logging.getLogger(__name__)

class RerankingService:
    """
    Second-pass reranking for retrieval results.
    Supports provider-based reranking ('cohere', 'ollama') with a safe 'lexical' fallback.
    """
    
    def __init__(
        self, 
        provider: str = "lexical",
        model: str = "",
        base_url: str = "",
        api_key: str = "",
        top_n: int = 0
    ):
        self.provider = provider.lower() if provider else "lexical"
        self.model = model
        self.base_url = base_url
        self.api_key = api_key
        self.top_n = top_n
        self.timeout = httpx.Timeout(60.0)

    async def rerank(self, query: str, chunks: List[ChunkSearchResult]) -> List[ChunkSearchResult]:
        if not chunks:
            return []

        start_time = time.time()
        original_count = len(chunks)
        
        try:
            if self.provider == "cohere":
                chunks = await self._rerank_cohere(query, chunks)
            elif self.provider == "ollama":
                chunks = await self._rerank_ollama(query, chunks)
            else:
                chunks = self._rerank_lexical(query, chunks)
        except Exception as e:
            logger.warning(f"Reranking with provider '{self.provider}' failed: {str(e)}. Falling back to lexical.")
            # Graceful degradation: fallback to the safe lexical baseline
            chunks = self._rerank_lexical(query, chunks)

        if self.top_n > 0:
            chunks = chunks[:self.top_n]
            
        duration = (time.time() - start_time) * 1000
        logger.info(f"Reranked {original_count} results to {len(chunks)} via '{self.provider}' in {duration:.2f}ms")
        return chunks

    def _rerank_lexical(self, query: str, chunks: List[ChunkSearchResult]) -> List[ChunkSearchResult]:
        """
        Lexical Boost strategy (70% original similarity, 30% lexical overlap)
        Simplest viable approach for local-first.
        """
        query_words = set(re.findall(r'\w+', query.lower()))
        
        for chunk in chunks:
            chunk_words = set(re.findall(r'\w+', chunk.content.lower()))
            overlap = len(query_words.intersection(chunk_words))
            lexical_score = overlap / len(query_words) if query_words else 0.0
            
            # Combine original similarity (vector/hybrid) with lexical overlap
            chunk.similarity = (chunk.similarity * 0.7) + (lexical_score * 0.3)
            
        # Re-sort by updated similarity
        chunks.sort(key=lambda x: x.similarity, reverse=True)
        return chunks

    async def _rerank_cohere(self, query: str, chunks: List[ChunkSearchResult]) -> List[ChunkSearchResult]:
        """
        Calls Cohere API to rerank the chunks.
        Expects Cohere /v2/rerank payload structure.
        """
        if not self.api_key:
            raise ValueError("API key is required for Cohere reranking")
            
        url = self.base_url or "https://api.cohere.com/v2/rerank"
        docs = [c.content for c in chunks]
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model or "rerank-v3.5",
            "query": query,
            "documents": docs,
            "top_n": self.top_n if self.top_n > 0 else len(docs)
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            
        results = data.get("results", [])
        reranked_chunks = []
        for r in results:
            idx = r.get("index")
            score = r.get("relevance_score", 0.0)
            if idx is not None and idx < len(chunks):
                chunk = chunks[idx]
                chunk.similarity = float(score)
                reranked_chunks.append(chunk)
                
        return reranked_chunks

    async def _rerank_ollama(self, query: str, chunks: List[ChunkSearchResult]) -> List[ChunkSearchResult]:
        """
        Calls an Ollama-compatible rerank API.
        Assumes Jina/BGE style rerank format via Ollama /api/rerank or similar proxy.
        """
        if not self.model:
            raise ValueError("Model is required for Ollama reranking")
            
        url = self.base_url.rstrip('/') + "/api/rerank" if self.base_url else "http://localhost:11434/api/rerank"
        docs = [c.content for c in chunks]
        
        payload = {
            "model": self.model,
            "query": query,
            "documents": docs
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    raise NotImplementedError(f"Ollama server at {url} does not support /api/rerank endpoint")
                raise e
                
            data = resp.json()
            
        # Try to parse different possible rerank response formats
        # Standard: {"results": [{"index": 0, "relevance_score": 0.9}]}
        # Alternatively maybe some return 'document_index' or 'score'
        results = data.get("results", [])
        
        if not results:
            raise ValueError("No results returned from Ollama rerank API")
            
        reranked_chunks = []
        for r in results:
            idx = r.get("index", r.get("document_index"))
            score = r.get("relevance_score", r.get("score", 0.0))
            if idx is not None and idx < len(chunks):
                chunk = chunks[idx]
                chunk.similarity = float(score)
                reranked_chunks.append(chunk)
                
        # Ollama might not sort them or limit them, so we sort just in case
        reranked_chunks.sort(key=lambda x: x.similarity, reverse=True)
        return reranked_chunks
