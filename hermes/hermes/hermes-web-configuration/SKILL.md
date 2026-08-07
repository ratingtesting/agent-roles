---
name: hermes-web-configuration
description: "Configure Hermes web tools (search + extraction) with free backends — DDGS for search, Crawl4AI plugin for full-page Markdown extraction, local Chromium browser as fallback"
version: 2.2.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [hermes, web, search, browser, configuration, free, ddgs, duckduckgo]
    related_skills: [hermes-agent, custom-provider-setup]
---

# Hermes Web Configuration — Free Setup

## Scope

This skill covers configuring Hermes's web tools (`web_search`, `web_extract`) to work **without paid services** like Firecrawl, Tavily, Parallel, or Exa. The free architecture:

1. **Search** → DuckDuckGo (`ddgs` Python package) — no API key needed  
2. **Extraction** → Crawl4AI (Hermes plugin `web-crawl4ai`) — full Markdown, no API keys, no Docker  
3. **Fallback page reading** → Local Chromium (`browser_navigate`) — for interactive pages / JS-heavy sites

## Backend Capability Reference

| Backend | Search | Extract | Cost | Requires |
|---------|--------|---------|------|----------|
| `firecrawl` | ✅ | ✅ | Paid | `FIRECRAWL_API_KEY` |
| `parallel` | ✅ | ✅ | Paid | `PARALLEL_API_KEY` |
| `tavily` | ✅ | ✅ | Paid | `TAVILY_API_KEY` |
| `exa` | ✅ | ✅ | Paid | `EXA_API_KEY` |
| `xai` | ✅ | ✅ | Paid | xAI credentials |
| `searxng` | ✅ | ❌ | Free self-hosted | `SEARXNG_URL` |
| `brave-free` | ✅ | ❌ | Free tier | `BRAVE_SEARCH_API_KEY` |
| `ddgs` | ✅ | ❌ | **Free** | `pip install ddgs` |
| **`crawl4ai`** | ❌ | ✅ | **Free** | `pip install crawl4ai` + playwright |

## Setup Steps

### 1. Install DDGS (Search)

```bash
HERMES_VENV_SITE=$(dirname "$(command -v hermes)")/../Lib/site-packages
uv pip install ddgs --target "$HERMES_VENV_SITE"
# Verify:
python -c "import ddgs; print('ddgs OK')"
```

On Windows (git-bash): `/c/Users/<user>/AppData/Local/hermes/hermes-agent/venv/Lib/site-packages`

### 2. Install Crawl4AI + Playwright (Extraction)

```bash
# Install to Hermes venv directly (Windows git-bash):
# Find the actual Hermes venv:
HERMES_VENV_SITE="/c/Users/Unicorn/AppData/Local/hermes/hermes-agent/venv/Lib/site-packages"

# Option A: Direct install (if pip available in Hermes venv)
/c/Users/Unicorn/AppData/Local/hermes/hermes-agent/venv/Scripts/python -m pip install crawl4ai
/c/Users/Unicorn/AppData/Local/hermes/hermes-agent/venv/Scripts/python -m playwright install chromium

# Option B: Isolated uv venv + copy (if Hermes venv pip is broken)
cd /tmp && uv venv c4aivenv && uv pip install crawl4ai
/tmp/c4aivenv/.venv/Scripts/python -m playwright install chromium
cp -r /tmp/c4aivenv/.venv/Lib/site-packages/crawl4ai* "$HERMES_VENV_SITE/"
```

> **HERMES_VENV path note:** The path is `/c/Users/Unicorn/AppData/Local/hermes/hermes-agent/venv`. Do NOT use `$(dirname $(dirname $(which hermes)))/venv` — that expands to `.../venv/venv` on Windows because `which hermes` returns the Scripts/ path, and running dirname twice goes one level too deep.

### 3. Create the Crawl4AI Hermes Plugin

Create `~/.hermes/plugins/web/crawl4ai/` OR (Hermes v0.19.0+) `AppData/Local/hermes/plugins/web/crawl4ai/` with three files.

> **Hermes v0.19.0 changed plugin home.** `get_hermes_home()` now returns `AppData\Local\hermes\` (e.g. `C:\Users\<user>\AppData\Local\hermes\`), NOT `~/.hermes/`. User plugins MUST go under the new home's `plugins/` directory to be discovered. The old `~/.hermes/plugins/` path is NOT scanned. Check with:
> ```python
> from hermes_cli.plugins import get_hermes_home
> print(get_hermes_home() / "plugins")
> ```

Files to create:

**`plugin.yaml`**:
```yaml
name: web-crawl4ai
version: 1.0.0
description: "Crawl4AI web content extraction — free, local, no API keys."
author: user
kind: backend
provides_web_providers:
  - crawl4ai
