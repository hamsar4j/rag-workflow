from typing import List, Tuple
import numpy as np
from tenacity import (
    retry,
    wait_exponential,
    stop_after_attempt,
    retry_if_exception_type,
)
import requests
from app.core.config import settings as config
from app.db.vector_db import VectorDB
from app.models.models import Document
from app.utils.utils import split_docs
from app.utils.progress import progress_bar
from app.ingestion.web_loader.bs_loader import load_web_docs
from fastembed import SparseTextEmbedding


def load_documents(urls: List[str]) -> List[Tuple[str, str]]:
    """Load documents from URLs."""
    return load_web_docs(urls)


def split_documents(
    docs: List[Tuple[str, str]], chunk_size: int = 500, overlap: int = 100
) -> List[Document]:
    """Split documents into chunks."""
    return split_docs(docs, chunk_size, overlap)


@retry(
    retry=retry_if_exception_type((requests.exceptions.RequestException, Exception)),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    stop=stop_after_attempt(5),
)
def _get_embedding_with_retry(
    vector_db: VectorDB, sparse_model: SparseTextEmbedding, text: str
):
    """Get embeddings with retry logic."""
    dense_embedding = vector_db.get_embeddings(text)
    sparse_embedding = list(sparse_model.embed([text]))[0]
    return dense_embedding, sparse_embedding


def generate_embeddings(chunks: List[Document]) -> Tuple[List[np.ndarray], List]:
    """Generate dense and sparse embeddings for document chunks."""
    vector_db = VectorDB(config)
    sparse_model = SparseTextEmbedding("Qdrant/bm25")

    dense_embeddings = []
    sparse_embeddings = []

    with progress_bar("Generating embeddings...") as progress:
        task = progress.add_task("Generating embeddings...", total=len(chunks))

        for i, chunk in enumerate(chunks):
            try:
                dense_embedding, sparse_embedding = _get_embedding_with_retry(
                    vector_db, sparse_model, chunk.text
                )
                dense_embeddings.append(dense_embedding)
                sparse_embeddings.append(sparse_embedding)

                progress.update(task, advance=1)

            except Exception as e:
                print(f"Failed after retries on chunk {i}: {str(e)}")
                # Append zero embeddings as fallback
                dense_embeddings.append(np.zeros(config.embeddings_dim))
                sparse_embeddings.append(None)

    return dense_embeddings, sparse_embeddings


def store_documents(
    chunks: List[Document], dense_embeddings: List[np.ndarray], sparse_embeddings: List
):
    """Store documents and their embeddings in the vector database."""
    vector_db = VectorDB(config)
    # Convert list of numpy arrays to numpy array for compatibility
    dense_embeddings_array = np.array(dense_embeddings)

    with progress_bar("Upserting documents...") as progress:
        task = progress.add_task("Upserting documents...", total=1)
        vector_db.add_documents(
            docs=chunks,
            dense_embeddings=dense_embeddings_array,
            sparse_embeddings=sparse_embeddings,
        )
        progress.update(task, advance=1)
