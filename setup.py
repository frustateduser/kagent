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
subprocess.run(["playwright", "install"], check=True)

print("Virtual environment created and dependencies installed.")

print("Downloading Ollama")

if platform.system() == "Windows":
    subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-Command", "irm https://ollama.com/install.ps1", "|", "iex"], check=True)
else:
    subprocess.run(["curl", "-fsSL", "https://ollama.ai/install.sh", "|", "sh"], check=True)

print("Ollama downloaded")

subprocess.run(["ollama", "pull", "llama3.1:8b"], check=True)

print("Ollama pulled llama3.1:8b successfully")

print("Installing Node")
if platform.system() == "Windows":
    subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-Command", "irm https://community.chocolatey.org/install.ps1", "|", "iex"], check=True)
    subprocess.run(["choco", "install", "nodejs", "--version=24.15.0", "-y"], check=True)
else:
    subprocess.run(["curl", "-o-", "https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.4/install.sh", "|", "bash"])
    subprocess.run(["\.", "$HOME/.nvm/nvm.sh"], check=True)
    subprocess.run(["nvm", "install", "24"], check=True)