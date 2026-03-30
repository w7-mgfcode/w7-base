from abc import ABC, abstractmethod
from typing import List, Optional
from ...models.search import SearchRequest, ChunkSearchResult

class BaseSearchStrategy(ABC):
    @abstractmethod
    async def search(self, request: SearchRequest, embedding: List[float]) -> List[ChunkSearchResult]:
        pass