```

**`__init__.py`** (relative import — обязателен для user-плагинов):
```python
from __future__ import annotations
from .provider import Crawl4AIWebProvider
def register(ctx) -> None:
    ctx.register_web_search_provider(Crawl4AIWebProvider())
```

> **Важно:** Используйте `from .provider import ...` (относительный импорт), НЕ `from plugins.web.crawl4ai.provider import ...` (абсолютный). Абсолютный импорт работает только для bundled-плагинов внутри `hermes-agent/plugins/`. User-плагины в `~/.hermes/plugins/` загружаются через другой namespace (`hermes_plugins.web__crawl4ai`), и абсолютный импорт выдаст `ModuleNotFoundError`.

**`provider.py`** — implements `WebSearchProvider` with `supports_extract()=True`:  

```python
"""Crawl4AI web search provider — local, free, full Markdown extraction."""
from __future__ import annotations
import asyncio, logging
from typing import Any, Dict, List, Optional
from agent.web_search_provider import WebSearchProvider
logger = logging.getLogger(__name__)
_CRAWL4AI_IMPORTABLE: bool | None = None
def _crawl4ai_importable() -> bool:
    global _CRAWL4AI_IMPORTABLE
    if _CRAWL4AI_IMPORTABLE is not None: return _CRAWL4AI_IMPORTABLE
    try:
        import crawl4ai
        _CRAWL4AI_IMPORTABLE = True
    except ImportError:
        _CRAWL4AI_IMPORTABLE = False
    return _CRAWL4AI_IMPORTABLE
class Crawl4AIWebProvider(WebSearchProvider):
    @property
    def name(self) -> str: return "crawl4ai"
    @property
    def display_name(self) -> str: return "Crawl4AI (free, local)"
    def is_available(self) -> bool: return _crawl4ai_importable()
    def supports_search(self) -> bool: return False  # extract-only
    def supports_extract(self) -> bool: return True
    def extract(self, urls: List[str], **kwargs: Any) -> Any:
        return asyncio.run(self._extract_async(urls, kwargs))
    async def _extract_async(self, urls: List[str], kwargs: Dict[str, Any]) -> List[Dict[str, Any]]:
        from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
        browser_config = BrowserConfig(headless=kwargs.get("headless", True), verbose=False)
        run_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS if kwargs.get("bypass_cache", True) else CacheMode.ENABLED)
        results: List[Dict[str, Any]] = []
        try:
            async with AsyncWebCrawler(config=browser_config) as crawler:
                for url in urls:
                    try:
                        result = await crawler.arun(url=url, config=run_config)
                        if result.success:
                            content = result.markdown or ""
                            title = (result.metadata.get("title", "") if result.metadata else "")
                            results.append({"url": url, "title": title, "content": content, "raw_content": content, "metadata": result.metadata or {}})
                        else:
                            results.append({"url": url, "title": "", "content": "", "raw_content": "", "error": result.error_message or "Extraction failed"})
                    except Exception as e:
                        logger.debug("crawl4ai error for %s: %s", url, e)
                        results.append({"url": url, "title": "", "content": "", "raw_content": "", "error": str(e)})
        except Exception as e:
            logger.debug("crawl4ai crawler error: %s", e)
            for url in urls: results.append({"url": url, "title": "", "content": "", "raw_content": "", "error": str(e)})
        return results
    def get_setup_schema(self) -> Dict[str, Any]:
        return {"name": "Crawl4AI (free, local)", "badge": "free", "tag": "No API key needed — uses local Chromium via Crawl4AI library.", "env_vars": []}
```

### 4. Configure Backends

```bash
# Free search
hermes config set web.search_backend ddgs
hermes config set web.use_gateway false

# Free extraction (critical: extract_backend must be crawl4ai)
hermes config set web.extract_backend crawl4ai

# Free local browser (fallback)
hermes config set browser.cloud_provider local
hermes config set browser.use_gateway false
```

> **Note:** `web.backend` can stay `ddgs` (search-only). Extraction routes via `web.extract_backend`. Setting `web.backend crawl4ai` also works since the plugin registers as a backend, but is not required.

### 5. Enable the Plugin + Activate

```bash
# On Hermes <0.19.0:
mkdir -p ~/.hermes/plugins/web/crawl4ai
hermes plugins enable web-crawl4ai

