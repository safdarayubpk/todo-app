# CLI Commands Contract: Phase I Console Todo App

**Feature**: 001-console-todo-app
**Date**: 2025-12-28
**Status**: Complete

## Overview

This document defines the command interface for the interactive console todo application. The application operates in REPL (Read-Eval-Print-Loop) mode with a numbered menu.

## Main Menu

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

## Commands

### 1. Add Task

**Purpose**: Create a new task with title and optional description

**Flow**:
```
User selects: 1
Prompt: "Enter task title: "
Input: <title>
  → If empty: "Error: Title cannot be empty" → Return to menu
  → If valid: Continue
Prompt: "Enter description (optional, press Enter to skip): "
Input: <description or empty>
Output: "Task added: {id}. {title}"
Return to menu
```

**Example**:
```
Enter choice: 1
Enter task title: Buy groceries
Enter description (optional, press Enter to skip): Milk, eggs, bread
Task added: 1. Buy groceries
```

### 2. List Tasks

**Purpose**: Display all tasks with ID, status, and title

**Flow**:
```
User selects: 2
  → If no tasks: "No tasks found."
  → If tasks exist: Display each task
Return to menu
```

**Output Format**:
```
=== Your Tasks ===
  1. [ ] Buy groceries
         Milk, eggs, bread
  2. [x] Call doctor
  3. [ ] Finish report
==================
```

**Format Rules**:
- Status indicator: `[ ]` = pending, `[x]` = completed
- Description shown indented on next line (if present)
- Tasks shown in creation order (by ID)

### 3. Update Task

**Purpose**: Modify title and/or description of existing task

**Flow**:
```
User selects: 3
Prompt: "Enter task ID to update: "
Input: <id>
  → If not numeric: "Error: Please enter a valid number" → Return to menu
  → If ≤ 0: "Error: ID must be a positive number" → Return to menu
  → If not found: "Error: Task not found" → Return to menu
  → If valid: Continue
Display: "Current title: {title}"
Prompt: "Enter new title (press Enter to keep current): "
Input: <new_title or empty>
  → If empty: Keep current title
  → If whitespace only: "Error: Title cannot be empty" → Return to menu
  → If valid: Update title
Display: "Current description: {description or 'None'}"
Prompt: "Enter new description (press Enter to keep current): "
Input: <new_description or empty>
  → If empty: Keep current description
  → If valid: Update description
Output: "Task {id} updated."
Return to menu
```

### 4. Delete Task

**Purpose**: Remove a task from the list

**Flow**:
```
User selects: 4
Prompt: "Enter task ID to delete: "
Input: <id>
  → If not numeric: "Error: Please enter a valid number" → Return to menu
  → If ≤ 0: "Error: ID must be a positive number" → Return to menu
  → If not found: "Error: Task not found" → Return to menu
  → If valid: Delete task
Output: "Task {id} deleted."
Return to menu
```

### 5. Toggle Complete

**Purpose**: Switch task between completed and pending status

**Flow**:
```
User selects: 5
Prompt: "Enter task ID to toggle: "
Input: <id>
  → If not numeric: "Error: Please enter a valid number" → Return to menu
  → If ≤ 0: "Error: ID must be a positive number" → Return to menu
  → If not found: "Error: Task not found" → Return to menu
  → If valid: Toggle completed status
Output: "Task {id} marked as {complete/incomplete}."
Return to menu
```

### 6. Quit

**Purpose**: Exit the application

**Flow**:
```
User selects: 6
Output: "Goodbye!"
Application terminates
```

## Error Handling

### Invalid Menu Choice

```
Enter choice: 7
Error: Invalid choice. Please enter 1-6.
```

```
Enter choice: abc
Error: Please enter a number (1-6).
```

### Keyboard Interrupt (Ctrl+C)

```
^C
Goodbye!
```

Application exits gracefully without traceback.

## Input Conventions

| Input Type | Validation | Error Message |
|------------|------------|---------------|
| Menu choice | Integer 1-6 | "Please enter a number (1-6)" |
| Task ID | Positive integer | "Please enter a valid number" / "ID must be a positive number" |
| Title | Non-empty string | "Title cannot be empty" |
| Description | Any string (including empty) | N/A |

## State Machine

```
                    ┌─────────────────────────────────────┐
                    │                                     │
                    ▼                                     │
              ┌──────────┐                                │
              │   MENU   │ ◀─────────────────────────┐    │
              └────┬─────┘                           │    │
                   │                                 │    │
    ┌──────────────┼──────────────┬─────────┬───────┼────┘
    │              │              │         │       │
    ▼              ▼              ▼         ▼       │
┌───────┐    ┌──────────┐   ┌────────┐  ┌───────┐  │
│  ADD  │    │   LIST   │   │ UPDATE │  │DELETE │  │
└───┬───┘    └────┬─────┘   └───┬────┘  └───┬───┘  │
    │             │             │           │       │
    └─────────────┴─────────────┴───────────┴───────┘

    (QUIT exits the loop)
```

## Session Example

```
$ python -m src.main

=== Todo App ===
1. Add task
2. List tasks
3. Update task
4. Delete task
5. Toggle complete
6. Quit
================
Enter choice: 1
Enter task title: Buy groceries
Enter description (optional, press Enter to skip): Milk and eggs
Task added: 1. Buy groceries

=== Todo App ===
...
Enter choice: 1
Enter task title: Call mom
Enter description (optional, press Enter to skip):
Task added: 2. Call mom

=== Todo App ===
...
Enter choice: 2

=== Your Tasks ===
  1. [ ] Buy groceries
         Milk and eggs
  2. [ ] Call mom
==================

=== Todo App ===
...
Enter choice: 5
Enter task ID to toggle: 1
Task 1 marked as complete.

=== Todo App ===
...
Enter choice: 2

=== Your Tasks ===
  1. [x] Buy groceries
         Milk and eggs
  2. [ ] Call mom
==================

=== Todo App ===
...
Enter choice: 6
Goodbye!
$
```
