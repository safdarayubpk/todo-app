# MCP Tools Contract

**Feature**: 003-ai-todo-chatbot
**Date**: 2025-12-29

## Overview

This document defines the MCP (Model Context Protocol) tools exposed by the FastMCP server for task management operations. These tools are consumed by the AI agent to execute user requests.

## MCP Server Configuration

```
Server Name: TodoMCP
Transport: SSE (Server-Sent Events) or Streamable HTTP
Base URL: /mcp (mounted on existing FastAPI backend)
```

## Tool Definitions

### 1. add_task

Creates a new task for the authenticated user.

**Tool Definition**:
```python
@mcp.tool()
async def add_task(
    title: str,
    description: str | None = None
) -> dict:
    """
    Add a new task to the user's todo list.

    Args:
        title: Task title (1-255 characters, required)
        description: Optional task description (max 1000 characters)

    Returns:
        Success response with created task details or error message.
    """
```

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "title": {
      "type": "string",
      "minLength": 1,
      "maxLength": 255,
      "description": "Task title (required)"
    },
    "description": {
      "type": "string",
      "maxLength": 1000,
      "description": "Optional task description"
    }
  },
  "required": ["title"]
}
```

**Success Response**:
```json
{
  "success": true,
  "task": {
    "id": 42,
    "title": "buy groceries",
    "description": null,
    "is_completed": false
  },
  "message": "Task 'buy groceries' created successfully"
}
```

**Error Response**:
```json
{
  "success": false,
  "error": "Title is required and must be 1-255 characters"
}
```

---

### 2. list_tasks

Retrieves all tasks for the authenticated user with optional filtering.

**Tool Definition**:
```python
@mcp.tool()
async def list_tasks(
    filter: Literal["all", "completed", "incomplete"] = "all"
) -> dict:
    """
    List all tasks for the current user.

    Args:
        filter: Filter tasks by completion status
                - "all": All tasks (default)
                - "completed": Only completed tasks
                - "incomplete": Only incomplete tasks

    Returns:
        List of tasks matching the filter criteria.
    """
```

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "filter": {
      "type": "string",
      "enum": ["all", "completed", "incomplete"],
      "default": "all",
      "description": "Filter by completion status"
    }
  }
}
```

**Success Response**:
```json
{
  "success": true,
  "tasks": [
    {
      "id": 1,
      "title": "buy groceries",
      "description": "Milk, bread, eggs",
      "is_completed": false
    },
    {
      "id": 2,
      "title": "call dentist",
      "description": null,
      "is_completed": true
    }
  ],
  "count": 2,
  "filter_applied": "all"
}
```

**Empty Response**:
```json
{
  "success": true,
  "tasks": [],
  "count": 0,
  "message": "No tasks found"
}
```

---

### 3. mark_complete

Marks a task as complete or incomplete.

**Tool Definition**:
```python
@mcp.tool()
async def mark_complete(
    task_identifier: str,
    completed: bool = True
) -> dict:
    """
    Mark a task as complete or incomplete.

    Args:
        task_identifier: Task ID (number) or partial title match
        completed: True to mark complete, False to mark incomplete

    Returns:
        Updated task details or disambiguation request if multiple matches.
    """
```

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "task_identifier": {
      "type": "string",
      "description": "Task ID or partial title to match"
    },
    "completed": {
      "type": "boolean",
      "default": true,
      "description": "Completion status to set"
    }
  },
  "required": ["task_identifier"]
}
```

**Success Response**:
```json
{
  "success": true,
  "task": {
    "id": 1,
    "title": "buy groceries",
    "is_completed": true
  },
  "message": "Task 'buy groceries' marked as complete"
}
```

**Disambiguation Response** (multiple matches):
```json
{
  "success": false,
  "error": "Multiple tasks match 'meeting'. Please be more specific.",
  "matches": [
    { "id": 3, "title": "Team meeting preparation" },
    { "id": 5, "title": "Schedule meeting with client" }
  ],
  "hint": "Try using the task ID or a more specific title"
}
```

**Not Found Response**:
```json
{
  "success": false,
  "error": "No task found matching 'xyz'",
  "suggestion": "Use 'list_tasks' to see all your tasks"
}
```

---

### 4. delete_task

Deletes a task from the user's todo list.

**Tool Definition**:
```python
@mcp.tool()
async def delete_task(
    task_identifier: str,
    confirm: bool = False
) -> dict:
    """
    Delete a task from the user's todo list.

    Args:
        task_identifier: Task ID (number) or partial title match
        confirm: Must be True to actually delete (safety measure)

    Returns:
        Confirmation request or deletion result.
    """
