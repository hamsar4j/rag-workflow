from typing_extensions import TypedDict, Any
from pydantic import BaseModel
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
