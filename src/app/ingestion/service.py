import logging
from dataclasses import dataclass
from typing import Iterable, Tuple

from app.core.config import settings
from app.ingestion.ingest import (
    generate_embeddings,
    split_documents,
    store_documents,
)

logger = logging.getLogger(__name__)

DocumentInput = Tuple[str, str]


@dataclass(slots=True)
class IngestionResult:
    """Summary of an ingestion run."""

    document_count: int
    chunk_count: int
    warnings: list[str]


def _normalize_documents(
    docs: Iterable[DocumentInput],
) -> tuple[list[DocumentInput], list[str]]:
    normalized: list[DocumentInput] = []
    warnings: list[str] = []

    for text, source in docs:
        label = source or "unknown"
        normalized_text = (text or "").strip()
        if not normalized_text:
            warnings.append(f"Skipping empty document from {label}.")
            continue
        normalized.append((normalized_text, label))

    return normalized, warnings


def ingest_text_documents(
    docs: Iterable[DocumentInput],
    chunk_size: int = settings.chunk_size,
    overlap: int = settings.chunk_overlap,
) -> IngestionResult:
    """
    Ingest a collection of text documents into the vector store.

    Args:
        docs: Iterable of ``(text, source_identifier)`` tuples.
        chunk_size: Chunk size for document splitting.
        overlap: Overlap between chunks.

    Returns:
        IngestionResult containing counts and warnings.

    Raises:
        RuntimeError: When ingestion fails before storing documents.
    """

    normalized_docs, warnings = _normalize_documents(docs)

    if not normalized_docs:
        warnings.append("No valid documents to ingest after preprocessing.")
        return IngestionResult(document_count=0, chunk_count=0, warnings=warnings)

    logger.info(
        "Starting ingestion for %d documents (chunk_size=%d, overlap=%d).",
        len(normalized_docs),
        chunk_size,
        overlap,
    )

    try:
        chunks = split_documents(
            normalized_docs,
            chunk_size=chunk_size,
            overlap=overlap,
        )
    except Exception as exc:
        logger.exception("Failed to split documents: %s", exc)
        raise RuntimeError(f"Failed to split documents: {exc}") from exc

    if not chunks:
        warnings.append(
            "Document splitting produced zero chunks; nothing was stored in the index."
        )
        return IngestionResult(
            document_count=len(normalized_docs),
            chunk_count=0,
            warnings=warnings,
        )

    try:
        dense_embeddings, sparse_embeddings = generate_embeddings(chunks)
    except Exception as exc:
        logger.exception("Failed to generate embeddings: %s", exc)
        raise RuntimeError(f"Failed to generate embeddings: {exc}") from exc

    try:
        store_documents(chunks, dense_embeddings, sparse_embeddings)
    except Exception as exc:
        logger.exception("Failed to store documents: %s", exc)
        raise RuntimeError(f"Failed to store documents: {exc}") from exc

    logger.info(
        "Completed ingestion: %d documents -> %d chunks.",
        len(normalized_docs),
        len(chunks),
    )

    return IngestionResult(
        document_count=len(normalized_docs),
        chunk_count=len(chunks),
        warnings=warnings,
    )
