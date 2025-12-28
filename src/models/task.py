"""Task model for Todo App.

Defines the Task dataclass representing a single todo item.
"""

from dataclasses import dataclass


@dataclass
class Task:
    """Represents a single todo item.

    Attributes:
        id: Unique sequential integer identifier (auto-assigned by TaskStore).
        title: Short text describing the task (required, non-empty).
        description: Optional longer text with additional details.
        completed: Boolean status indicating if task is done (defaults to False).
    """

    id: int
    title: str
    description: str | None = None
    completed: bool = False
