# RAG Workflow

## Overview

This project is a simple RAG workflow using LangGraph, Ollama Embeddings and Qdrant Vector Database.
Streamlit is used to create a simple chat interface.

![](https://github.com/hamsar4j/rag-workflow/blob/main/assets/rag_retrieval.png)

## Setup

#### optional (if you want to use your own local Qdrant server)

1. Start the Qdrant server

```console
docker compose up -d
```

#### run the main RAG app

1. Create a virtual environment

```console
python -m venv .venv
source .venv/bin/activate
```

2. Install the dependencies

```console
pip install -r requirements.txt
```

3. Run the workflow

```console
streamlit run app/main.py
```
