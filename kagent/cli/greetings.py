"""
CLI entrypoint for KAgent.

This module defines the main command-line interface using Typer.
It displays the banner, lets the user choose an operating mode,
and initializes the chat loop.
"""

import sys
import time

import typer
import questionary
from questionary import Choice
from prompt_toolkit.styles import Style
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from kagent.core.chat_loop import ChatLoop
from kagent.prompts.__init__ import prompt


app = typer.Typer()
console = Console()


BANNER = r"""
██╗  ██╗    █████╗  ██████╗ ███████╗███╗   ██╗████████╗
██║ ██╔╝   ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝
█████╔╝    ███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║   
██╔═██╗    ██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║   
██║  ██╗   ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║   
╚═╝  ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝   

                    AI CLI Agent

Welcome to KAgent, the knowledge agent that can help you with various tasks.
KAgent is a locally running AI agent system designed to assist you in daily task completion.
"""


def show_banner() -> None:
    """Display the application banner."""
    console.print(Panel.fit(BANNER, style="green"))


def get_prompt_style() -> Style:
    """Return the custom style used by questionary prompts."""
    return Style.from_dict(
        {
            "question": "bold",
            "pointer": "fg:#ff9d00 bold",
            "highlighted": "fg:#00ffcc bold",
        }
    )


def select_mode() -> str:
    """Prompt the user to choose an operating mode."""

    mode = questionary.select(
        "What do you want to do?",
        choices = [
            Choice("Ask questions / research", value="ask"),
            Choice("Generate code", value="code"),
            Choice("Debug errors", value="debug"),
            Choice("Ideas, architecture, planning", value="brainstorm"),
            Choice("Write content (email, blog, docs)", value="write"),
            Choice("Review code / content", value="review"),
            Choice("Step-by-step planning", value="plan"),
            Choice("Analyze data / logs", value="analyze"),
            Choice("Translate text", value="translate"),
            Choice("Exit → Exit kagent", value="exit"),
        ],
        style=get_prompt_style(),
    ).ask()

    return mode


def show_loading_sequence() -> None:
    """Display startup loading animation."""

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:

        task = progress.add_task("Starting kagent agent...", total=None)
        time.sleep(1)

        progress.update(task, description="Loading models...")
        time.sleep(1.5)

        progress.update(task, description="Initializing tools...")
        time.sleep(1)


def start_chat_mode(mode: str) -> None:
    """Start the chat loop depending on selected mode."""

    if mode == "ask":
        console.print("[yellow]Start typing your question...[/yellow]")
        from kagent.prompts.ask import ask_prompt
        final_prompt = prompt + "\n" + ask_prompt
        start_chat = ChatLoop(final_prompt)

    elif mode == "code":
        console.print("[yellow]Start typing your prompt...[/yellow]")
        from kagent.prompts.code import code_prompt
        final_prompt = prompt + "\n" + code_prompt
        start_chat = ChatLoop(final_prompt)

    elif mode == "debug":
        console.print("[yellow]Start typing your prompt...[/yellow]")
        from kagent.prompts.debug import debug_prompt
        final_prompt = prompt + "\n" + debug_prompt
        start_chat = ChatLoop(final_prompt)

    elif mode == "brainstorm":
        console.print("[yellow]Start typing your idea...[/yellow]")
        from kagent.prompts.brainstorm import brainstorm_prompt
        final_prompt = prompt + "\n" + brainstorm_prompt
        start_chat = ChatLoop(final_prompt)
    
    elif mode == "write":
        console.print("[yellow]Start typing your prompt...[/yellow]")
        from kagent.prompts.write import write_prompt
        final_prompt = prompt + "\n" + write_prompt
        start_chat = ChatLoop(final_prompt)

    elif mode == "review":
        console.print("[yellow]Start typing your prompt...[/yellow]")
        from kagent.prompts.review import review_prompt
        final_prompt = prompt + "\n" + review_prompt
        start_chat = ChatLoop(final_prompt)

    elif mode == "plan":
        console.print("[yellow]Start typing your prompt...[/yellow]")
        from kagent.prompts.plan import plan_prompt
        final_prompt = prompt + "\n" + plan_prompt
        start_chat = ChatLoop(final_prompt)

    elif mode == "analyze":
        console.print("[yellow]Start typing your prompt...[/yellow]")
        from kagent.prompts.analyze import analyze_prompt
        final_prompt = prompt + "\n" + analyze_prompt
        start_chat = ChatLoop(final_prompt)

    elif mode == "translate":
        console.print("[yellow]Start typing your prompt...[/yellow]")
        from kagent.prompts.translate import translate_prompt
        final_prompt = prompt + "\n" + translate_prompt
        start_chat = ChatLoop(final_prompt)


@app.command()
def start() -> None:
    """
    Start the KAgent interactive CLI session.
    """

    show_banner()

    console.print("[bold green]Welcome to kagent[/bold green] \n")

    mode = select_mode()

    if mode == "exit":
        console.print("[bold red]Exiting kagent...[/bold red]")
        sys.exit(0)

    console.print(f"\n[bold cyan]Mode selected:[/bold cyan] {mode}\n")

    show_loading_sequence()

    console.print("[bold green]kagent ready![/bold green]\n")

    start_chat_mode(mode)