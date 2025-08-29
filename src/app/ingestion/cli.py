import argparse
import os
from app.ingestion.ingest import (
    load_documents,
    split_documents,
    generate_embeddings,
    store_documents,
)
from app.ingestion.pdf_loader.pdf_to_text import extract_text_from_pdf
from app.ingestion.web_loader.bs_utils import urls as default_urls


def main():
    """Ingest documents into the vector database."""
    parser = argparse.ArgumentParser(
        description="Ingest documents into the vector database."
    )
    parser.add_argument("--urls", nargs="*", help="List of URLs to ingest")
    parser.add_argument("--pdfs", nargs="*", help="List of PDF file paths to ingest")
    parser.add_argument(
        "--chunk-size", type=int, default=500, help="Chunk size for document splitting"
    )
    parser.add_argument(
        "--overlap", type=int, default=100, help="Overlap between chunks"
    )

    args = parser.parse_args()

    # Load documents
    docs = []
    if args.urls:
        docs.extend(load_documents(args.urls))
    elif not args.pdfs:  # If no URLs or PDFs specified, use default URLs
        docs.extend(load_documents(default_urls))

    if args.pdfs:
        for pdf_path in args.pdfs:
            if os.path.exists(pdf_path):
                text = extract_text_from_pdf(pdf_path)
                docs.append((text, pdf_path))
            else:
                print(f"Warning: PDF file not found: {pdf_path}")

    # Split documents
    chunks = split_documents(docs, args.chunk_size, args.overlap)

    # Generate embeddings
    dense_embeddings, sparse_embeddings = generate_embeddings(chunks)

    # Store documents
    store_documents(chunks, dense_embeddings, sparse_embeddings)

    print(f"Successfully ingested {len(chunks)} document chunks.")


if __name__ == "__main__":
    main()
