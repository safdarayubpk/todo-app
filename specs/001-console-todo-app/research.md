# Research: Phase I Console Todo App

**Feature**: 001-console-todo-app
**Date**: 2025-12-28
**Status**: Complete

## Research Summary

This Phase I implementation requires minimal research as it uses standard Python patterns and built-in libraries. All technical decisions are straightforward with clear best practices.

## Technical Decisions

### TD-001: Python Dataclass for Task Model

**Decision**: Use `@dataclass` decorator from `dataclasses` module
**Rationale**:
- Native Python 3.7+ feature, no external dependencies
- Automatic `__init__`, `__repr__`, `__eq__` generation
- Type hints integrated naturally
- Mutable by default (needed for in-place updates)
- Can add `frozen=True` later for immutability if needed

**Implementation Pattern**:
```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Task:
    id: int
    title: str
    description: Optional[str] = None
    completed: bool = False
```

### TD-002: In-Memory Storage with List

**Decision**: Use Python list with TaskStore wrapper class
**Rationale**:
- Simple and efficient for <1000 items
- O(n) lookup by ID is acceptable for console app
- Easy to understand and debug
- Natural iteration for list display

**Implementation Pattern**:
```python
class TaskStore:
    def __init__(self):
        self._tasks: list[Task] = []
        self._next_id: int = 1

    def add(self, title: str, description: str | None = None) -> Task:
        task = Task(id=self._next_id, title=title, description=description)
        self._tasks.append(task)
        self._next_id += 1
        return task

    def get(self, task_id: int) -> Task | None:
        return next((t for t in self._tasks if t.id == task_id), None)

    def delete(self, task_id: int) -> bool:
        task = self.get(task_id)
        if task:
            self._tasks.remove(task)
            return True
        return False

    def list_all(self) -> list[Task]:
        return list(self._tasks)
```

### TD-003: Interactive CLI Pattern

**Decision**: REPL loop with numbered menu and input validation
**Rationale**:
- Standard pattern for interactive console applications
- User always knows available options
- Easy to extend with new commands
- Graceful error handling built-in

**Implementation Pattern**:
```python
def main():
    store = TaskStore()
    while True:
        display_menu()
        choice = get_user_choice()
        if choice == "quit":
            print("Goodbye!")
            break
        handle_command(choice, store)

def display_menu():
    print("\n=== Todo App ===")
    print("1. Add task")
    print("2. List tasks")
    print("3. Update task")
    print("4. Delete task")
    print("5. Toggle complete")
    print("6. Quit")
    print("================")
```

### TD-004: Input Validation Strategy

**Decision**: Validate at input point, display friendly errors, re-prompt
**Rationale**:
- Fail fast with clear messages
- Never crash on bad input
- Guide user to correct input

**Implementation Pattern**:
```python
def get_task_id() -> int | None:
    try:
        value = input("Enter task ID: ").strip()
        task_id = int(value)
        if task_id <= 0:
            print("Error: ID must be a positive number")
            return None
        return task_id
    except ValueError:
        print("Error: Please enter a valid number")
        return None
```

### TD-005: Task Display Format

**Decision**: Numbered list with status checkbox and title
**Rationale**:
- Familiar checkbox pattern ([x] done, [ ] pending)
- ID visible for reference in other operations
- Clean, readable output

**Implementation Pattern**:
```python
def display_task(task: Task):
    status = "[x]" if task.completed else "[ ]"
    print(f"  {task.id}. {status} {task.title}")
    if task.description:
        print(f"         {task.description}")
```

## Best Practices Applied

### BP-001: Graceful Interrupt Handling

Wrap main loop in try/except for KeyboardInterrupt:
```python
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nGoodbye!")
```

### BP-002: Type Annotations Throughout

All functions include return types and parameter types for IDE support and documentation.

### BP-003: Single Responsibility Modules

- `models/task.py`: Only Task dataclass
- `storage/memory.py`: Only storage operations
- `cli/menu.py`: Only menu display
- `cli/handlers.py`: Only command execution

### BP-004: Consistent Error Messages

All error messages follow pattern: `"Error: <what went wrong>"`

## Alternatives Rejected

| Alternative | Why Rejected |
|------------|--------------|
| Dict-based tasks | Less type safety, no IDE autocomplete |
| SQLite persistence | Out of scope for Phase I |
| argparse CLI | Designed for one-shot commands, not interactive REPL |
| Rich/click library | External dependencies prohibited |
| UUID for task IDs | Overkill for single-session, user-unfriendly |

## Dependencies

**Runtime**: None (pure Python standard library)
**Development**: UV for package management

## Risks and Mitigations

| Risk | Mitigation |
|------|-----------|
| Data loss on exit | Clearly documented as Phase I limitation; Phase II adds persistence |
| Large task lists slow | Unlikely for console use; optimize in Phase II if needed |
| Console encoding issues | Use UTF-8 explicitly if problems arise |

## Conclusion

No further research needed. All technical decisions are clear and use established Python patterns. Proceed to Phase 1 design artifacts.