# On Hermes v0.19.0+:
mkdir -p /c/Users/<user>/AppData/Local/hermes/plugins/web/crawl4ai
# Add to enabled list in config.yaml (manually — see pitfall below)
```
Add the plugin to `plugins.enabled` in your config.yaml (`AppData\Local\hermes\config.yaml` for v0.19.0+):
```yaml
plugins:
  enabled:
    - web/crawl4ai
    - web/ddgs
```

> **⚠️ Hermes v0.19.0+ critical change:** `hermes plugins enable web/crawl4ai` (note the slash, not hyphen) is the CLI command, but it may fail with `PermissionError` if the Hermes desktop app holds a lock on config.yaml. **Workaround:** edit config.yaml directly using Python or a text editor — add a `plugins.enabled` list (see above). Also, the plugin key is `web/crawl4ai` (directory-based path), NOT the old `web-crawl4ai` (manifest name). Using the wrong key silently does nothing.
>
> **Minimal config edit (Python, run once):**
> ```python
> import yaml
> from pathlib import Path
> conf = Path('C:/Users/<user>/AppData/Local/hermes/config.yaml')
> config = yaml.safe_load(conf.read_text(encoding='utf-8'))
> config.setdefault('plugins', {})['enabled'] = ['web/crawl4ai', 'web/ddgs']
> conf.write_text(yaml.dump(config, default_flow_style=False, allow_unicode=True), encoding='utf-8')
> ```

```bash
# ⚠️ Requires /reset (new session) to take effect
```

> **Important**: User plugins live in `AppData\Local\hermes\plugins\` (v0.19.0+) or `~/.hermes/plugins/` (older). Check with `python -c "from hermes_cli.plugins import get_hermes_home; print(get_hermes_home() / 'plugins')"`. The bundled plugins in `hermes-agent/plugins/` are read-only and overwritten on update.

### 6. Verify

```bash
hermes config | grep -iE "(search_backend|extract_backend|use_gateway|cloud_provider)"
hermes plugins list | grep crawl4ai                # should show "enabled"
hermes tools list | grep web                        # "✓ enabled  web"
```

Expected output:
```yaml
web.search_backend: ddgs
web.extract_backend: crawl4ai
web.use_gateway: false
browser.cloud_provider: local
browser.use_gateway: false
```

## Testing

```bash
# Search
hermes chat -q "search the web for: Hermes Agent" --toolsets web

# Extraction (now goes through Crawl4AI, not Firecrawl)
hermes chat -q "extract https://example.com" --toolsets web

