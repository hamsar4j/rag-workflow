from app.models.models import Document, SearchResult
from qdrant_client import QdrantClient, models
from fastembed import SparseTextEmbedding
import numpy as np
import logging
from openai import OpenAI
from typing import Optional, Any
import json
import uuid

logger = logging.getLogger(__name__)


class VectorDB:
    """Vector database client for Qdrant with hybrid search capabilities."""

    def __init__(self, config: Any):
        self.embeddings_model = config.embeddings_model
        self.client = QdrantClient(url=config.qdrant_url, api_key=config.qdrant_api_key)
        self.collection_name = config.qdrant_collection_name
        self.embeddings_client = OpenAI(
            api_key=config.embeddings_api_key, base_url=config.embeddings_base_url
        )
        self.embeddings_model = config.embeddings_model
        self.embeddings_dim = config.embeddings_dim
        self.sparse_model = SparseTextEmbedding("Qdrant/bm25")

        self._ensure_collection_exists()

    def collection_exists(self) -> bool:
        """Check if collection exists."""
        try:
            self.client.get_collection(self.collection_name)
            return True
        except Exception:
            return False

    def _ensure_collection_exists(self):
        """Ensure the collection exists, creating it if necessary."""
        if self.collection_exists():
            logger.info(f"Collection '{self.collection_name}' already exists")
            return

        try:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config={
                    "dense": models.VectorParams(
                        size=self.embeddings_dim, distance=models.Distance.COSINE
                    )
                },
                sparse_vectors_config={
                    "bm25": models.SparseVectorParams(modifier=models.Modifier.IDF)
                },
            )
            logger.info(f"Successfully created collection '{self.collection_name}'")
        except Exception as e:
            logger.error(f"Failed to create collection '{self.collection_name}': {e}")
            raise RuntimeError(f"Could not ensure collection exists: {e}")

    def get_embeddings(self, doc: str) -> np.ndarray:
        """Generate dense embeddings for a document using the configured embeddings API."""

        response = self.embeddings_client.embeddings.create(
            input=doc, model=self.embeddings_model
        )
        return np.array(response.data[0].embedding)

    def _generate_point_id(self, doc: Document) -> str:
        """Derive a stable identifier for a document chunk."""

        metadata = doc.metadata or {}
        try:
            metadata_blob = json.dumps(metadata, sort_keys=True, default=str)
        except TypeError:
            metadata_blob = str(metadata)

        raw_value = f"{metadata_blob}::{doc.text}"
        stable_uuid = uuid.uuid5(uuid.NAMESPACE_URL, raw_value)
        return str(stable_uuid)

    def add_documents(
        self,
        docs: list[Document],
        dense_embeddings: np.ndarray,
        sparse_embeddings: Optional[list[Any]] = None,
        batch_size: int = 1000,
    ) -> None:
        """
        Add documents and their embeddings to the vector database.

        Args:
            docs: List of Document objects to add
            dense_embeddings: Array of dense embeddings for the documents
            sparse_embeddings: Optional list of sparse embeddings for the documents
            batch_size: Number of documents to process in each batch
        """

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
                point_id = self._generate_point_id(doc)
                payload = {"text": doc.text}
                if doc.metadata:
                    payload.update(doc.metadata)

                point_data = {
                    "id": point_id,
                    "payload": payload,
                }

                # If sparse embeddings are provided, use hybrid vector format
                if (
                    batch_sparse is not None
                    and j < len(batch_sparse)
                    and batch_sparse[j] is not None
                ):
                    sparse_embedding = batch_sparse[j]
                    # Convert to object if it has as_object method, otherwise use directly
                    sparse_obj = (
                        sparse_embedding.as_object()
                        if hasattr(sparse_embedding, "as_object")
                        else sparse_embedding
                    )

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

            logger.info(
                f"Upserting {len(points)} points from {i} to {i + len(batch_docs)}..."
            )
            if len(points) > 0:  # Only upsert if we have points
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=points,
                )
            else:
                logger.warning("No points to upsert in this batch")

    def hybrid_search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        """
        Perform hybrid search using both dense and sparse embeddings with RRF fusion.

        Args:
            query: Search query text
            top_k: Number of results to return

        Returns:
            List of Search results ranked by relevance
        """
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
            SearchResult(
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
