from __future__ import annotations

from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from langchain_community.tools import DuckDuckGoSearchRun, WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_core.tools import tool

from chatbot.rag import PersonalDataRag


_personal_data_rag: PersonalDataRag | None = None


def _get_personal_data_rag() -> PersonalDataRag:
    global _personal_data_rag
    if _personal_data_rag is None:
        _personal_data_rag = PersonalDataRag()
    return _personal_data_rag


duckduckgo_search = DuckDuckGoSearchRun(
    name="duckduckgo_search",
    description="Search DuckDuckGo for recent or broad web information. Input should be a clear search query.",
)

wikipedia_search = WikipediaQueryRun(
    api_wrapper=WikipediaAPIWrapper(top_k_results=3, doc_content_chars_max=2500),
    name="wikipedia_search",
    description="Search Wikipedia for encyclopedic background. Input should be a topic or entity name.",
)


@tool
def google_search(query: str, max_results: int = 5) -> str:
    """Search Google and return result URLs/snippets when DuckDuckGo is insufficient."""
    try:
        from googlesearch import search

        results = list(search(query, num_results=max(1, min(max_results, 10)), advanced=True))
    except Exception as exc:
        return f"Google search failed: {exc}"

    if not results:
        return "No Google results found."

    lines: list[str] = []
    for index, result in enumerate(results, start=1):
        title = getattr(result, "title", "") or "Untitled"
        url = getattr(result, "url", "") or str(result)
        description = getattr(result, "description", "") or ""
        lines.append(f"{index}. {title}\nURL: {url}\nSnippet: {description}".strip())
    return "\n\n".join(lines)


@tool
def scrape_url(url: str, max_chars: int = 5000) -> str:
    """Scrape readable text from a public web page URL."""
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return "Invalid URL. Provide a full http or https URL."

    try:
        response = requests.get(
            url,
            timeout=12,
            headers={"User-Agent": "Mozilla/5.0 compatible LangGraphChatbot/1.0"},
        )
        response.raise_for_status()
    except Exception as exc:
        return f"Failed to fetch URL: {exc}"

    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
        tag.decompose()

    title = soup.title.string.strip() if soup.title and soup.title.string else url
    text = " ".join(soup.get_text(separator=" ").split())
    if not text:
        return f"No readable text found for {url}"

    limit = max(500, min(max_chars, 12000))
    return f"Title: {title}\nURL: {url}\n\n{text[:limit]}"


@tool
def google_scraper(query: str, max_results: int = 3, chars_per_page: int = 2500) -> str:
    """Search Google, scrape top result pages, and return compact page text."""
    search_output = google_search.invoke({"query": query, "max_results": max_results})
    urls = [line.removeprefix("URL: ").strip() for line in search_output.splitlines() if line.startswith("URL: ")]

    if not urls:
        return search_output

    scraped_pages: list[str] = []
    for url in urls[: max(1, min(max_results, 5))]:
        scraped_pages.append(scrape_url.invoke({"url": url, "max_chars": chars_per_page}))
    return "\n\n---\n\n".join(scraped_pages)


@tool
def personal_data_rag_search(query: str, k: int = 5) -> str:
    """Search private personal data memory in Qdrant. Use this for personal facts, preferences, documents, and custom data."""
    return _get_personal_data_rag().search(query=query, k=max(1, min(k, 10)))


def build_tools() -> list:
    return [
        duckduckgo_search,
        wikipedia_search,
        google_search,
        google_scraper,
        scrape_url,
        personal_data_rag_search,
    ]
