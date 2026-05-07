import httpx
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class KnowRagApiClient:
    """Thin HTTP client for the Phase 8 knowrag-api (Gitea + Qdrant artifacts)."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.timeout = httpx.Timeout(30.0)

    async def get_health(self) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()

    async def list_artifacts(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            params = {"category": category} if category else None
            response = await client.get(f"{self.base_url}/api/artifacts", params=params)
            response.raise_for_status()
            return response.json()

    async def get_artifact(self, path: str, ref: Optional[str] = None) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            params = {"ref": ref} if ref else None
            response = await client.get(f"{self.base_url}/api/artifacts/{path}", params=params)
            response.raise_for_status()
            return response.json()

    async def related_artifacts(
        self, path: str, k: int = 5, visibility: str = "public"
    ) -> List[Dict[str, Any]]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/api/artifacts/{path}/related",
                params={"k": k, "visibility": visibility},
            )
            response.raise_for_status()
            return response.json()

    async def search_artifacts(
        self,
        query: str,
        tags: Optional[List[str]] = None,
        status: Optional[List[str]] = None,
        owner: Optional[str] = None,
        visibility: str = "public",
        top_k: int = 20,
        use_hybrid: bool = False,
        use_rerank: bool = False,
    ) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            payload: Dict[str, Any] = {
                "query": query,
                "visibility": visibility,
                "top_k": top_k,
                "use_hybrid": use_hybrid,
                "use_rerank": use_rerank,
            }
            if tags:
                payload["tags"] = tags
            if status:
                payload["status"] = status
            if owner:
                payload["owner"] = owner
            response = await client.post(
                f"{self.base_url}/api/artifacts/search", json=payload
            )
            response.raise_for_status()
            return response.json()
