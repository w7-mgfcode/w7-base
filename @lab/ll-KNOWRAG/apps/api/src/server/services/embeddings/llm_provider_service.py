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

    async def generate_text(self, model: str, prompt: str, system: Optional[str] = None) -> str:
        """
        Generic text generator for contextual tasks.
        """
        if "ollama" in self.base_url or ":11434" in self.base_url:
            return await self._generate_ollama_text(model, prompt, system)
        else:
            return await self._generate_openai_compatible_text(model, prompt, system)

    async def _generate_ollama_text(self, model: str, prompt: str, system: Optional[str] = None) -> str:
        url = f"{self.base_url}/api/generate"
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {"model": model, "prompt": prompt, "stream": False}
        if system:
            payload["system"] = system

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json().get("response", "")

    async def _generate_openai_compatible_text(self, model: str, prompt: str, system: Optional[str] = None) -> str:
        url = f"{self.base_url}/v1/chat/completions"
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {"model": model, "messages": messages, "stream": False}

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data.get("choices", [{}])[0].get("message", {}).get("content", "")

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
