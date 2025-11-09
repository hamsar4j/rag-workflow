from pydantic import BaseModel, Field
from typing_extensions import Any, NotRequired, TypedDict
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


class State(TypedDict):
    question: str
    query: SearchResult
    answer: str
    context: list[Document]
    model: NotRequired[str]
    # history: list[dict]


class QueryRequest(BaseModel):
    query: str
    chat_id: str | None = None
    model: str | None = None
    config: dict[str, Any] = {"configurable": {"thread_id": "abc123"}}


class IngestWebRequest(BaseModel):
    urls: list[str] = Field(..., min_length=1, description="List of URLs to ingest.")


class IngestionResponse(BaseModel):
    chunk_count: int
    document_count: int
    warnings: list[str] = Field(default_factory=list)


class UpdateModelRequest(BaseModel):
    model: str = Field(..., description="LLM model identifier to activate.")


class TextSegment(BaseModel):
    """A text segment with optional source citation."""

    text: str
    source: str | None = None


class QueryResponse(BaseModel):
    """Structured response with text segments and sources for hover citations."""

    chat_id: str
    segments: list[TextSegment]


class CreateChatRequest(BaseModel):
    """Request to create a new chat session."""

    title: str | None = None


class ChatSessionResponse(BaseModel):
    """Response model for a chat session."""

    id: str
    title: str
    created_at: str
    updated_at: str
    message_count: int = 0

    model_config = {"from_attributes": True}


class ChatMessageResponse(BaseModel):
    """Response model for a chat message."""

    id: str
    role: str
    content: str
    segments: list[TextSegment] | None = None
    created_at: str

    model_config = {"from_attributes": True}


class ChatWithMessagesResponse(BaseModel):
    """Response model for a chat session with its messages."""

    id: str
    title: str
    created_at: str
    updated_at: str
    messages: list[ChatMessageResponse]

    model_config = {"from_attributes": True}
