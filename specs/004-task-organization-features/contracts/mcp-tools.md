# MCP Tools Contract: Task Organization Features

**Feature**: 004-task-organization-features
**Date**: 2026-01-05

## Extended Tool Signatures

### add_task (Extended)

```python
@mcp.tool()
def add_task(
    user_id: str,
    title: str,
    description: str | None = None,
    priority: str = "medium",  # NEW: high, medium, low
    tags: list[str] | None = None,  # NEW: list of tag strings
) -> dict:
    """Add a new task to the user's todo list.

    Args:
        user_id: The authenticated user's ID (required for isolation)
        title: Task title (1-255 characters, required)
        description: Optional task description (max 1000 characters)
        priority: Priority level - "high", "medium" (default), or "low"
        tags: Optional list of tags (will be normalized to lowercase)

    Returns:
        Dict with task_id, status, title, priority, and tags of the created task

    Examples:
        - add_task(user_id="abc", title="Buy groceries")
        - add_task(user_id="abc", title="Finish report", priority="high", tags=["work"])
    """
```

**Response Format**:
```json
{
    "task_id": 42,
    "status": "created",
    "title": "Finish report",
    "priority": "high",
    "tags": ["work"]
}
```

### list_tasks (Extended)

```python
@mcp.tool()
def list_tasks(
    user_id: str,
    status: str = "all",
    priority: str | None = None,  # NEW: filter by priority
    tags: list[str] | None = None,  # NEW: filter by tags (AND logic)
    search: str | None = None,  # NEW: keyword search
    sort_by: str = "created_at",  # NEW: created_at, priority, title
    sort_dir: str = "desc",  # NEW: asc, desc
) -> list[dict]:
    """List tasks with optional filtering, search, and sorting.

    Args:
        user_id: The authenticated user's ID (required for isolation)
        status: Filter by status - "all", "pending", or "completed"
        priority: Filter by priority - "high", "medium", or "low" (None = all)
        tags: Filter by tags - task must have ALL specified tags
        search: Search keyword (matches title or description, case-insensitive)
        sort_by: Sort field - "created_at" (default), "priority", or "title"
        sort_dir: Sort direction - "desc" (default) or "asc"

    Returns:
        Array of task objects with id, title, description, completed, priority, tags

    Examples:
        - list_tasks(user_id="abc") - all tasks
        - list_tasks(user_id="abc", priority="high") - high priority tasks
        - list_tasks(user_id="abc", tags=["work"]) - tasks tagged "work"
        - list_tasks(user_id="abc", search="meeting") - tasks with "meeting"
        - list_tasks(user_id="abc", sort_by="priority", sort_dir="asc")
    """
```

**Response Format**:
```json
[
    {
        "id": 42,
        "title": "Finish report",
        "description": "Q4 sales report",
        "completed": false,
        "priority": "high",
        "tags": ["work", "urgent"]
    }
]
```

### complete_task (No Change)

Signature remains the same. No new parameters needed.

### delete_task (No Change)

Signature remains the same. No new parameters needed.

### update_task (Extended)

```python
@mcp.tool()
def update_task(
    user_id: str,
    task_identifier: str,
    new_title: str | None = None,
    new_description: str | None = None,
    new_priority: str | None = None,  # NEW: update priority
    add_tags: list[str] | None = None,  # NEW: add tags
    remove_tags: list[str] | None = None,  # NEW: remove tags
) -> dict:
    """Update a task's title, description, priority, or tags.

    Args:
        user_id: The authenticated user's ID (required for isolation)
        task_identifier: Task ID (number) OR task title (partial match supported)
        new_title: New title for the task (optional)
        new_description: New description for the task (optional)
        new_priority: New priority - "high", "medium", or "low" (optional)
        add_tags: Tags to add to existing tags (optional)
        remove_tags: Tags to remove from existing tags (optional)

    Returns:
        Dict with task_id, status, title, priority, tags of the updated task

    Examples:
        - update_task(user_id="abc", task_identifier="42", new_priority="high")
        - update_task(user_id="abc", task_identifier="report", add_tags=["urgent"])
        - update_task(user_id="abc", task_identifier="42", remove_tags=["work"])
    """
```

**Response Format**:
```json
{
    "task_id": 42,
    "status": "updated",
    "title": "Finish report",
    "priority": "high",
    "tags": ["work", "urgent"]
}
```

## Natural Language Examples

### Priority Operations

| User Says | Tool Call |
|-----------|-----------|
| "add a high priority task: finish report" | `add_task(user_id, "finish report", priority="high")` |
| "show my high priority tasks" | `list_tasks(user_id, priority="high")` |
| "change task 42 to low priority" | `update_task(user_id, "42", new_priority="low")` |
| "what are my urgent tasks?" | `list_tasks(user_id, priority="high")` |

### Tag Operations

| User Says | Tool Call |
|-----------|-----------|
| "add task buy milk with tag home" | `add_task(user_id, "buy milk", tags=["home"])` |
| "show work tasks" | `list_tasks(user_id, tags=["work"])` |
| "tag task 42 as urgent" | `update_task(user_id, "42", add_tags=["urgent"])` |
| "remove home tag from task 42" | `update_task(user_id, "42", remove_tags=["home"])` |
| "show high priority work tasks" | `list_tasks(user_id, priority="high", tags=["work"])` |

### Search Operations

| User Says | Tool Call |
|-----------|-----------|
| "find tasks about meeting" | `list_tasks(user_id, search="meeting")` |
| "search for report in my tasks" | `list_tasks(user_id, search="report")` |

### Sort Operations

| User Says | Tool Call |
|-----------|-----------|
| "sort my tasks by priority" | `list_tasks(user_id, sort_by="priority", sort_dir="desc")` |
| "show tasks alphabetically" | `list_tasks(user_id, sort_by="title", sort_dir="asc")` |
| "list tasks newest first" | `list_tasks(user_id, sort_by="created_at", sort_dir="desc")` |

### Combined Operations

| User Says | Tool Call |
|-----------|-----------|
| "show incomplete work tasks sorted by priority" | `list_tasks(user_id, status="pending", tags=["work"], sort_by="priority")` |
| "find high priority tasks about report" | `list_tasks(user_id, priority="high", search="report")` |

## Agent System Prompt Update

Add to the existing system prompt:

```
ORGANIZATION FEATURES:
- Tasks have priority (high/medium/low) - default is medium
- Tasks can have multiple tags (lowercase, e.g., work, home, personal)
- When user mentions urgency/importance, use priority parameter
- When user mentions categories, use tags parameter
- Filter and search can be combined for precise queries

EXAMPLES:
- "Add urgent task finish report" → add_task with priority="high"
- "Add task buy groceries for home" → add_task with tags=["home"]
- "Show my work tasks" → list_tasks with tags=["work"]
- "What are my high priority tasks?" → list_tasks with priority="high"
- "Sort tasks by importance" → list_tasks with sort_by="priority"
```
