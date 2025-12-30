"""Agent tools for task management operations.

Each tool is decorated with @function_tool from the OpenAI Agents SDK.
Tools operate on tasks filtered by user_id for isolation.
"""

from typing import Literal

from agents import function_tool, RunContextWrapper
from sqlmodel import select

from app.models import Task, utc_now
from database import async_session


# Type alias for context - will be defined in agent.py
# Using Any here to avoid circular imports
from typing import Any
AgentContext = Any


async def resolve_task(
    task_identifier: str,
    user_id: str,
) -> Task | list[Task] | None:
    """Resolve a task identifier to one or more tasks.

    Args:
        task_identifier: Task ID (numeric) or partial title match
        user_id: User ID for filtering

    Returns:
        Single Task if unique match, list of Tasks if multiple matches, None if not found
    """
    async with async_session() as session:
        # Try numeric ID first
        if task_identifier.isdigit():
            task_id = int(task_identifier)
            statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
            result = await session.execute(statement)
            task = result.scalar_one_or_none()
            if task:
                return task

        # Fall back to case-insensitive title search
        statement = select(Task).where(
            Task.user_id == user_id,
            Task.title.ilike(f"%{task_identifier}%")  # type: ignore
        )
        result = await session.execute(statement)
        matches = list(result.scalars().all())

        if len(matches) == 0:
            return None
        elif len(matches) == 1:
            return matches[0]
        else:
            return matches


def task_to_dict(task: Task) -> dict:
    """Convert a Task to a dictionary for tool responses."""
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "is_completed": task.is_completed,
    }


@function_tool
async def add_task(
    ctx: RunContextWrapper[AgentContext],
    title: str,
    description: str | None = None
) -> dict:
    """Add a new task to the user's todo list.

    Args:
        ctx: Agent context containing user information
        title: Task title (1-255 characters, required)
        description: Optional task description (max 1000 characters)

    Returns:
        Success response with created task details or error message.
    """
    # Validate title
    if not title or len(title.strip()) == 0:
        return {
            "success": False,
            "error": "Title is required and cannot be empty"
        }

    title = title.strip()
    if len(title) > 255:
        return {
            "success": False,
            "error": "Title must be 255 characters or less"
        }

    if description and len(description) > 1000:
        return {
            "success": False,
            "error": "Description must be 1000 characters or less"
        }

    # Get user_id from context
    user_id = ctx.context.user_id

    async with async_session() as session:
        task = Task(
            title=title,
            description=description.strip() if description else None,
            user_id=user_id,
        )
        session.add(task)
        await session.commit()
        await session.refresh(task)

        return {
            "success": True,
            "task": task_to_dict(task),
            "message": f"Task '{title}' created successfully"
        }


@function_tool
async def list_tasks(
    ctx: RunContextWrapper[AgentContext],
    filter: Literal["all", "completed", "incomplete"] = "all"
) -> dict:
    """List all tasks for the current user.

    Args:
        ctx: Agent context containing user information
        filter: Filter tasks by completion status
                - "all": All tasks (default)
                - "completed": Only completed tasks
                - "incomplete": Only incomplete tasks

    Returns:
        List of tasks matching the filter criteria.
    """
    user_id = ctx.context.user_id

    async with async_session() as session:
        statement = select(Task).where(Task.user_id == user_id)

        if filter == "completed":
            statement = statement.where(Task.is_completed == True)  # noqa: E712
        elif filter == "incomplete":
            statement = statement.where(Task.is_completed == False)  # noqa: E712

        statement = statement.order_by(Task.created_at.desc())  # type: ignore
        result = await session.execute(statement)
        tasks = list(result.scalars().all())

        if len(tasks) == 0:
            return {
                "success": True,
                "tasks": [],
                "count": 0,
                "filter_applied": filter,
                "message": "No tasks found"
            }

        return {
            "success": True,
            "tasks": [task_to_dict(t) for t in tasks],
            "count": len(tasks),
            "filter_applied": filter,
        }


@function_tool
async def mark_complete(
    ctx: RunContextWrapper[AgentContext],
    task_identifier: str,
    completed: bool = True
) -> dict:
    """Mark a task as complete or incomplete.

    Args:
        ctx: Agent context containing user information
        task_identifier: Task ID (number) or partial title match
        completed: True to mark complete, False to mark incomplete

    Returns:
        Updated task details or disambiguation request if multiple matches.
    """
    user_id = ctx.context.user_id
    result = await resolve_task(task_identifier, user_id)

    if result is None:
        return {
            "success": False,
            "error": f"No task found matching '{task_identifier}'",
            "suggestion": "Use list_tasks to see all your tasks"
        }

    if isinstance(result, list):
        return {
            "success": False,
            "error": f"Multiple tasks match '{task_identifier}'. Please be more specific.",
            "matches": [{"id": t.id, "title": t.title} for t in result],
            "hint": "Try using the task ID or a more specific title"
        }

    # Single task found - update it
    task = result
    async with async_session() as session:
        # Re-fetch in this session
        statement = select(Task).where(Task.id == task.id)
        db_result = await session.execute(statement)
        db_task = db_result.scalar_one()

        db_task.is_completed = completed
        db_task.updated_at = utc_now()
        await session.commit()
        await session.refresh(db_task)

        status_text = "complete" if completed else "incomplete"
        return {
            "success": True,
            "task": task_to_dict(db_task),
            "message": f"Task '{db_task.title}' marked as {status_text}"
        }


