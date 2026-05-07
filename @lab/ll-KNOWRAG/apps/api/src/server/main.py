import uvicorn
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.api_routes import artifacts_api, ingest_api
from server.config.config import settings
from server.dependencies import provider_svc

logger = logging.getLogger("uvicorn.error")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.getLogger().setLevel(settings.log_level.upper())

    logger.info("Performing startup model validation...")
    emb_ok = await provider_svc.check_model(settings.embedding_model)
    if not emb_ok:
        logger.warning(f"EMBEDDING_MODEL '{settings.embedding_model}' not found at {provider_svc.base_url}!")
    else:
        logger.info(f"EMBEDDING_MODEL '{settings.embedding_model}' verified.")

    if settings.use_reranking:
        logger.info("USE_RERANKING enabled (using Lexical Boost fallback).")

    # Phase 8 bootstrap: ensure KB repo + directory shape + webhook on Gitea.
    # Best-effort — log and proceed if Gitea is misconfigured so the app can
    # still serve endpoints that don't depend on it.
    if settings.gitea_token and settings.gitea_base_url:
        try:
            from server.services.storage.gitea_bootstrap import GiteaBootstrap
            async with GiteaBootstrap(
                base_url=settings.gitea_base_url,
                token=settings.gitea_token,
                owner=settings.gitea_kb_owner,
                repo=settings.gitea_kb_repo,
                branch=settings.gitea_kb_branch,
            ) as bs:
                await bs.run()
                if settings.gitea_webhook_secret and settings.ingest_webhook_url:
                    created = await bs.ensure_webhook(
                        target_url=settings.ingest_webhook_url,
                        secret=settings.gitea_webhook_secret,
                    )
                    logger.info(
                        "Webhook %s on %s/%s",
                        "created" if created else "already present",
                        settings.gitea_kb_owner, settings.gitea_kb_repo,
                    )
        except Exception as exc:  # noqa: BLE001 — bootstrap is non-fatal
            logger.warning("Gitea bootstrap skipped/failed: %s", exc)

    yield

app = FastAPI(title="KnowRAG API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(artifacts_api.router)
app.include_router(ingest_api.router)

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
