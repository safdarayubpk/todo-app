"""MCP Server module for Todo Task Operations.

This module provides an MCP (Model Context Protocol) server that exposes
task management tools to AI agents. The server uses FastMCP with stdio transport.

Run via: uv run python -m app.mcp_server.server
"""

# Note: Do not import mcp here as this module is run as a subprocess
# The server is accessed via MCPServerStdio, not direct import

__all__: list[str] = []
