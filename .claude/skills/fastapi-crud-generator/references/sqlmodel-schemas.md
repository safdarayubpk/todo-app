# SQLModel Schemas Reference

## Model Inheritance Pattern

Use separate models for database, create, read, and update operations:

```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

# Base model (shared fields)
class TaskBase(SQLModel):
    """Base task fields shared across all schemas."""
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    is_completed: bool = Field(default=False)

# Database model (table=True)
class Task(TaskBase, table=True):
    """Task database model."""
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Create schema (input)
class TaskCreate(TaskBase):
    """Schema for creating a task."""
    pass

# Read schema (output)
class TaskRead(TaskBase):
    """Schema for reading a task."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

# Update schema (partial update)
class TaskUpdate(SQLModel):
    """Schema for updating a task (all fields optional)."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    is_completed: Optional[bool] = None
```

## User Model Example

```python
class UserBase(SQLModel):
    """Base user fields."""
    email: str = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True)

class User(UserBase, table=True):
    """User database model."""
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(UserBase):
    """Schema for user registration."""
    password: str = Field(min_length=8)

class UserRead(UserBase):
    """Schema for reading user data."""
    id: int
    is_active: bool
    created_at: datetime
```

## Relationship Pattern

```python
from sqlmodel import Relationship

class User(UserBase, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True)
    tasks: list["Task"] = Relationship(back_populates="user")

class Task(TaskBase, table=True):
    __tablename__ = "tasks"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    user: Optional[User] = Relationship(back_populates="tasks")
```

## Validation Examples

```python
from pydantic import validator, EmailStr

class UserCreate(SQLModel):
    email: EmailStr
    password: str

    @validator("password")
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain uppercase letter")
        return v
```
