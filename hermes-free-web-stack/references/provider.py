"""Crawl4AI web search provider — local, free, full Markdown extraction.

Implements WebSearchProvider ABC. Registers as search-only (supports_search=True)
but its main value is full-page extraction via Crawl4AI.
"""

from __future__ import annotations

import os
import sys
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any

try:
    from pydantic import BaseModel
except ImportError:  # pragma: no cover
    BaseModel = object  # type: ignore

from hermes import tool  # type: ignore


# --- Config ---
# IMPORTANT: Adjust these paths to match your environment
C4AI_VENV = Path(os.environ.get(
    "CRAWL4AI_VENV",
    r"C:\Users\Unicorn\AppData\Local\Temp\c4aivenv\.venv"
))
C4AI_SCRIPT = Path(os.environ.get(
    "CRAWL4AI_SCRIPT",
    r"C:\Users\Unicorn\AppData\Local\hermes\skills\web\crawl4ai-extractor\scripts\crawl4ai_extract.py"
))
C4AI_PYTHON = C4AI_VENV / "Scripts" / "python.exe"
C4AI_TIMEOUT = 120


class Provider:
    name = "crawl4ai"
    supports_search = True
    supports_extract = True

    def __init__(self, config: dict | None = None):
        self._config = config or {}

    def search(self, query: str, max_results: int = 5) -> list[dict]:
        """Search via DDGS — delegate to built-in ddgs backend."""
        # Hermes routes search to ddgs backend automatically.
        return []

    def extract(self, url: str) -> str:
        """Extract full Markdown from a URL using Crawl4AI."""
        if not C4AI_PYTHON.exists():
            return f"[crawl4ai] Python not found: {C4AI_PYTHON}"

        if not C4AI_SCRIPT.exists():
            return f"[crawl4ai] Script not found: {C4AI_SCRIPT}"

        try:
            result = subprocess.run(
                [str(C4AI_PYTHON), str(C4AI_SCRIPT), url, "true", "true"],
                capture_output=True,
                text=True,
                timeout=C4AI_TIMEOUT,
                env={**os.environ, "PYTHONIOENCODING": "utf-8"},
            )
            if result.returncode == 0:
                return result.stdout
            return f"[crawl4ai] Error (rc={result.returncode}): {result.stderr[-500:]}"
        except subprocess.TimeoutExpired:
            return f"[crawl4ai] Timeout after {C4AI_TIMEOUT}s"
        except Exception as e:
            return f"[crawl4ai] {type(e).__name__}: {e}"


def register():
    return Provider()