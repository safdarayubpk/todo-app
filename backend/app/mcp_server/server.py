"""MCP Server for Todo Task Operations.

This module implements the MCP Server using FastMCP with stdio transport.
It exposes 5 tools for task management: add_task, list_tasks, complete_task,
delete_task, and update_task.

Each tool requires user_id as the first parameter to enforce data isolation.
"""

import re
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


def parse_task_identifier(identifier: str) -> tuple[int | None, str]:
    """Parse a task identifier to extract ID and/or title.

    Handles formats like:
    - "39" → (39, "39")
    - "visit" → (None, "visit")
    - "visit (ID: 39)" → (39, "visit")
    - "(ID: 39)" → (39, "")
    - "ID: 39" → (39, "")
    - "task 39" → (39, "task")

    Returns:
        Tuple of (extracted_id or None, cleaned_title)
    """
    identifier = identifier.strip()

    # Pattern 1: "(ID: X)" or "(ID:X)" anywhere in string
    id_pattern = r'\(ID:\s*(\d+)\)'
    match = re.search(id_pattern, identifier, re.IGNORECASE)
    if match:
        task_id = int(match.group(1))
        # Remove the ID part to get the title
        title = re.sub(id_pattern, '', identifier, flags=re.IGNORECASE).strip()
        return (task_id, title)

    # Pattern 2: "ID: X" or "ID:X" at start or end
    id_pattern2 = r'(?:^|\s)ID:\s*(\d+)(?:\s|$)'
    match = re.search(id_pattern2, identifier, re.IGNORECASE)
    if match:
        task_id = int(match.group(1))
        title = re.sub(id_pattern2, ' ', identifier, flags=re.IGNORECASE).strip()
        return (task_id, title)

    # Pattern 3: Just a number
    if identifier.isdigit():
        return (int(identifier), identifier)

    # Pattern 4: "task X" where X is a number
    task_num_pattern = r'^task\s+(\d+)$'
    match = re.search(task_num_pattern, identifier, re.IGNORECASE)
    if match:
        return (int(match.group(1)), "")

    # No ID found, return as title
    return (None, identifier)


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
                        Accepts formats: "39", "visit", "visit (ID: 39)", "ID: 39"

    Returns:
        Dict with task_id, status, and title of the completed task
    """
    if not user_id or len(user_id.strip()) == 0:
        return {"error": "user_id is required"}

    if not task_identifier or len(str(task_identifier).strip()) == 0:
        return {"error": "task_identifier is required (task ID or title)"}

    # Parse the identifier to extract ID and/or title
    parsed_id, parsed_title = parse_task_identifier(str(task_identifier))

    try:
        with get_sync_session() as session:
            task = None

            # Try to find by extracted ID first
            if parsed_id is not None:
                statement = select(Task).where(
                    Task.id == parsed_id,
                    Task.user_id == user_id.strip()
                )
                result = session.execute(statement)
                task = result.scalar_one_or_none()

            # If not found by ID and we have a title, search by title
            if task is None and parsed_title:
                statement = select(Task).where(
                    Task.user_id == user_id.strip(),
                    Task.title.ilike(f"%{parsed_title}%")
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
            elif task is None:
                return {"error": f"No task found matching '{task_identifier}'"}

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
                        Accepts formats: "39", "visit", "visit (ID: 39)", "ID: 39"

    Returns:
        Dict with task_id, status, and title of the deleted task
    """
    if not user_id or len(user_id.strip()) == 0:
        return {"error": "user_id is required"}

    if not task_identifier or len(str(task_identifier).strip()) == 0:
        return {"error": "task_identifier is required (task ID or title)"}

    # Parse the identifier to extract ID and/or title
    parsed_id, parsed_title = parse_task_identifier(str(task_identifier))

    try:
        with get_sync_session() as session:
            task = None

            # Try to find by extracted ID first
            if parsed_id is not None:
                statement = select(Task).where(
                    Task.id == parsed_id,
                    Task.user_id == user_id.strip()
                )
                result = session.execute(statement)
                task = result.scalar_one_or_none()

            # If not found by ID and we have a title, search by title
            if task is None and parsed_title:
                statement = select(Task).where(
                    Task.user_id == user_id.strip(),
                    Task.title.ilike(f"%{parsed_title}%")
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
            elif task is None:
                return {"error": f"No task found matching '{task_identifier}'"}

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
                        Accepts formats: "39", "visit", "visit (ID: 39)", "ID: 39"
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

    # Parse the identifier to extract ID and/or title
    parsed_id, parsed_title = parse_task_identifier(str(task_identifier))

    try:
        with get_sync_session() as session:
            task = None

            # Try to find by extracted ID first
            if parsed_id is not None:
                statement = select(Task).where(
                    Task.id == parsed_id,
                    Task.user_id == user_id.strip()
                )
                result = session.execute(statement)
                task = result.scalar_one_or_none()

            # If not found by ID and we have a title, search by title
            if task is None and parsed_title:
                statement = select(Task).where(
                    Task.user_id == user_id.strip(),
                    Task.title.ilike(f"%{parsed_title}%")
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
            elif task is None:
                return {"error": f"No task found matching '{task_identifier}'"}

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
