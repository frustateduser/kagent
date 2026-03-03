# kagent

**Local AI agent for all your tasks**

kagent is a locally running AI agent designed for developers, researchers, and power users.
It supports multiple local LLM backends, filesystem access, command execution, a knowledge base, and semi-autonomous operation with security controls.

---

### Features

- Supports Ollama models

- Supports HuggingFace local models

- Automatic GPU detection (CUDA / ROCm / Metal)

- ReAct-style reasoning loop

- Full local filesystem interaction

- Shell command execution with output capture

- Web search & scraping

- Persistent local knowledge base (vector store)

- Risk detection + confirmation system

- Dynamic model switching

- Modular plugin architecture

- Cross-platform (Windows, Linux, macOS)

---

### Requirements

- Python 3.11+
- ollama
- CUDA / ROCm / Metal drivers (if using GPU)

---

### ⚙️ Installation/ Setup

1. Fork the reop on your github.
2. Execute the command 
```bash 
git clone https://github.com/<your-username>/kagent.git
```
3. Move into the directory 
```
cd kagent
```
4. Create virtual enviornment, and activate it. 
```bash
python -m venv venv

# windows
.\venv\Scripts\activate

# linux / mac
source venv/bin/activate

```
5. Install dependencies 
```
pip install -r requirements.txt
```
6. Download [ollama](https://ollama.com/) and install it.
7. After ollama is successfully installed run `ollama pull llama3`, and verify it by `ollama run llama3`.

Alternatively, you can run the **setup.py** file.