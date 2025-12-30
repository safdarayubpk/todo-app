"""MCP Tool Unit Tests (T074).

Tests the 5 MCP tools independently via direct function calls.
Verifies user isolation, input validation, and error handling.
"""

import os
import sys
import uuid

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv

load_dotenv()

# Import MCP tools directly
from app.mcp_server.server import (
    add_task,
    list_tasks,
    complete_task,
    delete_task,
    update_task,
)


class TestAddTask:
    """Tests for add_task MCP tool."""

    def test_add_task_success(self):
        """Test successful task creation."""
        user_id = f"test-user-{uuid.uuid4().hex[:8]}"
        result = add_task(user_id, "Test task", "Test description")

        assert "error" not in result
        assert result["status"] == "created"
        assert result["title"] == "Test task"
        assert "task_id" in result
        print(f"  PASS: add_task creates task successfully (ID: {result['task_id']})")

    def test_add_task_no_user_id(self):
        """Test add_task fails without user_id."""
        result = add_task("", "Test task")

        assert "error" in result
        assert "user_id is required" in result["error"]
        print("  PASS: add_task rejects empty user_id")

    def test_add_task_no_title(self):
        """Test add_task fails without title."""
        user_id = f"test-user-{uuid.uuid4().hex[:8]}"
        result = add_task(user_id, "")

        assert "error" in result
        assert "Title is required" in result["error"]
        print("  PASS: add_task rejects empty title")

    def test_add_task_title_too_long(self):
        """Test add_task fails with title > 255 chars."""
        user_id = f"test-user-{uuid.uuid4().hex[:8]}"
        long_title = "x" * 256
        result = add_task(user_id, long_title)

        assert "error" in result
        assert "255 characters" in result["error"]
        print("  PASS: add_task rejects title > 255 chars")


class TestListTasks:
    """Tests for list_tasks MCP tool."""

    def test_list_tasks_empty(self):
        """Test list_tasks returns empty for new user."""
        user_id = f"test-user-{uuid.uuid4().hex[:8]}"
        result = list_tasks(user_id)

        assert isinstance(result, list)
        assert len(result) == 0 or (len(result) > 0 and "error" not in result[0])
        print("  PASS: list_tasks returns list for new user")

    def test_list_tasks_with_tasks(self):
        """Test list_tasks returns created tasks."""
        user_id = f"test-user-{uuid.uuid4().hex[:8]}"

        # Create a task first
        add_result = add_task(user_id, "List test task")
        assert "error" not in add_result

        # List tasks
        result = list_tasks(user_id)

        assert isinstance(result, list)
        assert len(result) >= 1
        assert any(t["title"] == "List test task" for t in result)
        print("  PASS: list_tasks returns created tasks")

    def test_list_tasks_no_user_id(self):
        """Test list_tasks fails without user_id."""
        result = list_tasks("")

        assert len(result) == 1
        assert "error" in result[0]
        print("  PASS: list_tasks rejects empty user_id")

    def test_list_tasks_user_isolation(self):
        """Test user A cannot see user B's tasks."""
        user_a = f"user-a-{uuid.uuid4().hex[:8]}"
        user_b = f"user-b-{uuid.uuid4().hex[:8]}"

        # User A creates a task
        add_result = add_task(user_a, "User A private task")
        assert "error" not in add_result

        # User B should not see User A's task
        result = list_tasks(user_b)
        assert isinstance(result, list)
        for task in result:
            if "title" in task:
                assert "User A private task" not in task["title"]

        print("  PASS: list_tasks enforces user isolation")


class TestCompleteTask:
    """Tests for complete_task MCP tool."""

    def test_complete_task_success(self):
        """Test successful task completion."""
        user_id = f"test-user-{uuid.uuid4().hex[:8]}"

        # Create a task first
        add_result = add_task(user_id, "Complete me")
        task_id = add_result["task_id"]

        # Complete it
        result = complete_task(user_id, task_id)

        assert "error" not in result
        assert result["status"] == "completed"
        print(f"  PASS: complete_task marks task as complete (ID: {task_id})")

    def test_complete_task_not_found(self):
        """Test complete_task fails for non-existent task."""
        user_id = f"test-user-{uuid.uuid4().hex[:8]}"
        result = complete_task(user_id, 99999999)

        assert "error" in result
        assert "not found" in result["error"].lower()
        print("  PASS: complete_task rejects non-existent task")

    def test_complete_task_wrong_user(self):
        """Test user B cannot complete user A's task."""
        user_a = f"user-a-{uuid.uuid4().hex[:8]}"
        user_b = f"user-b-{uuid.uuid4().hex[:8]}"

        # User A creates a task
        add_result = add_task(user_a, "User A task to complete")
        task_id = add_result["task_id"]

        # User B tries to complete it
        result = complete_task(user_b, task_id)

        assert "error" in result
        assert "not found" in result["error"].lower() or "not owned" in result["error"].lower()
        print("  PASS: complete_task enforces user isolation")


