# Todo App - Phase I Console Application

A simple command-line todo application with in-memory storage, implementing basic CRUD operations.

## Features

- **Add tasks** with title and optional description
- **List tasks** with completion status indicators ([x] / [ ])
- **Update tasks** - modify title and description
- **Delete tasks** by ID
- **Toggle completion** status

## Requirements

- Python 3.13+
- UV package manager

## Installation

```bash
cd todoapp
uv sync
```

## Usage

```bash
uv run python -m src.main
```

### Menu Options

```
=== Todo App ===
1. Add task
2. List tasks
3. Update task
4. Delete task
5. Toggle complete
6. Quit
================
```

## Project Structure

```
src/
├── __init__.py          # Package marker
├── main.py              # Entry point with REPL loop
├── models/
│   └── task.py          # Task dataclass
├── storage/
│   └── memory.py        # In-memory TaskStore
└── cli/
    ├── menu.py          # Menu display
    └── handlers.py      # Command handlers
```

## Phase I Limitations

- In-memory storage only (data lost on exit)
- Single-user, single-session
- Console interface only

These will be addressed in subsequent phases.

## License

MIT
