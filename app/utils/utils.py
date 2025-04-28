from app.models.models import Document
import logging

logger = logging.getLogger(__name__)


def recursive_split(
    text: str,
    chunk_size: int = 500,
    overlap: int = 100,
    separators: list[str] = ["\n\n", "\n", ".", " ", ""],
) -> list[str]:
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
    all_chunks = []
    for text, url in docs:
        metadata = {"source": url}
        for chunk in recursive_split(str(text), chunk_size, overlap):
            all_chunks.append(Document(text=chunk, metadata=metadata))
    logging.info(f"Split documents into {len(all_chunks)} chunks.")
    return all_chunks
