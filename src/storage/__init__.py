"""Storage package for Todo App.

Contains storage implementations for task persistence.
"""

from src.storage.memory import TaskStore

__all__ = ["TaskStore"]
