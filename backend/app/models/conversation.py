"""Conversation model for chat history persistence."""

from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


def utc_now() -> datetime:
    """Return current UTC datetime (naive for PostgreSQL TIMESTAMP)."""
    return datetime.utcnow()


class Conversation(SQLModel, table=True):
    """Represents a chat conversation session.
    
    Each conversation belongs to a single user and contains multiple messages.
    """
    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, max_length=255, description="Better Auth user ID")
    title: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Auto-generated conversation title from first message"
    )
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