# Search + page reading (browser fallback)
hermes chat -q "find and read the top result for LLM agents" --toolsets web,browser
```

**Expected**: Zero Firecrawl/Browser-Use in config, zero paid gateway calls.

## When to Use Browser vs Crawl4AI

| Scenario | Tool | Reason |
|----------|------|--------|
| You need full article/document text | `web_extract` (→ Crawl4AI) | Full Markdown, no truncation |
| Page is JS-heavy / interactive SPA | `browser_navigate` + `snapshot` | Crawl4AI uses Playwright too but browser tools give raw DOM |
| Page fails or times out | `browser_navigate` as fallback | Different rendering pipeline |
| Need search results | `web_search` (→ DDGS) | Search-only |

## Pitfalls

### Named Profiles Have Their OWN Plugin Home (silent paid fallback!)

**The most expensive pitfall in this skill.** Under a named profile (`hermes --profile app ...`), `HERMES_HOME` is NOT the shared `AppData\Local\hermes\` — it is `AppData\Local\hermes\profiles\<profile>\`. Verified on a real machine:

```
HERMES_HOME  = C:\Users\Unicorn\AppData\Local\hermes\profiles\app
user plugins = ...\profiles\app\plugins    exists = False
```

A crawl4ai plugin sitting in the shared `AppData\Local\hermes\plugins\web\crawl4ai\` (or legacy `~/.hermes/plugins/`) is **invisible** to that profile. Profiles do NOT inherit user plugins from the shared home. This bites when the free stack was configured *before* the profile existed.

Everything then fails silently:
- `plugins.enabled: [web/crawl4ai, web/ddgs]` in the profile config is only an **allow-list** — it happily permits a plugin that isn't physically there. No warning.
- `web.extract_backend: crawl4ai` resolves to nothing. In `tools/web_tools.py` (~line 876) `provider is None` is read as "typo / uninstalled plugin" and falls through to `get_active_extract_provider()` → **firecrawl** → paid call.
- `ddgs` keeps working and masks the whole problem, because `ddgs` is **bundled** (`hermes-agent/plugins/web/ddgs`) and every profile sees bundled plugins. Search stays free while extract silently goes paid.

Diagnose per profile, before trusting any "free" setup:
```bash
python -c "from hermes_cli.plugins import get_hermes_home; p=get_hermes_home()/'plugins'; print(p, p.exists())"
ls "$(python -c "from hermes_cli.plugins import get_hermes_home; print(get_hermes_home())")/plugins/web/"
```

Fix — copy the plugin into **each** profile's own plugin home, then restart the session:
```bash
PROF_HOME="/c/Users/<user>/AppData/Local/hermes/profiles/<profile>"
mkdir -p "$PROF_HOME/plugins/web"
cp -r /c/Users/<user>/AppData/Local/hermes/plugins/web/crawl4ai "$PROF_HOME/plugins/web/"
```

Audit whether paid calls already happened — the log names the culprit:
```bash
grep -n -i firecrawl ~/AppData/Local/hermes/profiles/<profile>/logs/agent.log | grep -v registered
```
`Firecrawl scraping: <url>` = a real billed call. `Plugin 'web-firecrawl' registered` = harmless discovery noise. The bracketed session id (e.g. `[20260806_171733_9c136e]`) identifies who did it: grep that id for `conversation turn:` and read `platform=cli` (a kanban swarm worker) vs `platform=desktop` (the interactive agent), and for `work kanban task t_xxxx` to pin the exact card.

### Find the Correct Hermes Home (Version Detection)
Hermes v0.19.0+ changed `get_hermes_home()` from `~/.hermes/` to `AppData\Local\hermes\` on Windows. **Never assume the path** — detect it:

```bash
python -c "from hermes_cli.plugins import get_hermes_home; print(get_hermes_home() / 'plugins')"
```

This returns the correct user-plugins directory regardless of version. Use this to decide where to create plugin directories and edit config.yaml.

### `hermes plugins enable` Fails with PermissionError (v0.19.0+)
When Hermes desktop is running, `config.yaml` is locked and `hermes plugins enable web/crawl4ai` raises `PermissionError: [WinError 5]`. **Do not retry the CLI command** — edit the YAML directly instead:
```python
import yaml
from pathlib import Path
conf = Path('C:/Users/<user>/AppData/Local/hermes/config.yaml')
c = yaml.safe_load(conf.read_text(encoding='utf-8'))
c.setdefault('plugins', {})['enabled'] = ['web/crawl4ai', 'web/ddgs']
conf.write_text(yaml.dump(c, default_flow_style=False, allow_unicode=True), encoding='utf-8')
```

### MCP Server Fails on Windows
The MCP-based integration (`mcp` package + `crawl4ai_mcp_server.py`) fails on Windows because `mcp` depends on `pywin32`, which has venv-path conflicts when Hermes's built-in Python has a different `pywin32` version. **Do not attempt MCP on Windows** — use the plugin approach instead. It directly registers as a `WebSearchProvider` via Hermes's plugin system.

### Plugin Activation in Hermes v0.19.0+ — Two-Step Process

Hermes v0.19.0 uses an opt-in plugin system: `plugins.enabled` in config.yaml. The plugin must be:

1. **Installed** in the correct directory (`AppData\Local\hermes\plugins\web\crawl4ai\`)
2. **Enabled** via config.yaml's `plugins.enabled` list

**Verification that the plugin will load on next session:**

```bash
# Check the plugin is physically present:
ls -la /c/Users/<user>/AppData/Local/hermes/plugins/web/crawl4ai/
# Should show: __init__.py  plugin.yaml  provider.py

# Check it's in the enabled list:
python -c "
import yaml
from pathlib import Path
conf = yaml.safe_load(Path('C:/Users/<user>/AppData/Local/hermes/config.yaml').read_text())
print('enabled plugins:', conf.get('plugins', {}).get('enabled', []))
"
```

**To verify active registration in the current process (does NOT persist):**

```python
import sys; sys.path.insert(0, '<hermes-agent-path>')
from hermes_cli.plugins import discover_plugins, get_plugin_manager, PluginContext
discover_plugins()
pm = get_plugin_manager()
plugin = pm._plugins.get('web/crawl4ai')
if plugin and plugin.module and hasattr(plugin.module, 'register'):
    ctx = PluginContext(plugin.manifest, pm)
    plugin.module.register(ctx)
    print("✅ crawl4ai registered")