@function_tool
async def delete_task(
    ctx: RunContextWrapper[AgentContext],
    task_identifier: str,
    confirm: bool = False
) -> dict:
    """Delete a task from the user's todo list.

    Args:
        ctx: Agent context containing user information
        task_identifier: Task ID (number) or partial title match
        confirm: Must be True to actually delete (safety measure)

    Returns:
        Confirmation request or deletion result.
    """
    user_id = ctx.context.user_id
    result = await resolve_task(task_identifier, user_id)

    if result is None:
        return {
            "success": False,
            "error": f"No task found matching '{task_identifier}'",
            "suggestion": "Use list_tasks to see all your tasks"
        }

    if isinstance(result, list):
        return {
            "success": False,
            "error": f"Multiple tasks match '{task_identifier}'. Please be more specific.",
            "matches": [{"id": t.id, "title": t.title} for t in result],
            "hint": "Try using the task ID or a more specific title"
        }

    task = result

    # If not confirmed, return confirmation request
    if not confirm:
        return {
            "success": False,
            "requires_confirmation": True,
            "task_to_delete": {"id": task.id, "title": task.title},
            "message": f"Are you sure you want to delete '{task.title}'? This action cannot be undone."
        }

    # Confirmed - delete the task
    async with async_session() as session:
        statement = select(Task).where(Task.id == task.id)
        db_result = await session.execute(statement)
        db_task = db_result.scalar_one()

        deleted_info = {"id": db_task.id, "title": db_task.title}
        await session.delete(db_task)
        await session.commit()

        return {
            "success": True,
            "deleted_task": deleted_info,
            "message": f"Task '{deleted_info['title']}' has been deleted"
        }


@function_tool
async def update_task(
    ctx: RunContextWrapper[AgentContext],
    task_identifier: str,
    new_title: str | None = None,
    new_description: str | None = None
) -> dict:
    """Update a task's title or description.

    Args:
        ctx: Agent context containing user information
        task_identifier: Task ID (number) or partial title match
        new_title: New title for the task (optional)
        new_description: New description for the task (optional)

    Returns:
        Updated task details or error if task not found.
    """
    # Validate inputs
    if new_title is None and new_description is None:
        return {
            "success": False,
            "error": "No changes specified. Provide new_title or new_description."
        }

    if new_title is not None:
        new_title = new_title.strip()
        if len(new_title) == 0:
            return {
                "success": False,
                "error": "Title cannot be empty"
            }
        if len(new_title) > 255:
            return {
                "success": False,
                "error": "Title must be 255 characters or less"
            }

    if new_description is not None and len(new_description) > 1000:
        return {
            "success": False,
            "error": "Description must be 1000 characters or less"
        }

    user_id = ctx.context.user_id
    result = await resolve_task(task_identifier, user_id)

    if result is None:
        return {
            "success": False,
            "error": f"No task found matching '{task_identifier}'",
            "suggestion": "Use list_tasks to see all your tasks"
        }

    if isinstance(result, list):
        return {
            "success": False,
            "error": f"Multiple tasks match '{task_identifier}'. Please be more specific.",
            "matches": [{"id": t.id, "title": t.title} for t in result],
            "hint": "Try using the task ID or a more specific title"
        }

    task = result
    changes = {}

    async with async_session() as session:
        statement = select(Task).where(Task.id == task.id)
        db_result = await session.execute(statement)
        db_task = db_result.scalar_one()

        if new_title is not None and new_title != db_task.title:
            changes["title"] = {"old": db_task.title, "new": new_title}
            db_task.title = new_title

        if new_description is not None and new_description != db_task.description:
            changes["description"] = {"old": db_task.description, "new": new_description}
            db_task.description = new_description.strip() if new_description else None

        if not changes:
            return {
                "success": True,
                "task": task_to_dict(db_task),
                "message": "No changes were needed",
                "changes": {}
            }

        db_task.updated_at = utc_now()
        await session.commit()
        await session.refresh(db_task)

        return {
            "success": True,
            "task": task_to_dict(db_task),
            "changes": changes,
            "message": "Task updated successfully"
        }
