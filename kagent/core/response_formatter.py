from rich.markdown import Markdown
from rich.console import Console

def print_formatted_response(response):
    console = Console()
    markdown = Markdown(response)
    console.print("\nAI:\n", style="bold green")
    console.print(markdown)