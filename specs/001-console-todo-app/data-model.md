# Data Model: Phase I Console Todo App

**Feature**: 001-console-todo-app
**Date**: 2025-12-28
**Status**: Complete

## Entity Overview

Phase I has a single entity: **Task**. No relationships exist (single-entity model).

## Entities

### Task

Represents a single todo item in the user's list.

| Attribute | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| id | int | Yes | Auto-generated | Unique sequential identifier (1, 2, 3, ...) |
| title | str | Yes | - | Short text describing the task (non-empty) |
| description | str \| None | No | None | Optional longer text with additional details |
| completed | bool | Yes | False | Completion status (False = pending, True = done) |

**Invariants**:
- `id` MUST be a positive integer (> 0)
- `id` MUST be unique within a session
- `title` MUST be non-empty (at least 1 character after trimming whitespace)
- `completed` defaults to `False` on creation

**State Transitions**:
```
[Created] ──toggle()──▶ [Completed]
    ▲                        │
    └────── toggle() ────────┘
```

## Storage Model

### In-Memory Store (Phase I)

```
TaskStore
├── _tasks: list[Task]     # Ordered collection of tasks
└── _next_id: int          # Counter for ID generation (starts at 1)
```

**Operations**:

| Operation | Input | Output | Description |
|-----------|-------|--------|-------------|
| add | title, description? | Task | Create new task, assign ID, append to list |
| get | id | Task \| None | Find task by ID |
| list_all | - | list[Task] | Return all tasks in creation order |
| update | id, title?, description? | bool | Modify task attributes |
| delete | id | bool | Remove task from list |
| toggle_complete | id | bool | Flip completed status |

**ID Generation**:
- Sequential counter starting at 1
- Never reused within session (even after deletion)
- Example: Add 3 tasks → IDs 1, 2, 3. Delete task 2 → IDs 1, 3. Add new task → ID 4.

## Validation Rules

### Title Validation

```
Input: raw_title (str)
Process:
  1. Strip leading/trailing whitespace
  2. Check length > 0
Output: Valid title OR error "Title cannot be empty"
```

### ID Validation

```
Input: raw_id (str from user input)
Process:
  1. Attempt conversion to int
  2. Check value > 0
  3. Check task exists in store
Output: Valid ID OR error message:
  - "Invalid input: please enter a number" (not numeric)
  - "Invalid ID: must be a positive number" (≤ 0)
  - "Task not found" (valid number but no matching task)
```

## Future Evolution (Phase II+)

The data model is designed for extension:

| Phase | Changes |
|-------|---------|
| II | Add `user_id` foreign key, `created_at`, `updated_at` timestamps |
| III | Add `ai_generated` flag, `natural_language_input` field |
| IV-V | Add soft delete (`deleted_at`), optimistic locking (`version`) |

**Migration Strategy**:
- Task dataclass fields are additive (new fields have defaults)
- Storage interface (`add`, `get`, `update`, `delete`) remains stable
- New storage implementations (database) implement same interface
