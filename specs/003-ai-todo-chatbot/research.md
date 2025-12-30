# Technology Research: AI-Powered Todo Chatbot (MCP Architecture)

**Feature**: 003-ai-todo-chatbot
**Date**: 2025-12-29 (Updated)
**Spec**: [spec.md](./spec.md)

## Executive Summary

This document captures technology research for implementing the AI-Powered Todo Chatbot feature using the **required Phase III tech stack**: OpenAI ChatKit (frontend), OpenAI Agents SDK (AI framework), and **Official MCP SDK** (tool integration via MCP protocol).

**Key Architecture Decision**: Per hackathon requirements, task tools MUST be implemented as an MCP Server using the Official MCP SDK, with the OpenAI Agents SDK connecting to MCP tools via the MCP protocol.

## Required Technology Stack

| Component | Technology | Package | Status |
|-----------|------------|---------|--------|
| Frontend Chat UI | OpenAI ChatKit | `@openai/chatkit-react` | Existing |
| Backend Server | FastAPI | `fastapi` | Existing |
| AI Framework | OpenAI Agents SDK | `openai-agents` | Existing |
| **MCP Server** | **Official MCP SDK** | **`mcp`** | **NEW - Required** |
| ORM | SQLModel | `sqlmodel` | Existing |
| Database | Neon PostgreSQL | (existing) | Existing |
| Authentication | Better Auth | (existing) | Existing |

## Architecture Overview (Updated for MCP)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Next.js Frontend                                 │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │                  OpenAI ChatKit Component                            ││
│  │   • Embedded chat widget with streaming                              ││
│  │   • Session management via getClientSecret                           ││
│  └─────────────────────────────────────────────────────────────────────┘│
│                              │                                           │
│                              ▼ HTTP/SSE                                  │
└──────────────────────────────│──────────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────────┐
│                     FastAPI Backend                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │              POST /chatkit Endpoint (SSE Streaming)                  ││
│  └─────────────────────────────────────────────────────────────────────┘│
│                              │                                           │
│                              ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │              OpenAI Agents SDK (Agent + Runner)                      ││
│  │   • Task Assistant Agent with system prompt                          ││
│  │   • Connects to MCP Server via MCPServerStdio                        ││
│  │   • Uses mcp_servers parameter for tool access                       ││
│  └───────────────────────────┬─────────────────────────────────────────┘│
│                              │ MCP Protocol                              │
│                              ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │              MCP Server (Official MCP SDK - FastMCP)                 ││
│  │   • 5 MCP Tools: add_task, list_tasks, complete_task,                ││
│  │                  delete_task, update_task                            ││
│  │   • Direct database access via SQLModel                              ││
│  │   • User isolation via user_id parameter                             ││
│  └───────────────────────────┬─────────────────────────────────────────┘│
│                              │                                           │
└──────────────────────────────│──────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        Neon PostgreSQL                                   │
│                     (tasks, conversations, messages)                     │
└─────────────────────────────────────────────────────────────────────────┘
```

## MCP Integration Research

### Decision: MCP Server Implementation Pattern

**Chosen Pattern**: FastMCP with stdio transport + MCPServerStdio connection

**Rationale**:
1. Official MCP SDK provides `FastMCP` for easy server creation
2. OpenAI Agents SDK provides `MCPServerStdio` for subprocess-based MCP connections
3. This pattern is well-documented and supported by both SDKs
4. Allows tools to run in the same process as FastAPI (spawned as subprocess)

**Alternatives Considered**:

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| FastMCP stdio + MCPServerStdio | Official, simple, well-documented | Subprocess overhead | **Selected** |
| FastMCP HTTP + MCPServerStreamableHttp | Network-based, scalable | More complex, separate port | Not selected |
| openai-agents-mcp package | Simplified API | Less control, additional dependency | Alternative |

### MCP Server Implementation (FastMCP)

**Package**: `mcp` (Official MCP Python SDK)

**Pattern**: Define MCP server with `@mcp.tool()` decorators:

```python
# backend/app/mcp_server/server.py
from mcp.server.fastmcp import FastMCP

# Initialize MCP Server
mcp = FastMCP("Todo MCP Server")

@mcp.tool()
def add_task(user_id: str, title: str, description: str | None = None) -> dict:
    """Add a new task to the user's todo list.

    Args:
        user_id: The authenticated user's ID
        title: The task title (required)
        description: Optional task description

    Returns:
        Dict with task_id, status, and title
    """
    # Database operation via SQLModel
    task = Task(user_id=user_id, title=title, description=description)
    session.add(task)
    session.commit()
    return {"task_id": task.id, "status": "created", "title": task.title}

@mcp.tool()
def list_tasks(user_id: str, status: str = "all") -> list[dict]:
    """Retrieve tasks for the specified user.

    Args:
        user_id: The authenticated user's ID
        status: Filter by "all", "pending", or "completed"

    Returns:
        Array of task objects
    """
    query = select(Task).where(Task.user_id == user_id)
    if status == "pending":
        query = query.where(Task.is_completed == False)
    elif status == "completed":
        query = query.where(Task.is_completed == True)
    tasks = session.exec(query).all()
    return [{"id": t.id, "title": t.title, "completed": t.is_completed} for t in tasks]

@mcp.tool()
def complete_task(user_id: str, task_id: int) -> dict:
    """Mark a task as complete."""
    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        return {"error": "Task not found"}
    task.is_completed = True
    session.commit()
    return {"task_id": task.id, "status": "completed", "title": task.title}

