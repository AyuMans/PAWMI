from providers.groq_provider import GroqProvider
from providers.gemini_provider import GeminiProvider


class APIManager:

    def __init__(self):

        self.providers = [
            ("Groq", GroqProvider()),
            ("Gemini", GeminiProvider())
        ]

    def ask(self, messages, tools=None):

        last_error = None

        for name, provider in self.providers:

            try:
                print(f"[API] Trying {name}...")

                response = provider.ask(
                    messages,
                    tools
                )

                print(f"[API] {name} responded.")

                return response

            except Exception as error:

                print(f"[API] {name} failed: {error}")

                last_error = error

        raise RuntimeError(
            f"All AI providers failed. Last error: {last_error}"
        )