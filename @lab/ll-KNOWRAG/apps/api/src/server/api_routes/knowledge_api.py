from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Annotated
from server.models.knowledge import Source, SourceUpdateRequest, SourceRefreshResponse, SourceChunkListResponse
from server.models.crawling import CrawlRequest, CrawlProgress
from server.services.crawling.crawling_service import CrawlingService
from server.services.storage.storage_operations import StorageOperations
from server.dependencies import get_storage_ops, get_crawling_svc

router = APIRouter(prefix="/api/knowledge-items", tags=["Knowledge"])

@router.get("", response_model=List[Source])
async def list_sources(storage_ops: Annotated[StorageOperations, Depends(get_storage_ops)]):
    try:
        result = storage_ops.supabase.rpc("get_sources_with_counts").execute()
        sources = []
        for item in result.data:
            page_count = item.pop("page_count", 0)
            chunk_count = item.pop("chunk_count", 0)
            metadata = item.get("metadata") or {}
            metadata["page_count"] = page_count
            metadata["chunk_count"] = chunk_count
            item["metadata"] = metadata
            sources.append(Source(**item))
        return sources
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary")
async def get_summary(storage_ops: Annotated[StorageOperations, Depends(get_storage_ops)]):
    try:
        sources = storage_ops.supabase.table("kb_sources").select("source_id", count="exact").execute()
        pages = storage_ops.supabase.table("kb_pages").select("id", count="exact").execute()
        chunks = storage_ops.supabase.table("kb_chunks").select("id", count="exact").execute()
        return {
            "total_sources": sources.count or 0,
            "total_pages": pages.count or 0,
            "total_chunks": chunks.count or 0,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/crawl")
async def start_crawl(request: CrawlRequest, crawling_service: Annotated[CrawlingService, Depends(get_crawling_svc)]):
    try:
        crawl_id = await crawling_service.start_crawl(request)
        return {"crawl_id": crawl_id, "status": "started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/crawl-progress/{progress_id}", response_model=CrawlProgress)
async def get_crawl_progress(progress_id: str, crawling_service: Annotated[CrawlingService, Depends(get_crawling_svc)]):
    progress = crawling_service.get_progress(progress_id)
    if not progress:
        raise HTTPException(status_code=404, detail="Crawl operation not found")
    return progress

@router.post("/stop/{progress_id}")
async def stop_crawl(progress_id: str, crawling_service: Annotated[CrawlingService, Depends(get_crawling_svc)]):
    stopped = crawling_service.stop_crawl(progress_id)
    if not stopped:
        raise HTTPException(status_code=404, detail="Crawl operation not found or already finished")
    return {"status": "cancelled", "progress_id": progress_id}

@router.delete("/{source_id}")
async def delete_source(source_id: str, storage_ops: Annotated[StorageOperations, Depends(get_storage_ops)]):
    try:
        await storage_ops.delete_source(source_id)
        return {"status": "deleted", "source_id": source_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{source_id}", response_model=Source)
async def update_source_metadata(
    source_id: str,
    request: SourceUpdateRequest,
    storage_ops: Annotated[StorageOperations, Depends(get_storage_ops)],
):
    try:
        source = await storage_ops.update_source(
            source_id=source_id,
            title=request.title,
            display_name=request.display_name,
            tags=request.tags,
        )
        if not source:
            raise HTTPException(status_code=404, detail="Source not found")
        return source
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{source_id}/refresh", response_model=SourceRefreshResponse)
async def refresh_source(
    source_id: str,
    crawling_service: Annotated[CrawlingService, Depends(get_crawling_svc)],
    storage_ops: Annotated[StorageOperations, Depends(get_storage_ops)],
):
    try:
        source = await storage_ops.get_source(source_id)
        if not source:
            raise HTTPException(status_code=404, detail="Source not found")

        base_url = source.metadata.get("base_url") or source.source_url
        if not base_url:
            raise HTTPException(status_code=400, detail="Source does not have a refreshable URL")

        crawl_id = await crawling_service.start_crawl(
            CrawlRequest(
                base_url=base_url,
                source_id=source_id,
                metadata=source.metadata or {},
            )
        )
        return SourceRefreshResponse(source_id=source_id, crawl_id=crawl_id, status="started")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{source_id}/chunks", response_model=SourceChunkListResponse)
async def list_source_chunks(
    source_id: str,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    storage_ops: Annotated[StorageOperations, Depends(get_storage_ops)] = None,
):
    try:
        source = await storage_ops.get_source(source_id)
        if not source:
            raise HTTPException(status_code=404, detail="Source not found")

        total, items = await storage_ops.list_source_chunks(source_id, offset=offset, limit=limit)
        return SourceChunkListResponse(
            source_id=source_id,
            total=total,
            offset=offset,
            limit=limit,
            items=items,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
