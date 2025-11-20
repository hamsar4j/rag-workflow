import logging
from typing import Optional

from app.models.models import Document
from app.utils.progress import progress_bar

logger = logging.getLogger(__name__)


def recursive_split(
    text: str,
    chunk_size: int = 512,
    overlap: int = 96,
    separators: Optional[list[str]] = None,
) -> list[str]:
    """Recursively split text into chunks of specified size with overlap."""

    if separators is None:
        separators = ["\n\n", "\n", ".", " ", ""]

    if len(text) <= chunk_size:
        return [text]

    for sep in separators:
        if sep and sep in text:
            splits = text.split(sep)
            chunks = []
            current = ""
            for part in splits:
                if current and len(current) + len(part) + len(sep) > chunk_size:
                    chunks.append(current.strip())
                    current = ""
                current += (sep if current else "") + part
            if current:
                chunks.append(current.strip())
            # recursively split chunks that are still too large
            result = []
            for chunk in chunks:
                if len(chunk) > chunk_size:
                    result.extend(
                        recursive_split(chunk, chunk_size, overlap, separators[1:])
                    )
                else:
                    result.append(chunk)
            return result
    # fallback: hard split
    return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size - overlap)]


def split_docs(
    docs: list[tuple[str, str]], chunk_size: int = 500, overlap: int = 100
) -> list[Document]:
    """Split a list of documents into smaller chunks."""

    all_chunks = []

    with progress_bar("Splitting documents...") as progress:
        task = progress.add_task("Splitting documents...", total=len(docs))

        for text, url in docs:
            metadata = {"source": url}
            for chunk in recursive_split(str(text), chunk_size, overlap):
                all_chunks.append(Document(text=chunk, metadata=metadata))
            progress.update(task, advance=1)

    logging.info(f"Split documents into {len(all_chunks)} chunks.")

    return all_chunks
