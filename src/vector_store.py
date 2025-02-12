from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from langchain_ollama import OllamaEmbeddings

class VectorStore:
    def __init__(self, config):
        # using ollama embeddings
        self.embeddings = OllamaEmbeddings(model=config.embeddings_model)
        # qdrant client
        self.client = QdrantClient(config.qdrant_url)
        # qdrant collection name
        self.collection_name = config.qdrant_collection_name

        self.vector_store = QdrantVectorStore(
            client=self.client,
            collection_name=self.collection_name,
            embedding=self.embeddings,
        )
    
    def get_vector_store(self):
        return self.vector_store
    
    def add_documents(self, documents):
        vector_store = self.get_vector_store()
        document_ids = vector_store.add_documents(documents)
        return document_ids