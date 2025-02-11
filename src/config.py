from pydantic_settings import BaseSettings
import os

class Config(BaseSettings):
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str = os.getenv("QDRANT_API_KEY")
    groq_api_key: str = os.getenv("GROQ_API_KEY")
    llm_model: str = "llama3-70b-8192"
    embeddings_model: str = "llama3"
    qdrant_collection_name: str = "test"

config = Config()