# Import the ollama library which allows us to interact with
# locally running LLM models through the Ollama API
import ollama

class OllamaModel:
    # Default model is "llama3.1:latest"
    def __init__(self, model="llama3.1:latest"):
        self.model = model # store the model name inside the object
    # Method used to generate a response from the model
    # "messages" is a list of chat messages (like system, user, assistant)
    def generate(self, messages):
        # Call Ollama's chat API
        # Pass the selected model and the messages conversation
        response = ollama.chat(
            model= self.model,
            messages=messages
        )
        # The response returned by Ollama is a dictionary
        # We extract only the actual generated text from it
        return response["message"]["content"]