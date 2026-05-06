from pydantic_settings import BaseSettings
from typing import Optional
from pydantic import Field

class Settings(BaseSettings):
    supabase_url: str = Field(default="http://localhost:8000")
    supabase_service_key: str = Field(default="your_service_role_key")
    embedding_provider_url: str = Field(default="http://localhost:11434", validation_alias="OLLAMA_BASE_URL")
    embedding_model: str = "nomic-embed-text"
    embedding_dimension: int = 768
    chat_model: str = "llama3"
    api_host: str = "0.0.0.0"
    api_port: int = 8181
    log_level: str = "info"

    # Feature flags (Blueprint Section 18)
    use_hybrid_search: bool = False
    use_reranking: bool = False
    use_contextual_embeddings: bool = False
    enable_code_examples: bool = False

    # Reranking settings
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

    # Crawl4AI browser-based crawling
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
