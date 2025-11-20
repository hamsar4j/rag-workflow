import logging
import os
import time
from contextlib import asynccontextmanager
from typing import Iterable, Sequence

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from starlette.concurrency import run_in_threadpool

from app.core.config import settings
from app.db.chat_db import ChatDB
from app.ingestion.ingest import load_documents
from app.ingestion.pdf_loader.pdf_to_text import extract_text_from_pdf
from app.ingestion.service import ingest_text_documents
from app.models.models import (
    ChatSessionResponse,
    ChatWithMessagesResponse,
    CreateChatRequest,
    IngestionResponse,
    IngestWebRequest,
    QueryRequest,
    QueryResponse,
    UpdateModelRequest,
)
from app.utils.citation_parser import parse_citations
from app.utils.id import create_id
from app.workflow import build_rag_workflow

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

rag_workflow = None
chat_db = None
ALLOWED_PDF_CONTENT_TYPES = {"application/pdf", "application/octet-stream"}
QDRANT_COLLECTION = settings.qdrant_collection_name


@asynccontextmanager
async def lifespan(app: FastAPI):
    global rag_workflow, chat_db
    try:
        rag_workflow = build_rag_workflow()
        logger.info("RAG workflow initialized successfully")

        chat_db = ChatDB()
        logger.info("Chat database initialized successfully")

        yield
    except Exception as e:
        logger.error(f"Error initializing application: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to initialize application: {str(e)}"
        )


app = FastAPI(lifespan=lifespan)

allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins + ["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware to log all HTTP requests and track metrics."""
    start_time = time.time()

    # Process the request
    response = await call_next(request)

    # Calculate processing time
    process_time = time.time() - start_time

    # Log the request
    logger.info(
        f"{request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.4f}s"
    )

    return response


@app.post("/query", response_model=QueryResponse)
async def run_query(request: QueryRequest):
    """Process a query request through the RAG workflow."""
    # Log the incoming request
    logger.info(f"Processing query: {request.query}")

    if rag_workflow is None:
        raise HTTPException(status_code=500, detail="RAG workflow not initialized")

    if chat_db is None:
        raise HTTPException(status_code=500, detail="Chat database not initialized")

    try:
        # Get or create chat session
        chat_id = request.chat_id
        if not chat_id:
            # Create a new chat session with a title from the first query
            chat_id = create_id()
            title = request.query[:50] + ("..." if len(request.query) > 50 else "")
            chat_db.create_chat(chat_id=chat_id, title=title)
            logger.info(f"Created new chat session: {chat_id}")

        # Save user message
        user_message_id = create_id()
        chat_db.add_message(
            message_id=user_message_id,
            chat_id=chat_id,
            role="user",
            content=request.query,
            segments=None,
        )

        selected_model = request.model or settings.llm_model
        if request.model and request.model != settings.llm_model:
            os.environ["LLM_MODEL"] = request.model
            settings.llm_model = request.model

        state = {"question": request.query, "model": selected_model}
        # Use chat_id as thread_id for LangGraph checkpointing
        config = {"configurable": {"thread_id": chat_id}}

        # Process the query through the RAG workflow
        response = rag_workflow.invoke(state, config=config)
        answer = response["answer"]

        # Parse citations from the answer
        segments = parse_citations(answer)

        # Save assistant message
        assistant_message_id = create_id()
        full_text = "".join([seg.text for seg in segments])
        chat_db.add_message(
            message_id=assistant_message_id,
            chat_id=chat_id,
            role="assistant",
            content=full_text,
            segments=[{"text": seg.text, "source": seg.source} for seg in segments],
        )

        # Log successful response
        logger.info(f"Successfully processed query in chat {chat_id}")

        return QueryResponse(chat_id=chat_id, segments=segments)
    except Exception as e:
        logger.error(f"Error during RAG workflow invocation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"RAG workflow failed: {str(e)}")


@app.get("/settings/model")
async def get_active_model():
    """Return the currently configured LLM model."""

    return {"model": settings.llm_model}


@app.post("/settings/model")
async def update_active_model(payload: UpdateModelRequest):
    """Update the active LLM model for subsequent requests."""

    model = payload.model.strip()
    if not model:
        raise HTTPException(status_code=400, detail="Model identifier cannot be empty.")

    os.environ["LLM_MODEL"] = model
    settings.llm_model = model
    logger.info("Active LLM model updated to %s", model)

    return {"model": settings.llm_model}


def _combine_warnings(*warning_sequences: Sequence[str]) -> list[str]:
    """Merge warning sequences while removing empty entries."""

    merged: list[str] = []
    for seq in warning_sequences:
        for warning in seq or []:
            warning_text = warning.strip()
            if warning_text:
                merged.append(warning_text)
    return merged


def _sanitize_filename(filename: str | None) -> str:
    """Return a safe filename for metadata and logs."""

    if not filename:
        return "uploaded-document.pdf"
    return os.path.basename(filename)


def _loader_warning(text: str) -> str | None:
    """Check whether scraped content indicates an error and return a warning message."""

    normalized = text.strip().lower()
    for prefix, message in (
        ("error", "loader reported an error"),
        ("unexpected error", "loader reported an error"),
        ("could not find the main content", "unable to locate main content"),
    ):
        if normalized.startswith(prefix):
            return message
    return None


async def _ingest_documents(
    docs: Iterable[tuple[str, str]],
    extra_warnings: Sequence[str] | None = None,
) -> IngestionResponse:
    try:
        result = await run_in_threadpool(ingest_text_documents, docs)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    warnings = _combine_warnings(extra_warnings or [], result.warnings)
    return IngestionResponse(
        chunk_count=result.chunk_count,
        document_count=result.document_count,
        warnings=warnings,
    )


@app.post("/ingest/web", response_model=IngestionResponse)
async def ingest_web(request: IngestWebRequest):
    """Ingest documents by crawling the provided URLs."""

    urls = [url.strip() for url in request.urls if url.strip()]
    if not urls:
        raise HTTPException(
            status_code=400, detail="Provide at least one URL to ingest."
        )

    try:
        raw_docs = await run_in_threadpool(load_documents, urls)
    except Exception as exc:
        logger.error("Failed to fetch URLs: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch URLs: {exc}"
        ) from exc

    preprocessed: list[tuple[str, str]] = []
    warnings: list[str] = []
    for text, source in raw_docs:
        normalized_text = (text or "").strip()
        if not normalized_text:
            warnings.append(f"{source}: no content extracted.")
            continue
        loader_issue = _loader_warning(normalized_text)
        if loader_issue:
            warnings.append(f"{source}: {loader_issue} – skipping.")
            continue
        preprocessed.append((normalized_text, source))

    if not preprocessed:
        detail = (
            warnings[0]
            if warnings
            else "No usable content retrieved from the supplied URLs."
        )
        raise HTTPException(status_code=400, detail=detail)

    return await _ingest_documents(preprocessed, warnings)


@app.post("/ingest/pdf", response_model=IngestionResponse)
async def ingest_pdf(files: list[UploadFile] = File(...)):
    """Ingest uploaded PDF files."""

    if not files:
        raise HTTPException(status_code=400, detail="Attach at least one PDF file.")

    preprocessed: list[tuple[str, str]] = []
    warnings: list[str] = []
    for upload in files:
        filename = _sanitize_filename(upload.filename)
        content_type = (upload.content_type or "").lower()
        if content_type and content_type not in ALLOWED_PDF_CONTENT_TYPES:
            warnings.append(
                f"{filename}: unsupported content type '{upload.content_type}'."
            )
            continue

        data = await upload.read()
        if not data:
            warnings.append(f"{filename}: file is empty.")
            continue

        try:
            text = await run_in_threadpool(
                extract_text_from_pdf,
                data,
                filename,
            )
        except Exception as exc:
            logger.warning("Failed to parse PDF %s: %s", filename, exc, exc_info=True)
            warnings.append(f"{filename}: failed to extract text ({exc}).")
            continue

        normalized_text = text.strip()
        if not normalized_text:
            warnings.append(f"{filename}: produced empty text after extraction.")
            continue

        preprocessed.append((normalized_text, f"file://{filename}"))

    if not preprocessed:
        detail = warnings[0] if warnings else "No valid PDFs were processed."
        raise HTTPException(status_code=400, detail=detail)

    return await _ingest_documents(preprocessed, warnings)


@app.post("/chats", response_model=ChatSessionResponse)
async def create_chat(request: CreateChatRequest):
    """Create a new chat session."""
    if chat_db is None:
        raise HTTPException(status_code=500, detail="Chat database not initialized")

    chat_id = create_id()
    title = request.title or "New Chat"

    chat = chat_db.create_chat(chat_id=chat_id, title=title)

    return ChatSessionResponse(
        id=chat.id,
        title=chat.title,
        created_at=chat.created_at.isoformat(),
        updated_at=chat.updated_at.isoformat(),
        message_count=0,
    )


@app.get("/chats", response_model=list[ChatSessionResponse])
async def list_chats():
    """List all chat sessions."""
    if chat_db is None:
        raise HTTPException(status_code=500, detail="Chat database not initialized")

    chats = chat_db.list_chats()

    return [
        ChatSessionResponse(
            id=chat.id,
            title=chat.title,
            created_at=chat.created_at.isoformat(),
            updated_at=chat.updated_at.isoformat(),
            message_count=len(chat.messages),
        )
        for chat in chats
    ]


@app.get("/chats/{chat_id}", response_model=ChatWithMessagesResponse)
async def get_chat(chat_id: str):
    """Get a chat session with all its messages."""
    if chat_db is None:
        raise HTTPException(status_code=500, detail="Chat database not initialized")

    chat = chat_db.get_chat(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail=f"Chat {chat_id} not found")

    from app.models.models import ChatMessageResponse, TextSegment

    messages = [
        ChatMessageResponse(
            id=msg.id,
            role=msg.role,
            content=msg.content,
            segments=(
                [
                    TextSegment(text=seg["text"], source=seg.get("source"))
                    for seg in (msg.segments or [])
                ]
                if msg.segments
                else None
            ),
            created_at=msg.created_at.isoformat(),
        )
        for msg in chat.messages
    ]

    return ChatWithMessagesResponse(
        id=chat.id,
        title=chat.title,
        created_at=chat.created_at.isoformat(),
        updated_at=chat.updated_at.isoformat(),
        messages=messages,
    )


@app.delete("/chats/{chat_id}")
async def delete_chat(chat_id: str):
    """Delete a chat session."""
    if chat_db is None:
        raise HTTPException(status_code=500, detail="Chat database not initialized")

    deleted = chat_db.delete_chat(chat_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Chat {chat_id} not found")

    return {"message": f"Chat {chat_id} deleted successfully"}


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "qdrant_collection": QDRANT_COLLECTION,
    }
