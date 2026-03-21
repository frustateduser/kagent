import questionary
from prompt_toolkit.styles import Style
from rich.console import Console

class CommandSecurityCheck:
    """
    Security check, confirmation and logging before execution of commands.
    """

    def __init__(self):
        self.console = Console()


    def get_prompt_style(self) -> Style:
        """Return the custom style used by questionary prompts."""
        return Style.from_dict(
            {
                "question": "bold",
                "pointer": "fg:#ff9d00 bold",
                "highlighted": "fg:#4d4dff bold",
            }
        )
        
    def print_command(self, commands: list[str]):
        cmd = " ".join(commands)
        return cmd
    
    def ask(self, commands: list[str]):
        self.console.print("Do you want to execute this command?\n")
        confirmation = questionary.confirm(
            message=self.print_command(commands),
            style=self.get_prompt_style(),
        ).ask()
        return confirmation