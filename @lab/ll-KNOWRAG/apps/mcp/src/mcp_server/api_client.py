import httpx
import os
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class KnowRagApiClient:
    """
    Thin client for communicating with knowrag-api.
    Ported from Archon: adapted for simple HTTP forwarding.
    """
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.timeout = httpx.Timeout(30.0)

    async def get_health(self) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()

    async def list_sources(self) -> List[Dict[str, Any]]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/api/knowledge-items")
            response.raise_for_status()
            return response.json()

    async def search_kb(self, query: str, mode: str = "chunk", limit: int = 10, use_hybrid: bool = False, use_reranking: bool = False) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            payload = {
                "query": query,
                "mode": mode,
                "limit": limit,
                "use_hybrid": use_hybrid,
                "use_reranking": use_reranking
            }
            response = await client.post(f"{self.base_url}/api/rag/query", json=payload)
            response.raise_for_status()
            return response.json()

    async def list_pages(self, source_id: Optional[str] = None) -> List[Dict[str, Any]]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            params = {}
            if source_id:
                params["source_id"] = source_id
            response = await client.get(f"{self.base_url}/api/pages", params=params)
            response.raise_for_status()
            return response.json()

    async def get_page(self, page_id: str) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/api/pages/{page_id}")
            response.raise_for_status()
            return response.json()

    async def start_crawl(self, base_url: str, source_id: Optional[str] = None) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            payload = {
                "base_url": base_url,
                "source_id": source_id
            }
            response = await client.post(f"{self.base_url}/api/knowledge-items/crawl", json=payload)
            response.raise_for_status()
            return response.json()
