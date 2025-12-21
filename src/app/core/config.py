import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    """Configuration settings for the RAG application."""

    # fastAPI backend
    backend_url: str = os.getenv("BACKEND_URL", "http://localhost:8000")

    # PostgreSQL vector db (pgvector)
    postgres_url: str = os.getenv(
        "POSTGRES_URL", "postgresql://rag_user:rag_password@localhost:5433/rag_db"
    )
    postgres_table_name: str = os.getenv("POSTGRES_TABLE_NAME", "documents")
    postgres_search_top_k: int = int(os.getenv("POSTGRES_SEARCH_TOP_K", "10"))

    # llm api
    llm_base_url: str = os.getenv("LLM_BASE_URL", "https://api.together.xyz/v1")
    llm_api_key: str = os.getenv("LLM_API_KEY", "")
    llm_model: str = os.getenv("LLM_MODEL", "moonshotai/Kimi-K2-Instruct-0905")

    # embeddings api
    embeddings_base_url: str = os.getenv(
        "EMBEDDINGS_BASE_URL", "https://api.together.xyz/v1"
    )
    embeddings_api_key: str = os.getenv("EMBEDDINGS_API_KEY", "")
    embeddings_model: str = os.getenv(
        "EMBEDDINGS_MODEL", "intfloat/multilingual-e5-large-instruct"
    )
    embeddings_dim: int = int(os.getenv("EMBEDDINGS_DIM", "1024"))

    # ingestion settings
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "500"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "100"))

    # reranker
    reranker_base_url: str = os.getenv(
        "RERANKING_BASE_URL", "https://api.jina.ai/v1/rerank"
    )
    reranker_api_key: str = os.getenv("RERANKING_API_KEY", "")
    reranker_model: str = os.getenv("RERANKING_MODEL", "jina-reranker-v1-tiny-en")
    enable_reranker: bool = os.getenv("ENABLE_RERANKER", "false").lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


settings = Settings()
