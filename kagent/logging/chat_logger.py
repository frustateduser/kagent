import uuid
import json
from pathlib import Path
from datetime import datetime


# ChatLogger
# for creating a convenient user readable markdown file for a session
class ChatLogger:
    def __init__(self, log_dir: str="kagent/logs/chats"):
        self.session_id = str(uuid.uuid4()) # unique identification for chats/session
        self.start_time = datetime.now() # time stamp
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True) # verify path
        self.file_path = self.log_dir / f"{self.session_id}.md"
        self._init_file()

    def _init_file(self):
        # create file and log session id and time stamp
        with open(self.file_path, "w", encoding="utf-8") as f:
            f.write("# kagent chat session\n\n")
            f.write(f"Session ID: {self.session_id}\n\n")
            f.write(f"Start Time: {self.start_time}\n\n")
            f.write("---\n\n")
        
    def log_user(self, message: str):
        # log user message
        with open(self.file_path, "a", encoding="utf-8") as f:
            f.write("\n## User\n")
            f.write(message + "\n")

    def log_agent(self, message: str):
        if isinstance(message, dict):
            message = json.dumps(message, indent=2)

        # log agent response
        with open(self.file_path, "a", encoding="utf-8") as f:
            f.write("\n## Agent\n")
            f.write(message + "\n")
            f.write("\n---\n")

    def log_tool(self, tool_response):
        tool = tool_response.get("tool")
        input = tool_response.get("input")
        output = tool_response.get("output")

        with open(self.file_path, "a", encoding="utf-8") as f:
            f.write(f"\n## Tool: {tool}\n")
            f.write(f"Input: {input}\n")
            f.write(f"Output: {output}\n")
            f.write("\n---\n")