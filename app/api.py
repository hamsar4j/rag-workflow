from fastapi import FastAPI, HTTPException, Depends
from models import QueryRequest
from rag_workflow import build_rag_workflow
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI()


def get_rag_workflow():
    try:
        rag_workflow = build_rag_workflow()
        return rag_workflow
    except Exception as e:
        logging.error(f"Error building RAG workflow: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to initialize RAG workflow: {str(e)}"
        )


@app.post("/query")
async def run_query(request: QueryRequest, rag_workflow=Depends(get_rag_workflow)):
    try:
        state = {"question": request.query}
        response = rag_workflow.invoke(state, config=request.config)
        answer = response["answer"]
        return {"answer": answer}
    except Exception as e:
        logging.error(f"Error during RAG workflow invocation: {e}")
        raise HTTPException(status_code=500, detail=f"RAG workflow failed: {str(e)}")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}
