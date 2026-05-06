import logging
import asyncio
from typing import List, Optional, Dict, Any
from .llm_provider_service import LLMProviderService
from server.models.knowledge import ChunkCreate

logger = logging.getLogger(__name__)

class EmbeddingService:
    """
    Orchestrates embedding generation with batching and provider abstraction.
    Ported from Archon: adapted for local-first KB.
    """
    
    def __init__(self, provider_service: LLMProviderService, model: str, dimension: int = 768):
        self.provider = provider_service
        self.model = model
        self.dimension = dimension
        self.batch_size = 32

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed raw texts in batches; satisfies the ``Embedder`` protocol used
        by Phase 8 indexing and retrieval coordinators."""
        if not texts:
            return []
        all_embeddings: List[List[float]] = []
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            embeddings = await self.provider.get_embeddings(self.model, batch)
            for emb in embeddings:
                if len(emb) != self.dimension:
                    raise ValueError(
                        f"Embedding dimension mismatch: {len(emb)} != {self.dimension}"
                    )
            all_embeddings.extend(embeddings)
        return all_embeddings

    async def embed_chunks(self, chunks: List[ChunkCreate]) -> List[ChunkCreate]:
        """
        Generates embeddings for a list of chunks in batches.
        """
        if not chunks:
            return []

        # Extract content for embedding
        texts = [chunk.contextual_content if chunk.contextual_content else chunk.content for chunk in chunks]
        
        all_embeddings = []
        for i in range(0, len(texts), self.batch_size):
            batch_texts = texts[i:i + self.batch_size]
            logger.info(f"Generating embeddings for batch {i//self.batch_size + 1} ({len(batch_texts)} items)")
            
            try:
                batch_embeddings = await self.provider.get_embeddings(self.model, batch_texts)
                
                # Validation: dimension check
                for idx, emb in enumerate(batch_embeddings):
                    if len(emb) != self.dimension:
                        logger.error(f"Dimension mismatch! Expected {self.dimension}, got {len(emb)}")
                        # In YOLO mode, we might want to fail hard here or skip
                        raise ValueError(f"Embedding dimension mismatch: {len(emb)} != {self.dimension}")
                
                all_embeddings.extend(batch_embeddings)
            except Exception as e:
                logger.exception(f"Failed to generate embeddings for batch: {str(e)}")
                raise

        # Map back to chunks
        for idx, chunk in enumerate(chunks):
            if idx < len(all_embeddings):
                chunk.embedding = all_embeddings[idx]
                chunk.embedding_model = self.model
                chunk.embedding_dimension = self.dimension
        
        return chunks
