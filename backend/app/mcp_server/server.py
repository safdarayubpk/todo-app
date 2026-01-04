"""MCP Server for Todo Task Operations.

This module implements the MCP Server using FastMCP with stdio transport.
It exposes 5 tools for task management: add_task, list_tasks, complete_task,
delete_task, and update_task.

Each tool requires user_id as the first parameter to enforce data isolation.
"""

from mcp.server.fastmcp import FastMCP
from sqlmodel import select

# Import models and database helper
import sys
import os

# Add parent directories to path for imports when running as subprocess
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from app.models import Task, utc_now
from app.mcp_server.db import get_sync_session

# Initialize MCP Server
mcp = FastMCP("Todo MCP Server")


@mcp.tool()
def add_task(user_id: str, title: str, description: str | None = None) -> dict:
    """Add a new task to the user's todo list.

    Args:
        user_id: The authenticated user's ID (required for isolation)
        title: Task title (1-255 characters, required)
        description: Optional task description (max 1000 characters)

    Returns:
        Dict with task_id, status, and title of the created task
    """
    # Validate inputs
    if not user_id or len(user_id.strip()) == 0:
        return {"error": "user_id is required"}

    if not title or len(title.strip()) == 0:
        return {"error": "Title is required and cannot be empty"}

    title = title.strip()
    if len(title) > 255:
        return {"error": "Title must be 255 characters or less"}

    if description and len(description) > 1000:
        return {"error": "Description must be 1000 characters or less"}

    try:
        with get_sync_session() as session:
            task = Task(
                title=title,
                description=description.strip() if description else None,
                user_id=user_id.strip(),
            )
            session.add(task)
            session.flush()  # Get the ID
            session.refresh(task)
            session.commit()  # Commit the transaction

            return {
                "task_id": task.id,
                "status": "created",
                "title": task.title,
            }
    except Exception as e:
        return {"error": f"Database error: Unable to create task. Please try again. ({type(e).__name__})"}


@mcp.tool()
def list_tasks(user_id: str, status: str = "all") -> list[dict]:
    """List all tasks for the specified user.

    Args:
        user_id: The authenticated user's ID (required for isolation)
        status: Filter by status - "all", "pending", or "completed"

    Returns:
        Array of task objects with id, title, description, and completed status
    """
    if not user_id or len(user_id.strip()) == 0:
        return [{"error": "user_id is required"}]

    try:
        with get_sync_session() as session:
            statement = select(Task).where(Task.user_id == user_id.strip())

            if status == "pending":
                statement = statement.where(Task.is_completed == False)  # noqa: E712
            elif status == "completed":
                statement = statement.where(Task.is_completed == True)  # noqa: E712

            statement = statement.order_by(Task.created_at.desc())  # type: ignore
            result = session.execute(statement)
            tasks = list(result.scalars().all())

            return [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.is_completed,
                }
                for task in tasks
            ]
    except Exception as e:
        return [{"error": f"Database error: Unable to retrieve tasks. Please try again. ({type(e).__name__})"}]


@mcp.tool()
def complete_task(user_id: str, task_identifier: str) -> dict:
    """Mark a task as complete.

    Args:
        user_id: The authenticated user's ID (required for isolation)
        task_identifier: Task ID (number) OR task title (partial match supported)

    Returns:
        Dict with task_id, status, and title of the completed task
    """
    if not user_id or len(user_id.strip()) == 0:
        return {"error": "user_id is required"}

    if not task_identifier or len(str(task_identifier).strip()) == 0:
        return {"error": "task_identifier is required (task ID or title)"}

    task_identifier = str(task_identifier).strip()

    try:
        with get_sync_session() as session:
            task = None

            # Try to parse as integer task ID first
            if task_identifier.isdigit():
                task_id = int(task_identifier)
                statement = select(Task).where(
                    Task.id == task_id,
                    Task.user_id == user_id.strip()
                )
                result = session.execute(statement)
                task = result.scalar_one_or_none()

            # If not found by ID, search by title (case-insensitive)
            if task is None:
                statement = select(Task).where(
                    Task.user_id == user_id.strip(),
                    Task.title.ilike(f"%{task_identifier}%")
                )
                result = session.execute(statement)
                matches = list(result.scalars().all())

                if len(matches) == 0:
                    return {"error": f"No task found matching '{task_identifier}'"}
                elif len(matches) == 1:
                    task = matches[0]
                else:
                    return {
                        "error": f"Multiple tasks match '{task_identifier}'. Please be more specific.",
                        "matches": [{"id": t.id, "title": t.title} for t in matches]
                    }

            task.is_completed = True
            task.updated_at = utc_now()
            session.flush()
            session.refresh(task)
            session.commit()  # Commit the transaction

            return {
                "task_id": task.id,
                "status": "completed",
                "title": task.title,
            }
    except Exception as e:
        return {"error": f"Database error: Unable to complete task. Please try again. ({type(e).__name__})"}


