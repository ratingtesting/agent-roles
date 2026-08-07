#!/usr/bin/env python3
"""
Crawl4AI web content extraction tool for Hermes Agent.
Free, local, no API keys needed.
"""

import asyncio
import json
import sys
from typing import Optional

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode


async def extract_url(url: str, bypass_cache: bool = True, headless: bool = True) -> str:
    """Extract full page content as Markdown using Crawl4AI."""
    browser_config = BrowserConfig(headless=headless, verbose=True)
    cache_mode = CacheMode.BYPASS if bypass_cache else CacheMode.ENABLED
    run_config = CrawlerRunConfig(cache_mode=cache_mode)

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url=url, config=run_config)

        if result.success:
            return result.markdown
        else:
            raise RuntimeError(f"Extraction failed: {result.error_message}")


def main():
    if len(sys.argv) < 2:
        print("Usage: crawl4ai_extract.py <url> [bypass_cache] [headless]")
        sys.exit(1)

    url = sys.argv[1]
    bypass_cache = sys.argv[2].lower() == "true" if len(sys.argv) > 2 else True
    headless = sys.argv[3].lower() == "true" if len(sys.argv) > 3 else True

    try:
        result = asyncio.run(extract_url(url, bypass_cache, headless))
        print(result)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()