# open-search-mcp

Web search, page fetching, and research from the terminal or any MCP client — **no API key required**.

Built on DuckDuckGo for search and Trafilatura for content extraction.

## Install

### Homebrew (macOS/Linux)

```bash
brew install rockindahizzy/tap/open-search-mcp
```

### pipx / uv

```bash
# One-shot (no install)
uvx open-search-mcp search "your query"

# Permanent install
uv tool install open-search-mcp
# or
pipx install open-search-mcp
```

### pip

```bash
pip install open-search-mcp
```

## CLI Usage

```bash
# Search the web
open-search search "python async tutorial"
open-search search "react native" -n 5 -t w
open-search search "security CVE" -s github.com

# Fetch a page and extract readable content
open-search fetch https://example.com/article
open-search fetch https://news.ycombinator.com -m 5000

# Research: search + auto-fetch top results
open-search research "philosophy of mind AI"
open-search research "rust vs go 2025" -f 5 -v

# JSON output (pipe to jq, etc.)
open-search search "AI agents" --json
open-search research "MCP protocol" --json | jq '.results[0].content'
```

### Commands

| Command | Description |
|---------|-------------|
| `search` | Search the web via DuckDuckGo |
| `fetch` | Fetch a URL → clean readable text |
| `research` | Search + auto-fetch top N results |

### Query Tips

- Exact phrases: `"financial literacy"`
- Exclude terms: `-pinterest`
- Site filter: `-s github.com` or `site:stackoverflow.com` in query
- Time range: `-t d` (day), `-t w` (week), `-t m` (month), `-t y` (year)
- Combine: `"react native" expo -reddit`

## MCP Server Usage

The package also runs as an MCP server for AI assistants and agents.

### As stdio server

```bash
open-search-mcp
```

### With Claude Desktop / MCP clients

```json
{
  "mcpServers": {
    "open-search": {
      "command": "uvx",
      "args": ["open-search-mcp"]
    }
  }
}
```

### MCP Tools

- **`search`** — Web search with filters (region, time, site)
- **`fetch`** — URL → clean text extraction
- **`research`** — Search + auto-fetch combined

## Dependencies

- [click](https://click.palletsprojects.com/) — CLI framework
- [ddgs](https://github.com/deedy5/duckduckgo_search) — DuckDuckGo search
- [httpx](https://github.com/encode/httpx) — HTTP client
- [trafilatura](https://github.com/adbar/trafilatura) — Web content extraction
- [mcp](https://github.com/modelcontextprotocol/python-sdk) — Model Context Protocol SDK

## License

MIT
