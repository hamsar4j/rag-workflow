from models import Document, Search
from typing import List
from qdrant_client import QdrantClient, models
import ollama


class VectorStore:
    def __init__(self, config):
        self.embeddings_model = config.embeddings_model
        self.client = QdrantClient(url=config.qdrant_url, api_key=config.qdrant_api_key)
        self.collection_name = config.qdrant_collection_name

    def get_embeddings(self, doc):
        response = ollama.embed(model=self.embeddings_model, input=doc)
        return response["embeddings"][0]

    def add_documents(self, docs: List[Document]):

        embeddings = [self.get_embeddings(doc.text) for doc in docs]

        points = [
            models.PointStruct(
                id=i,
                vector=embedding,
                payload={"text": doc.text, "metadata": doc.metadata},
            )
            for i, (doc, embedding) in enumerate(zip(docs, embeddings))
        ]

        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
        )

    def semantic_search(self, query: str, top_k: int = 5) -> List[Search]:
        query_vector = self.get_embeddings(query)

        results = self.client.search(
            collection_name=self.collection_name, query_vector=query_vector, limit=top_k
        )

        print(f"Retrieved {len(results)} results.")

        return [
            Search(
                text=hit.payload["text"],
                metadata={k: v for k, v in hit.payload.items() if k != "text"},
                score=hit.score,
            )
            for hit in results
        ]
