# Quickstart: Phase I Console Todo App

**Feature**: 001-console-todo-app
**Date**: 2025-12-28

## Prerequisites

- Python 3.13+ installed
- UV package manager installed ([install UV](https://docs.astral.sh/uv/getting-started/installation/))

## Setup

### 1. Clone and Navigate

```bash
cd todoapp
```

### 2. Initialize UV Project (if not done)

```bash
uv init --python 3.13
```

### 3. Verify Python Version

```bash
uv run python --version
# Should output: Python 3.13.x
```

## Running the Application

### Start the Todo App

```bash
uv run python -m src.main
```

### Expected Output

```
=== Todo App ===
1. Add task
2. List tasks
3. Update task
4. Delete task
5. Toggle complete
6. Quit
================
Enter choice:
```

## Basic Usage

### Add a Task

1. Enter `1` at the menu
2. Type your task title (e.g., "Buy groceries")
3. Optionally add a description, or press Enter to skip

```
Enter choice: 1
Enter task title: Buy groceries
Enter description (optional, press Enter to skip): Milk, bread, eggs
Task added: 1. Buy groceries
```

### List All Tasks

1. Enter `2` at the menu

```
Enter choice: 2

=== Your Tasks ===
  1. [ ] Buy groceries
         Milk, bread, eggs
==================
```

### Mark Task Complete

1. Enter `5` at the menu
2. Enter the task ID

```
Enter choice: 5
Enter task ID to toggle: 1
Task 1 marked as complete.
```

### Update a Task

1. Enter `3` at the menu
2. Enter the task ID
3. Enter new title (or press Enter to keep)
4. Enter new description (or press Enter to keep)

```
Enter choice: 3
Enter task ID to update: 1
Current title: Buy groceries
Enter new title (press Enter to keep current): Get groceries
Current description: Milk, bread, eggs
Enter new description (press Enter to keep current):
Task 1 updated.
```

### Delete a Task

1. Enter `4` at the menu
2. Enter the task ID

```
Enter choice: 4
Enter task ID to delete: 1
Task 1 deleted.
```

### Quit

1. Enter `6` at the menu

```
Enter choice: 6
Goodbye!
```

## Demo Workflow

Complete this workflow to verify all features work:

```bash
# 1. Start the app
uv run python -m src.main

# 2. Add 3 tasks
# Choice: 1 → "Task A" → ""
# Choice: 1 → "Task B" → "With description"
# Choice: 1 → "Task C" → ""

# 3. List tasks (should show 3 tasks, all [ ])
# Choice: 2

# 4. Mark task 2 complete
# Choice: 5 → 2

# 5. Update task 1
# Choice: 3 → 1 → "Updated Task A" → "New description"

# 6. Delete task 3
# Choice: 4 → 3

# 7. List tasks (should show 2 tasks: 1 updated, 2 completed)
# Choice: 2

# 8. Quit
# Choice: 6
```

## Troubleshooting

### "Module not found" Error

Ensure you're running from the project root:
```bash
cd /path/to/todoapp
uv run python -m src.main
```

### Invalid Input Handling

The app handles invalid inputs gracefully:
- Non-numeric menu choice → "Please enter a number (1-6)"
- Invalid task ID → "Please enter a valid number"
- Empty title → "Title cannot be empty"
- Non-existent ID → "Task not found"

### Keyboard Interrupt

Press `Ctrl+C` anytime to exit gracefully:
```
^C
Goodbye!
```

## Project Structure

```
todoapp/
├── src/
│   ├── __init__.py
│   ├── main.py           # Entry point
│   ├── models/
│   │   └── task.py       # Task dataclass
│   ├── storage/
│   │   └── memory.py     # In-memory store
│   └── cli/
│       ├── menu.py       # Menu display
│       └── handlers.py   # Command handlers
└── pyproject.toml        # UV configuration
```

## Limitations (Phase I)

- **No persistence**: Tasks are lost when app exits
- **Single session**: No multi-user support
- **Console only**: No web or API interface

These limitations will be addressed in subsequent phases.
