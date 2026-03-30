from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
from .discovery import DiscoveryType

class CrawlMode(str, Enum):
    SINGLE_PAGE = "single_page"
    SITEMAP = "sitemap"
    RECURSIVE = "recursive"
    DISCOVERY_AUTO = "discovery_auto"

class CrawlStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class CrawlTask(BaseModel):
    url: str
    status: CrawlStatus = CrawlStatus.PENDING
    target_type: DiscoveryType
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class CrawlRequest(BaseModel):
    base_url: str
    source_id: Optional[str] = None
    mode: CrawlMode = CrawlMode.DISCOVERY_AUTO
    max_depth: int = 1
    max_pages: int = 100
    metadata: Dict[str, Any] = Field(default_factory=dict)

class CrawlProgress(BaseModel):
    id: str
    status: CrawlStatus = CrawlStatus.PENDING
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    current_task_url: Optional[str] = None
    results: List[Dict[str, Any]] = Field(default_factory=list)
    error: Optional[str] = None
