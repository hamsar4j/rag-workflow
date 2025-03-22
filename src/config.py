from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseSettings):
    # qdrant vector db
    qdrant_url: str = os.getenv("QDRANT_URL")
    qdrant_api_key: str = os.getenv("QDRANT_API_KEY")
    qdrant_collection_name: str = "test"

    # llm api
    groq_api_key: str = os.getenv("GROQ_API_KEY")
    llm_model: str = "groq:llama-3.3-70b-versatile"
    # together_api_key: str = os.getenv("TOGETHER_API_KEY")
    # llm_model: str = "together:meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"

    # ollama embeddings
    embeddings_model: str = "nomic-embed-text"
    embeddings_dim: int = 768


config = Settings()
