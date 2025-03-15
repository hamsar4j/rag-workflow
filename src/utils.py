from langchain_text_splitters import RecursiveCharacterTextSplitter


# split the documents into chunks
def split_docs(docs):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(docs)
    print(f"Split blog post into {len(chunks)} sub-documents.")
    return chunks
