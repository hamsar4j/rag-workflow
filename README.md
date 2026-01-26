# RAG Workflow

## Overview

This project implements a Retrieval-Augmented Generation (RAG) workflow for building AI-powered question-answering systems. The application combines LangGraph for workflow orchestration, PostgreSQL with pgvector for vector storage, and various LLM providers for embeddings and generation.

![RAG Workflow](assets/rag-workflow.png)
![RAG Chat](assets/rag-chat.png)
![RAG KB](assets/rag-kb.png)

## Architecture

The application follows a modular architecture with the following components:

1. **Frontend**: Next.js chat interface (`frontend/`) for live chat supervision with multi-chat support
2. **Backend**: FastAPI server exposing REST endpoints
3. **Workflow Engine**: LangGraph-powered RAG pipeline with multiple stages
4. **Vector Store**: PostgreSQL with pgvector extension for efficient similarity search
5. **Chat Persistence**: SQLite database for storing chat sessions and message history
6. **AI Models**:
   - Dense Embeddings: intfloat/multilingual-e5-large-instruct via Together AI
   - Full-Text Search: PostgreSQL native tsvector with GIN index
   - Generation: moonshotai/Kimi-K2-Instruct-0905 via Together AI
   - Re-ranking: jina-reranker-v1-tiny-en via Jina AI (optional)

## Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) for dependency management
- Docker and Docker Compose (for PostgreSQL with pgvector)
- API keys for Together AI and optionally Jina AI

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
   - `POSTGRES_URL` (default `postgresql://rag_user:rag_password@localhost:5433/rag_db`), plus optional overrides such as `POSTGRES_TABLE_NAME` (`documents`) and `POSTGRES_SEARCH_TOP_K` (`10`)
   - `LLM_API_KEY` with optional `LLM_BASE_URL` / `LLM_MODEL` (default `moonshotai/Kimi-K2-Instruct-0905`). You can swap models at runtime from the chat dropdown or the `/settings/model` API; the latest choice is stored in-process.
   - `EMBEDDINGS_API_KEY` with optional `EMBEDDINGS_BASE_URL`, `EMBEDDINGS_MODEL` (default `intfloat/multilingual-e5-large-instruct`), and `EMBEDDINGS_DIM` (`1024`)
   - `ENABLE_RERANKER` (`false` by default) plus `RERANKING_API_KEY` when enabling the Jina reranker

   Review `src/app/core/config.py` if you need to adjust defaults beyond these variables.

3. **Ingest data**

   Use the chat UI or the `/ingest/web` and `/ingest/pdf` endpoints documented below to add sources. Upload PDFs directly from the Knowledge Base tab or call the APIs with curl/Postman.

4. **Run services**

   ```bash
   docker compose up -d
   uv run fastapi run src/app/api.py
   ```

   In a separate terminal, start the frontend:

   ```bash
   cd frontend
   bun install
   bun run dev
   ```

   The FastAPI server listens on `http://localhost:8000`. The Next.js app proxies requests to `/query`; export `NEXT_PUBLIC_RAG_API` if the backend runs elsewhere.

## Ingestion Pipeline

Regardless of entry point (UI or API), ingestion flows through the same stages:

- **Load sources**: Scrapes URLs or extracts text from uploaded PDFs.
- **Chunk documents**: Splits text using recursive chunking with configurable size/overlap.
- **Generate embeddings**: Creates dense vectors with `intfloat/multilingual-e5-large-instruct`.
- **Store in PostgreSQL**: Persists chunks, embeddings, and metadata. Full-text search vectors (tsvector) are auto-generated.

## Usage

1. With FastAPI and the Next.js dev server running, open:
   - Chat UI: <http://localhost:3000>
   - FastAPI docs: <http://localhost:8000/docs>

2. In the chat, use the model dropdown to pick an LLM, then issue questions against your knowledge base. The UI forwards each prompt to `/query` with the selected model and renders the grounded answer with interactive source citations. Your conversation is automatically saved to the database.

3. The system will:
   - Analyze your query
   - Retrieve relevant documents from the vector store using hybrid search (dense vectors + full-text search with RRF fusion)
   - Optionally re-rank results for better quality
   - Generate a response based on the retrieved context
   - Display source citations as hoverable tooltips in the chat interface
   - Save both your question and the assistant's response to the chat database

4. Use the **chat history sidebar** to:
   - View all your conversations (ordered by recent activity)
   - Switch between different chat sessions
   - Start a new conversation with the "New Chat" button
   - Delete conversations you no longer need (hover over a chat to reveal the delete button)
   - Chat history persists across browser refreshes and server restarts

### API Access

You can also interact with the RAG system programmatically via its API:

