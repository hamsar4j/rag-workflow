from typing_extensions import TypedDict
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
