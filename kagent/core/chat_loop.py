from kagent.history.convo_memory import ConversationMemory
from kagent.models.ollama_model import OllamaModel
from kagent.logging.chat_logger import ChatLogger
from kagent.core.response_formatter import print_formatted_response
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.console import Console  #used for different color of user input
from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings

console = Console()
kb = KeyBindings()

#ctrl+enter will submit the message
@kb.add("c-d")
def _(event):
    event.app.exit(result=event.app.current_buffer.text)
    
#create prompt session    
session = PromptSession(key_bindings=kb)
# This function starts the interactive chat session
def start_chat():
    # Create a memory object to store conversation history
    memory = ConversationMemory()
    # Create a model object to interact with the LLM
    model = OllamaModel()
    chatLogger = ChatLogger() # initialize object for conversation logging

    console.print("[red]\nType 'exit' to quit[/red]\n")
    console.print("[red]Press 'ctrl+D' to send the message[/red]\n")

    while True:

        console.print("[bold red]You:[/bold red] ",end="")
        
        #multi-line input
        user_input = session.prompt(multiline=True)

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
        chatLogger.log_agent(response) # logs agent response

        print_formatted_response(response)
        print()
