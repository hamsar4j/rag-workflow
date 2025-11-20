# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Backend Development

```bash
# Install dependencies
uv sync
uv pip install -e .

# Start Qdrant vector database
docker compose up -d

# Run FastAPI server (development)
uv run fastapi run src/app/api.py

# Run FastAPI server (production)
uv run fastapi run src/app/api.py --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd frontend
pnpm install        # First time setup
pnpm dev           # Development server (http://localhost:3000)
pnpm build         # Production build
pnpm start         # Production server
```

### Environment Configuration

Copy `.env.example` to `.env` and populate required API keys:

- `QDRANT_URL` / `QDRANT_API_KEY` for vector database
- `LLM_API_KEY` for generation model (default: Together AI)
- `EMBEDDINGS_API_KEY` for embedding model (default: Together AI)
- `RERANKING_API_KEY` (optional, for Jina reranker when `ENABLE_RERANKER=true`)

**Data Storage**:

- Qdrant vector database runs in Docker (configured in `docker-compose.yaml`)
- Chat history stored in SQLite database at `data/chats.db` (auto-created on first run)
- Both databases persist across server restarts

## Architecture

### RAG Workflow Pipeline (LangGraph)

The core RAG workflow is implemented in `src/app/workflow/rag_workflow.py` using LangGraph with four sequential stages:

1. **analyze_query**: Prepares the query for retrieval (currently pass-through, extensible for query expansion)
2. **retrieve**: Performs hybrid search using dense + sparse embeddings via `VectorDB.hybrid_search()`
3. **rerank**: Optional Jina reranker stage (enabled via `ENABLE_RERANKER=true` in config)
4. **generate**: LLM generation with context from retrieved documents

The workflow maintains state through a `State` TypedDict containing `question`, `query`, `context`, `answer`, and optional `model` override.

### Hybrid Search Implementation

Located in `src/app/db/vector_db.py`, the `VectorDB` class implements Reciprocal Rank Fusion (RRF) combining:

- **Dense vectors**: `intfloat/multilingual-e5-large-instruct` (1024 dimensions) via Together AI
- **Sparse vectors**: Qdrant BM25 via fastembed

The `hybrid_search()` method uses Qdrant's `query_points()` with `FusionQuery` to merge both retrieval approaches. Falls back to dense-only search if hybrid fails.

### Document Ingestion

Two entry points (`/ingest/web` and `/ingest/pdf`) flow through the same pipeline:

1. **Load**: `load_documents()` for URLs (via BeautifulSoup loader) or `extract_text_from_pdf()` for PDFs
2. **Chunk**: `split_documents()` using recursive text splitting (configurable `CHUNK_SIZE` / `CHUNK_OVERLAP`)
3. **Embed**: `generate_embeddings()` creates both dense and sparse embeddings with retry logic
4. **Store**: `store_documents()` upserts to Qdrant with UUID-based deduplication (`_generate_point_id()`)

All ingestion goes through `src/app/ingestion/service.py` which wraps the pipeline and returns `IngestionResponse` with warnings.

### FastAPI Server Structure

`src/app/api.py` exposes REST endpoints:

- `POST /query`: Main RAG query endpoint (accepts optional `model` and `chat_id`; auto-creates chats if none provided)
- `POST /chats`: Create new chat session with optional title
- `GET /chats`: List all chat sessions (ordered by recent activity)
- `GET /chats/{chat_id}`: Get chat with full message history
- `DELETE /chats/{chat_id}`: Delete chat and all messages
- `GET/POST /settings/model`: Get/update active LLM model (persists in-memory via `settings.llm_model`)
- `POST /ingest/web`: Ingest URLs (validates content, filters errors)
- `POST /ingest/pdf`: Ingest PDF uploads (content-type validation)
- `GET /health`: Health check with Qdrant collection name

The workflow and chat database are initialized once at startup via `lifespan` context manager and stored in global variables (`rag_workflow`, `chat_db`).

### Citation Parsing

The backend parses inline citations from LLM responses using `src/app/utils/citation_parser.py`:

- LLM generates responses with sources in square brackets: `text[https://example.com]`
- `parse_citations()` extracts URLs and creates `TextSegment` objects with separate text/source fields
- `/query` endpoint returns `QueryResponse` containing a list of segments
- Frontend renders segments with hover tooltips for cited text (dotted underline indicates source)

Example flow:

```
LLM output: "SUTD offers BSc[https://sutd.edu.sg/education]."
Parsed segments: [
  {text: "SUTD offers BSc", source: "https://sutd.edu.sg/education"},
  {text: ".", source: null}
]
```

### Chat Persistence

Multi-chat support with SQLite database implemented in `src/app/db/chat_db.py`:

- **Database**: SQLite with SQLAlchemy ORM (stored at `data/chats.db`)
- **Models**:
  - `ChatSession`: id, title, created_at, updated_at (relationship to messages)
  - `ChatMessage`: id, chat_id, role, content, segments (JSON), created_at
- **Operations**: `ChatDB` class provides CRUD operations with eager loading via `joinedload()` to prevent detached instance errors
- **Auto-save**: `/query` endpoint saves both user and assistant messages to database
- **Thread integration**: Uses `chat_id` as LangGraph `thread_id` for conversation threading
- **Title generation**: First query (truncated to 50 chars) becomes the chat title

Key implementation details:

- Messages eagerly loaded using `.options(joinedload(ChatSession.messages))` to avoid SQLAlchemy detachment errors
- `session.expunge()` used to detach objects after loading all relationships
- UUID-based chat and message IDs via `src/app/utils/id.py`
- Cascade delete configured so deleting a chat removes all its messages

### Frontend Integration

Next.js 15 app in `frontend/` with:

- Chat interface that proxies to `/query` endpoint with `chat_id` tracking
- Chat history sidebar (visible when on Chat tab) with:
  - "New Chat" button to start fresh conversations
  - List of chat sessions with titles and message counts
  - Active chat highlighting
  - Delete functionality (hover to reveal delete button)
- Model selection dropdown (syncs via `/settings/model`)
- Knowledge Base tab for PDF uploads
- Interactive source citations with hover tooltips (cited text shows dotted underline, reveals URL on hover)
- Environment variable `NEXT_PUBLIC_RAG_API` for backend URL (defaults to `http://localhost:8000`)

**Hooks**:

- `useChats` (`hooks/useChats.ts`): Manages chat list, creation, deletion, fetching
- `useChat` (`hooks/useChat.ts`): Handles current chat state, message sending, chat loading, with callbacks for chat creation
- State synchronization: When backend creates a new chat, `onChatCreated` callback updates frontend state and refreshes chat list

## Configuration Management

All settings centralized in `src/app/core/config.py` using Pydantic Settings with `.env` overrides:

- Qdrant connection and collection settings
- LLM/embeddings model selection and API credentials
- Chunking parameters (`chunk_size`, `chunk_overlap`)
- Optional reranker toggle (`enable_reranker`)

When changing models at runtime via `/settings/model`, the code updates both `os.environ["LLM_MODEL"]` and `settings.llm_model` to maintain consistency.

## Code Style

- Python 3.12+ with type hints (use `list[Type]` not `List[Type]`)
- Follow existing patterns: `snake_case` for functions/modules, PEP8 with 88-100 char lines
- Use `logging.getLogger(__name__)` not print statements
- Docstrings in Google style (see `rag_workflow.py` examples)
- Frontend: TypeScript with Tailwind CSS v4, React 19

## Evaluation

Use `notebooks/ragas_eval.ipynb` for RAGAS-based evaluation after modifying retrieval or generation logic. Test data stored in `notebooks/evaluation_records.json`.
