import os

# This file gives the agent access to project files
class FileAccess:

    def __init__(self, root_dir="."):
        """
        root_dir defines the project directory.

        By default "." means the current project folder.
        """
        self.root_dir = os.path.abspath(root_dir)

    def list_files(self):
        """
        Returns a list of all files inside the project directory.
        """

        files = []

        # os.walk scans all folders recursively
        for root, dirs, filenames in os.walk(self.root_dir):

            for name in filenames:

                # Create full file path
                full_path = os.path.join(root, name)

                # Convert to relative path from project root
                relative_path = os.path.relpath(full_path, self.root_dir)

                # Add file to list
                files.append(relative_path)

        return files

    def read_file(self, file_path):
        """
        Reads the content of a specific file.
        Example: read_file("cli/greetings.py")
        """

        # Build full file path
        full_path = os.path.join(self.root_dir, file_path)

        # If file does not exist
        if not os.path.exists(full_path):
            return f"Error: file '{file_path}' does not exist."

        try:
            # Open and read file
            with open(full_path, "r", encoding="utf-8") as file:
                content = file.read()

            return content

        except Exception as e:
            return f"Error reading file: {str(e)}"
        
    