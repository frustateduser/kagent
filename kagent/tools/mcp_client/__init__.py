"""
kagent.tools.mcp_client

Generic MCP client layer for kagent.

Usage:
    from kagent.tools.mcp_client.registry import MCPRegistry

    registry = MCPRegistry()
    registry.load()                         # connects all servers from mcp_servers.json
    mcp_tools = registry.get_all_tools()    # list of agent-compatible tool dicts
    result = registry.call_tool("mcp__fetch__fetch", {"url": "https://example.com"})
    registry.shutdown()
"""

from kagent.tools.mcp_client.registry import MCPRegistry
from kagent.tools.mcp_client.client import MCPClient

__all__ = ["MCPRegistry", "MCPClient"]