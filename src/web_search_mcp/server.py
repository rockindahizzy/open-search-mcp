"""
web-search-mcp: Keyless web search, fetch, and research via DuckDuckGo + Trafilatura.
"""

import json
import logging
from typing import Any

import httpx
import trafilatura
from ddgs import DDGS
from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("web-search-mcp")

mcp = FastMCP("web-search")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _search_ddg(
    query: str,
    max_results: int = 10,
    region: str = "wt-wt",
    time_range: str | None = None,
    site: str | None = None,
) -> list[dict[str, Any]]:
    """Run a DuckDuckGo search with optional filters."""
    q = query
    if site:
        q = f"site:{site} {q}"

    with DDGS() as ddgs:
        results = list(
            ddgs.text(
                q,
                region=region,
                timelimit=time_range,  # d=day, w=week, m=month, y=year
                max_results=max_results,
            )
        )
    return results


def _fetch_url(url: str, max_chars: int = 20000) -> dict[str, Any]:
    """Fetch a URL and extract readable content."""
    try:
        resp = httpx.get(
            url,
            follow_redirects=True,
            timeout=15.0,
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; web-search-mcp/0.1)"
            },
        )
        resp.raise_for_status()
        html = resp.text

        # Extract with trafilatura
        text = trafilatura.extract(
            html,
            include_links=True,
            include_tables=True,
            output_format="txt",
            favor_recall=True,
        )

        if not text:
            return {
                "url": url,
                "status": resp.status_code,
                "content": "[No readable content extracted]",
                "chars": 0,
            }

        truncated = len(text) > max_chars
        content = text[:max_chars]

        return {
            "url": url,
            "status": resp.status_code,
            "content": content,
            "chars": len(content),
            "truncated": truncated,
        }
    except httpx.HTTPStatusError as e:
        return {"url": url, "error": f"HTTP {e.response.status_code}"}
    except Exception as e:
        return {"url": url, "error": str(e)}


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@mcp.tool()
def search(
    query: str,
    max_results: int = 10,
    region: str = "wt-wt",
    time_range: str | None = None,
    site: str | None = None,
) -> str:
    """
    Search the web via DuckDuckGo. No API key needed.

    Use advanced query techniques for best results:
    - Exact phrases: "financial literacy"
    - Exclude terms: -pinterest
    - Site filter: site param or site: in query
    - Combine operators: "react native" expo -reddit

    Args:
        query: Search query (use operators for precision)
        max_results: Number of results (1-25, default 10)
        region: Region code (wt-wt=global, us-en, uk-en, etc.)
        time_range: d=past day, w=past week, m=past month, y=past year
        site: Limit to domain (e.g. "github.com", "stackoverflow.com")
    """
    max_results = min(max(1, max_results), 25)

    results = _search_ddg(
        query=query,
        max_results=max_results,
        region=region,
        time_range=time_range,
        site=site,
    )

    if not results:
        return json.dumps({"query": query, "results": [], "count": 0})

    formatted = []
    for r in results:
        formatted.append({
            "title": r.get("title", ""),
            "url": r.get("href", r.get("link", "")),
            "snippet": r.get("body", r.get("snippet", "")),
        })

    return json.dumps({"query": query, "results": formatted, "count": len(formatted)}, indent=2)


@mcp.tool()
def fetch(
    url: str,
    max_chars: int = 20000,
) -> str:
    """
    Fetch a URL and extract readable content (HTML → clean text).

    Args:
        url: The URL to fetch
        max_chars: Max characters to return (default 20000, truncates if exceeded)
    """
    max_chars = min(max(1000, max_chars), 100000)
    result = _fetch_url(url, max_chars=max_chars)
    return json.dumps(result, indent=2)


@mcp.tool()
def research(
    query: str,
    max_results: int = 5,
    fetch_top: int = 3,
    max_chars_per_page: int = 10000,
    region: str = "wt-wt",
    time_range: str | None = None,
    site: str | None = None,
) -> str:
    """
    Combined search + fetch: searches, then fetches the top N result pages.
    Returns search results with full extracted content for the top hits.

    Use advanced query techniques — don't just pass raw user questions.
    Reformulate into precise search operators.

    Args:
        query: Search query (use operators for precision)
        max_results: Total search results to return (default 5)
        fetch_top: How many top results to auto-fetch content from (default 3)
        max_chars_per_page: Max chars per fetched page (default 10000)
        region: Region code
        time_range: d=day, w=week, m=month, y=year
        site: Limit to domain
    """
    max_results = min(max(1, max_results), 25)
    fetch_top = min(max(0, fetch_top), max_results, 5)
    max_chars_per_page = min(max(1000, max_chars_per_page), 50000)

    results = _search_ddg(
        query=query,
        max_results=max_results,
        region=region,
        time_range=time_range,
        site=site,
    )

    if not results:
        return json.dumps({"query": query, "results": [], "count": 0, "fetched": 0})

    formatted = []
    fetched_count = 0
    for i, r in enumerate(results):
        entry: dict[str, Any] = {
            "title": r.get("title", ""),
            "url": r.get("href", r.get("link", "")),
            "snippet": r.get("body", r.get("snippet", "")),
        }

        # Auto-fetch top results
        if i < fetch_top and entry["url"]:
            logger.info(f"Fetching [{i+1}/{fetch_top}]: {entry['url']}")
            page = _fetch_url(entry["url"], max_chars=max_chars_per_page)
            entry["content"] = page.get("content")
            entry["content_chars"] = page.get("chars", 0)
            entry["content_truncated"] = page.get("truncated", False)
            entry["fetch_error"] = page.get("error")
            fetched_count += 1

        formatted.append(entry)

    return json.dumps(
        {
            "query": query,
            "results": formatted,
            "count": len(formatted),
            "fetched": fetched_count,
        },
        indent=2,
    )


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
