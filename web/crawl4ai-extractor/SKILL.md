---
name: crawl4ai-extractor
description: Free local web content extraction using Crawl4AI (no API keys, no Docker)
version: "1.1.0"
category: web
tags:
  - web
  - extraction
  - crawl4ai
  - free
  - local
author: Hermes Agent
---

# Crawl4AI Extractor Skill

Provides `crawl4ai_extract` script for extracting clean Markdown content from any URL using the Crawl4AI Python library. Completely free, runs locally via Playwright/Chromium.

**Primary integration: AGENTS.md mandates this as default web extractor.** Agents must use this before falling back to `browser_navigate`.

## Working Environment

The Hermes venv has pywin32/cryptography conflicts preventing MCP server. Use the **working isolated venv**:

```bash
# Working venv (created during setup)
/c/Users/Unicorn/AppData/Local/Temp/c4aivenv/.venv/Scripts/python.exe
```

## Installation (One-time)

```bash
# Create isolated venv
uv venv /c/Users/Unicorn/AppData/Local/Temp/c4aivenv
/c/Users/Unicorn/AppData/Local/Temp/c4aivenv/.venv/Scripts/python -m pip install crawl4ai playwright
/c/Users/Unicorn/AppData/Local/Temp/c4aivenv/.venv/Scripts/python -m playwright install chromium
```

## Usage (Direct Script Call)

```bash
/c/Users/Unicorn/AppData/Local/Temp/c4aivenv/.venv/Scripts/python.exe \
  /c/Users/Unicorn/AppData/Local/hermes/skills/web/crawl4ai-extractor/scripts/crawl4ai_extract.py \
  "<URL>" true true
```

**Args:** `<URL> <bypass_cache:true|false> <headless:true|false>`

**Returns:** Full Markdown content to stdout (no truncation, no 15k char limit).

## AGENTS.md Integration

The global `/c/Users/Unicorn/AGENTS.md` now mandates extraction priority:

```
1. web_search (DDGS) → 2. crawl4ai_extract (this skill) → 3. browser_navigate (fallback only)
```

Agents automatically use this skill for web content extraction without explicit prompting.

## Pitfalls Fixed

- **MCP server fails** in Hermes venv due to pywin32 import error → use direct script
- **Hermes venv packages broken** (cryptography version conflict) → use isolated c4aivenv
- **browser_navigate truncates at 15k chars** → crawl4ai returns full Markdown
- **web_extract has no free backend** → this skill fills the gap

## Tested Performance

| Page Type | Time | Output |
|-----------|------|--------|
| example.com | ~1.5s | 166 chars |
| Wikipedia (Python) | ~4.5s | Full article Markdown |
| News article | ~3-6s | Full article Markdown |