# Data Model: Task Organization Features

**Feature**: 004-task-organization-features
**Date**: 2026-01-05

## Entity: Task (Extended)

### Current Schema

```
tasks
├── id: INTEGER PRIMARY KEY
├── title: VARCHAR(255) NOT NULL
├── description: VARCHAR(1000)
├── is_completed: BOOLEAN DEFAULT FALSE
├── user_id: VARCHAR(255) NOT NULL (indexed)
├── created_at: TIMESTAMP
└── updated_at: TIMESTAMP
```

### Extended Schema

```
tasks
├── id: INTEGER PRIMARY KEY
├── title: VARCHAR(255) NOT NULL
├── description: VARCHAR(1000)
├── is_completed: BOOLEAN DEFAULT FALSE
├── priority: VARCHAR(10) DEFAULT 'medium' NOT NULL  # NEW
├── tags: VARCHAR[] DEFAULT '{}'  NOT NULL            # NEW (PostgreSQL array)
├── user_id: VARCHAR(255) NOT NULL (indexed)
├── created_at: TIMESTAMP
└── updated_at: TIMESTAMP
```

### New Fields

| Field | Type | Default | Constraints | Description |
|-------|------|---------|-------------|-------------|
| priority | VARCHAR(10) | "medium" | NOT NULL, CHECK(priority IN ('high', 'medium', 'low')) | Task importance level |
| tags | VARCHAR[] | {} | NOT NULL | Array of lowercase tag strings |

### Indexes

| Index Name | Column(s) | Type | Purpose |
|------------|-----------|------|---------|
| idx_tasks_user_id | user_id | B-tree | Existing: user isolation |
| idx_tasks_priority | priority | B-tree | Filter by priority |
| idx_tasks_tags | tags | GIN | Filter by tag membership |
| idx_tasks_title_search | title | GIN (pg_trgm) | Optional: faster ILIKE searches |

### Validation Rules

#### Priority
- Must be one of: "high", "medium", "low"
- Case-sensitive (lowercase only)
- Required (defaults to "medium" if not provided)

#### Tags
- Array of strings
- Each tag: 1-50 characters
- Maximum 20 tags per task
- Normalized to lowercase before storage
- Whitespace trimmed
- Empty strings filtered out
- Duplicates removed

### State Transitions

No new state machines. Existing `is_completed` toggle behavior unchanged.

## Entity: Filter State (Client-Side Only)

Not persisted. Represents current UI filter/sort configuration.

```typescript
interface FilterState {
  status: "all" | "pending" | "completed";
  priority: "all" | "high" | "medium" | "low";
  tags: string[];  // Selected tag filters (AND logic)
  search: string;  // Keyword search query
  sortBy: "created_at" | "priority" | "title";
  sortDir: "asc" | "desc";
}
```

### Default Values

```typescript
const defaultFilters: FilterState = {
  status: "all",
  priority: "all",
  tags: [],
  search: "",
  sortBy: "created_at",
  sortDir: "desc",
};
```

## SQLModel Implementation

### Task Model (Python)

```python
from typing import Optional, Literal
from datetime import datetime
from sqlalchemy import ARRAY, String, Column
from sqlmodel import SQLModel, Field

PriorityLevel = Literal["high", "medium", "low"]

class Task(SQLModel, table=True):
    """Task database model with organization features."""

    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    is_completed: bool = Field(default=False)
    priority: str = Field(
        default="medium",
        max_length=10,
        description="Priority: high, medium, low"
    )
    tags: list[str] = Field(
        default=[],
        sa_column=Column(ARRAY(String), nullable=False, server_default="{}")
    )
    user_id: str = Field(index=True, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### Pydantic Schemas

```python
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator

PriorityLevel = Literal["high", "medium", "low"]

class TaskCreate(BaseModel):
    """Schema for creating a new task."""
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    is_completed: bool = Field(default=False)
    priority: PriorityLevel = Field(default="medium")
    tags: list[str] = Field(default=[])

    @field_validator("tags", mode="before")
    @classmethod
    def normalize_tags(cls, v: list[str]) -> list[str]:
        """Normalize tags to lowercase, remove empty/duplicates."""
        if not v:
            return []
        normalized = [tag.strip().lower() for tag in v if tag.strip()]
        return list(dict.fromkeys(normalized))  # Preserve order, remove dupes

class TaskUpdate(BaseModel):
    """Schema for updating an existing task."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    is_completed: Optional[bool] = Field(default=None)
    priority: Optional[PriorityLevel] = Field(default=None)
    tags: Optional[list[str]] = Field(default=None)

    @field_validator("tags", mode="before")
    @classmethod
    def normalize_tags(cls, v: Optional[list[str]]) -> Optional[list[str]]:
        if v is None:
            return None
        normalized = [tag.strip().lower() for tag in v if tag.strip()]
        return list(dict.fromkeys(normalized))

class TaskRead(BaseModel):
    """Schema for reading task data."""
    id: int
    title: str
    description: Optional[str]
    is_completed: bool
    priority: str
    tags: list[str]
    user_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
```

## Migration Script

```sql
-- Migration: Add priority and tags columns to tasks table
-- Backward compatible: existing tasks get default values

-- Add priority column
ALTER TABLE tasks
ADD COLUMN IF NOT EXISTS priority VARCHAR(10) DEFAULT 'medium' NOT NULL;

-- Add constraint for valid priority values
ALTER TABLE tasks
ADD CONSTRAINT chk_tasks_priority
CHECK (priority IN ('high', 'medium', 'low'));

-- Add tags column (PostgreSQL array)
ALTER TABLE tasks
ADD COLUMN IF NOT EXISTS tags VARCHAR[] DEFAULT '{}' NOT NULL;

-- Create index for priority filtering
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks (priority);

-- Create GIN index for tag array queries (ANY/contains)
CREATE INDEX IF NOT EXISTS idx_tasks_tags ON tasks USING GIN (tags);

-- Optional: Enable pg_trgm extension for faster ILIKE searches
-- CREATE EXTENSION IF NOT EXISTS pg_trgm;
-- CREATE INDEX IF NOT EXISTS idx_tasks_title_trgm ON tasks USING GIN (title gin_trgm_ops);
```

## Relationships

No new relationships introduced. Task remains a standalone entity associated with user via `user_id` foreign key pattern.

```
User (Better Auth) 1:N Task
```
