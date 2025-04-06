from typing_extensions import TypedDict, Any
from pydantic import BaseModel
from dataclasses import dataclass


@dataclass
class Search:
    text: str
    metadata: dict
    score: float


@dataclass
class Document:
    text: str
    metadata: dict = None


@dataclass
class State(TypedDict):
    question: str
    query: Search
    answer: str
    context: list[Document]
    # history: list[dict]


class QueryRequest(BaseModel):
    query: str
    config: dict[str, Any] = {"configurable": {"thread_id": "abc123"}}
