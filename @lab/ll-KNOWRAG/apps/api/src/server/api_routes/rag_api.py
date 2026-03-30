from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated, List
from server.models.search import SearchRequest, SearchResponse
from server.models.knowledge import Source
from server.services.search.rag_service import RagService
from server.services.storage.storage_operations import StorageOperations
from server.dependencies import get_rag_svc, get_storage_ops

router = APIRouter(prefix="/api/rag", tags=["RAG"])

@router.get("/sources", response_model=List[Source])
async def list_rag_sources(storage_ops: Annotated[StorageOperations, Depends(get_storage_ops)]):
    try:
        result = storage_ops.supabase.table("kb_sources").select("*").execute()
        return [Source(**item) for item in result.data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query", response_model=SearchResponse)
async def query_kb(request: SearchRequest, rag_service: Annotated[RagService, Depends(get_rag_svc)]):
    try:
        return await rag_service.query(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
