"""
kagent/tools/mcp_client/client.py

Wraps the async MCP Python SDK in a background thread so it integrates
cleanly with kagent's synchronous chat loop.

Each MCPClient manages ONE MCP server connection (stdio transport).
The server subprocess is kept alive for the duration of the session.
"""

import asyncio
import threading
from contextlib import AsyncExitStack
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPClient:
    """
    A synchronous wrapper around an async MCP ClientSession.

    Runs the async event loop in a daemon background thread so the
    subprocess pipe stays alive, while the main thread can call
    list_tools() / call_tool() as ordinary blocking calls.
    """

    def __init__(self, name: str, config: dict):
        """
        Args:
            name:   The server key from mcp_servers.json (e.g. "fetch", "git")
            config: The server config dict  {"command": ..., "args": [...], "env": {...}}
        """
        self.name = name
        self.config = config

        self.session: ClientSession | None = None
        self._tools: list = []          # raw mcp Tool objects
        self._error: Exception | None = None

        self._loop = asyncio.new_event_loop()
        self._thread: threading.Thread | None = None
        self._ready = threading.Event()  # set once connected (or failed)
        self._stop_event: asyncio.Event | None = None  # set to tear down

    # ------------------------------------------------------------------
    # Public sync API
    # ------------------------------------------------------------------

    def start(self) -> bool:
        """
        Spawn the background thread and wait until the server is ready.
        Returns True if connected successfully, False on timeout/error.
        """
        self._thread = threading.Thread(
            target=self._run_loop, daemon=True, name=f"mcp-{self.name}"
        )
        self._thread.start()
        connected = self._ready.wait(timeout=20)

        if not connected or self._error or self.session is None:
            return False
        return True

    def list_tools(self) -> list:
        """Return the list of mcp.types.Tool objects from this server."""
        return self._tools

    def call_tool(self, tool_name: str, arguments: dict) -> Any:
        """
        Call a tool on this server synchronously.
        Blocks until the server responds (timeout: 60 s).

        Returns a mcp.types.CallToolResult.
        """
        if not self.session:
            raise RuntimeError(f"MCP client '{self.name}' is not connected.")

        future = asyncio.run_coroutine_threadsafe(
            self.session.call_tool(tool_name, arguments),
            self._loop,
        )
        return future.result(timeout=60)

    def stop(self):
        """Gracefully shut down the server connection and subprocess."""
        if self._stop_event and self._loop and self._loop.is_running():
            self._loop.call_soon_threadsafe(self._stop_event.set)

    # ------------------------------------------------------------------
    # Internal async machinery
    # ------------------------------------------------------------------

    def _run_loop(self):
        """Entry point for the background thread."""
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._connect_and_run())

    async def _connect_and_run(self):
        """
        Opens the stdio transport + MCP session, fetches tools, signals
        readiness, then parks on an asyncio.Event so the session stays alive.
        Tool calls submitted via run_coroutine_threadsafe() execute here
        while this coroutine is suspended on the Event.
        """
        self._stop_event = asyncio.Event()

        try:
            async with AsyncExitStack() as stack:
                command = self.config["command"]
                args    = self.config.get("args", [])
                env     = self.config.get("env") or None

                params = StdioServerParameters(
                    command=command, args=args, env=env
                )

                read, write = await stack.enter_async_context(
                    stdio_client(params)
                )
                self.session = await stack.enter_async_context(
                    ClientSession(read, write)
                )
                await self.session.initialize()

                result = await self.session.list_tools()
                self._tools = result.tools

                self._ready.set()           # unblock start()

                await self._stop_event.wait()   # stay alive until stop()

        except Exception as exc:
            self._error = exc
            self._ready.set()               # unblock start() on failure