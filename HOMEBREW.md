# Homebrew Distribution Guide

## Setup (one-time)

### 1. Create the tap repo

Create a GitHub repo named `homebrew-tap` under your account:

```bash
gh repo create rockindahizzy/homebrew-tap --public --description "Homebrew formulae"
```

### 2. Publish to PyPI first

Homebrew formulas pull from PyPI (stable, versioned tarballs):

```bash
cd web-search-mcp

# Build the distribution
uv build

# Upload to PyPI (needs account + token)
uv publish
# or: twine upload dist/*
```

### 3. Generate the formula

Use `homebrew-pypi-poet` to auto-generate all virtualenv resource blocks:

```bash
# Install poet
pipx install homebrew-pypi-poet

# Generate resources for all dependencies
poet -r open-search-mcp
```

This outputs the `resource` blocks. Paste them into the formula.

### 4. Get the SHA256

```bash
# From the PyPI tarball URL:
curl -sL https://pypi.io/packages/source/o/open-search-mcp/open_search_mcp-0.1.0.tar.gz | shasum -a 256
```

Replace `PLACEHOLDER` in the formula with the real hash.

### 5. Copy formula to tap repo

```bash
cp Formula/open-search-mcp.rb ~/path/to/homebrew-tap/Formula/
cd ~/path/to/homebrew-tap
git add Formula/open-search-mcp.rb
git commit -m "Add open-search-mcp formula"
git push
```

### 6. Users install with

```bash
brew tap rockindahizzy/tap
brew install open-search-mcp
```

After that, `open-search` and `open-search-mcp` are both on PATH.

## Updating

When you release a new version:

1. Bump version in `pyproject.toml`
2. `uv build && uv publish`
3. Update formula: new URL, new sha256, re-run `poet -r` if deps changed
4. Push to tap repo

## Alternative: Homebrew core

If the tool gets popular enough, you can submit to homebrew-core (no tap needed).
Requirements: 75+ GitHub stars, stable releases, passing `brew audit --strict`.
