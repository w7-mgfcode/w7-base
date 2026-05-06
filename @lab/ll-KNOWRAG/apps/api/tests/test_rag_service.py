import asyncio
import uuid

from server.models.search import ChunkSearchResult
from server.services.search.rag_service import RagService


def test_group_by_page_groups_chunks_and_sorts_by_similarity():
    page_a = uuid.uuid4()
    page_b = uuid.uuid4()
    chunks = [
        ChunkSearchResult(
            id=1,
            source_id="source-a",
            page_id=page_a,
            content="chunk a1",
            metadata={"page_url": "https://example.com/a", "page_title": "Page A"},
            similarity=0.7,
        ),
        ChunkSearchResult(
            id=2,
            source_id="source-a",
            page_id=page_a,
            content="chunk a2",
            metadata={"page_url": "https://example.com/a", "page_title": "Page A"},
            similarity=0.9,
        ),
        ChunkSearchResult(
            id=3,
            source_id="source-b",
            page_id=page_b,
            content="chunk b1",
            metadata={"page_url": "https://example.com/b", "page_title": "Page B"},
            similarity=0.8,
        ),
    ]

    service = RagService(embedding_service=None, vector_strategy=None, hybrid_strategy=None)
    results = asyncio.run(service._group_by_page(chunks))

    assert len(results) == 2
    assert results[0].page_id == page_a
    assert results[0].max_similarity == 0.9
    assert results[0].chunk_count == 2
    assert results[1].page_id == page_b


def test_group_by_page_ignores_chunks_without_page_id():
    page_a = uuid.uuid4()
    chunks = [
        ChunkSearchResult(
            id=1,
            source_id="source-a",
            page_id=None,
            content="orphan chunk",
            metadata={},
            similarity=0.95,
        ),
        ChunkSearchResult(
            id=2,
            source_id="source-a",
            page_id=page_a,
            content="attached chunk",
            metadata={"page_url": "https://example.com/a", "page_title": "Page A"},
            similarity=0.75,
        ),
    ]

    service = RagService(embedding_service=None, vector_strategy=None, hybrid_strategy=None)
    results = asyncio.run(service._group_by_page(chunks))

    assert len(results) == 1
    assert results[0].page_id == page_a
    assert results[0].chunk_count == 1

import pytest
from unittest.mock import AsyncMock, MagicMock
from server.models.search import SearchRequest, SearchMode

@pytest.mark.asyncio
async def test_rag_service_sets_reranking_applied_true_when_successful():
    mock_embedding_svc = MagicMock()
    mock_embedding_svc.provider.get_embeddings = AsyncMock(return_value=[[0.1, 0.2]])
    mock_vector_strategy = MagicMock()
    mock_vector_strategy.search = AsyncMock(return_value=[
        ChunkSearchResult(id=1, source_id="s1", content="test", similarity=0.9)
    ])
    mock_reranking_svc = MagicMock()
    mock_reranking_svc.rerank = AsyncMock(return_value=[
        ChunkSearchResult(id=1, source_id="s1", content="test", similarity=0.95)
    ])
    
    service = RagService(
        embedding_service=mock_embedding_svc, 
        vector_strategy=mock_vector_strategy,
        reranking_service=mock_reranking_svc
    )
    
    request = SearchRequest(query="test", use_reranking=True, mode=SearchMode.CHUNK)
    response = await service.query(request)
    
    assert response.reranking_applied is True
    assert len(response.results) == 1

@pytest.mark.asyncio
async def test_rag_service_sets_reranking_applied_false_on_failure():
    mock_embedding_svc = MagicMock()
    mock_embedding_svc.provider.get_embeddings = AsyncMock(return_value=[[0.1, 0.2]])
    mock_vector_strategy = MagicMock()
    mock_vector_strategy.search = AsyncMock(return_value=[
        ChunkSearchResult(id=1, source_id="s1", content="test", similarity=0.9)
    ])
    mock_reranking_svc = MagicMock()
    mock_reranking_svc.rerank = AsyncMock(side_effect=Exception("API failure"))
    
    service = RagService(
        embedding_service=mock_embedding_svc, 
        vector_strategy=mock_vector_strategy,
        reranking_service=mock_reranking_svc
    )
    
    request = SearchRequest(query="test", use_reranking=True, mode=SearchMode.CHUNK)
    response = await service.query(request)
    
    # Reranking failed, but it gracefully degraded
    assert response.reranking_applied is False
    assert len(response.results) == 1

