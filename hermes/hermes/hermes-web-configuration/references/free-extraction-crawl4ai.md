# Free Web Extraction: Crawl4AI as Alternative to Firecrawl

## Overview

Crawl4AI (72.5k ⭐) is a Python library for local web content extraction — no Docker, no API keys, completely free.

## Installation

```bash
# In Hermes venv
/c/Users/Unicorn/AppData/Local/hermes/hermes-agent/venv/Scripts/python -m pip install crawl4ai
/c/Users/Unicorn/AppData/Local/hermes/hermes-agent/venv/Scripts/python -m playwright install chromium
```

## Usage as Standalone Script

```bash
/c/Users/Unicorn/AppData/Local/Temp/c4aivenv/.venv/Scripts/python crawl4ai_extract.py <url>
```

Returns full Markdown with structure (headings, lists, tables, code blocks).

## Comparison

| Feature | browser_navigate + snapshot | Crawl4AI |
|---------|----------------------------|----------|
| **Time** | ~6s | ~5s |
| **Content** | Truncated (15k chars) | Full page |
| **Format** | Accessibility tree | Clean Markdown |
| **Structure** | DOM-ish | Semantic (H1-H6, tables, code) |
| **Metrics** | None | links, images, media, fit_markdown |
| **Cache** | None | CacheMode (BYPASS/ENABLED/READ_ONLY) |

## Key Finding

**browser_navigate reads pages but truncates at 15000 chars.** Crawl4AI returns complete Markdown without truncation — critical for long articles, documentation, large pages.

## Integration Options

1. **Standalone script** (current): Call via shell, parse stdout
2. **MCP server**: Expose as `extract_url` tool (needs `mcp` + `pywin32` in venv)
3. **Direct skill tool**: Add `crawl4ai_extract` tool to skill

## Why Not MCP Currently

MCP package requires `pywin32` which has Windows-specific installation quirks. The standalone script works reliably now; MCP can be added later when needed.

## Source

- GitHub: https://github.com/unclecode/crawl4AI (72.5k stars)
- Docs: https://docs.crawl4ai.com/