"""Message model for chat history persistence."""

from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


def utc_now() -> datetime:
    """Return current UTC datetime (naive for PostgreSQL TIMESTAMP)."""
    return datetime.utcnow()


class Message(SQLModel, table=True):
    """Represents a single message in a conversation.
    
    Messages have a role (user or assistant) and content.
    """
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(
        foreign_key="conversations.id",
        index=True,
        description="Reference to parent conversation"
    )
    user_id: str = Field(
        index=True,
        max_length=255,
        description="Redundant for query efficiency"
    )
    role: str = Field(
        max_length=20,
        description="Message role: 'user' or 'assistant'"
    )
    content: str = Field(description="Message text content")
    created_at: datetime = Field(default_factory=utc_now)
