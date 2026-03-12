class OpenSearchMcp < Formula
  include Language::Python::Virtualenv

  desc "Keyless web search CLI and MCP server via DuckDuckGo"
  homepage "https://github.com/rockindahizzy/open-search-mcp"
  url "https://pypi.io/packages/source/o/open-search-mcp/open_search_mcp-0.1.0.tar.gz"
  sha256 "PLACEHOLDER"
  license "MIT"

  depends_on "python@3.13"

  # Dependencies will be populated after first PyPI release.
  # Run: poet -r open-search-mcp
  # to auto-generate virtualenv resource blocks.

  def install
    virtualenv_install_with_resources
  end

  test do
    assert_match "open-search", shell_output("#{bin}/open-search --help")
  end
end