from agent.web_search_registry import get_provider, get_active_extract_provider
p = get_provider('crawl4ai')
assert p is not None and p.is_available(), "❌ crawl4ai not available"
print(f"Active extract provider: {get_active_extract_provider().name}")
```

### Root Cause: The Firecrawl Fallback

When Hermes calls `web_extract`, it goes through `_get_backend()` in `web_tools.py`:

```
1. Читает web.extract_backend из config → "crawl4ai"
2. "crawl4ai" NOT in _LEGACY_WEB_BACKENDS → не предустановленный бэкенд
3. Проверяет _registered_web_provider("crawl4ai") → None (если плагин не загрузился)
4. None → падает в fallback: ("firecrawl", _is_tool_gateway_ready())
5. _is_tool_gateway_ready() → True (есть Nous OAuth)
6. → Возвращает firecrawl → СПИСАНИЕ!
```

**Условие для корректной маршрутизации:**  
`_registered_web_provider("crawl4ai")` должно вернуть объект провайдера, а не None. Это происходит ТОЛЬКО если плагин загрузился И вызвал `ctx.register_web_search_provider(Crawl4AIWebProvider())`.

**Проверка:**
```python
from agent.web_search_registry import get_active_extract_provider
print(get_active_extract_provider().name)  # Должно быть "crawl4ai", не "firecrawl"
```

### Crawl4AI Is Extract-Only
`crawl4ai` `supports_search()` returns `False`. Always keep `web.search_backend: ddgs` for search — `web.backend` can be left on `ddgs` too; only `web.extract_backend` must be `crawl4ai`.

### No Free Backend Does Both Search + Extract
If you want a single backend, only paid options exist (firecrawl, tavily, exa, parallel). With the dual-backend setup (`search: ddgs` + `extract: crawl4ai`) both capabilities work for $0.
### Config Durability — Verify After Every Change

After running `hermes config set web.<key> ...` or `browser.<key> ...`, always read back the active config file and confirm the section/key is present. Hermes can silently drop the entire `web:` or `browser:` block, and in that state it falls back to bundled defaults, which may include **paid** Firecrawl/Browser-Use routes. Do not trust `hermes config set` success messages alone.

Concrete check:
```bash
# Find the active config path (version-safe)
CONF=$(hermes config path 2>/dev/null)
if [ -z "$CONF" ]; then
  # Fallback: detect version
  HERMES_HOME=$(python -c "from hermes_cli.plugins import get_hermes_home; print(get_hermes_home())" 2>/dev/null)
  if [ -n "$HERMES_HOME" ]; then
    CONF="$HERMES_HOME/config.yaml"
  else
    CONF="$HOME/.hermes/config.yaml"
  fi
fi
echo "Config: $CONF"
# Verify web/browser sections exist and contain expected keys
grep -A5 '^web:' "$CONF"
grep -A5 '^browser:' "$CONF"
grep -E "search_backend|extract_backend|use_gateway|cloud_provider" "$CONF"
# Detect paid remnants
grep -iE "(Firecrawl|Browserbase|Browser Use|use_gateway: true|backend: firecrawl|cloud_provider: browser-use)" "$CONF" || true
```

If any paid-remnant regex matches, or the section is missing, re-apply immediately and re-check.

### Transparency on Config Changes (Critical)
Whenever you switch `web.backend` or `web.extract_backend` to a backend that loses a capability, explicitly tell the user: what still works, what broke, what replaces it, and how to get the old capability back for free.

### DDGS Dependencies
`ddgs` pulls transitive deps (httpx, primp, lxml, h2, hpack, brotli, idna, socksio, fake_useragent). After pip install, always verify with the *Hermes venv's Python*, not system Python.

## References

- `references/ddgs-venv-install-windows.md` — DDGS install walkthrough for Windows
- `references/crawl4ai-provider-py.md` — Full `provider.py` template for the Crawl4AI Hermes plugin
- `references/crawl4ai-venv-workaround-windows.md` — When pip is missing in Hermes venv, use uv temp venv + copy
- `references/hermes-v019-plugin-migration.md` — Plugin system changes in Hermes v0.19.0 (home path, enable mechanism, config location, PermissionError workaround)
- `references/free-extraction-crawl4ai.md` — Additional Crawl4AI setup notes
- `scripts/crawl4ai_extract.py` — Standalone Crawl4AI extraction script (for external use or testing)
- `scripts/verify_free_web_stack.sh` — Run this to prove the free stack is live for the CURRENT profile: resolves `get_hermes_home()`, checks the crawl4ai plugin is physically in that profile, prints the ACTIVE extract provider, and counts past billed `Firecrawl scraping:` calls in the profile log.
