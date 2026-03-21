from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from kagent.core.response_formatter import print_formatted_response
from kagent.history.convo_memory import ConversationMemory
from kagent.logging.chat_logger import ChatLogger
from kagent.models.ollama_model import OllamaModel


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
            response = self.generate_ai_response(self.model, self.memory)

            # Store conversation
            self.memory.add_ai_message(response.get("content", ""))

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
