"""Pydantic schemas for API request/response models."""

from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel, Field, field_validator


# Type alias for priority levels
PriorityLevel = Literal["high", "medium", "low"]


def normalize_tags(tags: list[str] | None) -> list[str] | None:
    """Normalize tags: lowercase, trim whitespace, remove empty/duplicates."""
    if tags is None:
        return None
    if not tags:
        return []
    # Normalize: strip whitespace, lowercase, filter empty
    normalized = [tag.strip().lower() for tag in tags if tag and tag.strip()]
    # Remove duplicates while preserving order
    return list(dict.fromkeys(normalized))


class TaskCreate(BaseModel):
    """Schema for creating a new task."""

    title: str = Field(
        min_length=1,
        max_length=255,
        description="Task title",
        examples=["Buy groceries"],
    )
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Optional task description",
        examples=["Milk, bread, eggs"],
    )
    is_completed: bool = Field(
        default=False,
        description="Initial completion status",
    )
    priority: PriorityLevel = Field(
        default="medium",
        description="Task priority: high, medium, or low",
        examples=["high"],
    )
    tags: list[str] = Field(
        default=[],
        description="List of tags for categorization",
        examples=[["work", "urgent"]],
    )

    @field_validator("tags", mode="before")
    @classmethod
    def validate_tags(cls, v: list[str] | None) -> list[str]:
        """Normalize tags to lowercase, remove empty/duplicates."""
        return normalize_tags(v) or []


class TaskUpdate(BaseModel):
    """Schema for updating an existing task."""

    title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Updated title",
    )
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Updated description",
    )
    is_completed: Optional[bool] = Field(
        default=None,
        description="Updated completion status",
    )
    priority: Optional[PriorityLevel] = Field(
        default=None,
        description="Updated priority: high, medium, or low",
    )
    tags: Optional[list[str]] = Field(
        default=None,
        description="Updated list of tags (replaces existing tags)",
    )

    @field_validator("tags", mode="before")
    @classmethod
    def validate_tags(cls, v: list[str] | None) -> list[str] | None:
        """Normalize tags to lowercase, remove empty/duplicates."""
        return normalize_tags(v)


class TaskRead(BaseModel):
    """Schema for reading task data."""

    id: int = Field(description="Task ID", examples=[1])
    title: str = Field(description="Task title", examples=["Buy groceries"])
    description: Optional[str] = Field(
        description="Task description",
        examples=["Milk, bread, eggs"],
    )
    is_completed: bool = Field(
        description="Completion status",
        examples=[False],
    )
    priority: str = Field(
        description="Task priority: high, medium, or low",
        examples=["medium"],
    )
    tags: list[str] = Field(
        description="List of tags",
        examples=[["work", "urgent"]],
    )
    user_id: str = Field(description="Owner user ID (Better Auth)", examples=["abc123"])
    created_at: datetime = Field(
        description="Creation timestamp",
        examples=["2025-12-28T10:30:00Z"],
    )
    updated_at: datetime = Field(
        description="Last update timestamp",
        examples=["2025-12-28T10:30:00Z"],
    )

    model_config = {"from_attributes": True}


class HealthResponse(BaseModel):
    """Schema for health check response."""

    status: str = Field(examples=["healthy"])
    database: str = Field(examples=["connected"])


class ErrorResponse(BaseModel):
    """Schema for error responses."""

    detail: str = Field(description="Error message", examples=["Task not found"])
