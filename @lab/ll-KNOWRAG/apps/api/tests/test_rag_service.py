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
