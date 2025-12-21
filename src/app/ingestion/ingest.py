from typing import List, Tuple

import numpy as np
import requests
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.config import settings as config
from app.db.vector_db import VectorDB
from app.ingestion.web_loader.bs_loader import load_web_docs
from app.models.models import Document
from app.utils.progress import progress_bar
from app.utils.utils import split_docs


def load_documents(urls: List[str]) -> List[Tuple[str, str]]:
    """Load documents from URLs."""
    return load_web_docs(urls)


def split_documents(
    docs: List[Tuple[str, str]], chunk_size: int, overlap: int
) -> List[Document]:
    """Split documents into chunks."""
    return split_docs(docs, chunk_size, overlap)


@retry(
    retry=retry_if_exception_type((requests.exceptions.RequestException, Exception)),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    stop=stop_after_attempt(5),
)
def _get_embedding_with_retry(vector_db: VectorDB, text: str) -> np.ndarray:
    """Get dense embedding with retry logic."""
    return vector_db.get_embeddings(text)


def generate_embeddings(chunks: List[Document]) -> Tuple[List[np.ndarray], None]:
    """Generate dense embeddings for document chunks.

    Note: Sparse embeddings are no longer generated as PostgreSQL's tsvector
    handles full-text search automatically.
    """
    vector_db = VectorDB(config)

    dense_embeddings = []

    with progress_bar("Generating embeddings...") as progress:
        task = progress.add_task("Generating embeddings...", total=len(chunks))

        for i, chunk in enumerate(chunks):
            try:
                dense_embedding = _get_embedding_with_retry(vector_db, chunk.text)
                dense_embeddings.append(dense_embedding)
                progress.update(task, advance=1)

            except Exception as e:
                print(f"Failed after retries on chunk {i}: {str(e)}")
                # Append zero embeddings as fallback
                dense_embeddings.append(np.zeros(config.embeddings_dim))

    # Return None for sparse_embeddings (not needed with PostgreSQL tsvector)
    return dense_embeddings, None


def store_documents(
    chunks: List[Document], dense_embeddings: List[np.ndarray], sparse_embeddings: None
):
    """Store the embeddings in the vector database."""
    vector_db = VectorDB(config)
    # Convert list of numpy arrays to numpy array for compatibility
    dense_embeddings_array = np.array(dense_embeddings)

    with progress_bar("Upserting embeddings...") as progress:
        task = progress.add_task("Upserting embeddings...", total=1)
        vector_db.add_documents(
            docs=chunks,
            dense_embeddings=dense_embeddings_array,
            sparse_embeddings=None,  # PostgreSQL generates tsvector automatically
        )
        progress.update(task, advance=1)
