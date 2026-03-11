from kagent.history.convo_memory import ConversationMemory
from kagent.models.ollama_model import OllamaModel
from kagent.logging.chat_logger import ChatLogger
from kagent.core.response_formatter import print_formatted_response
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.console import Console  #used for different color of user input
from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
#file reading
from kagent.tools.fileaccess import FileAccess


console = Console()

kb = KeyBindings()

    
#create prompt session    
session = PromptSession(key_bindings=kb)

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
    file_tool = FileAccess(root_dir="kagent")
    chatLogger = ChatLogger() # initialize object for conversation logging

    console.print("[red]\nType 'exit' to quit[/red]\n")
    console.print("[red]Press 'ctrl+D' to send the message[/red]\n")
    console.print("[red]\nType 'exit' to quit[/red]\n")
    console.print("[red]Press 'ctrl+D' to send the message[/red]\n")

    while True:

        console.print("[bold red]You:[/bold red] \n",end="")
        
        #multi-line input
        user_input = session.prompt("[bold red]You:[/bold red] ",multiline=True)
        

        if user_input.lower() in ["exit", "quit"]:
            break
        # log user message
        chatLogger.log_user(user_input)
        #read file
        if user_input.lower().startswith("read file"):

            file_name = user_input.replace("read file", "").strip()

            file_content = file_tool.read_file(file_name)
            
            console.print("\n[bold cyan]File content:[/bold cyan]\n")
            console.print(file_content)
            continue 
            

        with Progress(
             SpinnerColumn(),
             TextColumn("[bold cyan]AI is thinking..."),
              transient=True,
        ) as progress:

            progress.add_task("thinking", total=None)
            response = model.generate(memory.get_history())
        # Store the AI response in the memory
        memory.add_ai_message(response)
        chatLogger.log_agent(response) # logs agent response

        print_formatted_response(response)
        print()
