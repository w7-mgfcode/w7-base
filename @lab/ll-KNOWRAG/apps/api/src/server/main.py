import uvicorn
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.api_routes import knowledge_api, rag_api, pages_api, upload_api, artifacts_api
from server.config.config import settings
from server.dependencies import provider_svc, crawler_mgr

logger = logging.getLogger("uvicorn.error")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Set log level
    logging.getLogger().setLevel(settings.log_level.upper())
    
    # Startup validation
    logger.info("Performing startup model validation...")
    
    # Check embedding model
    emb_ok = await provider_svc.check_model(settings.embedding_model)
    if not emb_ok:
        logger.warning(f"EMBEDDING_MODEL '{settings.embedding_model}' not found at {provider_svc.base_url}!")
    else:
        logger.info(f"EMBEDDING_MODEL '{settings.embedding_model}' verified.")
        
    # Check chat model if contextual embeddings are enabled
    if settings.use_contextual_embeddings:
        chat_ok = await provider_svc.check_model(settings.chat_model)
        if not chat_ok:
            logger.warning(f"CHAT_MODEL '{settings.chat_model}' not found at {provider_svc.base_url}, but USE_CONTEXTUAL_EMBEDDINGS is enabled!")
        else:
            logger.info(f"CHAT_MODEL '{settings.chat_model}' verified.")
            
    # Check reranking fallback
    if settings.use_reranking:
        logger.info("USE_RERANKING enabled (using Lexical Boost fallback).")
        
    # Start Crawl4AI browser
    await crawler_mgr.startup()

    yield

    # Shutdown browser
    await crawler_mgr.shutdown()

app = FastAPI(title="KnowRAG API", lifespan=lifespan)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(knowledge_api.router)
app.include_router(upload_api.router)
app.include_router(rag_api.router)
app.include_router(pages_api.router)
app.include_router(artifacts_api.router)

@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "KnowRAG API",
        "docs": "/docs",
        "status": "ready"
    }

@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "service": "knowrag-api"}

@app.get("/api/health", tags=["Health"])
async def api_health():
    return {"status": "ok", "service": "knowrag-api"}

if __name__ == "__main__":
    uvicorn.run("server.main:app", host=settings.api_host, port=settings.api_port, reload=True)
