from pydantic_settings import BaseSettings
from typing import Optional
from pydantic import Field

class Settings(BaseSettings):
    supabase_url: str = Field(default="http://localhost:8000")
    supabase_service_key: str = Field(default="your_service_role_key")
    embedding_provider_url: str = Field(default="http://localhost:11434", validation_alias="OLLAMA_BASE_URL")
    embedding_model: str = "nomic-embed-text"
    embedding_dimension: int = 768
    api_host: str = "0.0.0.0"
    api_port: int = 8181

    # Feature flags (Blueprint Section 18)
    use_hybrid_search: bool = False
    use_reranking: bool = False
    use_contextual_embeddings: bool = False
    enable_code_examples: bool = False

    # Upload limits
    max_upload_size_mb: int = 50

    # Crawl tuning
    crawl_page_timeout: int = 30
    crawl_wait_strategy: str = "networkidle"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
