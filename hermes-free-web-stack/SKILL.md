---
name: hermes-free-web-stack
description: Configure Hermes Agent for completely free web search and extraction using ddgs and Crawl4AI, avoiding paid gateways.
category: hermes
version: 1.1.0
---

# Hermes Free Web Stack

Configure Hermes Agent to use entirely free, local web backends — no paid APIs, no Docker, no API keys.

## What This Covers
- **Search**: DuckDuckGo via `ddgs` (built-in plugin)
- **Extract**: Crawl4AI (full Markdown, no character limits, ~3-5s per page)
- **Browser**: Local Chromium (not Browser-Use cloud)

## Why This Matters
Hermes defaults to paid services (Firecrawl, Browser-Use) via the Nous managed gateway when free backends are misconfigured or missing. This skill locks in the free stack and provides a verification script to catch regressions.

## Setup Steps

### 1. Install Crawl4AI Dependencies (One-Time)
```bash
# Create an isolated venv for crawl4ai (avoids Hermes venv conflicts)
cd /tmp && uv venv c4aivenv && uv pip install crawl4ai
/tmp/c4aivenv/.venv/Scripts/python -m playwright install chromium
```

### 2. Create the Hermes Plugin
Place three files in `~/.hermes/plugins/web/crawl4ai/`:
- `plugin.yaml` — plugin metadata (see `references/plugin.yaml`)
- `provider.py` — provider implementation (see `references/provider.py`)
- `__init__.py` — registration entry point (calls `ctx.register_web_search_provider`)

Enable it:
```bash
hermes plugins enable web-crawl4ai
```

### 3. Apply Configuration
Add the following to `~/.hermes/config.yaml` (or profile-specific config):
```yaml
web:
  backend: crawl4ai
  search_backend: ddgs
  extract_backend: crawl4ai
  use_gateway: false
browser:
  cloud_provider: local
  use_gateway: false
```

### 4. Force-Register the Plugin in Web Provider Registry (CRITICAL)

Without this step, `web_extract` falls back to **Firecrawl** even when the plugin is enabled and configured. Run this Python snippet once per Hermes session (or add it to a startup skill):

```python
import sys
sys.path.insert(0, r'C:\Users\Unicorn\AppData\Local\hermes\hermes-agent')
from hermes_cli.plugins import discover_plugins, get_plugin_manager, PluginContext
discover_plugins()
pm = get_plugin_manager()
plugin = pm._plugins.get('web/crawl4ai')
if plugin and plugin.module and hasattr(plugin.module, 'register'):
    ctx = PluginContext(plugin.manifest, pm)
    plugin.module.register(ctx)
    print("✅ crawl4ai registered in web provider registry")
from agent.web_search_registry import get_provider, get_active_extract_provider
p = get_provider('crawl4ai')
assert p is not None and p.is_available(), "❌ crawl4ai NOT available — fix before proceeding"
print(f"✅ Active extract provider: {get_active_extract_provider().name}")
```

To avoid repeating this across sessions, create a startup script that auto-registers the plugin on Hermes boot. See `references/auto-register-startup.py`.

### 5. Verify
Run the verification script:
```bash
bash ~/.hermes/skills/hermes-free-web-stack/scripts/verify-free-web.sh
```
Expected: all checks pass, 0 errors.

### 6. Quick Functional Test
```bash
hermes chat -q "extract https://example.com" --toolsets web 2>&1 | tee /tmp/test_extract.log
grep -ic firecrawl /tmp/test_extract.log   # should be 0
grep -ic browser-use /tmp/test_extract.log # should be 0
```

## How It Works (Critical: Registry Registration)
- `web_search` → built-in `ddgs` plugin (no config needed beyond `search_backend: ddgs`)
- `web_extract` → `web-crawl4ai` plugin → calls local crawl4ai script via subprocess
- `browser_navigate` → local Chromium when `browser.cloud_provider = local`
- `*_use_gateway: false` prevents the Nous managed gateway from being used as a paid fallback

