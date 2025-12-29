# Database Setup Reference

## Async Engine Configuration

### Basic Async Setup

```python
# database.py
import os
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://user:password@localhost/todoapp"
)

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Set to False in production
    future=True,
)

# Session factory
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncSession:
    """Dependency for FastAPI routes."""
    async with async_session() as session:
        yield session


async def create_db_and_tables():
    """Create all tables (call on startup)."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
```

### FastAPI Integration

```python
# main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await create_db_and_tables()
    yield
    # Shutdown (cleanup if needed)


app = FastAPI(lifespan=lifespan)
```

## Neon PostgreSQL Configuration

### Connection String Format

```bash
# .env
DATABASE_URL=postgresql+asyncpg://username:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require
```

### Neon-Specific Settings

```python
import os
from sqlalchemy.ext.asyncio import create_async_engine

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,  # Check connection health
    pool_size=5,         # Connection pool size
    max_overflow=10,     # Max overflow connections
    connect_args={
        "ssl": "require",           # Require SSL for Neon
        "server_settings": {
            "application_name": "todoapp"
        }
    }
)
```

### Connection Pooling for Serverless

```python
# For serverless environments (Vercel, etc.)
engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=1,        # Minimal pool for serverless
    max_overflow=2,
    pool_recycle=300,   # Recycle connections after 5 min
)
```

## Session Patterns

### Basic CRUD Operations

```python
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession


async def create_task(session: AsyncSession, task: TaskCreate, user_id: int) -> Task:
    """Create a new task."""
    db_task = Task(**task.model_dump(), user_id=user_id)
    session.add(db_task)
    await session.commit()
    await session.refresh(db_task)
    return db_task


async def get_task(session: AsyncSession, task_id: int) -> Task | None:
    """Get task by ID."""
    return await session.get(Task, task_id)


async def get_user_tasks(session: AsyncSession, user_id: int) -> list[Task]:
    """Get all tasks for a user."""
    statement = select(Task).where(Task.user_id == user_id)
    result = await session.exec(statement)
    return result.all()


async def update_task(
    session: AsyncSession,
    task: Task,
    task_update: TaskUpdate
) -> Task:
    """Update a task."""
    update_data = task_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


async def delete_task(session: AsyncSession, task: Task) -> None:
    """Delete a task."""
    await session.delete(task)
    await session.commit()
```

### Filtering and Ordering

```python
from sqlmodel import select, col


async def get_filtered_tasks(
    session: AsyncSession,
    user_id: int,
    is_completed: bool | None = None,
    search: str | None = None,
    limit: int = 10,
    offset: int = 0,
) -> list[Task]:
    """Get filtered and paginated tasks."""
    statement = select(Task).where(Task.user_id == user_id)

    if is_completed is not None:
        statement = statement.where(Task.is_completed == is_completed)

    if search:
        statement = statement.where(
            col(Task.title).ilike(f"%{search}%")
        )

    statement = statement.order_by(Task.created_at.desc())
    statement = statement.offset(offset).limit(limit)

    result = await session.exec(statement)
    return result.all()
```

### Eager Loading Relationships

```python
from sqlmodel import select
from sqlalchemy.orm import selectinload


async def get_user_with_tasks(session: AsyncSession, user_id: int) -> User | None:
    """Get user with eagerly loaded tasks."""
    statement = (
        select(User)
        .where(User.id == user_id)
        .options(selectinload(User.tasks))
    )
    result = await session.exec(statement)
    return result.first()
```

## Transaction Patterns

### Explicit Transaction

```python
async def transfer_task(
    session: AsyncSession,
    task_id: int,
    from_user_id: int,
    to_user_id: int
) -> Task:
    """Transfer task ownership (atomic operation)."""
    async with session.begin():
        task = await session.get(Task, task_id)
        if task.user_id != from_user_id:
            raise ValueError("Not task owner")

        task.user_id = to_user_id
        session.add(task)
        # Commit happens automatically at end of `begin()` block
    return task
```

### Rollback on Error

```python
async def bulk_create_tasks(
    session: AsyncSession,
    tasks: list[TaskCreate],
    user_id: int
) -> list[Task]:
    """Create multiple tasks atomically."""
    try:
        db_tasks = []
        for task in tasks:
            db_task = Task(**task.model_dump(), user_id=user_id)
            session.add(db_task)
            db_tasks.append(db_task)

        await session.commit()

        for task in db_tasks:
            await session.refresh(task)

        return db_tasks
    except Exception:
        await session.rollback()
        raise
```

## Environment Configuration

### Development

```bash
# .env.development
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/todoapp_dev
```

### Production (Neon)

```bash
# .env.production
DATABASE_URL=postgresql+asyncpg://user:pass@ep-xxx.neon.tech/todoapp?sslmode=require
```

### Testing

```bash
# .env.test
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/todoapp_test
```

## Health Check

```python
from sqlalchemy import text


async def check_db_health(session: AsyncSession) -> bool:
    """Check database connectivity."""
    try:
        await session.exec(text("SELECT 1"))
        return True
    except Exception:
        return False


# FastAPI endpoint
@app.get("/health")
async def health_check(session: AsyncSession = Depends(get_session)):
    db_healthy = await check_db_health(session)
    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "database": "connected" if db_healthy else "disconnected"
    }
```
