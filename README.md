# RAG Workflow

## Overview

This project is a simple RAG workflow using LangGraph, Ollama Embeddings and Qdrant Vector Database.

![](https://github.com/hamsar4j/rag-workflow/blob/main/assets/rag_retrieval.png)

## Setup

#### optional (if you want to use your own local Qdrant server)

1. Start the Qdrant server

```console
docker compose up -d
```

#### run the main RAG app

2. Install the dependencies

```console
pip install -r requirements.txt
```

3. Run the workflow

```console
python src/main.py
```
