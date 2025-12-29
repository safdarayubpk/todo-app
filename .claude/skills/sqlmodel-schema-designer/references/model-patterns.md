# SQLModel Patterns Reference

## Model Inheritance Pattern

### Base/Create/Read/Update Separation

```python
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class TaskBase(SQLModel):
    """Base fields shared across all task schemas."""
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    is_completed: bool = Field(default=False)


class Task(TaskBase, table=True):
    """Database table model."""
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TaskCreate(TaskBase):
    """Schema for creating tasks (input)."""
    pass


class TaskRead(TaskBase):
    """Schema for reading tasks (output)."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime


class TaskUpdate(SQLModel):
    """Schema for updating tasks (all optional)."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    is_completed: Optional[bool] = None
```

## Relationship Patterns

### One-to-Many (User → Tasks)

```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True)
    hashed_password: str

    # Relationship: User has many tasks
    tasks: List["Task"] = Relationship(back_populates="user")


class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    user_id: int = Field(foreign_key="users.id", index=True)

    # Relationship: Task belongs to user
    user: Optional[User] = Relationship(back_populates="tasks")
```

### Many-to-Many (Tasks ↔ Tags)

```python
class TaskTagLink(SQLModel, table=True):
    """Association table for Task-Tag many-to-many."""
    __tablename__ = "task_tag_links"

    task_id: int = Field(foreign_key="tasks.id", primary_key=True)
    tag_id: int = Field(foreign_key="tags.id", primary_key=True)


class Tag(SQLModel, table=True):
    __tablename__ = "tags"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    color: Optional[str] = None

    tasks: List["Task"] = Relationship(
        back_populates="tags",
        link_model=TaskTagLink
    )


class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str

    tags: List[Tag] = Relationship(
        back_populates="tasks",
        link_model=TaskTagLink
    )
```

## Index Patterns

### Single Column Index

```python
class Task(SQLModel, table=True):
    user_id: int = Field(foreign_key="users.id", index=True)
    is_completed: bool = Field(default=False, index=True)
```

### Composite Index (via SQLAlchemy)

```python
from sqlalchemy import Index

class Task(SQLModel, table=True):
    __tablename__ = "tasks"
    __table_args__ = (
        Index("idx_user_completed", "user_id", "is_completed"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    is_completed: bool = Field(default=False)
```

## Field Validation

### Using Pydantic Validators

```python
from pydantic import validator, EmailStr
from sqlmodel import SQLModel, Field


class UserCreate(SQLModel):
    email: str
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8)

    @validator("email")
    def email_valid(cls, v):
        if "@" not in v:
            raise ValueError("Invalid email format")
        return v.lower()

    @validator("password")
    def password_strength(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain uppercase")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain digit")
        return v
```

### Field Constraints

```python
class Task(SQLModel, table=True):
    title: str = Field(
        min_length=1,
        max_length=255,
        description="Task title"
    )
    priority: int = Field(
        default=1,
        ge=1,  # >= 1
        le=5,  # <= 5
        description="Priority 1-5"
    )
    due_date: Optional[datetime] = Field(
        default=None,
        description="Optional due date"
    )
```

## Timestamp Patterns

### Auto Timestamps

```python
from datetime import datetime
from sqlmodel import SQLModel, Field


class TimestampMixin(SQLModel):
    """Mixin for created_at and updated_at timestamps."""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Task(TimestampMixin, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
```

### Update Timestamp on Change

```python
# In your update route
from datetime import datetime

async def update_task(task_id: int, task_in: TaskUpdate, session: AsyncSession):
    task = await session.get(Task, task_id)
    update_data = task_in.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()  # Update timestamp

    for key, value in update_data.items():
        setattr(task, key, value)

    await session.commit()
```

## Soft Delete Pattern

```python
from datetime import datetime
from typing import Optional


class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    deleted_at: Optional[datetime] = Field(default=None, index=True)

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None


# Query only non-deleted
async def get_active_tasks(session: AsyncSession, user_id: int):
    statement = select(Task).where(
        Task.user_id == user_id,
        Task.deleted_at.is_(None)  # Not deleted
    )
    result = await session.exec(statement)
    return result.all()


# Soft delete
async def soft_delete_task(task: Task, session: AsyncSession):
    task.deleted_at = datetime.utcnow()
    await session.commit()
```

## Enum Fields

```python
from enum import Enum
from sqlmodel import SQLModel, Field


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
```

## JSON Fields

```python
from sqlmodel import SQLModel, Field
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from typing import Dict, Any


class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str

    # JSON field for flexible metadata
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSONB)
    )
```

## Migration Considerations

### Adding New Required Field

```python
# Option 1: Add with default, then migrate
class Task(SQLModel, table=True):
    priority: int = Field(default=1)  # Has default

# Option 2: Make nullable first, then backfill
class Task(SQLModel, table=True):
    priority: Optional[int] = Field(default=None)  # Nullable initially
```

### Renaming Fields

```sql
-- In migration file
ALTER TABLE tasks RENAME COLUMN completed TO is_completed;
```

### Adding Index to Existing Table

```sql
-- In migration file
CREATE INDEX CONCURRENTLY idx_tasks_user_id ON tasks(user_id);
```
