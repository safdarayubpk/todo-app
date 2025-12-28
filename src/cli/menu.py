"""Menu display and input handling for Todo App CLI.

Provides functions for displaying the main menu and getting user input.
"""


def display_menu() -> None:
    """Display the main menu with all available options."""
    print("\n=== Todo App ===")
    print("1. Add task")
    print("2. List tasks")
    print("3. Update task")
    print("4. Delete task")
    print("5. Toggle complete")
    print("6. Quit")
    print("================")


def get_user_choice() -> str:
    """Get and validate user's menu choice.

    Returns:
        The user's choice as a string (1-6 or invalid input).
    """
    return input("Enter choice: ").strip()


def get_task_id(prompt: str = "Enter task ID: ") -> int | None:
    """Get and validate a task ID from user input.

    Args:
        prompt: The prompt to display to the user.

    Returns:
        Valid positive integer ID, or None if input is invalid.
        Prints appropriate error messages for invalid input.
    """
    try:
        value = input(prompt).strip()
        task_id = int(value)
        if task_id <= 0:
            print("Error: ID must be a positive number")
            return None
        return task_id
    except ValueError:
        print("Error: Please enter a valid number")
        return None
