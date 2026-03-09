# Import the ollama library which allows us to interact with
# locally running LLM models through the Ollama API
import ollama
from questionary import Choice
import questionary
from rich.console import Console

console = Console()


class OllamaModel:
    # Default model is "llama3.1:latest"
    def __init__(self):
        # user selects the model
        self.model = questionary.select(
            "Select a model",
            choices=self.model_choices(),
        ).ask()
    
    # store the model name inside the object
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
    

    # fetch locally available ollama models 
    def get_local_models(self):
        models = ollama.list()
        return [m.model for m in models["models"]]
    
    # converts the models into choices to be chosen from (uses Choice from questioner library) 
    def model_choices(self):
        models = self.get_local_models()
        return [Choice(title=f"{m}", value=m) for m in models]