import asyncio
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

from server.models.knowledge import ChunkCreate
from server.services.storage.storage_operations import StorageOperations


def test_insert_chunks_omits_optional_none_fields():
    supabase = MagicMock()
    table = supabase.table.return_value
    upsert = table.upsert.return_value
    upsert.execute.return_value = MagicMock(
        data=[
            {
                "id": 1,
                "source_id": "src",
                "page_id": str(uuid.uuid4()),
                "url": "https://example.com",
                "chunk_number": 0,
                "content": "chunk",
                "metadata": {},
                "embedding_model": None,
                "embedding_dimension": 768,
                "llm_chat_model": None,
                "created_at": "2026-01-01T00:00:00Z",
            }
        ]
    )

    ops = StorageOperations(supabase)
    chunk = ChunkCreate(
        source_id="src",
        page_id=uuid.uuid4(),
        url="https://example.com",
        chunk_number=0,
        content="chunk",
        metadata={},
    )

    async def fake_to_thread(fn):
        return fn()

    with patch("server.services.storage.storage_operations.asyncio.to_thread", new=AsyncMock(side_effect=fake_to_thread)):
        asyncio.run(ops.insert_chunks([chunk]))

    payload = table.upsert.call_args.args[0][0]
    assert "contextual_content" not in payload
    assert "embedding" not in payload
