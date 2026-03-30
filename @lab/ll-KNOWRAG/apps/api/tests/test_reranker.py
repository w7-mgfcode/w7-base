import pytest
import asyncio
from server.services.search.reranker import RerankingService
from server.models.search import ChunkSearchResult

@pytest.mark.asyncio
async def test_reranker_boosts_lexical_overlap():
    reranker = RerankingService()
    query = "fastapi docs"
    chunks = [
        ChunkSearchResult(
            id=1, source_id="s1", content="Some unrelated text", similarity=0.9, metadata={}
        ),
        ChunkSearchResult(
            id=2, source_id="s1", content="FastAPI documentation and guides", similarity=0.8, metadata={}
        ),
    ]
    
    # Before reranking, chunk 1 (0.9) is better than chunk 2 (0.8)
    results = await reranker.rerank(query, chunks)
    
    # After reranking, chunk 2 should have a boost from lexical overlap ("fastapi", "docs")
    # chunk 1: 0.9 * 0.7 + 0.0 * 0.3 = 0.63
    # chunk 2: 0.8 * 0.7 + 1.0 * 0.3 = 0.56 + 0.3 = 0.86 (if both words match)
    # Wait, "docs" matches "documentation"? No, only exact word match in my simple regex.
    # "fastapi" matches "FastAPI".
    
    assert len(results) == 2
    assert results[0].id == 2  # Chunk 2 should be first now
    assert results[0].similarity > results[1].similarity

@pytest.mark.asyncio
async def test_reranker_graceful_fallback_on_invalid_provider():
    reranker = RerankingService(provider="invalid_provider")
    query = "fastapi docs"
    chunks = [
        ChunkSearchResult(id=1, source_id="s1", content="text", similarity=0.9),
        ChunkSearchResult(id=2, source_id="s1", content="FastAPI", similarity=0.8),
    ]
    # Should fall back to lexical
    results = await reranker.rerank(query, chunks)
    assert len(results) == 2
    assert results[0].id == 2  # FastAPI gets lexical boost
