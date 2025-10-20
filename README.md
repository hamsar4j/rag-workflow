# RAG Workflow

## Overview

This project implements a Retrieval-Augmented Generation (RAG) workflow for building AI-powered question-answering systems. The application combines LangGraph for workflow orchestration, Qdrant for vector storage, and various LLM providers for embeddings and generation.

![RAG Workflow](assets/rag-workflow.png)

## Architecture

The application follows a modular architecture with the following components:

1. **Frontend**: Streamlit-based chat interface for user interaction
2. **Backend**: FastAPI server exposing REST endpoints
3. **Workflow Engine**: LangGraph-powered RAG pipeline with multiple stages
4. **Vector Store**: Qdrant for efficient similarity search
5. **AI Models**:
   - Dense Embeddings: intfloat/multilingual-e5-large-instruct via Together AI
   - Sparse Embeddings: Qdrant/bm25
   - Generation: moonshotai/Kimi-K2-Instruct-0905 via Together AI
   - Re-ranking: jina-reranker-v1-tiny-en via Jina AI (optional)

## Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) for dependency management
- Docker and Docker Compose (for Qdrant vector database)
- API keys for Together AI, Qdrant and optionally Jina AI

## Quickstart

1. **Install dependencies**

   ```bash
   uv sync
   uv pip install -e .
   ```

2. **Configure environment**

   ```bash
   cp .env.example .env
   ```

   Fill in the placeholders with your credentials. Key variables:
   - `BACKEND_URL` (default `http://localhost:8000`)
   - `QDRANT_URL` / `QDRANT_API_KEY`, plus optional overrides such as `QDRANT_COLLECTION_NAME` (`sutd`) and `QDRANT_SEARCH_TOP_K` (`10`)
   - `LLM_API_KEY` with optional `LLM_BASE_URL` / `LLM_MODEL` (default `moonshotai/Kimi-K2-Instruct-0905`)
   - `EMBEDDINGS_API_KEY` with optional `EMBEDDINGS_BASE_URL`, `EMBEDDINGS_MODEL` (default `intfloat/multilingual-e5-large-instruct`), and `EMBEDDINGS_DIM` (`1024`)
   - `ENABLE_RERANKER` (`false` by default) plus `RERANKING_API_KEY` when enabling the Jina reranker

   Review `src/app/core/config.py` if you need to adjust defaults beyond these variables.

3. **Ingest data** (first run)

   ```bash
   uv run python -m app.ingestion.cli
   ```

   The CLI accepts flags such as `--urls`, `--pdfs`, `--chunk-size`, and `--overlap`; run with `--help` to see all options.

4. **Run services**

   ```bash
   docker compose up -d
   uv run fastapi run src/app/api.py
   uv run streamlit run src/app/main.py
   ```

   The Streamlit UI expects the backend to be reachable at the `BACKEND_URL` defined in your `.env`.

## Ingestion Pipeline

The ingestion CLI orchestrates four stages:

- **Load sources**: Scrapes default URLs or user-provided URLs/PDFs.
- **Chunk documents**: Splits text using recursive chunking with configurable size/overlap.
- **Generate embeddings**: Creates dense vectors with `intfloat/multilingual-e5-large-instruct` and sparse BM25 vectors.
- **Store in Qdrant**: Persists chunks, embeddings, and metadata; cached runs skip unchanged work.

## Usage

1. After starting all services, open your browser to:
   - Streamlit UI: <http://localhost:8501>
   - FastAPI docs: <http://localhost:8000/docs>

2. In the Streamlit chat interface, ask questions related to your knowledge base.

3. The system will:
   - Analyze your query
   - Retrieve relevant documents from the vector store
   - Optionally re-rank results for better quality
   - Generate a response based on the retrieved context

### API Access

You can also interact with the RAG system programmatically via its API:

- `POST /query` - Submit a question to the RAG system

  ```bash
  curl -X POST "http://localhost:8000/query" \
       -H "Content-Type: application/json" \
       -d '{"query": "Your question here"}'
  ```

- `GET /health` - Health check endpoint

## Project Structure

```md
rag-workflow/
├── src/
│   ├── app/
│   │   ├── api.py              # FastAPI server
│   │   ├── main.py             # Streamlit frontend
│   │   ├── core/               # Configuration
│   │   ├── db/                 # Database integration (Qdrant)
│   │   ├── ingestion/          # Data ingestion utilities
│   │   │   ├── cli.py          # Command-line interface for ingestion
│   │   │   ├── ingest.py       # Core ingestion functions
│   │   │   ├── web_loader/     # Web document loading utilities
│   │   │   └── pdf_loader/     # PDF document loading utilities
│   │   ├── models/             # Data models
│   │   ├── utils/              # Utility functions
│   │   └── workflow/           # RAG workflow implementation
├── assets/                     # Images and documentation assets
├── notebooks/                  # Jupyter notebooks
│   ├── ingest_data.ipynb       # Jupyter notebook for data ingestion
│   └── ragas_eval.ipynb        # RAGAS-based evaluation walkthrough
├── .env.example                # Environment variable template
├── docker-compose.yaml         # Qdrant service configuration
├── pyproject.toml              # Project dependencies
└── README.md                   # This file
```

## Features

- **LangGraph RAG pipeline** that fuses retrieval and generation for grounded responses.
- **Streamlit + FastAPI surfaces** for conversational and programmatic access to the same workflow.
- **Hybrid search** combining `intfloat/multilingual-e5-large-instruct` dense vectors with Qdrant BM25 sparse vectors via Reciprocal Rank Fusion (`src/app/db/vector_db.py`).
- **Environment-driven configuration** covering models, retrieval parameters, and the optional Jina reranker switch.
- **Flexible ingestion CLI** for URLs/PDFs with chunk controls and caching to avoid reprocessing.

## Evaluation

The `notebooks/ragas_eval.ipynb` notebook walks through running RAGAS evaluations against recorded question/answer pairs (see `notebooks/evaluation_records.json`). Use it to track retrieval and generation quality as you iterate on the workflow.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
