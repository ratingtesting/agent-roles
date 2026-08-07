# Firecrawl Fallback Root Cause Analysis

## Problem
User reported continued Firecrawl charges ($0.000483 per `web_extract` call) even after setting `web.extract_backend: crawl4ai` in config.yaml. Charges persisted across new chats and model switches.

## Root Cause (Found in Source Code)

File: `tools/web_tools.py`, function `_get_backend()` (line 230):

```python
configured = (_load_web_config().get("backend") or "").lower().strip()
if configured in _LEGACY_WEB_BACKENDS or _registered_web_provider(configured) is not None:
    return configured
# Falls through to fallback candidates...
backend_candidates = (
    ...
    ("firecrawl", _is_tool_gateway_ready()),  # ← THIS FIRES
    ...
)
```

### Why Crawl4AI Virtualenv Broke the Chain

1. `crawl4ai` is NOT in `_LEGACY_WEB_BACKENDS` (which only includes: parallel, firecrawl, tavily, exa, searxng, brave-free, ddgs, xai)
2. So Hermes checks `_registered_web_provider("crawl4ai")` — which calls the plugin's `is_available()`
3. `is_available()` does `import crawl4ai` — but crawl4ai was installed in `/tmp/c4aivenv/`, NOT in the Hermes venv
4. `import crawl4ai` fails → `is_available()` returns False
5. Hermes falls through to legacy candidates
6. `_is_tool_gateway_ready()` returns True (Nous OAuth token present)
7. Returns `"firecrawl"` → paid gateway → $$$ charges

### Resolution Path

Two fixes needed (BOTH required):

**Fix 1: Install crawl4ai into Hermes venv (for import)**
```bash
# Copy crawl4ai package from isolated venv to Hermes venv site-packages
cd /c/Users/Unicorn/AppData/Local/Temp/c4aivenv
tar cf - .venv/Lib/site-packages/crawl4ai .venv/Lib/site-packages/crawl4ai-* \
  | (cd /c/Users/Unicorn/AppData/Local/hermes/hermes-agent && tar xf -)
```
This makes `import crawl4ai` succeed in Hermes venv, so `is_available()` returns True.

### Fix 2: Register the plugin properly + FORCE-REGISTER in session

The plugin must have `__init__.py` with a `register(ctx)` function that calls `ctx.register_web_search_provider()`. Hermes' plugin loader (`hermes_cli/plugins.py:_load_plugin`) imports the module and calls `register()` **only when the plugin manager's `discover_and_load()` runs**.

**⚠️ Critical gap discovered:** Even with all files correct and `hermes plugins enable` done, `register()` is NOT called on an already-running Hermes session. The plugin manager caches loaded plugins; `discover_plugins()` alone does NOT re-invoke `register()` for already-enabled user plugins. The plugin appears as "enabled" in `hermes plugins list`, but `web_search_registry.list_providers()` returns 0 providers for user plugins — the `register()` call simply never fires.

**The fix:** Force-call `register()` after `discover_plugins()`:
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
```

After this, `get_active_extract_provider()` returns `crawl4ai` instead of falling back to firecrawl.

**Root cause in Hermes code:** The `_get_backend()` function (tools/web_tools.py) does:
1. Check config → `crawl4ai`
2. `crawl4ai not in _LEGACY_WEB_BACKENDS` → call `_registered_web_provider("crawl4ai")`
3. If registry empty (plugin never registered) → return None
4. Fallback → `("firecrawl", _is_tool_gateway_ready())` → charges

### Verification

After fix, verify the provider is registered:
```python
import sys
sys.path.insert(0, 'C:/Users/Unicorn/AppData/Local/hermes/hermes-agent')
from hermes_cli.plugins import get_plugin_manager, discover_plugins
discover_plugins()
from agent.web_search_registry import list_providers
providers = list_providers()
for p in providers:
    if p.name == 'crawl4ai':
        print(f"crawl4ai: available={p.is_available()}")
```
Should show: `crawl4ai: available=True`

### Key Files in Backend Resolution

- `tools/web_tools.py` — `_get_backend()`, `_get_extract_backend()`, `_get_capability_backend()`
- `agent/web_search_registry.py` — `register_provider()`, `get_active_extract_provider()`, `_resolve()`
- `hermes_cli/plugins.py` — `_load_plugin()`, `discover_plugins()`
- `plugins/web/crawl4ai/provider.py` — `Crawl4AIWebProvider.is_available()` (the gate)

### Config That Must Be Set

```yaml
web:
  backend: crawl4ai        # Main switch — controls _get_backend()
  search_backend: ddgs     # Search override
  extract_backend: crawl4ai # Extract override — controls _get_extract_backend()
  use_gateway: false       # Disables Nous managed gateway fallback
browser:
  cloud_provider: local    # Local Chromium, not Browser-Use cloud
  use_gateway: false
```

ALL four web keys must be set. Missing `web.backend` causes `_get_backend()` to fall through to legacy candidates even if `extract_backend` is configured, because `_get_capability_backend()` falls back to `_get_backend()` when the specific backend is unavailable.
