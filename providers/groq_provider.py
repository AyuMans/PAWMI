import os
from groq import Groq


class GroqProvider:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment.")

        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"

    def ask(self, messages, tools=None):

        request = {
            "model": self.model,
            "messages": messages,
        }
    
        if tools:
            request["tools"] = tools
            request["tool_choice"] = "auto"
    
        response = self.client.chat.completions.create(
            **request
        )
    
        return response