from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Embedding provider — Ollama by default
    embedding_provider_url: str = Field(default="http://localhost:11434", validation_alias="OLLAMA_BASE_URL")
    embedding_model: str = "nomic-embed-text"
    embedding_dimension: int = 768

    # Chat-completions provider (used by /api/rag/query for generation).
    # CHAT_BASE_URL=""  → auto-default to OLLAMA_BASE_URL.
    # CHAT_PROVIDER is informational ("ollama" | "openai-compat") — provider
    # selection inside LLMProviderService is URL-based, not env-based.
    chat_provider: str = Field(default="ollama", validation_alias="CHAT_PROVIDER")
    chat_model: str = Field(default="llama3.2:1b", validation_alias="CHAT_MODEL")
    chat_base_url: str = Field(default="", validation_alias="CHAT_BASE_URL")
    chat_api_key: str = Field(default="", validation_alias="CHAT_API_KEY")

    # Qdrant
    qdrant_host: str = Field(default="qdrant", validation_alias="QDRANT_HOST")
    qdrant_port: int = Field(default=6333, validation_alias="QDRANT_PORT")
    qdrant_grpc_port: int = Field(default=6334, validation_alias="QDRANT_GRPC_PORT")

    # Gitea (artifact source-of-truth)
    gitea_base_url: str = Field(default="http://gitea:3000", validation_alias="GITEA_BASE_URL")
    gitea_token: str = Field(default="", validation_alias="GITEA_TOKEN")
    gitea_kb_owner: str = Field(default="knowrag", validation_alias="GITEA_KB_OWNER")
    gitea_kb_repo: str = Field(default="kb-default", validation_alias="GITEA_KB_REPO")
    gitea_kb_branch: str = Field(default="main", validation_alias="GITEA_KB_BRANCH")
    gitea_webhook_secret: str = Field(default="", validation_alias="GITEA_WEBHOOK_SECRET")
    ingest_webhook_url: str = Field(
        default="http://knowrag-api:8181/api/ingest/webhook",
        validation_alias="INGEST_WEBHOOK_URL",
    )

    api_host: str = "0.0.0.0"
    api_port: int = 8181
    log_level: str = "info"

    # Feature flags
    use_hybrid_search: bool = False
    use_reranking: bool = False

    # Reranking
    reranking_provider: str = "lexical"
    reranking_model: str = ""
    reranking_provider_url: str = ""
    reranking_api_key: str = ""
    reranking_top_n: int = 0

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
