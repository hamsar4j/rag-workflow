from app.models.models import Document, Search
from qdrant_client import QdrantClient, models
from fastembed import SparseTextEmbedding
import numpy as np
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)


class VectorDB:
    def __init__(self, config):
        self.embeddings_model = config.embeddings_model
        self.client = QdrantClient(url=config.qdrant_url, api_key=config.qdrant_api_key)
        self.collection_name = config.qdrant_collection_name
        self.embeddings_client = OpenAI(
            api_key=config.embeddings_api_key, base_url=config.embeddings_base_url
        )
        self.embeddings_model = config.embeddings_model
        self.sparse_model = SparseTextEmbedding("Qdrant/bm25")

    def get_embeddings(self, doc: str) -> np.ndarray:
        response = self.embeddings_client.embeddings.create(
            input=doc, model=self.embeddings_model
        )
        return np.array(response.data[0].embedding)

    def add_documents(
        self,
        docs: list[Document],
        dense_embeddings: np.ndarray,
        sparse_embeddings=None,
        batch_size: int = 1000,
    ) -> None:

        for i in range(0, len(docs), batch_size):
            batch_docs = docs[i : i + batch_size]
            batch_embeddings = dense_embeddings[i : i + batch_size]
            batch_sparse = (
                sparse_embeddings[i : i + batch_size]
                if sparse_embeddings is not None
                else None
            )

            points = []
            for j, (doc, embedding) in enumerate(zip(batch_docs, batch_embeddings)):
                point_data = {
                    "id": i + j,  # offset from overall start index
                    "payload": {"text": doc.text, "metadata": doc.metadata},
                }

                # If sparse embeddings are provided, use hybrid vector format
                if (
                    batch_sparse is not None
                    and j < len(batch_sparse)
                    and batch_sparse[j] is not None
                ):
                    # Make sure we're handling the sparse embedding correctly
                    sparse_embedding = batch_sparse[j]
                    # If it's a generator or iterator, convert to object
                    if hasattr(sparse_embedding, "as_object"):
                        sparse_obj = sparse_embedding.as_object()
                    else:
                        # If it's already in the right format, use it directly
                        sparse_obj = sparse_embedding

                    point_data["vector"] = {
                        "dense": (
                            embedding.tolist()
                            if hasattr(embedding, "tolist")
                            else embedding
                        ),  # Dense vector
                        "bm25": sparse_obj,  # Sparse vector
                    }
                else:
                    # Only dense vector
                    point_data["vector"] = (
                        embedding.tolist()
                        if hasattr(embedding, "tolist")
                        else embedding
                    )

                points.append(models.PointStruct(**point_data))

            print(
                f"Upserting {len(points)} points from {i} to {i + len(batch_docs)}..."
            )
            if len(points) > 0:  # Only upsert if we have points
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=points,
                )
            else:
                print("Warning: No points to upsert in this batch")

    # Hybrid search method using Reciprocal Rank Fusion (RRF)
    def hybrid_search(self, query: str, top_k: int = 5) -> list[Search]:

        # Get dense embedding
        dense_embedding = self.get_embeddings(query)

        # Get sparse embedding
        sparse_embedding_result = list(self.sparse_model.embed([query]))
        sparse_embedding = sparse_embedding_result[0]

        # Perform hybrid search using both dense and sparse vectors
        try:
            query_response = self.client.query_points(
                collection_name=self.collection_name,
                prefetch=[
                    models.Prefetch(query=dense_embedding, using="dense"),
                    models.Prefetch(
                        query=models.SparseVector(**sparse_embedding.as_object()),
                        using="bm25",
                    ),
                ],
                query=models.FusionQuery(fusion=models.Fusion.RRF),
                limit=top_k,
            )
        except Exception as e:
            logger.warning(
                f"Hybrid search failed, falling back to dense-only search: {e}"
            )
            query_response = self.client.query_points(
                collection_name=self.collection_name,
                query=dense_embedding,
                using="dense",
                limit=top_k,
            )

        results = query_response.points

        logger.info(f"Retrieved {len(results)} results.")

        return [
            Search(
                text=(
                    hit.payload["text"] if hit.payload and "text" in hit.payload else ""
                ),
                metadata={
                    k: v
                    for k, v in (hit.payload.items() if hit.payload else {}.items())
                    if k != "text"
                },
                score=hit.score,
            )
            for hit in results
        ]
