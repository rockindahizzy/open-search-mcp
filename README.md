# open-search-mcp

An MCP (Model Context Protocol) server that provides web search, page fetching, and combined research capabilities — **no API key required**.

Built on DuckDuckGo for search and Trafilatura for content extraction.

## Tools

### `search`
Search the web via DuckDuckGo with support for advanced query operators.

```
query: "react native expo" -reddit
max_results: 10
region: us-en
time_range: w        # d=day, w=week, m=month, y=year
site: github.com     # limit to domain
```

### `fetch`
Fetch a URL and extract clean, readable text from HTML.

```
url: https://example.com/article
max_chars: 20000
```

### `research`
Combined search + fetch — searches the web, then auto-fetches the top N results for full content extraction. Best for deep dives.

```
query: "philosophy of mind" AI consciousness
fetch_top: 3
max_chars_per_page: 10000
```

## Installation

Requires Python 3.11+.

```bash
# With uv
uv sync

# Or with pip
pip install .
```

## Usage

### As an MCP server (stdio transport)

```bash
open-search-mcp
```

### With mcporter

```bash
mcporter call open-search.search query="your search" max_results:5
mcporter call open-search.fetch url="https://example.com"
mcporter call open-search.research query="deep research topic" fetch_top:3
```

### With Claude Desktop / MCP clients

Add to your MCP config:

```json
{
  "mcpServers": {
    "open-search": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/open-search-mcp", "open-search-mcp"]
    }
  }
}
```

## Query Tips

- Exact phrases: `"financial literacy"`
- Exclude terms: `-pinterest`
- Site filter: `site:stackoverflow.com`
- Combine: `"react native" expo -reddit site:github.com`
- Time range: Use `time_range` param for freshness (`d`, `w`, `m`, `y`)

## Dependencies

- [mcp](https://github.com/modelcontextprotocol/python-sdk) — Model Context Protocol SDK
- [ddgs](https://github.com/deedy5/duckduckgo_search) — DuckDuckGo search
- [httpx](https://github.com/encode/httpx) — HTTP client
- [trafilatura](https://github.com/adbar/trafilatura) — Web content extraction

## License

MIT
