import logging
import re
from typing import List, Dict, Any, Optional
import uuid
from server.models.knowledge import SourceCreate, PageCreate, ChunkCreate
from server.services.storage.storage_operations import StorageOperations
from server.services.embeddings.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)

class IngestionService:
    """
    Orchestrates ingestion: Source -> Pages -> Chunks.
    Ported from Archon: adapted with Section 10 chunking strategy.
    Integrated with EmbeddingService.
    """
    
    def __init__(self, storage_ops: StorageOperations, embedding_service: Optional[EmbeddingService] = None, use_contextual: bool = False, chat_model: str = "llama3"):
        self.storage_ops = storage_ops
        self.embedding_service = embedding_service
        self.use_contextual = use_contextual
        self.chat_model = chat_model

    async def ingest_crawl_results(self, source_id: str, crawl_results: List[Dict[str, Any]], metadata: Dict[str, Any] = None):
        """
        Main entrypoint for ingesting crawled content.
        """
        # 1. Create/Update Source
        source_url = crawl_results[0].get("url") if crawl_results else ""
        source_title = crawl_results[0].get("title", source_id)
        
        source = SourceCreate(
            source_id=source_id,
            source_url=source_url,
            source_display_name=source_title,
            title=source_title,
            metadata=metadata or {}
        )
        await self.storage_ops.upsert_source(source)
        
        # 2. Process each result as a Page
        for result in crawl_results:
            content = result.get("content", "")
            url = self._normalize_url(result.get("url", ""))

            page = PageCreate(
                source_id=source_id,
                url=url,
                full_content=content,
                section_title=result.get("title"),
                word_count=len(content.split()),
                char_count=len(content),
                metadata=result.get("metadata", {})
            )
            stored_page = await self.storage_ops.upsert_page(page)

            # 3. Create Chunks (Blueprint Section 10)
            chunks = self._chunk_content(content, source_id, stored_page.id, url)
            
            # 3.5 Contextual Embeddings Pass
            if self.use_contextual and self.embedding_service and chunks:
                try:
                    for chunk in chunks:
                        prompt = f"Document Title/URL: {url}\n\nDocument Content:\n{content[:4000]}\n\nChunk:\n{chunk.content}\n\nPlease write a concise 1-2 sentence context to situate this chunk within the overall document."
                        context = await self.embedding_service.provider.generate_text(self.chat_model, prompt)
                        if context:
                            chunk.contextual_content = f"Context: {context}\n\nChunk: {chunk.content}"
                            chunk.llm_chat_model = self.chat_model
                except Exception as e:
                    logger.error(f"Failed to generate context for chunks: {str(e)}")

            # 4. Generate Embeddings if service is provided
            if self.embedding_service and chunks:
                try:
                    chunks = await self.embedding_service.embed_chunks(chunks)
                except Exception as e:
                    logger.error(f"Failed to generate embeddings during ingestion: {str(e)}")
                    # We proceed to store chunks even without embeddings, 
                    # as per Archon's logic (or we could fail depending on project policy)
            
            if chunks:
                await self.storage_ops.insert_chunks(chunks)

    @staticmethod
    def _normalize_url(url: str) -> str:
        """Strip fragment and trailing slash for consistent URL storage."""
        return url.split('#')[0].rstrip('/') if url else url

    def _chunk_content(self, content: str, source_id: str, page_id: uuid.UUID, url: str) -> List[ChunkCreate]:
        """
        Implements Section 10 chunking strategy.
        """
        # Simple structural split on common markdown/HTML headers
        sections = re.split(r'\n#+\s+|\n[=-]{3,}\n', content)
        chunks: List[ChunkCreate] = []
        chunk_num = 0
        
        for section in sections:
            section = section.strip()
            if not section:
                continue
                
            # Windowing fallback within section
            target_size = 1500
            overlap = 200
            
            start = 0
            while start < len(section):
                end = start + target_size
                chunk_text = section[start:end]
                
                chunks.append(ChunkCreate(
                    source_id=source_id,
                    page_id=page_id,
                    url=url,
                    chunk_number=chunk_num,
                    content=chunk_text,
                    metadata={"char_count": len(chunk_text)}
                ))
                
                chunk_num += 1
                if end >= len(section):
                    break
                start += target_size - overlap
                
        return chunks
