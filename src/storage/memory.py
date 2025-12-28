"""In-memory storage for Todo App.

Provides TaskStore class for managing tasks in memory.
"""

from src.models.task import Task


class TaskStore:
    """In-memory storage for tasks.

    Manages a list of tasks with CRUD operations and automatic ID generation.
    IDs are sequential and never reused within a session.

    Attributes:
        _tasks: Internal list of Task objects.
        _next_id: Counter for generating unique task IDs.
    """

    def __init__(self) -> None:
        """Initialize an empty task store."""
        self._tasks: list[Task] = []
        self._next_id: int = 1

    def add(self, title: str, description: str | None = None) -> Task:
        """Create a new task and add it to the store.

        Args:
            title: The task title (required, should be non-empty).
            description: Optional description for the task.

        Returns:
            The newly created Task with assigned ID.
        """
        task = Task(
            id=self._next_id,
            title=title,
            description=description,
            completed=False,
        )
        self._tasks.append(task)
        self._next_id += 1
        return task

    def get(self, task_id: int) -> Task | None:
        """Find a task by its ID.

        Args:
            task_id: The ID of the task to find.

        Returns:
            The Task if found, None otherwise.
        """
        for task in self._tasks:
            if task.id == task_id:
                return task
        return None

    def list_all(self) -> list[Task]:
        """Return all tasks in creation order.

        Returns:
            A list of all tasks (may be empty).
        """
        return list(self._tasks)

    def update(
        self,
        task_id: int,
        title: str | None = None,
        description: str | None = None,
    ) -> bool:
        """Update a task's title and/or description.

        Args:
            task_id: The ID of the task to update.
            title: New title (if provided and non-empty).
            description: New description (if provided).

        Returns:
            True if task was found and updated, False if not found.
        """
        task = self.get(task_id)
        if task is None:
            return False

        if title is not None:
            task.title = title
        if description is not None:
            task.description = description

        return True

    def delete(self, task_id: int) -> bool:
        """Remove a task from the store.

        Args:
            task_id: The ID of the task to delete.

        Returns:
            True if task was found and deleted, False if not found.
        """
        task = self.get(task_id)
        if task is None:
            return False

        self._tasks.remove(task)
        return True

    def toggle_complete(self, task_id: int) -> bool:
        """Toggle the completion status of a task.

        Args:
            task_id: The ID of the task to toggle.

        Returns:
            True if task was found and toggled, False if not found.
        """
        task = self.get(task_id)
        if task is None:
            return False

        task.completed = not task.completed
        return True
