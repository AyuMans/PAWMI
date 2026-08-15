import time

from providers.groq_provider import GroqProvider
from providers.gemini_provider import GeminiProvider
from providers.openrouter_provider import OpenRouterProvider


class APIManager:

    def __init__(self):

        self.providers = [
            ("Groq", GroqProvider()),
            ("Gemini", GeminiProvider()),
            ("OpenRouter", OpenRouterProvider())
        ]

        # Stores the time when each provider can be tried again
        self.cooldowns = {}

    def ask(self, messages, tools=None):

        last_error = None

        for name, provider in self.providers:

            # Check whether this provider is currently cooling down
            if self.is_on_cooldown(name):
                remaining = self.cooldowns[name] - time.time()

                print(
                    f"[API] {name} is on cooldown "
                    f"({remaining:.0f}s remaining). Skipping."
                )

                continue

            try:
                

                print(f"[API] Trying {name}...")

                response = provider.ask(
                    messages,
                    tools
                )

                print(f"[API] {name} responded.")

                # Successful request → remove any cooldown
                self.cooldowns.pop(name, None)

                return response

            except Exception as error:

                print(f"[API] {name} failed: {error}")

                last_error = error

                # Only rate-limit errors trigger cooldown
                if self.is_rate_limit_error(error):

                    cooldown = self.get_retry_seconds(error)

                    self.cooldowns[name] = (
                        time.time() + cooldown
                    )

                    print(
                        f"[API] {name} rate limited. "
                        f"Cooling down for {cooldown}s."
                    )

        raise RuntimeError(
            f"All AI providers failed. Last error: {last_error}"
        )

    def is_on_cooldown(self, name):

        if name not in self.cooldowns:
            return False

        if time.time() >= self.cooldowns[name]:

            # Cooldown expired
            del self.cooldowns[name]

            return False

        return True

    def is_rate_limit_error(self, error):

        # OpenAI/Groq errors normally expose a status_code
        status_code = getattr(
            error,
            "status_code",
            None
        )

        if status_code == 429:
            return True

        # Fallback for providers whose exception doesn't expose
        # status_code cleanly.
        error_text = str(error).lower()

        return (
            "429" in error_text
            or "rate limit" in error_text
            or "rate_limit" in error_text
            or "rate_limit_exceeded" in error_text
        )

    def get_retry_seconds(self, error):

        error_text = str(error)

        # Try to extract a retry time from errors such as:
        #
        # "Please try again in 4m33.024s"

        import re

        match = re.search(
            r"try again in (?:(\d+)m)?([\d.]+)s",
            error_text,
            re.IGNORECASE
        )

        if match:

            minutes = int(
                match.group(1) or 0
            )

            seconds = float(
                match.group(2)
            )

            return max(
                1,
                int(minutes * 60 + seconds)
            )

        # Safe fallback
        return 60