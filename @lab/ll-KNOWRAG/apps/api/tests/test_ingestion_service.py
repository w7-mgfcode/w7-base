import uuid

from server.services.knowledge.ingestion_service import IngestionService


def test_chunk_content_splits_structural_sections():
    service = IngestionService(storage_ops=None)
    page_id = uuid.uuid4()
    content = "Intro section\n# Heading One\nBody for heading one."

    chunks = service._chunk_content(content, "source-a", page_id, "https://example.com")

    assert len(chunks) == 2
    assert chunks[0].content == "Intro section"
    assert chunks[1].content.startswith("Heading One")


def test_chunk_content_windows_large_sections():
    service = IngestionService(storage_ops=None)
    page_id = uuid.uuid4()
    content = "A" * 1800

    chunks = service._chunk_content(content, "source-a", page_id, "https://example.com")

    assert len(chunks) == 2
    assert len(chunks[0].content) == 1500
    assert len(chunks[1].content) == 500


def test_chunk_content_applies_overlap_between_windows():
    service = IngestionService(storage_ops=None)
    page_id = uuid.uuid4()
    content = "".join(str(i % 10) for i in range(1800))

    chunks = service._chunk_content(content, "source-a", page_id, "https://example.com")

    assert len(chunks) == 2
    assert chunks[0].content[-200:] == chunks[1].content[:200]

import pytest
from unittest.mock import AsyncMock, MagicMock
from server.models.knowledge import SourceCreate

@pytest.mark.asyncio
async def test_ingest_crawl_results_persists_metadata_tags():
    mock_storage = MagicMock()
    mock_storage.upsert_source = AsyncMock(return_value=MagicMock())
    mock_storage.upsert_page = AsyncMock(return_value=MagicMock(id=uuid.uuid4()))
    mock_storage.insert_chunks = AsyncMock()
    
    service = IngestionService(storage_ops=mock_storage)
    
    source_id = "test-source"
    crawl_results = [{"url": "http://test.com", "content": "test content", "title": "Test"}]
    metadata = {"tags": ["tag1", "tag2"]}
    
    await service.ingest_crawl_results(source_id, crawl_results, metadata=metadata)
    
    # Check if upsert_source was called with the correct metadata including tags
    mock_storage.upsert_source.assert_called_once()
    args, _ = mock_storage.upsert_source.call_args
    source_create = args[0]
    assert isinstance(source_create, SourceCreate)
    assert source_create.metadata == {"tags": ["tag1", "tag2"]}

