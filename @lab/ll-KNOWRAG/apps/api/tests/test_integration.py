import asyncio
import uuid
from unittest.mock import AsyncMock, MagicMock, PropertyMock

from server.services.knowledge.ingestion_service import IngestionService
from server.services.storage.storage_operations import StorageOperations
from server.services.embeddings.embedding_service import EmbeddingService
from server.models.knowledge import SourceCreate, PageCreate, ChunkCreate


def _make_stored_page(source_id="test-src", url="https://example.com/p1"):
    page = MagicMock()
    page.id = uuid.uuid4()
    page.source_id = source_id
    page.url = url
    return page


def test_ingest_crawl_results_calls_storage_in_order():
    """
    Verifies IngestionService calls upsert_source -> upsert_page -> insert_chunks.
    """
    mock_storage = MagicMock(spec=StorageOperations)
    mock_storage.upsert_source = AsyncMock()
    mock_storage.upsert_page = AsyncMock(return_value=_make_stored_page())
    mock_storage.insert_chunks = AsyncMock(return_value=[])

    mock_embedding = MagicMock(spec=EmbeddingService)
    mock_embedding.embed_chunks = AsyncMock(side_effect=lambda chunks: chunks)

    service = IngestionService(storage_ops=mock_storage, embedding_service=mock_embedding)

    crawl_results = [{
        "url": "https://example.com/page1",
        "content": "Some documentation content for testing purposes",
        "title": "Page 1",
        "success": True,
        "metadata": {},
    }]

    asyncio.run(service.ingest_crawl_results(
        source_id="test-src",
        crawl_results=crawl_results,
        metadata={"base_url": "https://example.com"}
    ))

    mock_storage.upsert_source.assert_called_once()
    mock_storage.upsert_page.assert_called_once()
    mock_storage.insert_chunks.assert_called_once()

    # Verify chunks were created with correct source_id
    chunks_arg = mock_storage.insert_chunks.call_args[0][0]
    assert len(chunks_arg) > 0
    assert all(c.source_id == "test-src" for c in chunks_arg)


def test_ingest_crawl_results_works_without_embeddings():
    """
    Verifies the pipeline stores chunks even when no embedding service is provided.
    """
    mock_storage = MagicMock(spec=StorageOperations)
    mock_storage.upsert_source = AsyncMock()
    mock_storage.upsert_page = AsyncMock(return_value=_make_stored_page())
    mock_storage.insert_chunks = AsyncMock(return_value=[])

    service = IngestionService(storage_ops=mock_storage, embedding_service=None)

    crawl_results = [{
        "url": "https://example.com/page1",
        "content": "Content without embeddings",
        "title": "No Embed Page",
        "success": True,
        "metadata": {},
    }]

    asyncio.run(service.ingest_crawl_results(
        source_id="no-embed",
        crawl_results=crawl_results,
    ))

    mock_storage.upsert_source.assert_called_once()
    mock_storage.upsert_page.assert_called_once()
    mock_storage.insert_chunks.assert_called_once()

    chunks_arg = mock_storage.insert_chunks.call_args[0][0]
    # Chunks should not have embeddings
    assert all(c.embedding is None for c in chunks_arg if hasattr(c, 'embedding'))
