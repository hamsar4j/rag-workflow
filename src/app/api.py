import logging
import os
import time
from contextlib import asynccontextmanager
from typing import Iterable, Sequence

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from starlette.concurrency import run_in_threadpool

from app.core.config import settings
from app.ingestion.ingest import load_documents
from app.ingestion.pdf_loader.pdf_to_text import extract_text_from_pdf
from app.ingestion.service import ingest_text_documents
from app.models.models import (
    IngestionResponse,
    IngestWebRequest,
    QueryRequest,
    UpdateModelRequest,
)
from app.workflow import build_rag_workflow

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

rag_workflow = None
ALLOWED_PDF_CONTENT_TYPES = {"application/pdf", "application/octet-stream"}
QDRANT_COLLECTION = settings.qdrant_collection_name


@asynccontextmanager
async def lifespan(app: FastAPI):
    global rag_workflow
    try:
        rag_workflow = build_rag_workflow()
        logger.info("RAG workflow initialized successfully")
        yield
    except Exception as e:
        logger.error(f"Error initializing RAG workflow: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to initialize RAG workflow: {str(e)}"
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


@app.post("/query")
async def run_query(request: QueryRequest):
    """Process a query request through the RAG workflow."""
    # Log the incoming request
    logger.info(f"Processing query: {request.query}")

    if rag_workflow is None:
        logger.error("RAG workflow not initialized")
        raise HTTPException(status_code=500, detail="RAG workflow not initialized")

    try:
        selected_model = request.model or settings.llm_model
        if request.model and request.model != settings.llm_model:
            os.environ["LLM_MODEL"] = request.model
            settings.llm_model = request.model

        state = {"question": request.query, "model": selected_model}
        config = request.config if request.config else {}

        # Process the query through the RAG workflow
        response = rag_workflow.invoke(state, config=config)
        answer = response["answer"]

        # Log successful response
        logger.info(f"Successfully processed query: {request.query}")

        return {"answer": answer}
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


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "qdrant_collection": QDRANT_COLLECTION,
    }
