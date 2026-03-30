import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.api_routes import knowledge_api, rag_api, pages_api, upload_api
from server.config.config import settings

app = FastAPI(title="KnowRAG API")

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
