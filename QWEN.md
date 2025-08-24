# Qwen Code Context for `rag-workflow`

This document provides essential context about the `rag-workflow` project for Qwen Code to assist with future interactions.

## Project Overview

This is a Python-based Retrieval-Augmented Generation (RAG) application designed to build AI-powered question-answering systems. It integrates several key technologies:

* **LangGraph**: For orchestrating the RAG workflow stages.
* **Qdrant**: A vector database for efficient semantic search of document embeddings.
* **Together AI & Jina AI**: APIs for generating embeddings, performing language generation, and optional re-ranking.
* **FastAPI**: Backend server exposing REST endpoints for querying the RAG system.
* **Streamlit**: Provides a web-based chat interface for user interaction.

The core data flow involves ingesting documents (currently via a Jupyter notebook `ingest_data.ipynb`), storing them and their embeddings in Qdrant, and then using a multi-stage LangGraph workflow to analyze queries, retrieve relevant context, optionally re-rank it, and finally generate a response based on that context.

## Key Technologies & Dependencies

* **Python Version**: 3.12+
* **Dependency Management**: `uv`
* **Core Libraries**: `fastapi`, `langgraph`, `qdrant-client`, `openai`, `streamlit`, `pydantic-settings`, `unstructured`, `beautifulsoup4`.
* **Environment Management**: Uses `python-dotenv` and `pydantic-settings` for configuration via `.env` file.

## Configuration

Project configuration is managed primarily through environment variables loaded from a `.env` file (based on `.env.example`) and accessed via `pydantic-settings` in `app/core/config.py`.

Key configuration items include:

* `QDRANT_URL`, `QDRANT_API_KEY`: For connecting to the Qdrant vector database.
* `TOGETHER_API_KEY`: API key for Together AI, used for both LLM generation and embeddings.
* `JINA_API_KEY`: API key for Jina AI, used for the optional re-ranking component.
* Model names for LLM (`llm_model`), embeddings (`embeddings_model`), and re-ranker (`reranker_model`).
* `qdrant_collection_name`: The name of the collection in Qdrant to use.
* `enable_reranker`: A flag to enable/disable the Jina AI re-ranking step.

## Project Structure

The project follows a modular structure:

```
rag-workflow/
├── app/                  # Main application code
│   ├── api.py              # FastAPI server setup and endpoints
│   ├── main.py             # Streamlit frontend application
│   ├── core/               # Configuration (config.py)
│   ├── db/                 # Database integration (vector_db.py for Qdrant)
│   ├── models/             # Data models (State, Document, Search, QueryRequest)
│   ├── utils/              # Utility functions (currently empty)
│   ├── web_loader/         # Web document loading (currently empty, ingestion is in notebook)
│   └── workflow/           # RAG workflow implementation (rag_workflow.py, router.py, reranker.py)
├── assets/               # Images (e.g., architecture diagram)
├── ingest_data.ipynb     # Jupyter notebook for data ingestion process
├── .env.example          # Template for environment variables
├── docker-compose.yaml   # Configuration for running Qdrant locally
├── pyproject.toml        # Project dependencies and metadata
└── README.md             # Main project documentation
```

## Building, Running, and Testing

### Prerequisites

* Python 3.12+
* `uv` for managing dependencies.
* Docker and Docker Compose (for running Qdrant).
* API keys for Together AI, Qdrant, and optionally Jina AI.

### Setup

1. **Environment & Dependencies**:

    ```bash
    uv venv
    source .venv/bin/activate
    uv sync
    ```

2. **Configuration**:
    Copy `.env.example` to `.env` and populate it with your API keys and configuration details.
3. **Data Ingestion**:
    Ensure Qdrant is running (`docker-compose up -d`), then execute the steps in `ingest_data.ipynb` to load documents into the vector store.

### Running the Application

1. **Start the FastAPI Backend**:

    ```bash
    fastapi run app/api.py
    ```

    This starts the server, typically on `http://localhost:8000`. It initializes the LangGraph RAG workflow.
2. **Start the Streamlit Frontend** (in a new terminal):

    ```bash
    streamlit run app/main.py
    ```

    This starts the chat UI, typically on `http://localhost:8501`.

### API Access

The backend exposes a REST API:

* `POST /query`: Submit a question. Expects a JSON body like `{"query": "Your question here"}`.
* `GET /health`: Check if the backend is running.

Example `curl` command for querying:

```bash
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "Your question here"}'
```

### Testing

Testing commands are not explicitly defined in the project files (like in `pyproject.toml` scripts). Standard Python testing frameworks like `pytest` would typically be used if tests were present, but no test files or commands are configured in the provided files.

## Development Conventions

* **Configuration**: Centralized in `app/core/config.py` using Pydantic Settings.
* **Data Flow**: Managed by LangGraph in `app/workflow/rag_workflow.py`, defining states and transitions.
* **API Interaction**: Backend API logic is in `app/api.py`, frontend API calls in `app/main.py`.
* **Vector Store**: Interaction with Qdrant is encapsulated in `app/db/vector_db.py`.
* **Models**: Data structures are defined in `app/models/models.py` using Pydantic and dataclasses.
* **Dependencies**: Managed via `pyproject.toml` and `uv.lock` using the `uv` tool.
