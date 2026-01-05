"""Task CRUD API routes."""

from datetime import datetime
from typing import List, Optional, Literal

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import case, func
from sqlmodel import select

from app.dependencies import CurrentUserId, DbSession
from app.models import Task
from app.schemas import TaskCreate, TaskRead, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("", response_model=List[TaskRead])
async def list_tasks(
    current_user_id: CurrentUserId,
    session: DbSession,
    # Filter parameters
    task_status: Optional[Literal["all", "pending", "completed"]] = Query(
        default="all",
        alias="status",
        description="Filter by completion status",
    ),
    priority: Optional[Literal["all", "high", "medium", "low"]] = Query(
        default="all",
        description="Filter by priority level",
    ),
    tags: Optional[List[str]] = Query(
        default=None,
        description="Filter by tags (tasks must have ALL specified tags)",
    ),
    # Search parameter
    search: Optional[str] = Query(
        default=None,
        description="Search in title and description (case-insensitive)",
    ),
    # Sort parameters
    sort_by: Optional[Literal["created_at", "priority", "title"]] = Query(
        default="created_at",
        description="Field to sort by",
    ),
    sort_dir: Optional[Literal["asc", "desc"]] = Query(
        default="desc",
        description="Sort direction",
    ),
) -> List[Task]:
    """List all tasks for the current user with filtering, search, and sort.

    Returns only tasks owned by the authenticated user (user isolation).
    Supports filtering by status, priority, and tags.
    Supports keyword search in title and description.
    Supports sorting by created_at, priority, or title.
    """
    statement = select(Task).where(Task.user_id == current_user_id)

    # Apply status filter
    if task_status == "pending":
        statement = statement.where(Task.is_completed == False)  # noqa: E712
    elif task_status == "completed":
        statement = statement.where(Task.is_completed == True)  # noqa: E712

    # Apply priority filter
    if priority and priority != "all":
        statement = statement.where(Task.priority == priority)

    # Apply tags filter (AND logic - task must have ALL specified tags)
    if tags:
        # Normalize tags to lowercase
        normalized_tags = [tag.strip().lower() for tag in tags if tag.strip()]
        for tag in normalized_tags:
            statement = statement.where(Task.tags.contains([tag]))

    # Apply search filter (ILIKE on title and description)
    if search and search.strip():
        search_term = f"%{search.strip()}%"
        statement = statement.where(
            (Task.title.ilike(search_term)) | (Task.description.ilike(search_term))
        )

    # Apply sorting
    if sort_by == "priority":
        # Custom sort order: high=1, medium=2, low=3
        priority_order = case(
            (Task.priority == "high", 1),
            (Task.priority == "medium", 2),
            (Task.priority == "low", 3),
            else_=4,
        )
        if sort_dir == "asc":
            statement = statement.order_by(priority_order.asc())
        else:
            statement = statement.order_by(priority_order.desc())
    elif sort_by == "title":
        if sort_dir == "asc":
            statement = statement.order_by(func.lower(Task.title).asc())
        else:
            statement = statement.order_by(func.lower(Task.title).desc())
    else:  # Default: created_at
        if sort_dir == "asc":
            statement = statement.order_by(Task.created_at.asc())
        else:
            statement = statement.order_by(Task.created_at.desc())

    result = await session.execute(statement)
    tasks = result.scalars().all()
    return list(tasks)


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user_id: CurrentUserId,
    session: DbSession,
) -> Task:
    """Create a new task for the current user.

    The task is automatically associated with the authenticated user.
    Supports priority (high/medium/low) and tags.
    """
    task = Task(
        title=task_data.title,
        description=task_data.description,
        is_completed=task_data.is_completed,
        priority=task_data.priority,
        tags=task_data.tags,
        user_id=current_user_id,
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


@router.get("/{task_id}", response_model=TaskRead)
async def get_task(
    task_id: int,
    current_user_id: CurrentUserId,
    session: DbSession,
) -> Task:
    """Get a specific task by ID.

    Returns 404 if task doesn't exist or belongs to another user.
    """
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == current_user_id,
    )
    result = await session.execute(statement)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return task


@router.put("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    current_user_id: CurrentUserId,
    session: DbSession,
) -> Task:
    """Update an existing task.

    Only updates provided fields. Returns 404 if task doesn't exist
    or belongs to another user.
    Supports updating priority and tags.
    """
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == current_user_id,
    )
    result = await session.execute(statement)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Update only provided fields
    update_data = task_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    task.updated_at = datetime.utcnow()

    session.add(task)
    await session.commit()
    await session.refresh(task)

    return task


@router.post("/{task_id}/tags", response_model=TaskRead)
async def add_tag(
    task_id: int,
    tag: str = Query(..., description="Tag to add"),
    current_user_id: CurrentUserId = None,
    session: DbSession = None,
) -> Task:
    """Add a single tag to a task.

    Normalizes tag to lowercase and skips if already present.
    """
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == current_user_id,
    )
    result = await session.execute(statement)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Normalize tag
    normalized_tag = tag.strip().lower()
    if not normalized_tag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tag cannot be empty",
        )

    # Add tag if not already present
    if normalized_tag not in task.tags:
        task.tags = task.tags + [normalized_tag]
        task.updated_at = datetime.utcnow()
        session.add(task)
        await session.commit()
        await session.refresh(task)

    return task


@router.delete("/{task_id}/tags", response_model=TaskRead)
async def remove_tag(
    task_id: int,
    tag: str = Query(..., description="Tag to remove"),
    current_user_id: CurrentUserId = None,
    session: DbSession = None,
) -> Task:
    """Remove a single tag from a task.

    Does nothing if tag doesn't exist on the task.
    """
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == current_user_id,
    )
    result = await session.execute(statement)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Normalize tag
    normalized_tag = tag.strip().lower()

    # Remove tag if present
    if normalized_tag in task.tags:
        task.tags = [t for t in task.tags if t != normalized_tag]
        task.updated_at = datetime.utcnow()
        session.add(task)
        await session.commit()
        await session.refresh(task)

    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    current_user_id: CurrentUserId,
    session: DbSession,
) -> None:
    """Delete a task.

    Returns 404 if task doesn't exist or belongs to another user.
    """
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == current_user_id,
    )
    result = await session.execute(statement)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    await session.delete(task)
    await session.commit()


@router.patch("/{task_id}/toggle", response_model=TaskRead)
async def toggle_task(
    task_id: int,
    current_user_id: CurrentUserId,
    session: DbSession,
) -> Task:
    """Toggle task completion status.

    Returns 404 if task doesn't exist or belongs to another user.
    """
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == current_user_id,
    )
    result = await session.execute(statement)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    task.is_completed = not task.is_completed
    task.updated_at = datetime.utcnow()

    session.add(task)
    await session.commit()
    await session.refresh(task)

    return task
