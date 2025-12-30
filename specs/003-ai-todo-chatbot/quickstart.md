# Quickstart Guide: AI-Powered Todo Chatbot (MCP Architecture)

**Feature**: 003-ai-todo-chatbot
**Date**: 2025-12-29 (Updated for MCP)

## Prerequisites

- Node.js 18+ (for frontend)
- Python 3.11+ with UV (for backend)
- OpenAI API key
- Existing Phase II Todo app running (frontend + backend)

## Technology Stack

| Component | Package | Version |
|-----------|---------|---------|
| Frontend Chat UI | Existing ChatKit UI | - |
| Backend Server | FastAPI | Existing |
| AI Framework | `openai-agents` | ^0.6.0 |
| **MCP SDK** | **`mcp`** | **^1.0.0** |

## Environment Setup

### 1. Backend Environment

Verify `backend/.env` contains:

```bash
# Existing variables (should already be present)
DATABASE_URL=postgresql+asyncpg://...
BETTER_AUTH_URL=http://localhost:3000

# OpenAI API key for Agents SDK (already present)
OPENAI_API_KEY=sk-your-openai-api-key

# Secret for signing ChatKit session tokens (already present)
CHATKIT_SECRET_KEY=your-random-secret-key-here
```

### 2. Frontend Environment

Verify `frontend/.env.local` contains:

```bash
# Existing variables (should already be present)
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_CHATKIT_URL=http://localhost:8000
```

## Installation

### Backend Dependencies (MCP SDK)

```bash
cd backend

# Add Official MCP SDK (FastMCP)
uv add mcp

# Verify installation
uv run python -c "from mcp.server.fastmcp import FastMCP; print('MCP SDK OK')"

# Verify Agents SDK with MCP support
uv run python -c "from agents.mcp import MCPServerStdio; print('Agents MCP OK')"
```

## MCP Server Setup

### 1. Create MCP Server Module

```bash
mkdir -p backend/app/mcp_server
touch backend/app/mcp_server/__init__.py
touch backend/app/mcp_server/server.py
```

### 2. Implement MCP Server

Create `backend/app/mcp_server/server.py`:

```python
"""MCP Server for Todo Task Operations"""
from mcp.server.fastmcp import FastMCP

# Initialize MCP Server
mcp = FastMCP("Todo MCP Server")

@mcp.tool()
def add_task(user_id: str, title: str, description: str | None = None) -> dict:
    """Add a new task to the user's todo list."""
    # Implementation connects to database
    ...

@mcp.tool()
def list_tasks(user_id: str, status: str = "all") -> list[dict]:
    """List all tasks for the specified user."""
    ...

@mcp.tool()
def complete_task(user_id: str, task_id: int) -> dict:
    """Mark a task as complete."""
    ...

@mcp.tool()
def delete_task(user_id: str, task_id: int) -> dict:
    """Delete a task from the user's list."""
    ...

@mcp.tool()
def update_task(user_id: str, task_id: int, title: str | None = None, description: str | None = None) -> dict:
    """Update a task's title or description."""
    ...

if __name__ == "__main__":
    mcp.run()  # Runs with stdio transport
```

### 3. Test MCP Server Independently

```bash
cd backend

# Test MCP server starts without errors
uv run python -m app.mcp_server.server
# Should start and wait for MCP protocol commands via stdin
# Press Ctrl+C to exit
```

### 4. Connect Agent to MCP Server

Update `backend/app/chatkit/agent.py`:

```python
from agents import Agent, Runner
from agents.mcp import MCPServerStdio

# MCP Server connection
mcp_server = MCPServerStdio(
    name="Todo MCP Server",
    params={
        "command": "uv",
        "args": ["run", "python", "-m", "app.mcp_server.server"],
    },
)

async def handle_chat(message: str, user_id: str):
    """Handle chat message with MCP tools."""
    async with mcp_server as server:
        agent = Agent(
            name="TaskAssistant",
            instructions=f"You are a task assistant for user {user_id}. Always pass user_id=\"{user_id}\" to all tools.",
            mcp_servers=[server],
        )
        result = await Runner.run(agent, message)
        return result.final_output
```

## Quick Verification

### Test Backend with MCP

```bash
cd backend

# Start the backend server
uv run uvicorn app.main:app --reload --port 8000

# Test health endpoint
curl http://localhost:8000/api/v1/health
# Expected: {"status": "healthy"}

# Test chat endpoint (requires auth)
curl -X POST http://localhost:8000/chatkit \
  -H "Content-Type: application/json" \
  -d '{"message": "Show my tasks"}'
# Expected: Streaming response or 401 if not authenticated
```

### Test Frontend Chat

1. Start frontend: `cd frontend && npm run dev`
2. Open http://localhost:3000
3. Log in with existing credentials
4. Navigate to `/chat` or click "Chat Assistant" button
5. Type "Show my tasks" and press Enter
6. Verify streaming response with task list

