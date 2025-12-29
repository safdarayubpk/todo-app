# Data Model: Full-Stack Multi-User Web Todo Application

**Feature Branch**: `002-fullstack-web-app`
**Created**: 2025-12-28
**Status**: Complete

## Entity Overview

This document defines the data models for Phase II, extending Phase I's Task model with user ownership and authentication.

---

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                          users                               │
├─────────────────────────────────────────────────────────────┤
│ id          : INTEGER (PK, auto-increment)                  │
│ email       : VARCHAR(255) (UNIQUE, NOT NULL, indexed)      │
│ username    : VARCHAR(50) (UNIQUE, NOT NULL, indexed)       │
│ hashed_pass : VARCHAR(255) (NOT NULL)                       │
│ is_active   : BOOLEAN (DEFAULT TRUE)                        │
│ created_at  : TIMESTAMP (DEFAULT NOW)                       │
│ updated_at  : TIMESTAMP (DEFAULT NOW)                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ 1:N
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                          tasks                               │
├─────────────────────────────────────────────────────────────┤
│ id          : INTEGER (PK, auto-increment)                  │
│ title       : VARCHAR(255) (NOT NULL)                       │
│ description : VARCHAR(1000) (NULLABLE)                      │
│ is_completed: BOOLEAN (DEFAULT FALSE)                       │
│ user_id     : INTEGER (FK → users.id, indexed, NOT NULL)    │
│ created_at  : TIMESTAMP (DEFAULT NOW)                       │
│ updated_at  : TIMESTAMP (DEFAULT NOW)                       │
└─────────────────────────────────────────────────────────────┘
```

---

## Entity: User

### Description
Represents a registered user who can authenticate and manage their own tasks.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | INTEGER | PK, auto-increment | Unique identifier |
| email | VARCHAR(255) | UNIQUE, NOT NULL, indexed | User's email for login |
| username | VARCHAR(50) | UNIQUE, NOT NULL, indexed | Display name (3-50 chars) |
| hashed_password | VARCHAR(255) | NOT NULL | Bcrypt-hashed password |
| is_active | BOOLEAN | DEFAULT TRUE | Account active status |
| created_at | TIMESTAMP | DEFAULT NOW | Account creation time |
| updated_at | TIMESTAMP | DEFAULT NOW | Last modification time |

### Validation Rules
- **email**: Valid email format, case-insensitive unique check
- **username**: 3-50 alphanumeric characters, underscores allowed
- **password** (input): Minimum 8 characters

### Relationships
- **tasks**: One-to-Many → User owns zero or more Tasks

---

## Entity: Task

### Description
Represents a todo item owned by a specific user.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | INTEGER | PK, auto-increment | Unique identifier |
| title | VARCHAR(255) | NOT NULL, min 1 char | Task title |
| description | VARCHAR(1000) | NULLABLE | Optional details |
| is_completed | BOOLEAN | DEFAULT FALSE | Completion status |
| user_id | INTEGER | FK, NOT NULL, indexed | Owner reference |
| created_at | TIMESTAMP | DEFAULT NOW | Creation time |
| updated_at | TIMESTAMP | DEFAULT NOW | Last modification time |

### Validation Rules
- **title**: 1-255 characters, required
- **description**: 0-1000 characters, optional
- **user_id**: Must reference existing active user

### Relationships
- **user**: Many-to-One → Each Task belongs to exactly one User

### State Transitions
```
[Created] ─────────────────────────────────────────────────────►
     │                                                          │
     ▼                                                          ▼
is_completed: false ◄────────────── toggle ──────────────► is_completed: true
     │                                                          │
     ▼                                                          ▼
  [Updated] ◄─────────────────────────────────────────────────►
     │                                                          │
     ▼                                                          ▼
 [Deleted] ─────────────────────────────────────────────────────
```

---

## SQLModel Implementation

### User Model

```python
from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

class UserBase(SQLModel):
    """Base fields for User."""
    email: str = Field(
        unique=True,
        index=True,
        max_length=255,
        description="User email address"
    )
    username: str = Field(
        unique=True,
        index=True,
        min_length=3,
        max_length=50,
        description="Unique username"
    )

class User(UserBase, table=True):
    """User database model."""
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str = Field(description="Bcrypt hashed password")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship
    tasks: List["Task"] = Relationship(back_populates="user")

class UserCreate(UserBase):
    """Schema for creating a user."""
    password: str = Field(min_length=8, max_length=100)

class UserRead(UserBase):
    """Schema for reading user data (public)."""
    id: int
    is_active: bool
    created_at: datetime
```

### Task Model

```python
class TaskBase(SQLModel):
    """Base fields for Task."""
    title: str = Field(
        min_length=1,
        max_length=255,
        description="Task title"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Optional description"
    )
    is_completed: bool = Field(
        default=False,
        description="Completion status"
    )

class Task(TaskBase, table=True):
    """Task database model."""
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(
        foreign_key="users.id",
        index=True,
        description="Owner user ID"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship
    user: Optional[User] = Relationship(back_populates="tasks")

class TaskCreate(TaskBase):
    """Schema for creating a task (user_id set from auth)."""
    pass

class TaskUpdate(SQLModel):
    """Schema for updating a task (all optional)."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    is_completed: Optional[bool] = None

class TaskRead(TaskBase):
    """Schema for reading task data."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
```

---

## Database Indexes

| Table | Index | Columns | Purpose |
|-------|-------|---------|---------|
| users | idx_users_email | email | Fast login lookup |
| users | idx_users_username | username | Fast username lookup |
| tasks | idx_tasks_user_id | user_id | Fast user task filtering |

---

## Migration Notes

### From Phase I
- Phase I `Task` dataclass is **not migrated** to database
- New persistent `Task` model includes `user_id` field
- Existing Phase I console app continues to use in-memory storage

### Initial Schema Creation
```sql
-- Executed by SQLModel.metadata.create_all()

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    username VARCHAR(50) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description VARCHAR(1000),
    is_completed BOOLEAN DEFAULT FALSE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
```
