from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Phase 7 Supabase (kept for crawl/ingest paths still on the legacy backend
    # until they migrate; do not extend with new fields).
    supabase_url: str = Field(default="http://localhost:8000")
    supabase_service_key: str = Field(default="your_service_role_key")

    # Embedding provider — Ollama by default
    embedding_provider_url: str = Field(default="http://localhost:11434", validation_alias="OLLAMA_BASE_URL")
    embedding_model: str = "nomic-embed-text"
    embedding_dimension: int = 768
    chat_model: str = "llama3"

    # Phase 8 — Qdrant
    qdrant_host: str = Field(default="qdrant", validation_alias="QDRANT_HOST")
    qdrant_port: int = Field(default=6333, validation_alias="QDRANT_PORT")
    qdrant_grpc_port: int = Field(default=6334, validation_alias="QDRANT_GRPC_PORT")

    # Phase 8 — Gitea (artifact source-of-truth)
    gitea_base_url: str = Field(default="http://gitea:3000", validation_alias="GITEA_BASE_URL")
    gitea_token: str = Field(default="", validation_alias="GITEA_TOKEN")
    gitea_kb_owner: str = Field(default="knowrag", validation_alias="GITEA_KB_OWNER")
    gitea_kb_repo: str = Field(default="kb-default", validation_alias="GITEA_KB_REPO")
    gitea_kb_branch: str = Field(default="main", validation_alias="GITEA_KB_BRANCH")
    gitea_webhook_secret: str = Field(default="", validation_alias="GITEA_WEBHOOK_SECRET")

    api_host: str = "0.0.0.0"
    api_port: int = 8181
    log_level: str = "info"

    # Feature flags
    use_hybrid_search: bool = False
    use_reranking: bool = False
    use_contextual_embeddings: bool = False
    enable_code_examples: bool = False

    # Reranking
    reranking_provider: str = "lexical"
    reranking_model: str = ""
    reranking_provider_url: str = ""
    reranking_api_key: str = ""
    reranking_top_n: int = 0

    # Upload limits
    max_upload_size_mb: int = 50

    # Crawl tuning
    crawl_page_timeout: int = 30
    crawl_wait_strategy: str = "networkidle"

    # Crawl4AI
    use_crawl4ai: bool = True
    crawl4ai_headless: bool = True
    crawl4ai_viewport_width: int = 1920
    crawl4ai_viewport_height: int = 1080
    crawl4ai_delay_before_return: float = 1.0
    crawl4ai_scan_full_page: bool = True

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
