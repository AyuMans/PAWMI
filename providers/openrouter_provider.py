import os
from openai import OpenAI


class OpenRouterProvider:

    def __init__(self):
        api_key = os.getenv("OPENROUTER_API_KEY")

        if not api_key:
            raise ValueError(
                "OPENROUTER_API_KEY not found in environment."
            )

        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )

        self.model = "nvidia/nemotron-3-ultra-550b-a55b:free"

    def ask(self, messages, tools=None):

        request = {
            "model": self.model,
            "messages": messages
        }

        if tools:
            request["tools"] = tools
            request["tool_choice"] = "auto"

        return self.client.chat.completions.create(
            **request
        )