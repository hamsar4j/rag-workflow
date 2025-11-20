"""Database models and operations for chat persistence."""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    ForeignKey,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import (
    Session,
    declarative_base,
    joinedload,
    relationship,
    sessionmaker,
)

logger = logging.getLogger(__name__)

Base = declarative_base()


class ChatSession(Base):
    """Model for chat sessions/conversations."""

    __tablename__ = "chat_sessions"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.now, onupdate=datetime.now, nullable=False
    )

    # Relationship to messages
    messages = relationship(
        "ChatMessage",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at",
    )


class ChatMessage(Base):
    """Model for individual chat messages."""

    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True)
    chat_id = Column(String, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String, nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    segments = Column(JSON, nullable=True)  # Store TextSegment list as JSON
    created_at = Column(DateTime, default=datetime.now, nullable=False)

    # Relationship to session
    session = relationship("ChatSession", back_populates="messages")


class ChatDB:
    """Database handler for chat operations."""

    def __init__(self, db_path: str = "data/chats.db"):
        """Initialize database connection."""
        # Create data directory if it doesn't exist
        db_file = Path(db_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)

        # Create engine and session
        self.engine = create_engine(f"sqlite:///{db_path}", echo=False)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)

        logger.info(f"Chat database initialized at {db_path}")

    def get_session(self) -> Session:
        """Get a new database session."""
        return self.SessionLocal()

    def create_chat(self, chat_id: str, title: str) -> ChatSession:
        """Create a new chat session."""
        session = self.get_session()
        try:
            chat = ChatSession(id=chat_id, title=title)
            session.add(chat)
            session.commit()
            session.refresh(chat)
            logger.info(f"Created chat session: {chat_id}")
            return chat
        finally:
            session.close()

    def get_chat(self, chat_id: str) -> ChatSession | None:
        """Get a chat session by ID with messages eagerly loaded."""
        session = self.get_session()
        try:
            chat = (
                session.query(ChatSession)
                .options(joinedload(ChatSession.messages))
                .filter(ChatSession.id == chat_id)
                .first()
            )
            if chat:
                # Make the instance detached but with all data loaded
                session.expunge(chat)
            return chat
        finally:
            session.close()

    def list_chats(self, limit: int = 50) -> list[ChatSession]:
        """List all chat sessions, ordered by most recent with messages eagerly loaded."""
        session = self.get_session()
        try:
            chats = (
                session.query(ChatSession)
                .options(joinedload(ChatSession.messages))
                .order_by(ChatSession.updated_at.desc())
                .limit(limit)
                .all()
            )
            # Expunge all chats to make them detached but with data loaded
            for chat in chats:
                session.expunge(chat)
            return chats
        finally:
            session.close()

    def delete_chat(self, chat_id: str) -> bool:
        """Delete a chat session and all its messages."""
        session = self.get_session()
        try:
            chat = session.query(ChatSession).filter(ChatSession.id == chat_id).first()
            if chat:
                session.delete(chat)
                session.commit()
                logger.info(f"Deleted chat session: {chat_id}")
                return True
            return False
        finally:
            session.close()

    def add_message(
        self,
        message_id: str,
        chat_id: str,
        role: str,
        content: str,
        segments: list[dict[str, Any]] | None = None,
    ) -> ChatMessage:
        """Add a message to a chat session."""
        session = self.get_session()
        try:
            message = ChatMessage(
                id=message_id,
                chat_id=chat_id,
                role=role,
                content=content,
                segments=segments,
            )
            session.add(message)

            # Update the chat's updated_at timestamp
            chat = session.query(ChatSession).filter(ChatSession.id == chat_id).first()
            if chat:
                chat.updated_at = datetime.now()

            session.commit()
            session.refresh(message)
            logger.info(f"Added message to chat {chat_id}")
            return message
        finally:
            session.close()

    def get_messages(self, chat_id: str) -> list[ChatMessage]:
        """Get all messages for a chat session."""
        session = self.get_session()
        try:
            return (
                session.query(ChatMessage)
                .filter(ChatMessage.chat_id == chat_id)
                .order_by(ChatMessage.created_at)
                .all()
            )
        finally:
            session.close()
