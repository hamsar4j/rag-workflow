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
    groq_api_key: str = os.getenv("GROQ_API_KEY")
    llm_model: str = "groq:llama-3.3-70b-versatile"

    # ollama embeddings
    embeddings_model: str = "bge-m3"
    embeddings_dim: int = 1024


config = Settings()
