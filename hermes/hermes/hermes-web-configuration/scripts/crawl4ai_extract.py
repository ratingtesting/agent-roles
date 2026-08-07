#!/usr/bin/env python3
"""
Standalone Crawl4AI extraction script for Hermes.
Usage: python crawl4ai_extract.py <url> [--max-chars N]
Outputs full Markdown to stdout.
"""

import asyncio
import sys
import argparse

try:
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
except ImportError:
    print("ERROR: crawl4ai not installed. Run: pip install crawl4ai && playwright install chromium", file=sys.stderr)
    sys.exit(1)

async def extract(url: str, max_chars: int = 0) -> str:
    config = BrowserConfig(headless=True, verbose=False)
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        wait_for="networkidle",
        screenshot=False,
        pdf=False,
    )
    
    async with AsyncWebCrawler(config=config) as crawler:
        result = await crawler.arun(url=url, config=run_config)
        
        if not result.success:
            raise RuntimeError(f"Crawl failed: {result.error_message}")
        
        markdown = result.markdown or ""
        
        if max_chars > 0 and len(markdown) > max_chars:
            markdown = markdown[:max_chars] + f"\n\n[TRUNCATED at {max_chars} chars]"
        
        return markdown

def main():
    parser = argparse.ArgumentParser(description="Extract URL content as Markdown using Crawl4AI")
    parser.add_argument("url", help="URL to extract")
    parser.add_argument("--max-chars", type=int, default=0, help="Truncate output (0 = no limit)")
    args = parser.parse_args()
    
    try:
        markdown = asyncio.run(extract(args.url, args.max_chars))
        print(markdown)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()