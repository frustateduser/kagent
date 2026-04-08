import os
import json

# This file gives the agent access to project files
class FileAccess:

    def __init__(self, root_dir=None):
        """
        root_dir:
        - If provided → restrict access to that folder
        - If None → allow full system access (use carefully ⚠️)
        """
        self.root_dir = os.path.abspath(root_dir) if root_dir else None
        
    def _resolve_path(self, file_path):
        """
        Resolves the correct full path
        """
        # If absolute path → use directly
        if os.path.isabs(file_path):
            return file_path

        # If root_dir is set → use it
        if self.root_dir:
            return os.path.join(self.root_dir, file_path)

        # Otherwise → relative to current working directory
        return os.path.abspath(file_path)

    def list_files(self, folder_path=None):
        """
        Returns a list of all files inside the directory.
        """

        base_path = self._resolve_path(folder_path) if folder_path else (
            self.root_dir or os.getcwd()
        )
        files = []

        # os.walk scans all folders recursively
        for root, dirs, filenames in os.walk(base_path):

            for name in filenames:

                # Create full file path
                full_path = os.path.join(root, name)

                # Add file to list
                files.append({
                    "name": name,
                    "path": full_path,
                    "size":os.path.getsize(full_path)
                })

        return json.dumps({
            "base_path": base_path,
            "total_files": len(files),
            "files": files
        }, indent=2)

    def read_file(self, file_path):
        """
        Reads the content of a specific file.
        Example: read_file("cli/greetings.py")
        """

        # Build full file path
        full_path = self._resolve_path(file_path)
        
        #Debug 
        print(f"[DEBUG] Reading from: {full_path}")

        # If file does not exist
        if not os.path.exists(full_path):
            return f"Error: file '{file_path}' does not exist."

        try:
            # Open and read file
            with open(full_path, "r", encoding="utf-8") as file:
                return file.read()

        except Exception as e:
            return f"Error reading file: {str(e)}"
        
    def write_file(self, file_path, content, mode="w"):
        """
        Writes content to a specific file. Mode can be "w" for overwrite or "a" for append.
        Example: write_file("cli/greetings.py", "print('Hello World')", mode="w")
        """

        # Build full file path
        full_path = self._resolve_path(file_path)

        try:
            # Open and write to file
            os.makedirs(os.path.dirname(full_path), exist_ok=True)  # Ensure directory exists
            with open(full_path, mode, encoding="utf-8") as file:
                file.write(content)
            return {
                "status": "success",
                "message": f"Content written to '{file_path}' successfully."
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Error writing to file: {str(e)}"
            }
    