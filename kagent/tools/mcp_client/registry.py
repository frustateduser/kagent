"""
kagent/tools/mcp_client/registry.py

Reads mcp_servers.json, boots an MCPClient for every server,
and provides a single interface to:
  - get all MCP tools (in kagent's tool-dict format)
  - call any MCP tool by its namespaced name
  - shut everything down cleanly

Tool naming convention:  mcp__{server}__{tool_name}
  e.g.  mcp__fetch__fetch
        mcp__git__git_log
        mcp__memory__create_entities
"""

import json
from pathlib import Path

from rich.console import Console

from kagent.tools.mcp_client.client import MCPClient

console = Console()


class MCPRegistry:
    """
    Manages all MCP server connections for a kagent session.
    """

    def __init__(self, config_path: Path | None = None):
        """
        Args:
            config_path: Path to mcp_servers.json.
                         Defaults to <project_root>/mcp_servers.json.
        """
        if config_path is None:
            # Walk up from this file to find the project root
            config_path = Path(__file__).parent.parent / "registry.json"
        self.config_path = Path(config_path)

        self.clients: dict[str, MCPClient] = {}

        # kagent-format tool dicts  {"name": ..., "description": ..., "parameters": ...}
        self._agent_tools: list[dict] = []

        # namespaced_name  →  (server_name, real_tool_name)
        self._tool_map: dict[str, tuple[str, str]] = {}

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def load(self) -> None:
        """
        Read mcp_servers.json and connect to every server.
        Missing / unreachable servers are skipped with a warning.
        """
        if not self.config_path.exists():
            console.print(
                f"[yellow]⚠ registry.json not found at {self.config_path} — "
                "no MCP servers loaded.[/yellow]"
            )
            return

        with open(self.config_path, encoding="utf-8") as f:
            config = json.load(f)

        servers: dict = config.get("mcpServers", {})
        if not servers:
            console.print("[yellow]⚠ mcp_servers.json has no servers defined.[/yellow]")
            return

        for name, server_config in servers.items():
            self._connect_server(name, server_config)

    def shutdown(self) -> None:
        """Gracefully stop all running MCP clients."""
        for client in self.clients.values():
            client.stop()

    # ------------------------------------------------------------------
    # Tool interface
    # ------------------------------------------------------------------

    def get_all_tools(self) -> list[dict]:
        """
        Returns all MCP tools as kagent tool dicts, ready to be merged
        with the existing tools list and injected into the system prompt.
        """
        return self._agent_tools

    def call_tool(self, namespaced_name: str, arguments: dict):
        """
        Route a tool call to the correct MCP client.

        Args:
            namespaced_name:  e.g. "mcp__fetch__fetch"
            arguments:        dict of tool arguments from the model

        Returns:
            Extracted text output (str) from the MCP tool result.

        Raises:
            ValueError: if the tool name is unknown.
            RuntimeError: if the server is not connected.
        """
        if namespaced_name not in self._tool_map:
            raise ValueError(f"Unknown MCP tool: {namespaced_name!r}")

        server_name, real_name = self._tool_map[namespaced_name]
        client = self.clients[server_name]
        result = client.call_tool(real_name, arguments)
        return self._extract_result(result)

    @staticmethod
    def is_mcp_tool(tool_name: str) -> bool:
        """True if the tool name belongs to an MCP server."""
        return tool_name.startswith("mcp__")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _connect_server(self, name: str, config: dict) -> None:
        client = MCPClient(name, config)
        console.print(f"[cyan]  → Connecting to MCP server: [bold]{name}[/bold]...[/cyan]")

        success = client.start()

        if not success or client.session is None:
            err = getattr(client, "_error", None)
            console.print(
                f"[red]  ✗ {name}: failed to connect"
                + (f" ({err})" if err else "") + "[/red]"
            )
            return

        tools = client.list_tools()
        self.clients[name] = client

        for tool in tools:
            namespaced = f"mcp__{name}__{tool.name}"
            self._tool_map[namespaced] = (name, tool.name)
            self._agent_tools.append(self._to_agent_tool(namespaced, tool))

        console.print(
            f"[green]  ✓ {name}: {len(tools)} tool(s) — "
            + ", ".join(t.name for t in tools)
            + "[/green]"
        )

    @staticmethod
    def _to_agent_tool(namespaced_name: str, tool) -> dict:
        """
        Convert an mcp.types.Tool into kagent's tool-dict format.

        kagent format:
          {
            "name": str,
            "description": str,
            "parameters": { "type": "object", "properties": {...}, "required": [...] }
          }
        """
        schema = tool.inputSchema or {
            "type": "object",
            "properties": {},
            "required": [],
        }
        return {
            "name": namespaced_name,
            "description": tool.description or "",
            "parameters": schema,
        }

    @staticmethod
    def _extract_result(call_result) -> str:
        """
        Pull plain text out of a mcp.types.CallToolResult.
        Content is a list of TextContent / ImageContent etc.
        """
        if call_result.isError:
            parts = []
            for block in call_result.content:
                if hasattr(block, "text"):
                    parts.append(block.text)
            return "MCP tool error: " + " ".join(parts)

        parts = []
        for block in call_result.content:
            if hasattr(block, "text"):
                parts.append(block.text)
        return "\n".join(parts)