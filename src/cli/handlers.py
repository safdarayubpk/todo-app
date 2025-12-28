"""Command handlers for Todo App CLI.

Provides handler functions for each menu operation.
"""

from src.cli.menu import get_task_id
from src.models.task import Task
from src.storage.memory import TaskStore


def list_tasks(store: TaskStore) -> None:
    """Display all tasks with ID, status indicator, and title.

    Args:
        store: The TaskStore containing tasks to display.
    """
    tasks = store.list_all()

    if not tasks:
        print("No tasks found.")
        return

    print("\n=== Your Tasks ===")
    for task in tasks:
        _display_task(task)
    print("==================")


def _display_task(task: Task) -> None:
    """Display a single task with formatting.

    Args:
        task: The Task to display.
    """
    status = "[x]" if task.completed else "[ ]"
    print(f"  {task.id}. {status} {task.title}")
    if task.description:
        print(f"         {task.description}")


def add_task(store: TaskStore) -> None:
    """Handle adding a new task.

    Prompts for title (required) and description (optional).

    Args:
        store: The TaskStore to add the task to.
    """
    # Get title with validation
    title = input("Enter task title: ").strip()
    if not title:
        print("Error: Title cannot be empty")
        return

    # Get optional description
    description = input("Enter description (optional, press Enter to skip): ").strip()
    if not description:
        description = None

    # Create the task
    task = store.add(title, description)
    print(f"Task added: {task.id}. {task.title}")


def toggle_complete(store: TaskStore) -> None:
    """Handle toggling task completion status.

    Args:
        store: The TaskStore containing the task.
    """
    task_id = get_task_id("Enter task ID to toggle: ")
    if task_id is None:
        return

    task = store.get(task_id)
    if task is None:
        print("Error: Task not found")
        return

    store.toggle_complete(task_id)
    status = "complete" if task.completed else "incomplete"
    print(f"Task {task_id} marked as {status}.")


def update_task(store: TaskStore) -> None:
    """Handle updating task title and/or description.

    Args:
        store: The TaskStore containing the task.
    """
    task_id = get_task_id("Enter task ID to update: ")
    if task_id is None:
        return

    task = store.get(task_id)
    if task is None:
        print("Error: Task not found")
        return

    # Get new title
    print(f"Current title: {task.title}")
    new_title = input("Enter new title (press Enter to keep current): ").strip()

    if new_title:
        # Validate non-empty if provided
        if not new_title.strip():
            print("Error: Title cannot be empty")
            return
    else:
        new_title = None  # Keep current

    # Get new description
    current_desc = task.description if task.description else "None"
    print(f"Current description: {current_desc}")
    new_description = input("Enter new description (press Enter to keep current): ")

    # Empty string means keep current, but we need to distinguish from "clear description"
    if new_description == "":
        new_description = None  # Keep current
    else:
        new_description = new_description.strip() if new_description.strip() else None

    # Apply updates
    if new_title is not None or new_description is not None:
        store.update(task_id, title=new_title, description=new_description)

    print(f"Task {task_id} updated.")


def delete_task(store: TaskStore) -> None:
    """Handle deleting a task.

    Args:
        store: The TaskStore containing the task.
    """
    task_id = get_task_id("Enter task ID to delete: ")
    if task_id is None:
        return

    if not store.delete(task_id):
        print("Error: Task not found")
        return

    print(f"Task {task_id} deleted.")
