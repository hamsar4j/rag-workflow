from app.models.models import Document
import logging

logger = logging.getLogger(__name__)


# split the documents into chunks
def split_docs(
    docs: list[tuple[str, str]], chunk_size: int = 500, overlap: int = 100
) -> list[Document]:
    all_chunks = []

    for i, doc in enumerate(docs):
        # doc is a tuple (text, url)
        text, url = doc
        text = str(text)
        metadata = {"source": url}
        for j in range(0, len(text), chunk_size - overlap):
            chunk = text[j : j + chunk_size]
            all_chunks.append(Document(text=chunk, metadata=metadata))

    logging.info(f"Split documents into {len(all_chunks)} chunks.")
    return all_chunks
