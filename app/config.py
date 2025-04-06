from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseSettings):
    # qdrant vector db
    qdrant_url: str = os.getenv("QDRANT_URL")
    qdrant_api_key: str = os.getenv("QDRANT_API_KEY")
    qdrant_collection_name: str = "sutd"

    # llm api
    llm_base_url: str = "https://api.groq.com/openai/v1"
    llm_api_key: str = os.getenv("GROQ_API_KEY")
    llm_model: str = "meta-llama/llama-4-scout-17b-16e-instruct"

    # ollama embeddings
    embeddings_model: str = "nomic-embed-text"
    embeddings_dim: int = 768


config = Settings()
