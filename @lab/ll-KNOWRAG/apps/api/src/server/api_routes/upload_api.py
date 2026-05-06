import re
import uuid
from pathlib import Path

from bs4 import BeautifulSoup
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from typing import Annotated, Optional

from server.config.config import settings
from server.dependencies import get_ingestion_svc, get_storage_ops
from server.models.knowledge import DocumentUploadResponse
from server.services.knowledge.ingestion_service import IngestionService
from server.services.storage.storage_operations import StorageOperations

router = APIRouter(prefix="/api/documents", tags=["Documents"])


def _derive_upload_source_id(filename: str) -> str:
    stem = Path(filename or "").stem.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", stem).strip("-")
    return slug or str(uuid.uuid4())[:8]


def _extract_upload_text(raw_bytes: bytes, filename: str, content_type: str) -> tuple[str, str]:
    decoded = raw_bytes.decode("utf-8", errors="ignore")
    lower_name = (filename or "").lower()
    is_html = (content_type or "").lower().startswith("text/html") or lower_name.endswith((".html", ".htm"))

    if is_html:
        soup = BeautifulSoup(decoded, "html.parser")
        title = soup.title.string.strip() if soup.title and soup.title.string else Path(filename).stem
        return soup.get_text(separator="\n", strip=True), title

    return decoded, Path(filename).stem or "Uploaded Document"


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    source_id: Optional[str] = Form(default=None),
    title: Optional[str] = Form(default=None),
    display_name: Optional[str] = Form(default=None),
    tags: Optional[str] = Form(default=None),
    ingestion_service: Annotated[IngestionService, Depends(get_ingestion_svc)] = None,
    storage_ops: Annotated[StorageOperations, Depends(get_storage_ops)] = None,
):
    raw_bytes = await file.read()
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(raw_bytes) > max_bytes:
        raise HTTPException(status_code=413, detail=f"File exceeds {settings.max_upload_size_mb}MB limit")
    if not raw_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    extracted_text, detected_title = _extract_upload_text(raw_bytes, file.filename or "", file.content_type or "")
    if not extracted_text.strip():
        raise HTTPException(status_code=400, detail="Uploaded file does not contain extractable text")

    resolved_source_id = source_id or _derive_upload_source_id(file.filename or "")
    parsed_tags = [tag.strip() for tag in (tags or "").split(",") if tag.strip()]
    source_title = title or display_name or detected_title

    await ingestion_service.ingest_crawl_results(
        source_id=resolved_source_id,
        crawl_results=[{
            "url": f"file-upload://{resolved_source_id}/{file.filename or 'document'}",
            "content": extracted_text,
            "title": source_title,
            "success": True,
            "metadata": {
                "filename": file.filename,
                "content_type": file.content_type,
                "upload": True,
            },
        }],
        metadata={
            "upload": True,
            "filename": file.filename,
            "content_type": file.content_type,
            "tags": parsed_tags,
        },
    )

    if title is not None or display_name is not None or parsed_tags:
        await storage_ops.update_source(
            source_id=resolved_source_id,
            title=title or source_title,
            display_name=display_name or source_title,
            tags=parsed_tags or None,
        )

    return DocumentUploadResponse(
        source_id=resolved_source_id,
        filename=file.filename or "document",
        status="ingested",
        pages_ingested=1,
    )
