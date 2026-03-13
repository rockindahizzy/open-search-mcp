"""
open-search: CLI for web search, fetch, and research via DuckDuckGo + Trafilatura.
No API key required.
"""

import json
import sys

import click

from web_search_mcp.server import _fetch_url, _search_ddg


def _print_json(data: dict) -> None:
    """Pretty-print JSON to stdout."""
    click.echo(json.dumps(data, indent=2))


def _print_results(results: list[dict], verbose: bool = False) -> None:
    """Human-friendly output for search results."""
    if not results:
        click.echo("No results found.")
        return

    for i, r in enumerate(results, 1):
        click.secho(f"  {i}. {r.get('title', '(no title)')}", fg="bright_white", bold=True)
        click.secho(f"     {r.get('url', '')}", fg="cyan")
        snippet = r.get("snippet", "")
        if snippet:
            # Wrap snippet to ~80 chars with indent
            click.echo(f"     {snippet[:200]}")
        if r.get("content"):
            chars = r.get("content_chars", len(r["content"]))
            click.secho(f"     📄 Fetched {chars:,} chars", fg="green")
            if verbose:
                click.echo()
                click.echo(r["content"])
                click.echo()
        click.echo()


@click.group()
@click.version_option(package_name="open-search-mcp")
def cli():
    """🔍 open-search — Keyless web search from the terminal.

    Search the web, fetch pages, and do research — all via DuckDuckGo.
    No API keys needed.
    """
    pass


@cli.command()
@click.argument("query")
@click.option("-n", "--max-results", default=10, show_default=True, help="Number of results (1-25)")
@click.option("-r", "--region", default="wt-wt", show_default=True, help="Region code (wt-wt=global, us-en, uk-en)")
@click.option("-t", "--time", "time_range", type=click.Choice(["d", "w", "m", "y"]), help="Time filter: d=day, w=week, m=month, y=year")
@click.option("-s", "--site", help="Limit to domain (e.g. github.com)")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON")
def search(query, max_results, region, time_range, site, as_json):
    """Search the web via DuckDuckGo.

    \b
    Examples:
      open-search search "python async tutorial"
      open-search search "react native" -n 5 -t w
      open-search search "security CVE" -s github.com
      open-search search "AI consciousness" --json
    """
    results = _search_ddg(
        query=query,
        max_results=min(max(1, max_results), 25),
        region=region,
        time_range=time_range,
        site=site,
    )

    formatted = [
        {
            "title": r.get("title", ""),
            "url": r.get("href", r.get("link", "")),
            "snippet": r.get("body", r.get("snippet", "")),
        }
        for r in results
    ]

    if as_json:
        _print_json({"query": query, "results": formatted, "count": len(formatted)})
    else:
        click.secho(f'🔍 "{query}" — {len(formatted)} results\n', fg="bright_white")
        _print_results(formatted)


@cli.command()
@click.argument("url")
@click.option("-m", "--max-chars", default=20000, show_default=True, help="Max characters to extract")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON")
def fetch(url, max_chars, as_json):
    """Fetch a URL and extract readable content.

    \b
    Examples:
      open-search fetch https://example.com/article
      open-search fetch https://news.ycombinator.com -m 5000
      open-search fetch https://example.com --json
    """
    max_chars = min(max(1000, max_chars), 100000)
    result = _fetch_url(url, max_chars=max_chars)

    if as_json:
        _print_json(result)
    else:
        if result.get("error"):
            click.secho(f"❌ Error: {result['error']}", fg="red", err=True)
            sys.exit(1)

        click.secho(f"📄 {url}", fg="cyan")
        click.secho(f"   Status: {result.get('status')} | {result.get('chars', 0):,} chars", fg="bright_black")
        if result.get("truncated"):
            click.secho(f"   ⚠️  Truncated to {max_chars:,} chars", fg="yellow")
        click.echo()
        click.echo(result.get("content", "[No content]"))


@cli.command()
@click.argument("query")
@click.option("-n", "--max-results", default=5, show_default=True, help="Total search results")
@click.option("-f", "--fetch-top", default=3, show_default=True, help="Auto-fetch top N results (0-5)")
@click.option("-m", "--max-chars", default=10000, show_default=True, help="Max chars per fetched page")
@click.option("-r", "--region", default="wt-wt", show_default=True, help="Region code")
@click.option("-t", "--time", "time_range", type=click.Choice(["d", "w", "m", "y"]), help="Time filter")
@click.option("-s", "--site", help="Limit to domain")
@click.option("-v", "--verbose", is_flag=True, help="Show full fetched content inline")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON")
def research(query, max_results, fetch_top, max_chars, region, time_range, site, verbose, as_json):
    """Search + auto-fetch: searches the web, then fetches top results.

    Best for deep dives where you need actual page content,
    not just snippets.

    \b
    Examples:
      open-search research "philosophy of mind AI"
      open-search research "rust vs go 2025" -f 5 -v
      open-search research "CVE-2025" -t w -s nvd.nist.gov --json
    """
    max_results = min(max(1, max_results), 25)
    fetch_top = min(max(0, fetch_top), max_results, 5)
    max_chars = min(max(1000, max_chars), 50000)

    results = _search_ddg(
        query=query,
        max_results=max_results,
        region=region,
        time_range=time_range,
        site=site,
    )

    formatted = []
    fetched_count = 0
    for i, r in enumerate(results):
        entry = {
            "title": r.get("title", ""),
            "url": r.get("href", r.get("link", "")),
            "snippet": r.get("body", r.get("snippet", "")),
        }

        if i < fetch_top and entry["url"]:
            if not as_json:
                click.secho(f"  ⏳ Fetching [{i+1}/{fetch_top}]: {entry['url']}", fg="bright_black", err=True)
            page = _fetch_url(entry["url"], max_chars=max_chars)
            entry["content"] = page.get("content")
            entry["content_chars"] = page.get("chars", 0)
            entry["content_truncated"] = page.get("truncated", False)
            entry["fetch_error"] = page.get("error")
            fetched_count += 1

        formatted.append(entry)

    if as_json:
        _print_json({
            "query": query,
            "results": formatted,
            "count": len(formatted),
            "fetched": fetched_count,
        })
    else:
        click.echo()
        click.secho(f'🔬 "{query}" — {len(formatted)} results, {fetched_count} fetched\n', fg="bright_white")
        _print_results(formatted, verbose=verbose)


def main():
    cli()


if __name__ == "__main__":
    main()
