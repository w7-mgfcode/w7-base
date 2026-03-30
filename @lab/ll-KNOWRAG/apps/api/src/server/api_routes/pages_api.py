from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Annotated
from server.models.knowledge import Page
from server.services.storage.storage_operations import StorageOperations
from server.dependencies import get_storage_ops
import uuid

router = APIRouter(prefix="/api/pages", tags=["Pages"])

@router.get("/by-url", response_model=Page)
async def get_page_by_url(url: str = Query(...), storage_ops: Annotated[StorageOperations, Depends(get_storage_ops)] = None):
    try:
        result = storage_ops.supabase.table("kb_pages").select("*").eq("url", url).limit(1).execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Page not found for URL")
        return Page(**result.data[0])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("", response_model=List[Page])
async def list_pages(source_id: Optional[str] = None, storage_ops: Annotated[StorageOperations, Depends(get_storage_ops)] = None):
    try:
        query = storage_ops.supabase.table("kb_pages").select("*")
        if source_id:
            query = query.eq("source_id", source_id)
        result = query.execute()
        return [Page(**item) for item in result.data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{page_id}", response_model=Page)
async def get_page(page_id: uuid.UUID, storage_ops: Annotated[StorageOperations, Depends(get_storage_ops)] = None):
    try:
        result = storage_ops.supabase.table("kb_pages").select("*").eq("id", str(page_id)).execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Page not found")
        return Page(**result.data[0])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
