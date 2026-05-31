from typing import Type

import requests
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

WIKIPEDIA_API = "https://en.wikipedia.org/w/api.php"
WIKIPEDIA_SUMMARY_API = "https://en.wikipedia.org/api/rest_v1/page/summary"


class WikiSearchInput(BaseModel):
    search_query: str = Field(
        ...,
        description="Topic or keyword to search for on Wikipedia",
    )


class WikiSearchTool(BaseTool):
    name: str = "Wikipedia Search"
    description: str = (
        "Search Wikipedia for factual information about a topic. "
        "Provide search_query as the topic or keyword to look up."
    )
    args_schema: Type[BaseModel] = WikiSearchInput

    def _run(self, search_query: str) -> str:
        try:
            search_response = requests.get(
                WIKIPEDIA_API,
                params={
                    "action": "query",
                    "list": "search",
                    "srsearch": search_query,
                    "format": "json",
                    "srlimit": 3,
                },
                timeout=10,
                headers={"User-Agent": "solid-lamp-python/1.0"},
            )
            search_response.raise_for_status()
            search_data = search_response.json()
            results = search_data.get("query", {}).get("search", [])
            if not results:
                return f"No Wikipedia results found for '{search_query}'."

            top_result = results[0]
            title = top_result["title"]
            snippet = top_result.get("snippet", "").replace("<span class=\"searchmatch\">", "").replace("</span>", "")

            summary_response = requests.get(
                f"{WIKIPEDIA_SUMMARY_API}/{title.replace(' ', '_')}",
                timeout=10,
                headers={"User-Agent": "solid-lamp-python/1.0"},
            )
            summary_response.raise_for_status()
            summary_data = summary_response.json()
            extract = summary_data.get("extract", snippet)
            url = summary_data.get("content_urls", {}).get("desktop", {}).get("page", "")

            related = [item["title"] for item in results[1:]]
            related_text = f"\n\nRelated pages: {', '.join(related)}" if related else ""

            return f"Title: {title}\n\nSummary: {extract}\n\nURL: {url}{related_text}"
        except Exception as exc:
            return f"Wikipedia search failed: {exc}"


wiki_search_tool = WikiSearchTool()
