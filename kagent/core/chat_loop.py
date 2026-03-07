from kagent.history.convo_memory import ConversationMemory
from kagent.models.ollama_model import OllamaModel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.console import Console  #used for different color of user input

console = Console()
# This function starts the interactive chat session
def start_chat():
    # Create a memory object to store conversation history
    memory = ConversationMemory()
    # Create a model object to interact with the LLM
    model = OllamaModel()

    print("\nType 'exit' to quit\n")

    while True:

        console.print("[bold red]You:[/bold red] ",end="")
        user_input = input()

        if user_input.lower() in ["exit", "quit"]:
            break
        
         # Add the user's message to conversation memory
        memory.add_user_message(user_input)

        #loader while ai is generating response
        # Send the entire conversation history to the model
        # The model will generate a response based on previous context
        with Progress(SpinnerColumn(), TextColumn("[bold cyan]AI is thinking..."),
                      transient=True,) as progress:
            progress.add_task("thinking",total=None)
            response = model.generate(memory.get_history())
        
        if not response:
            response = "I couldn't generate a response"

        # Store the AI response in the memory
        memory.add_ai_message(response)

        print("\nAI:", response)
        print()
