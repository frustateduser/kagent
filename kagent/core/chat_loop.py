from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from kagent.core.response_formatter import print_formatted_response
from kagent.history.convo_memory import ConversationMemory
from kagent.logging.chat_logger import ChatLogger
from kagent.models.ollama_model import OllamaModel
from kagent.tools.command_execution import CommandExecution
from kagent.tools.fileaccess import FileAccess
from kagent.config.tools import tools as builtin_tools
from kagent.tools.mcp_client.registry import MCPRegistry

"""
Main chat loop handler for the kagent application.
"""

class ChatLoop:
    console = Console()

    def __init__(self, system_prompt: str):
        """
        Start the interactive chat session.
        """

        self.memory = ConversationMemory(system_prompt)
        self.model = OllamaModel()
        self.chat_logger = ChatLogger()
        self.command_execution = CommandExecution()
        self.file_access = FileAccess()

        # ------------------------------------------------------------------
        # Boot MCP clients and merge their tools with the built-in tool list
        # ------------------------------------------------------------------
        self.console.print("\n[bold cyan]Loading MCP servers...[/bold cyan]")
        self.mcp = MCPRegistry()
        self.mcp.load()

        mcp_tools = self.mcp.get_all_tools()
        self.all_tools = builtin_tools + mcp_tools

        if mcp_tools:
            self.console.print(
                f"[green]{len(mcp_tools)} MCP tool(s) available across "
                f"{len(self.mcp.clients)} server(s).[/green]\n"
            )
            # Inject the MCP tool definitions into the system prompt so the
            # model knows it can call them.
            self._inject_mcp_tools_into_prompt(mcp_tools)
        else:
            self.console.print("[yellow]No MCP tools loaded.[/yellow]\n")

        # ------------------------------------------------------------------

        session = self.create_prompt_session()

        self.console.print("\n[red]Type 'exit' to quit[/red]\n")
        self.console.print("[red]Press 'ctrl + D' to send the message[/red]\n")

        try:
            while True:
                self.console.print("[bold red]You: [/bold red]")
                user_input = session.prompt(
                    "\n",
                      multiline=True
                )

                if user_input.lower() in {"exit", "quit"}:
                    self.console.print("[bold yellow]Goodbye![/bold yellow]")
                    self.mcp.shutdown()
                    break

                self.chat_logger.log_user(user_input)
                self.memory.add_user_message(user_input)

                # Generate AI response
                response = self.loop()

                # Log response
                self.chat_logger.log_agent(response)

                # Display response
                print_formatted_response(response)

        finally:
            # Always shut down MCP subprocesses cleanly on exit
            self.mcp.shutdown()

    # ------------------------------------------------------------------
    # MCP prompt injection
    # ------------------------------------------------------------------

    def _inject_mcp_tools_into_prompt(self, mcp_tools: list[dict]) -> None:
        """
        Append MCP tool descriptions to the system message in conversation memory
        so the model knows these tools exist.
        """
        lines = ["\n\n--- MCP Tools ---"]
        lines.append(
            "The following additional tools are available via MCP servers. "
            "Call them exactly like the built-in tools, using their full name.\n"
        )
        for t in mcp_tools:
            lines.append(f"Tool: {t['name']}")
            lines.append(f"  Description: {t['description']}")
            props = t["parameters"].get("properties", {})
            if props:
                lines.append(f"  Parameters: {', '.join(props.keys())}")
            lines.append("")

        mcp_section = "\n".join(lines)
        # self.console.print(mcp_section) # Debug: print the injected prompt section to verify formatting
        self.memory.add_system_message(mcp_section)

    # ------------------------------------------------------------------
    # Prompt session
    # ------------------------------------------------------------------

    def create_prompt_session(self) -> PromptSession:
        """
        Create a prompt session with custom key bindings.
        Ctrl+D will submit the multi-line message.
        """
        kb = KeyBindings()

        @kb.add("c-d")
        def submit_message(event):
            event.app.exit(result=event.app.current_buffer.text)

        return PromptSession(key_bindings=kb)

    # ------------------------------------------------------------------
    # Response generation
    # ------------------------------------------------------------------

    def generate_ai_response(self, model: OllamaModel, memory: ConversationMemory) -> str:
        """Generate response from LLM with spinner."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold cyan]Generating response...[/bold cyan]"),
            transient=True,
        ) as progress:
            progress.add_task("thinking", total=None)
            response = model.generate(memory.get_history())
        return response

    def loop(self):
        """
        ReACT loop: generate → handle tool → generate → ... → final response.
        """
        while True:
            response = self.generate_ai_response(self.model, self.memory)
            self.memory.add_ai_message(response.get("content", ""))

            if response.get("type") == "final":
                return response

            elif response.get("type") == "tool":
                tool_name  = response.get("tool")
                tool_input = response.get("input")

                tool_result  = self.handle_tool(tool_name, tool_input)
                tool_message = self.format_tool_result(tool_name, tool_result)
                self.memory.add_ai_message(tool_message)
                self.chat_logger.log_tool({
                    "tool":   tool_name,
                    "input":  tool_input,
                    "output": tool_result,
                })
            else:
                self.memory.add_ai_message(response.get("content", ""))
                self.chat_logger.log_agent(response)
                return response

    # ------------------------------------------------------------------
    # Tool routing
    # ------------------------------------------------------------------

    def handle_tool(self, tool_name: str, tool_input):
        """
        Route tool calls to the correct handler.
        MCP tools (prefixed mcp__) are forwarded to the MCPRegistry.
        """

        # --- MCP tools ---
        if MCPRegistry.is_mcp_tool(tool_name):
            return self._handle_mcp_tool(tool_name, tool_input)

        # --- Built-in tools ---
        match tool_name:
            case "shell":
                return self.command_execution.execute(tool_input)
            case "list_files":
                return self.file_access.list_files(tool_input)
            case "read_file":
                return self.file_access.read_file(tool_input)
            case "write_file":
                path    = tool_input[0].get("path")
                content = tool_input[0].get("content")
                return self.file_access.write_file(path, content)
            case _:
                return {"status": "error", "output": f"Unknown tool: {tool_name}"}

    def _handle_mcp_tool(self, tool_name: str, tool_input) -> dict:
        """
        Forward a namespaced MCP tool call to the registry and normalise
        the result into kagent's standard {"status", "output"} dict.
        """
        # tool_input may arrive as a dict or a list-of-dicts depending on
        # how the model serialises it — normalise to a plain dict.
        if isinstance(tool_input, list):
            arguments = tool_input[0] if tool_input else {}
        elif isinstance(tool_input, dict):
            arguments = tool_input
        else:
            arguments = {}

        try:
            output = self.mcp.call_tool(tool_name, arguments)
            return {"status": "success", "output": output}
        except Exception as exc:
            return {"status": "error", "output": str(exc)}

    # ------------------------------------------------------------------
    # Formatting
    # ------------------------------------------------------------------

    def format_tool_result(self, tool_name: str, tool_result) -> str:
        """Format tool result into an LLM-readable string."""
        if isinstance(tool_result, dict):
            output = tool_result.get("output", "")
            status = tool_result.get("status", "unknown")
        else:
            output = str(tool_result)
            status = "unknown"

        return f"""
            Role: Tool
            Tool: {tool_name}
            Status: {status}

            Output:
            {output}
        """