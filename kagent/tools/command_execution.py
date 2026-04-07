import subprocess

from kagent.security.command_security_check import CommandSecurityCheck
from kagent.logging.command_execution_logger import CommandLogger

class CommandExecution:
    """
    Tool for executing shell commands.
    """

    def __init__(self):
        self.logger = CommandLogger()
        self.security = CommandSecurityCheck()
    def execute(self, command_list):
        """
        Executes a command provided as a list of strings.
        Example: ["ls", "-la"]
        """
        confirmed = self.security.ask(command_list)

        if not confirmed:
            return {
                "status": "cancelled",
                "output": "Command execution cancelled by user.",
                "log_ref": self.logger.get_log_reference()
            }

        try:
            # Run the command and capture output
            result = subprocess.run(
                command_list,
                capture_output=True,
                text=True,
                shell=False  # Set to True if shell-specific features are needed, but False is safer
            )

            self.logger.log(
                command=command_list,
                output=result.stdout,
                error=result.stderr,
                returncode=result.returncode
            )

            return {
                "status": "success" if result.returncode == 0 else "error",
                "output": result.stdout if result.returncode == 0 else result.stderr,
                "log_ref": self.logger.get_log_reference()
            }
        
        except Exception as e:
            self.logger.log(
                command=command_list,
                output="",
                error=str(e),
                returncode=1
            )

            return {
                "status": "exception",
                "output": str(e),
                "log_ref": self.logger.get_log_reference()
            }
