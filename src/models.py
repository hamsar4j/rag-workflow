from typing_extensions import TypedDict, List
from langchain_core.documents import Document

class State(TypedDict):
    question: str
    answer: str
    context: List[Document]
    