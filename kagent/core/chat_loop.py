from kagent.history.convo_memory import ConversationMemory
from kagent.models.ollama_model import OllamaModel
from kagent.logging.chat_logger import ChatLogger
from kagent.core.response_formatter import print_formatted_response


# This function starts the interactive chat session
def start_chat():
    # Create a memory object to store conversation history
    memory = ConversationMemory()
    # Create a model object to interact with the LLM
    model = OllamaModel()
    chatLogger = ChatLogger() # initialize object for conversation logging

    print("\nType 'exit' to quit\n")

    while True:

        user_input = input("You: ")
        chatLogger.log_user(user_input) # logs user message 

        if user_input.lower() in ["exit", "quit"]:
            break
        
         # Add the user's message to conversation memory
        memory.add_user_message(user_input)

        # Send the entire conversation history to the model
        # The model will generate a response based on previous context
        response = model.generate(memory.get_history())
        
        if not response:
            response = "I couldn't generate a response"

        # Store the AI response in the memory
        memory.add_ai_message(response)
        chatLogger.log_agent(response) # logs agent response

        print_formatted_response(response)
        print()