@mcp.tool()
def delete_task(user_id: str, task_id: int) -> dict:
    """Delete a task from the user's list."""
    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        return {"error": "Task not found"}
    title = task.title
    session.delete(task)
    session.commit()
    return {"task_id": task_id, "status": "deleted", "title": title}

@mcp.tool()
def update_task(user_id: str, task_id: int, title: str | None = None, description: str | None = None) -> dict:
    """Update a task's title or description."""
    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        return {"error": "Task not found"}
    if title:
        task.title = title
    if description is not None:
        task.description = description
    session.commit()
    return {"task_id": task.id, "status": "updated", "title": task.title}

# Entry point for MCP server
if __name__ == "__main__":
    mcp.run()  # Runs with stdio transport by default
```

### OpenAI Agents SDK MCP Connection

**Package**: `openai-agents` (version 0.6+)

**Pattern**: Connect to MCP server using `MCPServerStdio`:

```python
# backend/app/chatkit/agent.py
from agents import Agent, Runner
from agents.mcp import MCPServerStdio
from agents.model_settings import ModelSettings

# MCP Server connection
mcp_server = MCPServerStdio(
    name="Todo MCP Server",
    params={
        "command": "python",
        "args": ["-m", "app.mcp_server.server"],
    },
)

# Agent with MCP tools
async def create_agent_with_mcp():
    async with mcp_server as server:
        agent = Agent(
            name="TaskAssistant",
            instructions=SYSTEM_PROMPT,
            mcp_servers=[server],
            model_settings=ModelSettings(tool_choice="auto"),
        )
        return agent

# Chat endpoint handler
async def handle_chat(message: str, user_id: str):
    async with mcp_server as server:
        agent = Agent(
            name="TaskAssistant",
            instructions=SYSTEM_PROMPT.replace("{user_id}", user_id),
            mcp_servers=[server],
        )
        result = await Runner.run(agent, message)
        return result.final_output
```

### Alternative: openai-agents-mcp Package

**Package**: `openai-agents-mcp` (by LastMile AI)

This package simplifies MCP integration with configuration file:

```yaml
# mcp_agent.config.yaml
mcp:
  servers:
    todo:
      command: python
      args: ["-m", "app.mcp_server.server"]
```

```python
from agents_mcp import Agent, RunnerContext

agent = Agent(
    name="TaskAssistant",
    instructions=SYSTEM_PROMPT,
    mcp_servers=["todo"],  # Reference config
)

result = await Runner.run(agent, message, context=RunnerContext())
```

**Decision**: Use direct `MCPServerStdio` for more control and fewer dependencies.

## User ID Injection Strategy

**Challenge**: MCP tools need `user_id` for data isolation, but the agent doesn't know the user automatically.

**Solution**: Inject user_id into the system prompt and require tools to accept it as parameter:

```python
SYSTEM_PROMPT = """You are a task assistant for user {user_id}.

When calling any tool, ALWAYS pass user_id="{user_id}" as the first parameter.
This ensures you only access this user's tasks.

Available tools:
- add_task(user_id, title, description) - Create a new task
- list_tasks(user_id, status) - List tasks (status: all/pending/completed)
- complete_task(user_id, task_id) - Mark task as done
- delete_task(user_id, task_id) - Remove a task
- update_task(user_id, task_id, title, description) - Modify a task

Always confirm actions and ask for clarification when needed.
"""

# At runtime:
system_prompt = SYSTEM_PROMPT.format(user_id=current_user_id)
```

## Dependencies Update

### Backend (pyproject.toml additions)
```toml
[project.dependencies]
mcp = ">=1.0.0"  # Official MCP SDK with FastMCP
openai-agents = ">=0.6.0"  # OpenAI Agents SDK with MCP support
```

### Environment Variables
```bash
# Backend (.env)
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql+asyncpg://...
CHATKIT_SECRET_KEY=...  # For session signing
```

## Migration from Current Implementation

Current implementation uses `@function_tool` decorators directly in Agents SDK. Migration steps:

1. **Create MCP Server module**: `backend/app/mcp_server/`
   - `server.py` - FastMCP server with 5 tools
   - `__init__.py` - Module initialization

2. **Update Agent configuration**:
   - Remove `@function_tool` decorated functions
   - Add `MCPServerStdio` connection
   - Update agent to use `mcp_servers` parameter

3. **Update chat endpoint**:
   - Wrap agent creation in `async with mcp_server`
   - Pass user_id through system prompt

4. **Test MCP tools independently**:
   - Run MCP server directly: `python -m app.mcp_server.server`
   - Test with MCP inspector or direct stdio

## Performance Considerations

| Concern | Mitigation |
|---------|------------|
| MCP subprocess startup | Use connection pooling or keep-alive |
| Protocol overhead | Minimal for stdio transport |
| Database connections | Share SQLModel session across tools |
| User ID validation | Validate in each tool, not just prompt |

## References

- [Official MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [FastMCP Documentation](https://github.com/modelcontextprotocol/python-sdk/blob/main/README.md)
- [OpenAI Agents SDK MCP Docs](https://github.com/openai/openai-agents-python/blob/main/docs/mcp.md)
- [openai-agents-mcp Package](https://github.com/lastmile-ai/openai-agents-mcp)
