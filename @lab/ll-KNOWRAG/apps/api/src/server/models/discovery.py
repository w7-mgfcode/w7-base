from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl
from enum import Enum

class DiscoveryType(str, Enum):
    LLMS_TXT = "llms.txt"
    LLMS_FULL_TXT = "llms-full.txt"
    SITEMAP_XML = "sitemap.xml"
    ROBOTS_TXT = "robots.txt"
    SINGLE_PAGE = "single_page"
    RECURSIVE_CRAWL = "recursive_crawl"

class DiscoveryTarget(BaseModel):
    url: str
    target_type: DiscoveryType
    priority: int = 0
    metadata: dict = Field(default_factory=dict)

class DiscoveryResult(BaseModel):
    base_url: str
    canonical_url: str
    targets: List[DiscoveryTarget] = Field(default_factory=list)
    success: bool = True
    error: Optional[str] = None
