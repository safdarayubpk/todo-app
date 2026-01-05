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
def add_task(
    user_id: str,
    title: str,
    description: str | None = None,
    priority: str | None = None,
    tags: list[str] | None = None,
) -> dict:
    """Add a new task to the user's todo list.

    Args:
        user_id: The authenticated user's ID (required for isolation)
        title: Task title (1-255 characters, required)
        description: Optional task description (max 1000 characters)
        priority: Priority level - "high", "medium", or "low" (default: "medium")
        tags: Optional list of tags for categorization

    Returns:
        Dict with task_id, status, title, priority, and tags of the created task
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

    # Validate and normalize priority
    valid_priorities = ["high", "medium", "low"]
    if priority:
        priority = priority.strip().lower()
        if priority not in valid_priorities:
            return {"error": f"Invalid priority. Must be one of: {', '.join(valid_priorities)}"}
    else:
        priority = "medium"

    # Normalize tags
    normalized_tags = []
    if tags:
        normalized_tags = list(dict.fromkeys(
            [tag.strip().lower() for tag in tags if tag and tag.strip()]
        ))

    try:
        with get_sync_session() as session:
            task = Task(
                title=title,
                description=description.strip() if description else None,
                priority=priority,
                tags=normalized_tags,
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
                "priority": task.priority,
                "tags": task.tags,
            }
    except Exception as e:
        return {"error": f"Database error: Unable to create task. Please try again. ({type(e).__name__})"}


@mcp.tool()
def list_tasks(
    user_id: str,
    status: str = "all",
    priority: str | None = None,
    tags: list[str] | None = None,
    search: str | None = None,
    sort_by: str = "created_at",
    sort_dir: str = "desc",
) -> list[dict]:
    """List all tasks for the specified user with optional filtering, search, and sorting.

    Args:
        user_id: The authenticated user's ID (required for isolation)
        status: Filter by status - "all", "pending", or "completed"
        priority: Filter by priority - "high", "medium", or "low" (optional)
        tags: Filter by tags - tasks must have ALL specified tags (optional)
        search: Search keyword in title and description (optional)
        sort_by: Sort field - "created_at", "priority", or "title" (default: created_at)
        sort_dir: Sort direction - "asc" or "desc" (default: desc)

    Returns:
        Array of task objects with id, title, description, completed, priority, and tags
    """
    if not user_id or len(user_id.strip()) == 0:
        return [{"error": "user_id is required"}]

    try:
        with get_sync_session() as session:
            from sqlalchemy import case, func

            statement = select(Task).where(Task.user_id == user_id.strip())

            # Apply status filter
            if status == "pending":
                statement = statement.where(Task.is_completed == False)  # noqa: E712
            elif status == "completed":
                statement = statement.where(Task.is_completed == True)  # noqa: E712

            # Apply priority filter
            if priority and priority.strip().lower() in ["high", "medium", "low"]:
                statement = statement.where(Task.priority == priority.strip().lower())

            # Apply tags filter (AND logic)
            if tags:
                normalized_tags = [tag.strip().lower() for tag in tags if tag and tag.strip()]
                for tag in normalized_tags:
                    statement = statement.where(Task.tags.contains([tag]))

            # Apply search filter
            if search and search.strip():
                search_term = f"%{search.strip()}%"
                statement = statement.where(
                    (Task.title.ilike(search_term)) | (Task.description.ilike(search_term))
                )

            # Apply sorting
            if sort_by == "priority":
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

            result = session.execute(statement)
            tasks = list(result.scalars().all())

            return [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.is_completed,
                    "priority": task.priority,
                    "tags": task.tags,
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
    new_description: str | None = None,
    new_priority: str | None = None,
    add_tags: list[str] | None = None,
    remove_tags: list[str] | None = None,
) -> dict:
    """Update a task's title, description, priority, or tags.

    Args:
        user_id: The authenticated user's ID (required for isolation)
        task_identifier: Task ID (number) OR task title (partial match supported)
                        Accepts formats: "39", "visit", "visit (ID: 39)", "ID: 39"
        new_title: New title for the task (optional)
        new_description: New description for the task (optional)
        new_priority: New priority - "high", "medium", or "low" (optional)
        add_tags: Tags to add to the task (optional)
        remove_tags: Tags to remove from the task (optional)

    Returns:
        Dict with task_id, status, title, priority, and tags of the updated task
    """
    if not user_id or len(user_id.strip()) == 0:
        return {"error": "user_id is required"}

    if not task_identifier or len(str(task_identifier).strip()) == 0:
        return {"error": "task_identifier is required (task ID or title)"}

    if all(v is None for v in [new_title, new_description, new_priority, add_tags, remove_tags]):
        return {"error": "No changes specified. Provide new_title, new_description, new_priority, add_tags, or remove_tags."}

    if new_title is not None:
        new_title = new_title.strip()
        if len(new_title) == 0:
            return {"error": "Title cannot be empty"}
        if len(new_title) > 255:
            return {"error": "Title must be 255 characters or less"}

    if new_description is not None and len(new_description) > 1000:
        return {"error": "Description must be 1000 characters or less"}

    # Validate priority
    valid_priorities = ["high", "medium", "low"]
    if new_priority is not None:
        new_priority = new_priority.strip().lower()
        if new_priority not in valid_priorities:
            return {"error": f"Invalid priority. Must be one of: {', '.join(valid_priorities)}"}

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
            if new_priority is not None:
                task.priority = new_priority

            # Handle tag modifications
            current_tags = list(task.tags) if task.tags else []

            if add_tags:
                normalized_add = [tag.strip().lower() for tag in add_tags if tag and tag.strip()]
                for tag in normalized_add:
                    if tag not in current_tags:
                        current_tags.append(tag)

            if remove_tags:
                normalized_remove = [tag.strip().lower() for tag in remove_tags if tag and tag.strip()]
                current_tags = [t for t in current_tags if t not in normalized_remove]

            task.tags = current_tags
            task.updated_at = utc_now()
            session.flush()
            session.refresh(task)
            session.commit()  # Commit the transaction

            return {
                "task_id": task.id,
                "status": "updated",
                "title": task.title,
                "priority": task.priority,
                "tags": task.tags,
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
