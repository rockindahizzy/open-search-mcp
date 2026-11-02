# dsh-plugin-open-search

A [DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness) plugin that gives the agent open-search's keyless web tools:

| Tool | What it does |
|------|--------------|
| `open_search` | DuckDuckGo search: titles, URLs, and snippets |
| `open_fetch` | Fetch a URL and extract its readable text |
| `open_research` | Search, then fetch the top N results in one call |

The tool names are prefixed `open_` so they don't clash with the harness's built-in `web_search` / `web_fetch`.

Each tool runs the `open-search` CLI with `--json`, so the Python package stays the only implementation.

## Requirements

- The `open-search` CLI on this machine:

  ```bash
  uv tool install open-search-mcp
  ```

  The plugin looks for it on `PATH`, then in `~/.local/bin`, `/opt/homebrew/bin`, and `/usr/local/bin`. Apps launched from Finder don't inherit your shell's `PATH`, which is why those extra directories are checked.
- DeepSeek Harness 0.2.x

## Build

```bash
cd dsh-plugin
npm install
npm run build
```

## Install into the harness

Install it as a bundle into your profile (`desktop` is the desktop app's profile). You can use the **Plugins** page and give it the absolute path to this directory, or run the bundled CLI:

```bash
"/Applications/DeepSeek Harness.app/Contents/Resources/runtime/cli/bin/dsh" plugin --profile desktop add "$PWD"
```

Run this from inside `dsh-plugin/` after building. Then restart the app, or let HMR reload the profile. If you rebuild after changing the code, restart the app so it loads the new module.

## Configuration

To change the defaults, add an override to `~/.dsh/profiles/desktop/cordis.patch.yml`:

```yaml
- id: open-search
  config:
    command: /absolute/path/to/open-search   # default: open-search
    timeoutMs: 120000                        # per-call timeout
```