@mcp.tool()
def delete_task(user_id: str, task_identifier: str) -> dict:
    """Delete a task from the user's list.

    Args:
        user_id: The authenticated user's ID (required for isolation)
        task_identifier: Task ID (number) OR task title (partial match supported)

    Returns:
        Dict with task_id, status, and title of the deleted task
    """
    if not user_id or len(user_id.strip()) == 0:
        return {"error": "user_id is required"}

    if not task_identifier or len(str(task_identifier).strip()) == 0:
        return {"error": "task_identifier is required (task ID or title)"}

    task_identifier = str(task_identifier).strip()

    try:
        with get_sync_session() as session:
            task = None

            # Try to parse as integer task ID first
            if task_identifier.isdigit():
                task_id = int(task_identifier)
                statement = select(Task).where(
                    Task.id == task_id,
                    Task.user_id == user_id.strip()
                )
                result = session.execute(statement)
                task = result.scalar_one_or_none()

            # If not found by ID, search by title (case-insensitive)
            if task is None:
                statement = select(Task).where(
                    Task.user_id == user_id.strip(),
                    Task.title.ilike(f"%{task_identifier}%")
                )
                result = session.execute(statement)
                matches = list(result.scalars().all())

                if len(matches) == 0:
                    return {"error": f"No task found matching '{task_identifier}'"}
                elif len(matches) == 1:
                    task = matches[0]
                else:
                    # Multiple matches - return them for clarification
                    return {
                        "error": f"Multiple tasks match '{task_identifier}'. Please be more specific.",
                        "matches": [{"id": t.id, "title": t.title} for t in matches]
                    }

            title = task.title
            task_id_deleted = task.id
            session.delete(task)
            session.flush()  # Execute DELETE SQL
            session.commit()  # Commit the transaction

            return {
                "task_id": task_id_deleted,
                "status": "deleted",
                "title": title,
            }
    except Exception as e:
        return {"error": f"Database error: Unable to delete task. Please try again. ({type(e).__name__})"}


@mcp.tool()
def update_task(
    user_id: str,
    task_identifier: str,
    new_title: str | None = None,
    new_description: str | None = None
) -> dict:
    """Update a task's title or description.

    Args:
        user_id: The authenticated user's ID (required for isolation)
        task_identifier: Task ID (number) OR task title (partial match supported)
        new_title: New title for the task (optional)
        new_description: New description for the task (optional)

    Returns:
        Dict with task_id, status, and title of the updated task
    """
    if not user_id or len(user_id.strip()) == 0:
        return {"error": "user_id is required"}

    if not task_identifier or len(str(task_identifier).strip()) == 0:
        return {"error": "task_identifier is required (task ID or title)"}

    if new_title is None and new_description is None:
        return {"error": "No changes specified. Provide new_title or new_description."}

    if new_title is not None:
        new_title = new_title.strip()
        if len(new_title) == 0:
            return {"error": "Title cannot be empty"}
        if len(new_title) > 255:
            return {"error": "Title must be 255 characters or less"}

    if new_description is not None and len(new_description) > 1000:
        return {"error": "Description must be 1000 characters or less"}

    task_identifier = str(task_identifier).strip()

    try:
        with get_sync_session() as session:
            task = None

            # Try to parse as integer task ID first
            if task_identifier.isdigit():
                task_id = int(task_identifier)
                statement = select(Task).where(
                    Task.id == task_id,
                    Task.user_id == user_id.strip()
                )
                result = session.execute(statement)
                task = result.scalar_one_or_none()

            # If not found by ID, search by title (case-insensitive)
            if task is None:
                statement = select(Task).where(
                    Task.user_id == user_id.strip(),
                    Task.title.ilike(f"%{task_identifier}%")
                )
                result = session.execute(statement)
                matches = list(result.scalars().all())

                if len(matches) == 0:
                    return {"error": f"No task found matching '{task_identifier}'"}
                elif len(matches) == 1:
                    task = matches[0]
                else:
                    return {
                        "error": f"Multiple tasks match '{task_identifier}'. Please be more specific.",
                        "matches": [{"id": t.id, "title": t.title} for t in matches]
                    }

            if new_title is not None:
                task.title = new_title
            if new_description is not None:
                task.description = new_description.strip() if new_description else None

            task.updated_at = utc_now()
            session.flush()
            session.refresh(task)
            session.commit()  # Commit the transaction

            return {
                "task_id": task.id,
                "status": "updated",
                "title": task.title,
            }
    except Exception as e:
        return {"error": f"Database error: Unable to update task. Please try again. ({type(e).__name__})"}


# Entry point for MCP server (stdio transport)
if __name__ == "__main__":
    from sqlalchemy import text

    # Pre-warm database connection to avoid cold start delays
    try:
        with get_sync_session() as session:
            session.execute(text("SELECT 1"))
    except Exception:
        pass  # Continue even if warmup fails

    mcp.run()
