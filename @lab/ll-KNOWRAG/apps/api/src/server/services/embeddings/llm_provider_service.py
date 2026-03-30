import httpx
import logging
from typing import List, Optional, Dict, Any

logger = logging.getLogger(__name__)

class LLMProviderService:
    """
    Direct interaction with LLM providers (Ollama, OpenAI-compatible).
    Ported from Archon: simplified for local-first KB.
    """
    
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = httpx.Timeout(60.0)

    async def get_embeddings(self, model: str, texts: List[str]) -> List[List[float]]:
        """
        Generic embedding fetcher.
        """
        if not texts:
            return []

        # Detect provider type based on URL or explicitly
        if "ollama" in self.base_url or ":11434" in self.base_url:
            return await self._get_ollama_embeddings(model, texts)
        else:
            return await self._get_openai_compatible_embeddings(model, texts)

    async def _get_ollama_embeddings(self, model: str, texts: List[str]) -> List[List[float]]:
        """
        Calls Ollama's /api/embed or /api/embeddings.
        """
        url = f"{self.base_url}/api/embed"
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            payload = {
                "model": model,
                "input": texts
            }
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            # Ollama /api/embed returns 'embeddings'
            return data.get("embeddings", [])

    async def _get_openai_compatible_embeddings(self, model: str, texts: List[str]) -> List[List[float]]:
        """
        Calls OpenAI-compatible /v1/embeddings.
        """
        url = f"{self.base_url}/v1/embeddings"
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            payload = {
                "model": model,
                "input": texts
            }
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            # OpenAI returns list of objects with 'embedding' key
            return [item["embedding"] for item in data.get("data", [])]
