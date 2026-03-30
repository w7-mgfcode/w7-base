from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

class SourceBase(BaseModel):
    source_id: str
    source_url: Optional[str] = None
    source_display_name: Optional[str] = None
    title: Optional[str] = None
    summary: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    total_word_count: int = 0

class SourceCreate(SourceBase):
    pass

class Source(SourceBase):
    created_at: datetime
    updated_at: datetime

class PageBase(BaseModel):
    source_id: str
    url: str
    full_content: str
    section_title: Optional[str] = None
    section_order: int = 0
    word_count: int = 0
    char_count: int = 0
    chunk_count: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)

class PageCreate(PageBase):
    pass

class Page(PageBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

class ChunkBase(BaseModel):
    source_id: str
    page_id: Optional[uuid.UUID] = None
    url: str
    chunk_number: int
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    embedding_model: Optional[str] = None
    embedding_dimension: Optional[int] = 768
    llm_chat_model: Optional[str] = None

class ChunkCreate(ChunkBase):
    embedding: Optional[List[float]] = None

class Chunk(ChunkBase):
    id: int
    created_at: datetime


class SourceUpdateRequest(BaseModel):
    title: Optional[str] = None
    display_name: Optional[str] = None
    tags: Optional[List[str]] = None


class SourceRefreshResponse(BaseModel):
    source_id: str
    crawl_id: str
    status: str


class SourceChunkListResponse(BaseModel):
    source_id: str
    total: int
    offset: int
    limit: int
    items: List[Chunk] = Field(default_factory=list)


class DocumentUploadResponse(BaseModel):
    source_id: str
    filename: str
    status: str
    pages_ingested: int = 1
