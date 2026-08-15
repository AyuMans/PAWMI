import os
from dotenv import load_dotenv
from tavily import TavilyClient


load_dotenv()


class TavilyProvider:

    def __init__(self):
        api_key = os.getenv("TAVILY_API_KEY")

        if not api_key:
            raise ValueError("TAVILY_API_KEY not found in environment.")

        self.client = TavilyClient(api_key=api_key)

    def search(self, query):
        return self.client.search(
            query=query,
            search_depth="basic",
            max_results=5
        )