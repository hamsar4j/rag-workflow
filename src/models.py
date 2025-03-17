from typing_extensions import TypedDict, List
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
    context: List[Document]
