# Implementation Plan: Phase I Console Todo App

**Branch**: `001-console-todo-app` | **Date**: 2025-12-28 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-console-todo-app/spec.md`

## Summary

Build a command-line todo application with in-memory storage implementing CRUD operations (Create, Read, Update, Delete) plus completion toggling. The application uses pure Python 3.13+ with dataclasses for the Task model, a list-based in-memory store, and an interactive menu-driven CLI interface.

## Technical Context

**Language/Version**: Python 3.13+ (managed with UV)
**Primary Dependencies**: None (pure standard library: dataclasses, typing)
**Storage**: In-memory (Python list of Task dataclass instances)
**Testing**: Manual interactive testing (pytest available for future phases)
**Target Platform**: Cross-platform console (Linux, macOS, Windows terminal)
**Project Type**: Single project (console application)
**Performance Goals**: Menu display within 1 second, instant task operations
**Constraints**: No external dependencies, no persistence, single-user single-session
**Scale/Scope**: Single user, ~100 tasks per session (memory-bounded)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Spec-Driven Development | ✅ PASS | spec.md complete with user stories, requirements, success criteria |
| II. AI-Only Implementation | ✅ PASS | All code will be generated via Claude Code |
| III. Iterative Evolution | ✅ PASS | Phase I foundation, designed for Phase II+ extension |
| IV. Reusability and Modularity | ✅ PASS | Task model + storage + CLI separated into modules |
| V. Security and Isolation | ⚪ N/A | Single-user console app, no auth required for Phase I |
| VI. Cloud-Native Readiness | ⚪ N/A | Phase I is local console; structure supports future containerization |

**Code Quality Standards Compliance**:
- ✅ Type annotations: All functions will include type hints
- ✅ Docstrings: All modules and functions will have docstrings
- ✅ PEP 8: Code will follow Python style guidelines
- ✅ Descriptive names: Clear variable and function naming

**Gate Result**: PASS - Proceed to Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/001-console-todo-app/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (internal CLI contracts)
│   └── cli-commands.md  # Command interface specification
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
src/
├── __init__.py          # Package marker
├── main.py              # Application entry point with REPL loop
├── models/
│   ├── __init__.py
│   └── task.py          # Task dataclass definition
├── storage/
│   ├── __init__.py
│   └── memory.py        # In-memory task storage (TaskStore class)
└── cli/
    ├── __init__.py
    ├── menu.py          # Menu display and input handling
    └── handlers.py      # Command handlers (add, list, update, delete, complete)

pyproject.toml           # UV project configuration
```

**Structure Decision**: Single project structure with modular separation:
- `models/` - Data structures (Task dataclass)
- `storage/` - Storage abstraction (enables future Phase II database integration)
- `cli/` - User interface (menu, handlers)

This separation enables:
1. Phase II: Replace `storage/memory.py` with `storage/database.py` without touching models or CLI
2. Phase III: Add AI handler alongside existing CLI handlers
3. Testing: Mock storage for unit tests

## Complexity Tracking

> No violations - design follows minimal complexity principle

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| Storage pattern | Simple class with list | Dict/list sufficient for in-memory; no repository pattern needed |
| CLI framework | Built-in input/print | No external libs per constraints; argparse unnecessary for interactive mode |
| Task IDs | Sequential counter | Simple, predictable, user-friendly |

## Architecture Decisions

### AD-001: Task Model as Dataclass

**Decision**: Use Python `dataclass` for Task entity
**Rationale**:
- Type safety with minimal boilerplate
- Built-in `__eq__`, `__repr__` for debugging
- Immutability option for future use
- Native Python, no dependencies

**Alternatives Considered**:
- Plain dict: Less type safety, no IDE support
- NamedTuple: Immutable by default, less flexible for updates
- Pydantic: External dependency, overkill for Phase I

### AD-002: Storage Abstraction Layer

**Decision**: Create `TaskStore` class wrapping in-memory list
**Rationale**:
- Encapsulates ID generation logic
- Single point for CRUD operations
- Easy to swap for database in Phase II
- Follows DRY - all task operations in one place

### AD-003: Command Handler Pattern

**Decision**: Separate handler functions for each operation
**Rationale**:
- Single responsibility per handler
- Easy to test individually
- Easy to extend (add new commands)
- Clear command-to-function mapping

### AD-004: Interactive REPL Loop

**Decision**: Infinite loop with menu display and command dispatch
**Rationale**:
- Standard CLI pattern for interactive apps
- User always sees available options
- Graceful exit via quit command
- Ctrl+C handled at top level
