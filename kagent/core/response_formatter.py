import json
from rich.markdown import Markdown
from rich.console import Console

def print_formatted_response(response):
    # If response is dict, extract content
    if isinstance(response, dict):
        content = response.get("content", "")

        # fallback if content is empty
        if not content:
            content = json.dumps(response, indent=2)
    else:
        content = str(response)

    console = Console()
    markdown = Markdown(content)
    console.print("\nAI:\n", style="bold green")
    console.print(markdown)