```

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "task_identifier": {
      "type": "string",
      "description": "Task ID or partial title to match"
    },
    "confirm": {
      "type": "boolean",
      "default": false,
      "description": "Confirmation flag (must be true to delete)"
    }
  },
  "required": ["task_identifier"]
}
```

**Confirmation Required Response** (confirm=false):
```json
{
  "success": false,
  "requires_confirmation": true,
  "task_to_delete": {
    "id": 1,
    "title": "buy groceries"
  },
  "message": "Are you sure you want to delete 'buy groceries'? Set confirm=true to proceed."
}
```

**Success Response** (confirm=true):
```json
{
  "success": true,
  "deleted_task": {
    "id": 1,
    "title": "buy groceries"
  },
  "message": "Task 'buy groceries' has been deleted"
}
```

---

### 5. update_task

Updates a task's title or description.

**Tool Definition**:
```python
@mcp.tool()
async def update_task(
    task_identifier: str,
    new_title: str | None = None,
    new_description: str | None = None
) -> dict:
    """
    Update a task's title or description.

    Args:
        task_identifier: Task ID (number) or partial title match
        new_title: New title for the task (optional)
        new_description: New description for the task (optional)

    Returns:
        Updated task details or error if task not found.
    """
```

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "task_identifier": {
      "type": "string",
      "description": "Task ID or partial title to match"
    },
    "new_title": {
      "type": "string",
      "minLength": 1,
      "maxLength": 255,
      "description": "New title (optional)"
    },
    "new_description": {
      "type": "string",
      "maxLength": 1000,
      "description": "New description (optional)"
    }
  },
  "required": ["task_identifier"]
}
```

**Success Response**:
```json
{
  "success": true,
  "task": {
    "id": 1,
    "title": "buy weekly groceries",
    "description": "From the farmer's market",
    "is_completed": false
  },
  "changes": {
    "title": { "old": "buy groceries", "new": "buy weekly groceries" },
    "description": { "old": null, "new": "From the farmer's market" }
  },
  "message": "Task updated successfully"
}
```

**No Changes Response**:
```json
{
  "success": false,
  "error": "No changes specified. Provide new_title or new_description."
}
```

## Task Identifier Resolution Algorithm

When a tool receives `task_identifier`, the following resolution logic applies:

```python
async def resolve_task(task_identifier: str, user_id: str) -> Task | list[Task]:
    """
    Resolve a task identifier to one or more tasks.

    1. Try to parse as integer (task ID)
    2. If numeric, fetch by ID with user_id filter
    3. If string, perform case-insensitive partial match on title
    4. Return single task if exactly one match
    5. Return list if multiple matches (for disambiguation)
    6. Raise NotFound if no matches
    """
    # Try numeric ID first
    if task_identifier.isdigit():
        task = await get_task_by_id(int(task_identifier), user_id)
        if task:
            return task

    # Fall back to title search
    matches = await search_tasks_by_title(task_identifier, user_id)

    if len(matches) == 0:
        raise TaskNotFound(task_identifier)
    elif len(matches) == 1:
        return matches[0]
    else:
        return matches  # Multiple matches - needs disambiguation
```

## Authentication Flow

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Next.js Chat   │───>│   MCP Server    │───>│  FastAPI API    │
│   API Route     │    │   (FastMCP)     │    │  (Backend)      │
└────────┬────────┘    └────────┬────────┘    └────────┬────────┘
         │                      │                      │
         │ JWT in Cookie        │ JWT in Header        │ Validate JWT
         │                      │                      │ Extract user_id
         ▼                      ▼                      ▼
    [Auth Check]          [Forward JWT]          [User Isolation]
```

1. Chat API route extracts JWT from Better Auth session
2. JWT passed to MCP server via `Authorization: Bearer <jwt>` header
3. MCP server includes JWT in all FastAPI requests
4. FastAPI validates JWT and filters all operations by user_id

## Error Handling

All tools return structured errors:

```json
{
  "success": false,
  "error": "Human-readable error message",
  "error_code": "TASK_NOT_FOUND",
  "details": { /* Additional context */ }
}
```

**Error Codes**:

| Code | Description |
|------|-------------|
| `TASK_NOT_FOUND` | No task matches the identifier |
| `MULTIPLE_MATCHES` | Multiple tasks match, disambiguation needed |
| `VALIDATION_ERROR` | Input validation failed |
| `AUTH_ERROR` | Authentication/authorization failed |
| `BACKEND_ERROR` | FastAPI backend returned an error |