- `POST /query` — Submit a question to the RAG system, optionally overriding the active model and chat session. Returns a structured response with text segments and source citations. If no `chat_id` is provided, a new chat session is automatically created.

  ```bash
  curl -X POST "http://localhost:8000/query" \
       -H "Content-Type: application/json" \
       -d '{"query": "Your question here", "chat_id": "existing-chat-id", "model": "deepseek-ai/DeepSeek-R1"}'
  ```

  Response format:

  ```json
  {
    "chat_id": "abc-123-def-456",
    "segments": [
      {"text": "Answer text here", "source": "https://example.com/source"},
      {"text": " More text.", "source": null}
    ]
  }
  ```

- `POST /ingest/web` — Provide a JSON body with `urls` to crawl and index web pages.

  ```bash
  curl -X POST "http://localhost:8000/ingest/web" \
       -H "Content-Type: application/json" \
       -d '{"urls": ["https://example.com/docs"]}'
  ```

- `POST /ingest/pdf` — Upload one or more PDF files for ingestion.

  ```bash
  curl -X POST "http://localhost:8000/ingest/pdf" \
       -F "files=@manual.pdf"
  ```

- `GET /settings/model` — Return the currently active LLM model.

- `POST /settings/model` — Update the active LLM model. The backend also updates its in-memory configuration so the chat UI stays synchronized.

  ```bash
  curl -X POST "http://localhost:8000/settings/model" \
       -H "Content-Type: application/json" \
       -d '{"model": "moonshotai/Kimi-K2-Instruct-0905"}'
  ```

- `POST /chats` — Create a new chat session with an optional custom title.

  ```bash
  curl -X POST "http://localhost:8000/chats" \
       -H "Content-Type: application/json" \
       -d '{"title": "My Custom Chat Title"}'
  ```

- `GET /chats` — List all chat sessions, ordered by most recent activity.

  ```bash
  curl "http://localhost:8000/chats"
  ```

- `GET /chats/{chat_id}` — Get a specific chat session with all its messages.

  ```bash
  curl "http://localhost:8000/chats/abc-123-def-456"
  ```

- `DELETE /chats/{chat_id}` — Delete a chat session and all its messages.

  ```bash
  curl -X DELETE "http://localhost:8000/chats/abc-123-def-456"
  ```

- `GET /health` — Health check endpoint (includes the active PostgreSQL table name).

## Project Structure

```md
rag-workflow/
├── src/
│   ├── app/
│   │   ├── api.py              # FastAPI server
│   │   ├── core/               # Configuration
│   │   ├── db/                 # Database integration
│   │   │   ├── vector_db.py    # PostgreSQL pgvector client
│   │   │   └── chat_db.py      # SQLite chat persistence (SQLAlchemy)
│   │   ├── ingestion/          # Data ingestion utilities
│   │   │   ├── ingest.py       # Core ingestion functions
│   │   │   ├── web_loader/     # Web document loading utilities
│   │   │   └── pdf_loader/     # PDF document loading utilities
│   │   ├── models/             # Data models
│   │   ├── utils/              # Utility functions
│   │   │   ├── citation_parser.py  # Citation extraction from LLM responses
│   │   │   └── id.py           # ID generation utility
│   │   └── workflow/           # RAG workflow implementation
├── frontend/                   # Next.js chat frontend
├── assets/                     # Images and documentation assets
├── notebooks/                  # Jupyter notebooks
│   ├── ingest_data.ipynb       # Jupyter notebook for data ingestion
│   └── ragas_eval.ipynb        # RAGAS-based evaluation walkthrough
├── .env.example                # Environment variable template
├── docker-compose.yaml         # PostgreSQL pgvector service configuration
├── pyproject.toml              # Project dependencies
└── README.md                   # This file
```

## Features

- **LangGraph RAG pipeline** that fuses retrieval and generation for grounded responses.
- **Multi-chat persistence** with SQLite database — chat sessions and messages are automatically saved and restored across browser refreshes and server restarts.
- **Interactive source citations** with hover tooltips in the chat UI — cited text appears with a dotted underline, revealing the source URL on hover.
- **Next.js chat UI + FastAPI API** for conversational oversight and programmatic access to the same workflow, including live LLM switching.
- **Chat history sidebar** — view, switch between, and manage multiple conversations with automatic title generation and delete functionality.
- **Hybrid search** combining `intfloat/multilingual-e5-large-instruct` dense vectors (HNSW index) with PostgreSQL full-text search (tsvector with GIN index) via Reciprocal Rank Fusion (`src/app/db/vector_db.py`).
- **Environment-driven configuration** covering models, retrieval parameters, and the optional Jina reranker switch.
- **Flexible ingestion CLI** for URLs/PDFs with chunk controls and caching to avoid reprocessing.

## Evaluation

The `notebooks/ragas_eval.ipynb` notebook walks through running RAGAS evaluations against recorded question/answer pairs (see `notebooks/evaluation_records.json`). Use it to track retrieval and generation quality as you iterate on the workflow.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
