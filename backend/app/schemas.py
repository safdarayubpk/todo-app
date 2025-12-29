"""Pydantic schemas for API request/response models."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


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
