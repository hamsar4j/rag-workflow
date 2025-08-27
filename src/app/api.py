from fastapi import FastAPI, HTTPException, Request
from contextlib import asynccontextmanager
from app.models.models import QueryRequest
from app.workflow import build_rag_workflow
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

rag_workflow = None


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
        state = {"question": request.query}
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


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}
