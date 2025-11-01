from pydantic import BaseModel, Field
from typing_extensions import Any, TypedDict
from dataclasses import dataclass


@dataclass
class SearchResult:
    text: str
    metadata: dict[str, Any]
    score: float


@dataclass
class Document:
    text: str
    metadata: dict[str, Any]


@dataclass
class State(TypedDict):
    question: str
    query: SearchResult
    answer: str
    context: list[Document]
    # history: list[dict]


class QueryRequest(BaseModel):
    query: str
    config: dict[str, Any] = {"configurable": {"thread_id": "abc123"}}


class IngestWebRequest(BaseModel):
    urls: list[str] = Field(..., min_length=1, description="List of URLs to ingest.")


class IngestionResponse(BaseModel):
    chunk_count: int
    document_count: int
    warnings: list[str] = Field(default_factory=list)
