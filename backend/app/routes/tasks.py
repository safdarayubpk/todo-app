"""Task CRUD API routes."""

from datetime import datetime
from typing import List

from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.dependencies import CurrentUserId, DbSession
from app.models import Task
from app.schemas import TaskCreate, TaskRead, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("", response_model=List[TaskRead])
async def list_tasks(
    current_user_id: CurrentUserId,
    session: DbSession,
) -> List[Task]:
    """List all tasks for the current user.

    Returns only tasks owned by the authenticated user (user isolation).
    """
    statement = select(Task).where(Task.user_id == current_user_id)
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
    """
    task = Task(
        title=task_data.title,
        description=task_data.description,
        is_completed=task_data.is_completed,
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
