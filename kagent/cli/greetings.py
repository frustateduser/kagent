import typer
import questionary
from questionary import Choice, Style
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
import time
custom_style = Style([
    ("qmark", "fg:#ff9d00 bold"),
    ("pointer", "fg:#ff9d00 bold"),   
])
app = typer.Typer()
console = Console()

BANNER = r"""
██╗  ██╗    █████╗  ██████╗ ███████╗███╗   ██╗████████╗
██║ ██╔╝   ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝
█████╔╝    ███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║   
██╔═██╗    ██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║   
██║  ██╗   ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║   
╚═╝  ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝   

        Local AI Agent Runtime
"""


def show_banner():
    console.print(Panel(BANNER, border_style="green"))


@app.command()
def start():
    """Start kagent interactive session"""

    show_banner()
    console.print("[bold green]Welcome to kagent[/bold green] 🤖\n")

    mode = questionary.select(
        "What do you want to do?",
    choices=[
        Choice("\033[31mask\033[0m → Ask questions / research", value="ask"),
        Choice("\033[33mcode\033[0m → Generate or debug code", value="code"),
        Choice("\033[35mbrainstorm\033[0m → Ideas, architecture, planning", value="brainstorm"),
        
    ],style=custom_style
    ).ask()

    if not mode:
        console.print("[red]No option selected. Exiting...[/red]")
        raise typer.Exit()

    console.print(f"\n[bold cyan]Mode selected:[/bold cyan] {mode}\n")

    # Spinner animation
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