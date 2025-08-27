from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseSettings):
    """Configuration settings for the RAG application."""

    # fastAPI backend
    backend_url: str = os.getenv("BACKEND_URL", "http://localhost:8000")

    # qdrant vector db
    qdrant_url: str = os.getenv("QDRANT_URL", "")
    qdrant_api_key: str = os.getenv("QDRANT_API_KEY", "")
    qdrant_collection_name: str = os.getenv("QDRANT_COLLECTION_NAME", "sutd")
    qdrant_search_top_k: int = int(os.getenv("QDRANT_SEARCH_TOP_K", "10"))

    # llm api
    llm_base_url: str = "https://api.together.xyz/v1"
    llm_api_key: str = os.getenv("TOGETHER_API_KEY", "")
    llm_model: str = "zai-org/GLM-4.5-Air-FP8"

    # embeddings api
    embeddings_base_url: str = "https://api.together.xyz/v1"
    embeddings_api_key: str = os.getenv("TOGETHER_API_KEY", "")
    embeddings_model: str = "Alibaba-NLP/gte-modernbert-base"
    embeddings_dim: int = 768

    # reranker
    reranker_base_url: str = "https://api.jina.ai/v1/rerank"
    reranker_api_key: str = os.getenv("JINA_API_KEY", "")
    reranker_model: str = "jina-reranker-v1-tiny-en"
    enable_reranker: bool = False


settings = Settings()
