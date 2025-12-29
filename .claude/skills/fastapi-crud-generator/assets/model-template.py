"""
SQLModel Model Template
========================
Copy and customize this template for new resources.

Replace:
- {Resource} with your model name (e.g., Task)
- {resources} with plural lowercase for table name (e.g., tasks)
- Add your specific fields
"""

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class {Resource}Base(SQLModel):
    """
    Base {resource} fields shared across all schemas.

    Add your resource-specific fields here.
    """
    title: str = Field(min_length=1, max_length=255, description="The {resource} title")
    description: Optional[str] = Field(default=None, max_length=1000, description="Optional description")
    # Add more fields as needed


class {Resource}({Resource}Base, table=True):
    """
    {Resource} database model.

    This is the actual table stored in the database.
    """
    __tablename__ = "{resources}"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True, description="Owner user ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")


class {Resource}Create({Resource}Base):
    """
    Schema for creating a new {resource}.

    Inherits all fields from {Resource}Base.
    user_id is set automatically from the authenticated user.
    """
    pass


class {Resource}Read({Resource}Base):
    """
    Schema for reading/returning a {resource}.

    Includes all fields that should be visible in API responses.
    """
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime


class {Resource}Update(SQLModel):
    """
    Schema for updating a {resource}.

    All fields are optional - only provided fields will be updated.
    """
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    # Add more optional fields as needed
