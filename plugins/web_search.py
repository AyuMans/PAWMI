from providers.tavily_provider import TavilyProvider

tavily = TavilyProvider()

def web_search(query):
    results = tavily.search(query)
    simplified_results = []
    for result in results.get("results", []):
        simplified_results.append({
            "title": result.get("title"),
            "url": result.get("url"),
            "content": result.get("content")
            })
    return {
        "query": query,
        "results": simplified_results
        }