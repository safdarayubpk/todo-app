"""SQLModel database models for Task entity."""

from datetime import datetime, timezone
from typing import Optional

from sqlmodel import SQLModel, Field


def utc_now() -> datetime:
    """Return current UTC datetime (naive for PostgreSQL TIMESTAMP)."""
    return datetime.utcnow()


class Task(SQLModel, table=True):
    """Task database model."""

    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(
        min_length=1,
        max_length=255,
        description="Task title",
    )
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Optional task description",
    )
    is_completed: bool = Field(
        default=False,
        description="Completion status",
    )
    # Use string user_id to match Better Auth's user IDs
    user_id: str = Field(
        index=True,
        max_length=255,
        description="Better Auth user ID",
    )
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
