from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from enum import Enum
import uuid

class SearchMode(str, Enum):
    CHUNK = "chunk"
    PAGE = "page"

class SearchRequest(BaseModel):
    query: str
    mode: SearchMode = SearchMode.CHUNK
    limit: int = 10
    match_threshold: float = 0.5
    filter_source_id: Optional[str] = None
    use_hybrid: bool = False
    use_reranking: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ChunkSearchResult(BaseModel):
    id: int
    source_id: str
    page_id: Optional[uuid.UUID] = None
    content: str
    contextual_content: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    similarity: float
    url: Optional[str] = None

class PageSearchResult(BaseModel):
    page_id: uuid.UUID
    source_id: str
    url: str
    title: Optional[str] = None
    summary: Optional[str] = None
    full_content: Optional[str] = None
    max_similarity: float
    chunk_count: int
    chunks: List[ChunkSearchResult] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class SearchResponse(BaseModel):
    query: str
    mode: SearchMode
    results: Union[List[ChunkSearchResult], List[PageSearchResult]]
    total_results: int
    processing_time_ms: float = 0.0
    reranking_applied: bool = False