## Development Workflow

### 1. Local Development

Start both services in separate terminals:

```bash
# Terminal 1: Backend
cd backend
uv run uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev
```

### 2. MCP Server Development

When modifying MCP tools, the backend will auto-reload. Test changes:

```bash
# Test MCP server directly
cd backend
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}' | uv run python -m app.mcp_server.server
```

## Demo Script

Use these interactions to verify the chatbot works with MCP:

```
1. User: "What can you help me with?"
   Expected: List of available MCP tools (add, list, complete, delete, update)

2. User: "Add a task to buy groceries"
   Expected: MCP tool call → task created confirmation

3. User: "Show my tasks"
   Expected: MCP tool call → list of tasks

4. User: "Mark groceries as done"
   Expected: MCP tool call → task marked complete

5. User: "Delete the groceries task"
   Expected: Confirmation prompt, then MCP tool call → task deleted
```

## File Structure After Implementation

```
backend/
├── app/
│   ├── mcp_server/           # NEW: MCP Server module
│   │   ├── __init__.py
│   │   └── server.py         # FastMCP server with 5 tools
│   ├── chatkit/              # UPDATED: Uses MCP
│   │   ├── __init__.py
│   │   ├── agent.py          # Agent with MCPServerStdio
│   │   ├── context.py        # Session handling
│   │   └── server.py         # Chat endpoint
│   ├── models/
│   │   ├── task.py           # Existing
│   │   ├── conversation.py   # NEW: Conversation model
│   │   └── message.py        # NEW: Message model
│   └── main.py

frontend/
├── app/
│   ├── chat/
│   │   └── page.tsx          # Chat page
│   └── api/
│       └── chatkit/
│           └── session/
│               └── route.ts  # Session endpoint
├── components/
│   └── chat/
│       └── TodoChat.tsx      # Chat component
└── lib/
    └── chatkit/
        └── config.ts
```

## Troubleshooting

### MCP Server not starting

```bash
# Check MCP SDK installed
uv run python -c "from mcp.server.fastmcp import FastMCP; print('OK')"

# Check server module path
uv run python -c "import app.mcp_server.server; print('OK')"
```

### "Tool not found" error

- Verify MCP server defines all 5 tools with `@mcp.tool()` decorator
- Check tool function signatures match expected parameters
- Restart backend after MCP server changes

### Agent not connecting to MCP

- Verify `MCPServerStdio` command and args are correct
- Check UV is available in PATH
- Test MCP server runs standalone first

### User ID not passed to tools

- Update system prompt to explicitly include user_id
- Verify agent instructions mention user_id requirement
- Check tool definitions require user_id parameter

## Testing

### Run MCP Tool Unit Tests (18 tests)

```bash
cd backend
uv run python tests/test_mcp_tools.py
```

Expected output: All 18 tests pass, covering:
- add_task, list_tasks, complete_task, delete_task, update_task
- User isolation verification
- Input validation

### Run Chat Integration Tests (8 tests)

```bash
cd backend
uv run python tests/test_chat_integration.py
```

Expected output: All 8 tests pass, covering:
- Session authentication
- Conversation history
- User isolation in chat
- Message persistence

### Run Demo Script

```bash
cd backend
uv run python tests/test_demo_script.py
```

This runs the 5 demo interactions from the Demo Script section above.

## Implementation Status

**✅ COMPLETE**: All phases implemented and tested

| Phase | Status | Key Files |
|-------|--------|-----------|
| Setup (MCP SDK) | ✅ | `pyproject.toml` |
| MCP Server | ✅ | `app/mcp_server/server.py` |
| Agent Integration | ✅ | `app/chatkit/agent.py` |
| Add Task (US1) | ✅ | MCP tool + tests |
| View Tasks (US2) | ✅ | MCP tool + tests |
| Complete Task (US3) | ✅ | MCP tool + tests |
| Delete Task (US4) | ✅ | MCP tool + tests |
| Update Task (US5) | ✅ | MCP tool + tests |
| Real-time Sync (US6) | ✅ | refresh-tasks event |
| Chat History (US7) | ✅ | conversation.py |
| Error Handling | ✅ | Try-catch in all tools |
| UX Polish | ✅ | Responsive design |
| Security | ✅ | User isolation verified |
| Testing | ✅ | 26 tests total |

## Next Steps (Post-Implementation)

1. Monitor OpenAI API usage and costs
2. Consider caching frequent queries
3. Add conversation search functionality
4. Implement conversation deletion

## References

- [Official MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [FastMCP Documentation](https://github.com/modelcontextprotocol/python-sdk#fastmcp)
- [OpenAI Agents SDK MCP Docs](https://github.com/openai/openai-agents-python/blob/main/docs/mcp.md)
