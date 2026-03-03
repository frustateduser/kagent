import subprocess
import sys
import os
import platform

subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)

if platform.system() == "Windows":
    venv_python = os.path.join("venv", "Scripts", "python.exe")
else:
    venv_python = os.path.join("venv", "bin", "python")

subprocess.run([venv_python, "-m", "pip", "install", "-r", "requirements.txt"], check=True)

print("Virtual environment created and dependencies installed.")

print("Downloading Ollama")

if platform.system() == "Windows":
    subprocess.run(["powershell", "-Command", "irm https://ollama.com/install.ps1", "|", "iex"], check=True)
else:
    subprocess.run(["curl", "-fsSL", "https://ollama.ai/install.sh", "|", "sh"], check=True)

print("Ollama downloaded")

subprocess.run(["ollama", "pull", "llama3.1:latest"])

print("Ollama pulled llama3.1:latest successfully")