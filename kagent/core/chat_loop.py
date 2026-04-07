from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from kagent.core.response_formatter import print_formatted_response
from kagent.history.convo_memory import ConversationMemory
from kagent.logging.chat_logger import ChatLogger
from kagent.models.ollama_model import OllamaModel
from kagent.tools.command_execution import CommandExecution


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


        session = self.create_prompt_session()

        self.console.print("\n[red]Type 'exit' to quit[/red]\n")
        self.console.print("[red]Press 'ctrl + D' to send the message[/red]\n")

        while True:
            self.console.print("[bold red]You: [/bold red]")
            user_input = session.prompt(
                "\n",
                multiline=True
            )

            if user_input.lower() in {"exit", "quit"}:
                self.console.print("[bold yellow]Goodbye![/bold yellow]")
                break

            self.chat_logger.log_user(user_input)
            self.memory.add_user_message(user_input)

            # Generate AI response
            response = self.loop()

            # Log response
            self.chat_logger.log_agent(response)

            # Display response
            print_formatted_response(response)


    def create_prompt_session(self) -> PromptSession:
        """
        Create a prompt session with custom key bindings.
        Ctrl+D will submit the multi-line message.
        """

        kb = KeyBindings()

        @kb.add("c-d")
        def submit_message(event):
            """Submit multiline message."""
            event.app.exit(result=event.app.current_buffer.text)

        return PromptSession(key_bindings=kb)


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
        Runs until the model returns a final response following ReACT loop
        """

        while True:
            # Generate AI response
            response = self.generate_ai_response(self.model, self.memory)
            # store AI response
            self.memory.add_ai_message(response.get("content", ""))
            if response.get("type") == "final":
                return response
            elif response.get("type") == "tool":
                tool_name = response.get("tool")
                tool_input = response.get("input")
                tool_result = self.handle_tool(tool_name, tool_input)
                tool_message = self.format_tool_result(tool_name, tool_result)
                self.memory.add_ai_message(tool_message)
                self.chat_logger.log_tool({
                    "tool": tool_name, 
                    "input":tool_input, 
                    "output":tool_result
                })
            else:
                self.memory.add_ai_message(response.get("content", ""))
                self.chat_logger.log_agent(response)
                return response
            
    def handle_tool(self, tool_name, tool_input):
        match tool_name:
            case "shell":
                result = self.command_execution.execute(tool_input)
                return result
            case "read_file":
                return "Not Implemented"
            case "write_file":
                return "Not Implemented"
            case _:
                return f"Unknown tool: {tool_name}"

    def format_tool_result(self, tool_name, tool_result):
        """
        Format to LLM readable format results
        """
        if isinstance(tool_result, dict):
            output = tool_result.get("output", "")
            status = tool_result.get("status", "")
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