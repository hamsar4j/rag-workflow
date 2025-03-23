from models import Document


# split the documents into chunks
def split_docs(
    docs: list[str], chunk_size: int = 300, overlap: int = 100
) -> list[Document]:
    all_chunks = []

    for i, doc in enumerate(docs):
        text = str(doc)
        metadata = {"source": f"doc_{i}"}
        for j in range(0, len(text), chunk_size - overlap):
            chunk = text[j : j + chunk_size]
            all_chunks.append(Document(text=chunk, metadata=metadata))

    print(f"Split documents into {len(all_chunks)} chunks.")
    return all_chunks
