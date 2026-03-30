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
