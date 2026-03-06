from kagent.history.convo_memory import ConversationMemory
from kagent.models.ollama_model import OllamaModel


def start_chat():

    memory = ConversationMemory()
    model = OllamaModel()

    print("\nType 'exit' to quit\n")

    while True:

        user_input = input("You: ")

        if user_input.lower() in ["exit", "quit"]:
            break

        memory.add_user_message(user_input)

        response = model.generate(memory.get_history())
        
        if not response:
            response = "I couldn't generate a response"

        memory.add_ai_message(response)

        print("\nAI:", response)
        print()
