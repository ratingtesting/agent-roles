# Dashboard Architecture Investigation — Source Code Deep-Dive

Investigation of the Hermes dashboard web UI for custom provider management.
Key files examined: `hermes_cli/web_server.py`, `hermes_cli/main.py`, `hermes_cli/subcommands/dashboard.py`.

## Question

How are custom providers added through the dashboard web UI? Can more than one be added?

## Answer

Custom providers are **not managed through dedicated dashboard forms**. They are stored in `config.yaml` under the `custom_providers:` key. The canonical management path is the CLI (`hermes model` items 34/35) or direct YAML editing. The dashboard is a general settings surface that reads/writes the same config — if it exposes custom provider forms at all, they are thin wrappers around the same config entries.

---

## Source Code Flow

### Entry Point: `cmd_dashboard()` in `main.py:11957`

```python
def cmd_dashboard(args):
    _headless_backend = getattr(args, "headless_backend", False)
    # ...
    if _headless_backend:
        os.environ["HERMES_SERVE_HEADLESS"] = "1"        # disables SPA
    elif "HERMES_WEB_DIST" not in os.environ and not args.skip_build:
        _build_web_ui(PROJECT_ROOT / "web", fatal=True)    # auto-build
    elif args.skip_build:
        # validate dist exists
        _dist_root = (Path(os.environ["HERMES_WEB_DIST"]) if "HERMES_WEB_DIST" in os.environ
                     else PROJECT_ROOT / "hermes_cli" / "web_dist")
        # ... check index.html exists
```

Key branches:
1. `_headless_backend=True` (from `hermes serve`): sets `HERMES_SERVE_HEADLESS=1`, skips build entirely
2. `dashboard` with no env var and no `--skip-build`: auto-runs `npm run build` from `web/`
3. `dashboard` with `--skip-build`: validates dist exists at `HERMES_WEB_DIST` or default path
4. `dashboard` with `HERMES_WEB_DIST` set (no `--skip-build`): validates the env-var path, expands it

### SPA Mount Decision: `mount_spa()` in `web_server.py:15716`

```python
def mount_spa(application):
    _headless = os.environ.get("HERMES_SERVE_HEADLESS") == "1"
    if _headless or not WEB_DIST.exists():
        _msg = ("Headless backend (hermes serve): web UI disabled — use "
                "`hermes dashboard` for the browser UI."
                if _headless
                else "Frontend not built. Run: cd web && npm run build")
        @application.get("/{full_path:path}")
        async def no_frontend(full_path: str):
            return JSONResponse({"error": _msg}, status_code=404)
        return
    # ... serves SPA from WEB_DIST / "index.html"
```

The `WEB_DIST` path comes from:
```python
WEB_DIST = Path(os.environ["HERMES_WEB_DIST"]) if "HERMES_WEB_DIST" in os.environ \
           else Path(__file__).parent / "web_dist"
```

### Subcommand Parsers: `dashboard.py:17-200`

- `dashboard`: `_add_server_runtime_args(parser)` + `--no-open` flag → `func=cmd_dashboard`
- `serve`: `_add_server_runtime_args(parser)` + defaults `no_open=True, headless_backend=True` → `func=cmd_dashboard`

The `serve` subcommand sets `headless_backend=True` as a default (line 156), which propagates through `cmd_dashboard` to set `HERMES_SERVE_HEADLESS=1`. The `dashboard` subcommand leaves it unset (defaults to `False`).

## Key Files

| File | Role |
|------|------|
| `hermes_cli/subcommands/dashboard.py` | Parser setup — `dashboard` vs `serve` args, defaults |
| `hermes_cli/main.py:11957-12156` | `cmd_dashboard()` — env var setup, build gate, server launch |
| `hermes_cli/web_server.py:15709-15731` | `mount_spa()` — the headless-vs-SPA decision point |
| `web/` (Vite + React SPA) | The browser UI source code |

## Env Var Summary

| Variable | Set By | Effect |
|----------|--------|--------|
| `HERMES_SERVE_HEADLESS=1` | `cmd_dashboard()` when `headless_backend=True` | `mount_spa()` serves 404 error instead of SPA |
| `HERMES_WEB_DIST=<path>` | User (or `cmd_dashboard()` on `--skip-build`) | Overrides default web dist location |
| `HERMES_SERVE_HEADLESS` absence | Normal `dashboard` invocation | SPA is served normally (if dist exists) |

## Pitfalls Found During Investigation

1. **Stale `HERMES_SERVE_HEADLESS` in env**: If a prior `hermes serve` or crashed dashboard left this set in the Python process env, the SPA never serves. Restart completely.
2. **Port held by zombie process**: `hermes dashboard --stop` only finds `hermes dashboard` / `hermes serve` cmdlines — manual `netstat + taskkill` may be needed.
3. **Windows path issues**: MSYS bash translates `/c/Users/...` to `\c\Users\...` when passed in env vars. Use native `C:\Users\...` or `$({command})` expansion carefully.
4. **Desktop app dist conflict**: The Electron desktop app's bundled dist (at `apps/desktop/release/...`) is NOT a replacement for the dashboard SPA — it's the desktop app's own UI. The dashboard SPA lives at `hermes_cli/web_dist/` after building.
