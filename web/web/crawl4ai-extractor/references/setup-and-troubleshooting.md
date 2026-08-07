# Crawl4AI Extractor — Setup & Troubleshooting

## Working Environment
- **Isolated venv**: `/c/Users/Unicorn/AppData/Local/Temp/c4aivenv/.venv/`
- **Python**: `/c/Users/Unicorn/AppData/Local/Temp/c4aivenv/.venv/Scripts/python.exe`
- **Script**: `/c/Users/Unicorn/AppData/Local/hermes/skills/web/crawl4ai-extractor/scripts/crawl4ai_extract.py`

## Why Not Hermes Venv?
Hermes venv has broken `pywin32`/`cryptography` causing `ModuleNotFoundError: pywintypes` when importing `mcp`. The isolated venv works cleanly.

## One-Time Setup
```bash
# Create venv
uv venv /c/Users/Unicorn/AppData/Local/Temp/c4aivenv

# Install deps
/c/Users/Unicorn/AppData/Local/Temp/c4aivenv/.venv/Scripts/python -m pip install crawl4ai playwright

# Install browser
/c/Users/Unicorn/AppData/Local/Temp/c4aivenv/.venv/Scripts/python -m playwright install chromium
```

## Direct Call (What Agents Use)
```bash
/c/Users/Unicorn/AppData/Local/Temp/c4aivenv/.venv/Scripts/python.exe \
  /c/Users/Unicorn/AppData/Local/hermes/skills/web/crawl4ai-extractor/scripts/crawl4ai_extract.py \
  "https://example.com" true true
```

## Verification Test
```bash
/c/Users/Unicorn/AppData/Local/Temp/c4aivenv/.venv/Scripts/python.exe \
  /c/Users/Unicorn/AppData/Local/hermes/skills/web/crawl4ai-extractor/scripts/crawl4ai_extract.py \
  "https://example.com" true true
```
Expected: Full Markdown output, no errors.

## AGENTS.md Mandate
Global `/c/Users/Unicorn/AGENTS.md` enforces extraction priority:
```
1. web_search (DDGS)
2. crawl4ai_extract (this skill — direct script call)
3. browser_navigate (fallback only)
```

## Common Issues

| Issue | Fix |
|-------|-----|
| `pywintypes` error | Use isolated venv, not Hermes venv |
| `crawl4ai` not found | Re-run pip install in isolated venv |
| Playwright browser missing | Run `playwright install chromium` in isolated venv |
| Script path wrong | Use absolute paths as shown above |
| Timeout | Increase timeout to 60-120s for heavy pages |

## Performance Notes
- First run: ~5-6s (browser init + fetch)
- Subsequent runs: ~1-3s (cached browser)
- Output: Complete Markdown, no character limit