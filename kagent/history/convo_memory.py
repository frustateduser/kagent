class ConversationMemory:
    def __init__(self):
        self.history = []
    # This method adds a message from the user to the conversation history
    # The message is stored as a dictionary with role "user"    
    def add_user_message(self, message):
        self.history.append({"role": "user","content":message})
    
    def add_ai_message(self, message):
        self.history.append({"role": "assistant","content":message})
    
    # This method returns the full conversation history
    # The history will be used when sending messages to the LLM
    def get_history(self):
        return self.history