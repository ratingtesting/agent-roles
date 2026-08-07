# Crawl4AI Hermes Plugin — provider.py Template

Copy this to `~/.hermes/plugins/web/crawl4ai/provider.py`.

## Full Source

```python
\"\"\"Crawl4AI web search provider — local, free, full Markdown extraction.

Implements WebSearchProvider ABC. Registers as extract-only
(supports_extract=True), providing full-page Markdown via Crawl4AI.
\"\"\"

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List, Optional

from agent.web_search_provider import WebSearchProvider

logger = logging.getLogger(__name__)

_CRAWL4AI_IMPORTABLE: bool | None = None


def _crawl4ai_importable() -> bool:
    global _CRAWL4AI_IMPORTABLE
    if _CRAWL4AI_IMPORTABLE is not None:
        return _CRAWL4AI_IMPORTABLE
    try:
        import crawl4ai  # noqa: F401
        _CRAWL4AI_IMPORTABLE = True
    except ImportError:
        _CRAWL4AI_IMPORTABLE = False
    return _CRAWL4AI_IMPORTABLE


class Crawl4AIWebProvider(WebSearchProvider):

    @property
    def name(self) -> str:
        return "crawl4ai"

    @property
    def display_name(self) -> str:
        return "Crawl4AI (free, local)"

    def is_available(self) -> bool:
        return _crawl4ai_importable()

    def supports_search(self) -> bool:
        return False

    def supports_extract(self) -> bool:
        return True

    def extract(self, urls: List[str], **kwargs: Any) -> Any:
        return asyncio.run(self._extract_async(urls, kwargs))

    async def _extract_async(
        self, urls: List[str], kwargs: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

        headless = kwargs.get("headless", True)
        bypass_cache = kwargs.get("bypass_cache", True)
        cache_mode = CacheMode.BYPASS if bypass_cache else CacheMode.ENABLED
        browser_config = BrowserConfig(headless=headless, verbose=False)
        run_config = CrawlerRunConfig(cache_mode=cache_mode)

        results = []
        try:
            async with AsyncWebCrawler(config=browser_config) as crawler:
                for url in urls:
                    try:
                        result = await crawler.arun(url=url, config=run_config)
                        if result.success:
                            content = result.markdown
                            title = (result.metadata or {}).get("title", "")
                            results.append({
                                "url": url, "title": title,
                                "content": content, "raw_content": content,
                                "metadata": result.metadata or {},
                            })
                        else:
                            results.append({
                                "url": url, "title": "", "content": "",
                                "raw_content": "", "error": result.error_message,
                            })
                    except Exception as e:
                        results.append({
                            "url": url, "title": "", "content": "",
                            "raw_content": "", "error": str(e),
                        })
        except Exception as e:
            for url in urls:
                results.append({
                    "url": url, "title": "", "content": "",
                    "raw_content": "", "error": str(e),
                })
        return results

    def get_setup_schema(self) -> Dict[str, Any]:
        return {
            "name": "Crawl4AI (free, local)",
            "badge": "free",
            "tag": "No API key needed — uses local Chromium via Crawl4AI.",
            "env_vars": [],
        }
```

## Files to Create (3 total)

```
~/.hermes/plugins/web/crawl4ai/
├── plugin.yaml     # from SKILL.md
├── __init__.py     # from SKILL.md
└── provider.py     # this file
```

## Enable

```bash
hermes plugins enable web-crawl4ai
# /reset to activate
```
