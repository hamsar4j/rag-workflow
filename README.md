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
   - Embeddings: BAAI/bge-base-en-v1.5 via Together AI
   - Generation: openai/gpt-oss-20b via Together AI
   - Re-ranking: jina-reranker-v1-tiny-en via Jina AI (optional)

## Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) for dependency management
- Docker and Docker Compose (for Qdrant vector database)
- API keys for Together AI, Qdrant and optionally Jina AI

## Setup

### 1. Environment Setup

Clone the repository and navigate to the project directory:

```bash
git clone <repository-url>
cd rag-workflow
```

Create a virtual environment using uv:

```bash
uv venv
source .venv/bin/activate
```

Install dependencies:

```bash
uv sync
```

### 2. Configuration

1. Copy the example environment file:

   ```bash
   cp .env.example .env
   ```

2. Update the `.env` file with your API keys:

   ```bash
   # Qdrant configuration
   QDRANT_URL=your_qdrant_url
   QDRANT_API_KEY=your_qdrant_api_key

   # Together AI (LLM, Embeddings)
   TOGETHER_API_KEY=your_together_api_key

   # Jina (Re-ranking, optional)
   JINA_API_KEY=your_jina_api_key
   ```

3. Update configuration in `app/core/config.py` if needed:

   ```python
   # Collection name in Qdrant
   qdrant_collection_name: str = "your_collection_name"
   
   # LLM and embedding models can be changed as needed
   llm_model: str = "openai/gpt-oss-20b"
   embeddings_model: str = "BAAI/bge-base-en-v1.5"
   ```

### 3. Ingest Data

Before querying, you need to ingest data into the vector store. This is done using the `ingest_data.ipynb` Jupyter notebook.

1. Ensure the Qdrant service is running (`docker-compose up -d`).
2. Open the `ingest_data.ipynb` notebook.
3. Run the cells in the notebook sequentially. This will:
   - Create the Qdrant collection.
   - Load web documents from predefined URLs.
   - Split the documents into chunks.
   - Generate embeddings for the chunks.
   - Store the documents and their embeddings in Qdrant.

### 4. Start Services

1. Run the FastAPI backend server:

   ```bash
   fastapi run app/api.py
   ```

2. In a new terminal, run the Streamlit frontend:

   ```bash
   streamlit run app/main.py
   ```

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
  curl -X POST "http://localhost:8000/query" \\
       -H "Content-Type: application/json" \\
       -d '{"query": "Your question here"}'
  ```

- `GET /health` - Health check endpoint

## Project Structure

```
rag-workflow/
├── app/
│   ├── api.py              # FastAPI server
│   ├── main.py             # Streamlit frontend
│   ├── core/               # Configuration
│   ├── db/                 # Database integration (Qdrant)
│   ├── models/             # Data models
│   ├── utils/              # Utility functions
│   ├── web_loader/         # Web document loading
│   └── workflow/           # RAG workflow implementation
├── assets/                 # Images and documentation assets
├── ingest_data.ipynb       # Jupyter notebook for data ingestion
├── .env.example            # Environment variable template
├── docker-compose.yaml     # Qdrant service configuration
├── pyproject.toml          # Project dependencies
└── README.md               # This file
```

## Key Features

- **Retrieval-Augmented Generation (RAG) Pipeline**: Combines semantic search with LLM generation for context-aware answers.
- **Modular Architecture**: Built with FastAPI, Streamlit, LangGraph, and Qdrant for scalability and maintainability.
- **Configurable Components**:
  - Toggle re-ranking functionality via `enable_reranker` in config.
  - Customize LLM and embedding models.
  - Adjust retrieval parameters (top_k, etc.).
- **Web Data Ingestion**: Includes a Jupyter notebook (`ingest_data.ipynb`) for loading and processing web documents into the vector store.

## Troubleshooting

### Common Issues

1. **Connection errors to Qdrant**:
   - Ensure Docker is running
   - Check that Qdrant service is up: `docker-compose ps`
   - Verify QDRANT_URL in your .env file

2. **API key issues**:
   - Confirm all required API keys are set in .env
   - Check that your API keys have appropriate permissions

3. **Slow responses**:
   - First requests may be slower due to model loading
   - Consider enabling re-ranking for better quality results

### Logs

Check logs for debugging information:

- FastAPI logs will show in the terminal where you started the server
- Streamlit logs will show in the terminal where you started the UI

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
