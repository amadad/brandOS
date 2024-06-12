import os
import requests
import rich

query = "elderly and aging stats 2024 in america"

def query_web_llm(query):
    api_key = os.getenv("YOU_API_KEY")
    headers = {"X-API-Key": api_key}
    params = {"query": query}
    response = requests.get(
        f"https://api.ydc-index.io/rag?query={query}",
        params=params,
        headers=headers,
    ).json()
    return [hit['ai_snippets'] for hit in response['hits']]

rich.print(query_web_llm(query))