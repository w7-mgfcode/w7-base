import asyncio
from typing import List, Optional, Dict, Any
from supabase import Client
import logging
from server.models.knowledge import SourceCreate, PageCreate, ChunkCreate, Source, Page, Chunk
import uuid

logger = logging.getLogger(__name__)

class StorageOperations:
    """
    Direct DB interactions for Source, Page, and Chunk.
    Ported from Archon: adapted for local Supabase/pgvector.
    """
    
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client

    async def upsert_source(self, source: SourceCreate) -> Source:
        """
        Upserts a knowledge source.
        """
        data = source.model_dump(mode="json", exclude_none=True)
        result = await asyncio.to_thread(lambda: self.supabase.table("kb_sources").upsert(data).execute())
        return Source(**result.data[0])

    async def upsert_page(self, page: PageCreate) -> Page:
        """
        Upserts a page and handles source-link.
        """
        data = page.model_dump(mode="json", exclude_none=True)
        result = await asyncio.to_thread(lambda: self.supabase.table("kb_pages").upsert(data, on_conflict="url").execute())
        return Page(**result.data[0])

    async def insert_chunks(self, chunks: List[ChunkCreate]) -> List[Chunk]:
        """
        Batch inserts chunks.
        """
        if not chunks:
            return []
        
        # PostgREST rejects unknown columns even when they are sent as null.
        # Excluding None keeps old schemas working until optional migrations are applied.
        data = [chunk.model_dump(mode="json", exclude_none=True) for chunk in chunks]
        # We use on_conflict (url, chunk_number) to avoid duplicates
        result = await asyncio.to_thread(
            lambda: self.supabase.table("kb_chunks").upsert(data, on_conflict="url,chunk_number").execute()
        )
        return [Chunk(**item) for item in result.data]

    async def delete_source(self, source_id: str):
        """
        Deletes a source and all its pages/chunks (cascading).
        """
        await asyncio.to_thread(
            lambda: self.supabase.table("kb_sources").delete().eq("source_id", source_id).execute()
        )

    async def get_source(self, source_id: str) -> Optional[Source]:
        """
        Fetches a single source by source_id.
        """
        result = await asyncio.to_thread(
            lambda: self.supabase.table("kb_sources").select("*").eq("source_id", source_id).limit(1).execute()
        )
        if not result.data:
            return None
        return Source(**result.data[0])

    async def update_source(self, source_id: str, title: Optional[str] = None, display_name: Optional[str] = None, tags: Optional[List[str]] = None) -> Optional[Source]:
        """
        Updates mutable source metadata fields.
        """
        existing = await self.get_source(source_id)
        if not existing:
            return None

        update_data: Dict[str, Any] = {}
        if title is not None:
            update_data["title"] = title
        if display_name is not None:
            update_data["source_display_name"] = display_name
        if tags is not None:
            metadata = dict(existing.metadata or {})
            metadata["tags"] = tags
            update_data["metadata"] = metadata

        if not update_data:
            return existing

        result = await asyncio.to_thread(
            lambda: self.supabase.table("kb_sources").update(update_data).eq("source_id", source_id).execute()
        )
        if not result.data:
            return None
        return Source(**result.data[0])

    async def list_source_chunks(self, source_id: str, offset: int = 0, limit: int = 50) -> tuple[int, List[Chunk]]:
        """
        Lists chunks for a source with pagination.
        """
        count_result = await asyncio.to_thread(
            lambda: self.supabase.table("kb_chunks").select("id", count="exact").eq("source_id", source_id).execute()
        )
        total = count_result.count or 0

        result = await asyncio.to_thread(
            lambda: (
                self.supabase
                .table("kb_chunks")
                .select("*")
                .eq("source_id", source_id)
                .order("chunk_number")
                .range(offset, offset + limit - 1)
                .execute()
            )
        )
        return total, [Chunk(**item) for item in result.data]