**⚠️ CRITICAL: Plugin registration is NOT automatic.** The `web-crawl4ai` plugin must be FORCE-REGISTERED in the web provider registry. Without this step, the Hermes `_get_backend()` function:
1. Reads `web.extract_backend = crawl4ai` from config
2. Sees `crawl4ai` is NOT in `_LEGACY_WEB_BACKENDS` (it's a plugin)
3. Calls `_registered_web_provider("crawl4ai")` → returns `None` (plugin not yet registered)
4. Falls through to the default fallback → returns `("firecrawl", _is_tool_gateway_ready())`
5. **Firecrawl → money charged through managed gateway**

The fix: after `hermes plugins enable`, run the force-registration Python snippet (see Setup Step 4a).

## Core Files Created in This Skill
The skill includes these reference files:
- `references/plugin.yaml` — exact plugin metadata we used
- `references/provider.py` — exact provider implementation we used
- `scripts/verify-free-web.sh` — verification script we developed

## Troubleshooting
- **Config overwritten by model switch?** Some users reported that `hermes model` resets config; reapply the `hermes config set` commands if you notice paid gateways reappearing. **Root cause**: The model switch process can trigger a config reset that clears web.* settings, causing fallback to legacy firecrawl backend. See `references/firecrawl-fallback-root-cause.md` for full details.
- **Plugin detected but web_extract still goes to firecrawl?** This is the #1 pitfall. Even with `web.extract_backend: crawl4ai` in config and plugin enabled, `_get_backend()` falls back to firecrawl if `crawl4ai` is not in the *in-memory registry* of web providers. The plugin's `is_available()` may return `True`, but if `register(ctx)` was never called, the provider isn't in the registry. **Fix**: Run the force-registration step (4a) — manually call `ctx.module.register(ctx)` via Python.
- **Plugin not detected?** Ensure the plugin directory contains all three files (`plugin.yaml`, `provider.py`, `__init__.py`) and that the plugin is enabled (`hermes plugins list` shows ✓).
- **Crawl4AI import errors?** Use the isolated venv and ensure the `provider.py` points to the correct Python executable and script path. **Important**: The MCP approach failed due to pywin32/cryptography conflicts in the Hermes venv - use the direct plugin approach instead.
- **ddgs not found in Hermes venv?** If `web_search` fails, install it in the Hermes venv:
  ```bash
  HERMES_PYTHON=$(hermes config path | xargs dirname)/venv/Scripts/python.exe
  $HERMES_PYTHON -m pip install ddgs
  ```
- **Extractor returns empty?** Check that the crawler can reach the site (network, firewall); confirm Playwright browsers are installed.
- **Still getting Firecrawl charges?** You MUST set BOTH `web.backend: crawl4ai` AND `web.extract_backend: crawl4ai` in config.yaml. Setting only one may still fall back to Firecrawl due to Hermes' backend resolution logic.

## Pitfall — truncating authoritative docs with `char_limit` is not free

This whole stack assumes the loop *search → extract (free) → cache on disk → read with `read_file offset`* saves paid tokens. The saving only works if the doc extraction is **complete**. A live failure mode observed in July 2026: `web_extract(urls=[doc], char_limit=7000)` was called on a 16,000-char OpenHands command-reference page to "save tokens". The truncation chopped the section that contained the only data the agent needed (`agent_settings.json` filename, `--override-with-envs` flag). The agent then guessed at JSON shape and burned four extra tool turns flushing far more tokens than the limit "saved".

Rule when this skill is in play: **set `char_limit` to 0 (full page) — or to enough headroom that the part you intend to read survives intact**. For canonical reference pages in the 2–30 KB range, default to no limit; the cached file at `~/.hermes/cache/web/<host>-<hash>.md` is already on disk and `read_file offset=N` paginates it for free. For multi-URL research where you only want summaries, a small `char_limit` is still correct — but **for an authoritative doc you intend to *act on*, never truncate on the first read**. Same logic applies to plain-text endpoints (`.md`/`.txt`/raw): curl or `web_extract` is faster and smaller than the TUI `browser_navigate`.

## Reference
- `references/plugin.yaml` — template for the plugin metadata file
- `references/provider.py` — reference implementation of the crawl4ai provider
- `references/config-snippet.yaml` — example `config.yaml` section
- `references/firecrawl-fallback-root-cause.md` — **critical**: why charges persist and the full fix path
- `scripts/verify-free-web.sh` — automated verification script
- `scripts/verify-free-config.sh` — config-only verification (no hermes chat call)

## Related Skills
- `hermes-agent` (bundled) — core Hermes configuration
- `crawl4ai-extractor` — the extraction skill/script that the provider calls