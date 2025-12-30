"""ChatKit server module for AI-powered todo chatbot.

This module provides:
- MCP Server with 5 task tools (add, list, complete, delete, update)
- AI agent with MCPServerStdio connection for natural language interactions
- Streaming chat endpoint with SSE
- Session management for authentication
"""

from .agent import AgentContext, get_system_prompt, get_mcp_server
from .server import router as chatkit_router

__all__ = ["AgentContext", "get_system_prompt", "get_mcp_server", "chatkit_router"]
