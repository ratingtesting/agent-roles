#!/usr/bin/env python3
"""
Crawl4AI MCP Server for Hermes.
Exposes `extract_url` tool via MCP stdio.
Run: python crawl4ai_mcp_server.py
"""

import asyncio
import sys
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.server.models import InitializationOptions
from mcp.server.lowlevel import NotificationOptions
from mcp.types import Tool, TextContent
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

app = Server("crawl4ai-extractor")

@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="extract_url",
            description="Extract full page content as clean Markdown using Crawl4AI (local, free, no API key)",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to extract"},
                    "max_chars": {"type": "integer", "default": 0, "description": "Truncate output (0 = no limit)"}
                },
                "required": ["url"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, args: dict):
    if name != "extract_url":
        return [TextContent(type="text", text=f"Unknown tool: {name}")]
    
    url = args.get("url")
    max_chars = args.get("max_chars", 0)
    
    if not url:
        return [TextContent(type="text", text="ERROR: url is required")]
    
    config = BrowserConfig(headless=True, verbose=False)
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        wait_for="networkidle",
        screenshot=False,
        pdf=False,
    )
    
    try:
        async with AsyncWebCrawler(config=config) as crawler:
            result = await crawler.arun(url=url, config=run_config)
            
            if not result.success:
                return [TextContent(type="text", text=f"ERROR: {result.error_message}")]
            
            markdown = result.markdown or ""
            
            if max_chars > 0 and len(markdown) > max_chars:
                markdown = markdown[:max_chars] + f"\n\n[TRUNCATED at {max_chars} chars]"
            
            return [TextContent(type="text", text=markdown)]
            
    except Exception as e:
        return [TextContent(type="text", text=f"ERROR: {e}")]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="crawl4ai-extractor",
                server_version="1.0.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(
                        tools_changed=True,
                        resources_changed=True,
                        prompts_changed=True
                    ),
                    experimental_capabilities=None,
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())