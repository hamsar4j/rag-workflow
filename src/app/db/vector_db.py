import json
import logging
import uuid
from typing import Any, Optional

import numpy as np
import psycopg
from openai import OpenAI
from pgvector.psycopg import register_vector

from app.models.models import Document, SearchResult

logger = logging.getLogger(__name__)


class VectorDB:
    """Vector database client for PostgreSQL with pgvector and hybrid search capabilities."""

    def __init__(self, config: Any):
        self.embeddings_model = config.embeddings_model
        self.embeddings_dim = config.embeddings_dim
        self.table_name = config.postgres_table_name

        # PostgreSQL connection
        self.conn = psycopg.connect(config.postgres_url)

        # Enable pgvector extension before registering vector type
        with self.conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
        self.conn.commit()

        register_vector(self.conn)

        # Embeddings client
        self.embeddings_client = OpenAI(
            api_key=config.embeddings_api_key, base_url=config.embeddings_base_url
        )

        self._ensure_table_exists()

    def table_exists(self) -> bool:
        """Check if table exists."""
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = %s
                )
                """,
                (self.table_name,),
            )
            result = cur.fetchone()
            return result[0] if result else False

    def _ensure_table_exists(self):
        """Ensure the documents table exists with required indexes."""
        with self.conn.cursor() as cur:
            # Create table with generated tsvector column
            cur.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    id UUID PRIMARY KEY,
                    text TEXT NOT NULL,
                    source TEXT,
                    dense_embedding vector({self.embeddings_dim}) NOT NULL,
                    text_search tsvector GENERATED ALWAYS AS (to_tsvector('english', text)) STORED,
                    metadata JSONB DEFAULT '{{}}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            # Create HNSW index for dense vectors (cosine similarity)
            cur.execute(
                f"""
                CREATE INDEX IF NOT EXISTS idx_{self.table_name}_dense
                ON {self.table_name}
                USING hnsw (dense_embedding vector_cosine_ops)
                """
            )

            # Create GIN index for full-text search
            cur.execute(
                f"""
                CREATE INDEX IF NOT EXISTS idx_{self.table_name}_fts
                ON {self.table_name}
                USING GIN (text_search)
                """
            )

            # Create index on source for filtering
            cur.execute(
                f"""
                CREATE INDEX IF NOT EXISTS idx_{self.table_name}_source
                ON {self.table_name} (source)
                """
            )

        self.conn.commit()
        logger.info(f"Table '{self.table_name}' ensured with indexes")

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
        sparse_embeddings: Optional[list[Any]] = None,  # Ignored - kept for interface
        batch_size: int = 1000,
    ) -> None:
        """
        Add documents and their embeddings to the vector database.

        Args:
            docs: List of Document objects to add
            dense_embeddings: Array of dense embeddings for the documents
            sparse_embeddings: Ignored (PostgreSQL generates tsvector automatically)
            batch_size: Number of documents to process in each batch
        """
        with self.conn.cursor() as cur:
            for i in range(0, len(docs), batch_size):
                batch_docs = docs[i : i + batch_size]
                batch_embeddings = dense_embeddings[i : i + batch_size]

                values = []
                for doc, embedding in zip(batch_docs, batch_embeddings):
                    point_id = self._generate_point_id(doc)
                    metadata = dict(doc.metadata) if doc.metadata else {}
                    source = metadata.pop("source", None)

                    embedding_list = (
                        embedding.tolist()
                        if hasattr(embedding, "tolist")
                        else list(embedding)
                    )

                    values.append(
                        (
                            point_id,
                            doc.text,
                            source,
                            embedding_list,
                            json.dumps(metadata),
                        )
                    )

                # Batch upsert with ON CONFLICT
                cur.executemany(
                    f"""
                    INSERT INTO {self.table_name} (id, text, source, dense_embedding, metadata)
                    VALUES (%s, %s, %s, %s::vector, %s::jsonb)
                    ON CONFLICT (id) DO UPDATE SET
                        text = EXCLUDED.text,
                        source = EXCLUDED.source,
                        dense_embedding = EXCLUDED.dense_embedding,
                        metadata = EXCLUDED.metadata
                    """,
                    values,
                )

                logger.info(
                    f"Upserted {len(values)} documents ({i} to {i + len(batch_docs)})"
                )

        self.conn.commit()

    def _rrf_fusion(
        self,
        dense_results: list[dict],
        fts_results: list[dict],
        k: int = 60,
        top_k: int = 5,
    ) -> list[dict]:
        """
        Combine results using Reciprocal Rank Fusion.

        Args:
            dense_results: Results from dense vector search
            fts_results: Results from full-text search
            k: RRF constant (typically 60)
            top_k: Number of results to return

        Returns:
            Fused and ranked results
        """
        # Build document lookup
        all_docs = {}
        for r in dense_results + fts_results:
            doc_id = r["id"]
            if doc_id not in all_docs:
                all_docs[doc_id] = r.copy()
                all_docs[doc_id]["rrf_score"] = 0.0

        # Calculate RRF scores
        for rank, r in enumerate(dense_results):
            all_docs[r["id"]]["rrf_score"] += 1.0 / (k + rank + 1)

        for rank, r in enumerate(fts_results):
            all_docs[r["id"]]["rrf_score"] += 1.0 / (k + rank + 1)

        # Sort by RRF score and return top_k
        sorted_docs = sorted(
            all_docs.values(), key=lambda x: x["rrf_score"], reverse=True
        )
        return sorted_docs[:top_k]

    def hybrid_search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        """
        Perform hybrid search using dense vectors + full-text search with RRF fusion.

        Args:
            query: Search query text
            top_k: Number of results to return

        Returns:
            List of SearchResult objects ranked by relevance
        """
        # Get dense embedding for query
        dense_embedding = self.get_embeddings(query)
        embedding_list = dense_embedding.tolist()

        # Prefetch more results for better RRF fusion
        prefetch_k = top_k * 3

        with self.conn.cursor() as cur:
            # Dense vector search (cosine similarity)
            # Note: <=> is cosine distance, so lower is better
            # We compute 1 - distance to get similarity score
            cur.execute(
                f"""
                SELECT id, text, source, metadata,
                       1 - (dense_embedding <=> %s::vector) as score
                FROM {self.table_name}
                ORDER BY dense_embedding <=> %s::vector
                LIMIT %s
                """,
                (embedding_list, embedding_list, prefetch_k),
            )

            dense_results = [
                {
                    "id": str(row[0]),
                    "text": row[1],
                    "source": row[2],
                    "metadata": row[3] or {},
                    "score": row[4],
                }
                for row in cur.fetchall()
            ]

            # Full-text search
            cur.execute(
                f"""
                SELECT id, text, source, metadata,
                       ts_rank_cd(text_search, plainto_tsquery('english', %s)) as score
                FROM {self.table_name}
                WHERE text_search @@ plainto_tsquery('english', %s)
                ORDER BY score DESC
                LIMIT %s
                """,
                (query, query, prefetch_k),
            )

            fts_results = [
                {
                    "id": str(row[0]),
                    "text": row[1],
                    "source": row[2],
                    "metadata": row[3] or {},
                    "score": row[4],
                }
                for row in cur.fetchall()
            ]

        # Apply RRF fusion
        if fts_results:
            fused_results = self._rrf_fusion(dense_results, fts_results, top_k=top_k)
        else:
            # If no FTS results, just use dense results
            fused_results = dense_results[:top_k]
            for r in fused_results:
                r["rrf_score"] = r["score"]

        logger.info(
            f"Retrieved {len(fused_results)} results "
            f"(dense: {len(dense_results)}, fts: {len(fts_results)})"
        )

        return [
            SearchResult(
                text=r["text"],
                metadata=(
                    {**r["metadata"], "source": r["source"]}
                    if r["source"]
                    else r["metadata"]
                ),
                score=r["rrf_score"],
            )
            for r in fused_results
        ]

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
