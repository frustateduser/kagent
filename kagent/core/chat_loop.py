from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from kagent.core.response_formatter import print_formatted_response
from kagent.history.convo_memory import ConversationMemory
from kagent.logging.chat_logger import ChatLogger
from kagent.models.ollama_model import OllamaModel
from kagent.tools.fileaccess import FileAccess


"""
Main chat loop handler for the kagent application.
"""
class ChatLoop:
    console = Console()

    def __init__(self):
        """
        Start the interactive chat session.
        """

        self.memory = ConversationMemory()
        self.model = OllamaModel()
        self.file_tool = FileAccess(root_dir="kagent")
        self.chat_logger = ChatLogger()


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


            # Tool: File Reading
            if self.handle_file_read(user_input, self.file_tool):
                continue

            # Generate AI response
            response = self.generate_ai_response(self.model, self.memory)

            # Store conversation
            self.memory.add_ai_message(response)

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


    def handle_file_read(self, user_input: str, file_tool: FileAccess) -> bool:
        """
        Handle file read command.

        Returns True if command was handled.
        """

        if not user_input.lower().startswith("read file"):
            return False

        file_name = user_input.replace("read file", "").strip()

        try:
            file_content = file_tool.read_file(file_name)

            self.console.print("\n[bold cyan]File content:[/bold cyan]\n")
            self.console.print(file_content)

        except Exception as e:
            self.console.print(f"[bold red]Error reading file:[/bold red] {e}")

        return True


    def generate_ai_response(self, model: OllamaModel, memory: ConversationMemory) -> str:
        """Generate response from LLM with spinner."""

        with Progress(
            SpinnerColumn(),
            TextColumn("[bold cyan]AI is thinking..."),
            transient=True,
        ) as progress:

            progress.add_task("thinking", total=None)
            response = model.generate(memory.get_history())

        return response
