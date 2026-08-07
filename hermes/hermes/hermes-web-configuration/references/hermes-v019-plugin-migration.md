# Hermes v0.19.0 Plugin System Migration

## Key Changes from Older Versions

| Aspect | Old (<0.19.0) | New (v0.19.0+) |
|--------|---------------|-----------------|
| Plugin home | `~/.hermes/plugins/` | `AppData\Local\hermes\plugins/` (Windows) |
| Enable method | `hermes plugins enable web-crawl4ai` | `plugins.enabled` in config.yaml |
| Plugin key | Manifest `name:` (e.g. `web-crawl4ai`) | Directory-based path (e.g. `web/crawl4ai`) |
| Default state | All plugins load | Opt-in: nothing loads until listed in `plugins.enabled` |

## Discovery Flow

1. Hermes calls `get_hermes_home() / "plugins"` — returns `AppData\\Local\\hermes\\plugins\\` on Windows
2. Scans that directory recursively via `_scan_directory_level()` (depth cap = 2) for `plugin.yaml` files:
   - **Flat layout:** `plugins/<name>/plugin.yaml` (e.g. `plugins/disk-cleanup/`)
   - **Category layout:** `plugins/<category>/<name>/plugin.yaml` (e.g. `plugins/web/crawl4ai/`)
   - Depth > 2 is ignored
3. Filters by `plugins.enabled` allowlist from config.yaml — **`None` = nothing enabled**
4. Loads and registers each enabled plugin's `register()` function

## Opt-In Default

In v0.19.0, `_get_enabled_plugins()` returns `None` when `plugins.enabled` key is absent → nothing loads. This is a breaking change from older versions where all discovered plugins loaded automatically. You MUST explicitly add `plugins.enabled` to config.yaml:

```yaml
plugins:
  enabled:
    - web/crawl4ai
    - web/ddgs
```

## Config Location

- **v0.19.0+:** `C:\Users\<user>\AppData\Local\hermes\config.yaml`
- **Old:** `~/.hermes/config.yaml`

## Registration Verification

```python
from agent.web_search_registry import get_active_extract_provider
p = get_active_extract_provider()
print(p.name if p else "NONE")  # Should be "crawl4ai", not "firecrawl"
```

## PermissionError Workaround

`hermes plugins enable` fails with `WinError 5` when Hermes desktop holds the config lock. Fix: edit config.yaml directly:

```python
import yaml
from pathlib import Path
conf = Path('C:/Users/<user>/AppData/Local/hermes/config.yaml')
c = yaml.safe_load(conf.read_text(encoding='utf-8'))
c.setdefault('plugins', {})['enabled'] = ['web/crawl4ai', 'web/ddgs']
conf.write_text(yaml.dump(c, default_flow_style=False, allow_unicode=True), encoding='utf-8')
```
