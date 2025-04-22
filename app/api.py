from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from app.models.models import QueryRequest
from app.workflow.rag_workflow import build_rag_workflow
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

rag_workflow = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global rag_workflow
    try:
        rag_workflow = build_rag_workflow()
        logging.info("RAG workflow initialized successfully")
        yield
    except Exception as e:
        logging.error(f"Error initializing RAG workflow: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to initialize RAG workflow: {str(e)}"
        )


app = FastAPI(lifespan=lifespan)


@app.post("/query")
async def run_query(request: QueryRequest):
    if rag_workflow is None:
        raise HTTPException(status_code=500, detail="RAG workflow not initialized")
    try:
        state = {"question": request.query}
        config = request.config if request.config else {}
        response = rag_workflow.invoke(state, config=config)
        answer = response["answer"]
        return {"answer": answer}
    except Exception as e:
        logging.error(f"Error during RAG workflow invocation: {e}")
        raise HTTPException(status_code=500, detail=f"RAG workflow failed: {str(e)}")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}
