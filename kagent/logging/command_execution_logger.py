import logging
import uuid
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.text import Text


class CommandLogger:
    """
    Logs executed commands, outputs, and errors.
    Creates a separate log file per session.
    """

    def __init__(self, log_dir: str = "kagent/logs/commands"):
        self.console = Console()
        self.session_id = str(uuid.uuid4())
        self.start_time = datetime.now()

        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.log_file = self.log_dir / f"cmd_session_{self.session_id}.log"

        self.logger = logging.getLogger(f"CommandLogger-{self.session_id}")
        self.logger.setLevel(logging.DEBUG)

        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        file_handler = logging.FileHandler(self.log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)

    def log(self, command: list[str], output: str, error: str = None, returncode: int = 0):
        """
        Logs command execution details.
        """
        cmd_str = " ".join(command)

        status = "SUCCESS" if returncode == 0 else "FAILED"

        log_entry = f"""
            COMMAND: {cmd_str}
            STATUS: {status}
            RETURN CODE: {returncode}

            STDOUT:
            {output}

            STDERR:
            {error if error else "None"}
            --------------------------------------------------
        """

        if returncode == 0:
            self.logger.info(log_entry)
        else:
            self.logger.error(log_entry)

        # ---- Rich Console Output ----
        if returncode == 0:
            self.console.print(
                Panel(
                    Text(output.strip() or "Command executed successfully.", style="green"),
                    title=f"Command Success",
                )
            )
        else:
            self.console.print(
                Panel(
                    Text(error or "Unknown error", style="bold red"),
                    title=f"Command Failed",
                )
            )

    def get_log_reference(self):
        """
        Returns reference info for ChatLogger.
        """
        return {
            "session_id": self.session_id,
            "log_file": str(self.log_file),
            "started_at": self.start_time.strftime("%Y-%m-%d %H:%M:%S"),
        }