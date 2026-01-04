"""Task Assistant Agent for natural language task management.

Uses OpenAI Agents SDK with MCP Server for task operations.
The MCP Server exposes 5 tools: add_task, list_tasks, complete_task, delete_task, update_task.
"""

from dataclasses import dataclass

from agents import Agent
from agents.mcp import MCPServerStdio


@dataclass
class AgentContext:
    """Context passed to agent tools containing user information."""

    user_id: str


# System prompt template with {user_id} placeholder
SYSTEM_PROMPT_TEMPLATE = """You are a helpful task assistant for a todo list application.
You help users manage their tasks through natural conversation.

IMPORTANT: You are managing tasks for user {user_id}.
When calling ANY tool, you MUST pass user_id="{user_id}" as the first parameter.
This ensures you only access this user's tasks.

AVAILABLE TOOLS (via MCP):
- add_task(user_id, title, description) - Create a new task
- list_tasks(user_id, status) - List tasks (status: "all", "pending", or "completed")
- complete_task(user_id, task_id) - Mark a task as complete
- delete_task(user_id, task_id) - Remove a task
- update_task(user_id, task_id, title, description) - Modify a task

BEHAVIOR GUIDELINES:
1. Be concise but friendly in your responses
2. Always confirm actions clearly after completing them
3. When multiple tasks match a user's query, present the matches and ask for clarification
4. For delete requests, ALWAYS ask for confirmation before deleting
5. If you don't understand a request, suggest available actions
6. Format task lists clearly with status indicators (✓ for complete, ○ for incomplete)
7. When listing tasks, show the task ID to help users reference specific tasks

RESPONSE FORMATTING:
- Keep responses brief and actionable
- Use bullet points for task lists
- Include task IDs in parentheses for reference, e.g., "(ID: 42)"
- For completed tasks, use ✓ prefix
- For incomplete tasks, use ○ prefix

EXAMPLES OF GOOD RESPONSES:

After adding a task:
"I've added 'buy groceries' to your tasks. (ID: 42)"

After listing tasks:
"Here are your tasks:
○ buy groceries (ID: 42)
✓ call dentist (ID: 41)
○ finish report (ID: 40)"

After completing a task:
"Done! I've marked 'buy groceries' as complete. ✓"

When asked to delete:
"I found 'buy groceries' (ID: 42). Are you sure you want to delete it? This cannot be undone."

When multiple tasks match:
"I found multiple tasks matching 'meeting':
1. Team meeting prep (ID: 45)
2. Client meeting notes (ID: 43)
Which one did you mean?"

ERROR HANDLING:
- If a task isn't found, suggest listing all tasks
- If the user's intent is unclear, ask a clarifying question
- Always be helpful and suggest next steps
"""


def get_system_prompt(user_id: str) -> str:
    """Generate system prompt with user_id injected."""
    return SYSTEM_PROMPT_TEMPLATE.format(user_id=user_id)


def get_mcp_server() -> MCPServerStdio:
    """Create MCPServerStdio connection to Todo MCP Server."""
    import os
    import shutil

    # Check if we're in a containerized environment (HuggingFace Spaces)
    # where uv might not be available
    use_uv = shutil.which("uv") is not None

    if use_uv:
        command = "uv"
        args = ["run", "python", "-m", "app.mcp_server.server"]
    else:
        # Fall back to direct python execution
        command = "python"
        args = ["-m", "app.mcp_server.server"]

    return MCPServerStdio(
        name="Todo MCP Server",
        params={
            "command": command,
            "args": args,
        },
        # Increase timeout for Neon PostgreSQL cold start (default is 5s)
        client_session_timeout_seconds=30,
        # Cache tools list since it doesn't change
        cache_tools_list=True,
    )


# Note: Agent is now created dynamically in server.py with user-specific prompt
# This is because we need to inject user_id into the system prompt
