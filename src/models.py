from typing_extensions import TypedDict, Annotated, List
from langchain_core.documents import Document

class Search(TypedDict):
    query: Annotated[str, ...,"The user's search query"]
    
class State(TypedDict):
    question: str
    query: Search
    answer: str
    context: List[Document]
    