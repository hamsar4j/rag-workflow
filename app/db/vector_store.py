from app.models import Document, Search
from qdrant_client import QdrantClient, models
import numpy as np
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)


class VectorStore:
    def __init__(self, config):
        self.embeddings_model = config.embeddings_model
        self.client = QdrantClient(url=config.qdrant_url, api_key=config.qdrant_api_key)
        self.collection_name = config.qdrant_collection_name
        self.openai_client = OpenAI(
            api_key=config.openai_api_key, base_url=config.openai_base_url
        )
        self.embeddings_model = config.embeddings_model

    def get_embeddings(self, doc: str) -> np.ndarray:
        response = self.openai_client.embeddings.create(
            input=doc, model=self.embeddings_model
        )
        return np.array(response.data[0].embedding)

    def add_documents(
        self, docs: list[Document], embeddings: list[np.ndarray], batch_size: int = 1000
    ) -> None:

        for i in range(0, len(docs), batch_size):
            batch_docs = docs[i : i + batch_size]
            batch_embeddings = embeddings[i : i + batch_size]

            points = [
                models.PointStruct(
                    id=i + j,  # offset from overall start index
                    vector=embedding,
                    payload={"text": doc.text, "metadata": doc.metadata},
                )
                for j, (doc, embedding) in enumerate(zip(batch_docs, batch_embeddings))
            ]

            print(f"Upserting points {i} to {i + len(batch_docs)}...")
            self.client.upsert(
                collection_name=self.collection_name,
                points=points,
            )

    def semantic_search(self, query: str, top_k: int = 5) -> list[Search]:
        query_vector = self.get_embeddings(query)

        results = self.client.search(
            collection_name=self.collection_name, query_vector=query_vector, limit=top_k
        )

        logging.info(f"Retrieved {len(results)} results.")

        return [
            Search(
                text=hit.payload["text"],
                metadata={k: v for k, v in hit.payload.items() if k != "text"},
                score=hit.score,
            )
            for hit in results
        ]
