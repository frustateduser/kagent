import ollama

class OllamaModel:
    def __init__(self, model="llama3.1:latest"):
        self.model = model
    
    def generate(self, messages):
        response = ollama.chat(
            model= self.model,
            messages=messages
        )
        return response["message"]["content"]