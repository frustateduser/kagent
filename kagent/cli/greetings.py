import typer
import questionary
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from questionary import Choice
import time
from prompt_toolkit.styles import Style

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


def show_banner():
    console.print(Panel(BANNER, style="green"))


@app.command()
def start():
    """Start kagent interactive session"""

    show_banner()

    console.print("[bold green]Welcome to kagent[/bold green] 🤖\n")

    custom_style = Style.from_dict({
        "question": "bold",
        "pointer": "fg:#ff9d00 bold",
        "highlighted": "fg:#00ffcc bold",
    })

    # Mode Selection
    mode = questionary.select(
        "What do you want to do?",
        choices=[
            Choice("ask  → Ask questions / research", value="ask"),
            Choice("code → Generate or debug code", value="code"),
            Choice("brainstorm → Ideas, architecture, planning", value="brainstorm"),
        ],
        style=custom_style,
    ).ask()

    console.print(f"\n[bold cyan]Mode selected:[/bold cyan] {mode}\n")

    # Spinner effect
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

    console.print("✨ [bold green]kagent ready![/bold green]\n")

    # Custom prompt based on mode
    if mode == "ask":
        console.print("[yellow]Start typing your question...[/yellow]")

    elif mode == "code":
        console.print("[yellow]Start typing your prompt...[/yellow]")

    elif mode == "brainstorm":
        console.print("[yellow]Start typing your idea...[/yellow]")


if __name__ == "__main__":
    app()