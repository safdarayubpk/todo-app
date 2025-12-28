"""Main entry point for Todo App.

Provides the REPL loop and command dispatch.
"""

from src.cli.handlers import (
    add_task,
    delete_task,
    list_tasks,
    toggle_complete,
    update_task,
)
from src.cli.menu import display_menu, get_user_choice
from src.storage.memory import TaskStore


def main() -> None:
    """Run the Todo App main loop.

    Displays menu, gets user choice, and dispatches to appropriate handler.
    Continues until user selects quit or presses Ctrl+C.
    """
    store = TaskStore()

    while True:
        display_menu()
        choice = get_user_choice()

        if choice == "1":
            add_task(store)
        elif choice == "2":
            list_tasks(store)
        elif choice == "3":
            update_task(store)
        elif choice == "4":
            delete_task(store)
        elif choice == "5":
            toggle_complete(store)
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Error: Invalid choice. Please enter 1-6.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except EOFError:
        print("\nGoodbye!")
