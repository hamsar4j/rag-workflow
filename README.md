# RAG Workflow

## Overview

This project implements a RAG (Retrieval-Augmented Generation) workflow using LangGraph, Gemini Text Embeddings, and Qdrant for vector storage. It incorporates a Jina re-ranking model to improve retrieval quality. A FastAPI backend serves the application, and Streamlit provides a user-friendly chat interface.

![](https://github.com/hamsar4j/rag-workflow/blob/main/assets/rag-workflow.png)

## Setup

#### optional (if you want to use your own local Qdrant server)

1. Start the Qdrant server

```console
docker compose up -d
```

#### run the main RAG app

1. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install the dependencies

```bash
pip install -r requirements.txt
```

3. Update the `.env` file with your API keys

4. Update the `app/config.py` file

5. Run the backend server

```bash
fastapi run app/api.py
```

6. Run the workflow with streamlit ui

```bash
streamlit run app/main.py
```