class TestDeleteTask:
    """Tests for delete_task MCP tool."""

    def test_delete_task_success(self):
        """Test successful task deletion."""
        user_id = f"test-user-{uuid.uuid4().hex[:8]}"

        # Create a task first
        add_result = add_task(user_id, "Delete me")
        task_id = add_result["task_id"]

        # Delete it
        result = delete_task(user_id, task_id)

        assert "error" not in result
        assert result["status"] == "deleted"
        print(f"  PASS: delete_task removes task (ID: {task_id})")

    def test_delete_task_not_found(self):
        """Test delete_task fails for non-existent task."""
        user_id = f"test-user-{uuid.uuid4().hex[:8]}"
        result = delete_task(user_id, 99999999)

        assert "error" in result
        assert "not found" in result["error"].lower()
        print("  PASS: delete_task rejects non-existent task")

    def test_delete_task_wrong_user(self):
        """Test user B cannot delete user A's task."""
        user_a = f"user-a-{uuid.uuid4().hex[:8]}"
        user_b = f"user-b-{uuid.uuid4().hex[:8]}"

        # User A creates a task
        add_result = add_task(user_a, "User A task to delete")
        task_id = add_result["task_id"]

        # User B tries to delete it
        result = delete_task(user_b, task_id)

        assert "error" in result
        print("  PASS: delete_task enforces user isolation")


class TestUpdateTask:
    """Tests for update_task MCP tool."""

    def test_update_task_title(self):
        """Test updating task title."""
        user_id = f"test-user-{uuid.uuid4().hex[:8]}"

        # Create a task first
        add_result = add_task(user_id, "Original title")
        task_id = add_result["task_id"]

        # Update it
        result = update_task(user_id, task_id, title="Updated title")

        assert "error" not in result
        assert result["status"] == "updated"
        assert result["title"] == "Updated title"
        print(f"  PASS: update_task changes title (ID: {task_id})")

    def test_update_task_description(self):
        """Test updating task description."""
        user_id = f"test-user-{uuid.uuid4().hex[:8]}"

        # Create a task first
        add_result = add_task(user_id, "Task with description")
        task_id = add_result["task_id"]

        # Update description only
        result = update_task(user_id, task_id, description="New description")

        assert "error" not in result
        assert result["status"] == "updated"
        print(f"  PASS: update_task changes description (ID: {task_id})")

    def test_update_task_no_changes(self):
        """Test update_task fails with no changes specified."""
        user_id = f"test-user-{uuid.uuid4().hex[:8]}"

        # Create a task first
        add_result = add_task(user_id, "Task")
        task_id = add_result["task_id"]

        # Try to update with no changes
        result = update_task(user_id, task_id)

        assert "error" in result
        assert "no changes" in result["error"].lower()
        print("  PASS: update_task rejects empty update")

    def test_update_task_wrong_user(self):
        """Test user B cannot update user A's task."""
        user_a = f"user-a-{uuid.uuid4().hex[:8]}"
        user_b = f"user-b-{uuid.uuid4().hex[:8]}"

        # User A creates a task
        add_result = add_task(user_a, "User A task")
        task_id = add_result["task_id"]

        # User B tries to update it
        result = update_task(user_b, task_id, title="Hacked title")

        assert "error" in result
        print("  PASS: update_task enforces user isolation")


def run_all_tests():
    """Run all MCP tool tests."""
    print("\n" + "#" * 60)
    print("# MCP Tool Unit Tests (T074)")
    print("#" * 60)

    test_classes = [
        TestAddTask,
        TestListTasks,
        TestCompleteTask,
        TestDeleteTask,
        TestUpdateTask,
    ]

    total = 0
    passed = 0
    failed = 0

    for test_class in test_classes:
        print(f"\n{'=' * 50}")
        print(f"Testing: {test_class.__name__}")
        print("=" * 50)

        instance = test_class()
        methods = [m for m in dir(instance) if m.startswith("test_")]

        for method_name in methods:
            total += 1
            try:
                getattr(instance, method_name)()
                passed += 1
            except Exception as e:
                failed += 1
                print(f"  FAIL: {method_name}: {e}")

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Total: {total}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    print("\n" + ("All tests passed!" if failed == 0 else f"{failed} test(s) failed"))

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
