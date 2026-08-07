# Headroom Proxy — Autostart Setup (Windows)

## Target

Run one or two `headroom proxy` instances at Windows login, configured via documented env vars (`OPENAI_TARGET_API_URL` / `ANTHROPIC_TARGET_API_URL`), not CLI flags.

**KEY LESSON: env vars, not CLI flags.** The documented approach uses `OPENAI_TARGET_API_URL` / `ANTHROPIC_TARGET_API_URL`. See https://headroomlabs-ai.github.io/headroom/proxy/#configuration-via-environment. CLI `--openai-api-url` / `--anthropic-api-url` flags exist but are unreliable — env vars are canonical.

## Two-instance deployment (Hermes-specific)

Hermes with two upstream providers needs TWO headroom processes:

| Port | Upstream | Env Vars |
|------|---------|----------|
| 8787 | 9router | `OPENAI_TARGET_API_URL=http://localhost:20128/v1`, `ANTHROPIC_TARGET_API_URL=http://localhost:20128/v1` |
| 8788 | agentrouter | `OPENAI_TARGET_API_URL=https://agentrouter.org/v1`, `ANTHROPIC_TARGET_API_URL=https://agentrouter.org` |

## Deployed files

Files live in `C:\Users\Unicorn\AppData\Local\hermes\`:
- `headroom_8787_launcher.py` / `headroom_8788_launcher.py` — Python bootstrap (sets env vars before import)
- `start_headroom_8787.cmd` / `start_headroom_8788.cmd` — `.cmd` wrappers with `start "" /MIN`
- `create_headroom_links.vbs` — VBS to create `.lnk` in Startup folder

## Deployment files

```
C:\Users\Unicorn\AppData\Local\hermes\
├── headroom_8787_launcher.py      # Python bootstrap (env vars before import)
├── headroom_8788_launcher.py      # Python bootstrap (env vars before import)
├── start_headroom_8787.cmd         # .cmd wrapper (start /MIN, env vars)
├── start_headroom_8788.cmd         # .cmd wrapper (start /MIN, env vars)
├── create_headroom_links.vbs      # Creates .lnk in Startup folder
└── ~/.headroom/                   # Headroom workspace (DB, logs, config)
```

## Pitfalls discovered

### 1. `pythonw.exe` kills uvicorn silently

`pythonw.exe` suppresses the console. Uvicorn reacts by exiting without error when it has no stdout/stderr. **Do not use pythonw.exe for server processes.** Use `python.exe` with `WindowStyle = 7` (minimized, no taskbar entry).

### 2. Hermes venv pollutes `sys.path`

When running a stand-alone Python (like `C:\Python314\python.exe`), `sys.path` may include `...\hermes-agent\venv\Lib\site-packages`. If those have incompatible compiled packages (e.g. `pydantic_core` without native `.pyd`), imports fail:

```
ModuleNotFoundError: No module named 'pydantic_core._pydantic_core'
```

**Fix**: bootstrap script cleans `sys.path` before imports:

```python
import sys, os
clean_paths = [p for p in sys.path if 'hermes' not in p.lower() and 'venv' not in p.lower()]
clean_paths.insert(0, r'C:\Python314\Lib\site-packages')
sys.path = clean_paths
os.environ['PYTHONPATH'] = r'C:\Python314\Lib\site-packages'
# Now safe to import headroom, fastapi, etc.
```

### 3. `.bat` + Python `-c` quoting is fragile

Batch files mangle quotes, newlines, and special chars inside `python -c "..."` strings. **Never use a .bat wrapper for Python server autostart.** Put the code in a `.py` file and have the `.lnk` point directly to `python.exe path\to\script.py`.

### 5. `headroom.exe` needs PYTHONPATH

On machines where Python is not in PATH or multiple Python installations exist, `headroom.exe` fails with:

```
ERROR: FastAPI required. Install: pip install fastapi uvicorn httpx
```

Even though packages are installed in the system Python. Fix: always set `PYTHONPATH` in `.cmd` wrapper before launching:

```
set PYTHONPATH=C:\Python314\Lib\site-packages;C:\Users\Unicorn\AppData\Roaming\Python\Python314\site-packages
```

### 6. `start /B` → process orphaned when console dies

`start /B "" headroom.exe` shares the parent console. When the parent cmd.exe exits (script finishes), the console may be destroyed, killing headroom.exe. **Fix**: use `start "" /MIN "headroom.exe"` (WITHOUT `/B`) to create a new minimized console.

### 7. Startup is slow on Windows (30-60s)

After the banner prints, uvicorn takes 30-60 seconds to bind the port. Normal on Windows 11 — autostart triggers at login; the proxy is ready by the time the user needs it.

### 8. `/v1/models` passthrough — headroom does NOT modify

`GET /v1/models` is proxied verbatim to the upstream. Verified in headroom source (proxy_routes.py, registry.py). Empty response = upstream returned empty, not a headroom issue.

Setting the env var after `headroom.cli` is imported has no effect — the proxy reads it at import time. Set `os.environ['HEADROOM_OUTPUT_SHAPER'] = '1'` as the **first** Python statement in the bootstrap script.

## Bootstrap script (full)

`headroom_8787_launcher.py`:
```python
import os, sys
os.environ['HEADROOM_OUTPUT_SHAPER'] = '1'
os.environ['OPENAI_TARGET_API_URL'] = 'http://localhost:20128/v1'
os.environ['ANTHROPIC_TARGET_API_URL'] = 'http://localhost:20128/v1'

# Strip Hermes venv paths
clean_paths = [p for p in sys.path if 'hermes' not in p.lower() and 'venv' not in p.lower()]
clean_paths.insert(0, r'C:\Python314\Lib\site-packages')
sys.path = clean_paths
os.environ['PYTHONPATH'] = r'C:\Python314\Lib\site-packages'

from headroom.cli import main
import sys as _sys
_sys.argv = ['headroom', 'proxy', '--port', '8787']
main()
```

## `.lnk` creation (VBS)

```vbscript
Set WshShell = CreateObject("WScript.Shell")
startup = WshShell.SpecialFolders("Startup")
python = "C:\Python314\python.exe"

' 8787 → 9router
Set Shortcut = WshShell.CreateShortcut(startup & "\Headroom-8787.lnk")
Shortcut.TargetPath = python
Shortcut.Arguments = """C:\Users\Unicorn\AppData\Local\hermes\headroom_8787_launcher.py"""
Shortcut.Description = "Headroom proxy 8787 → 9router"
Shortcut.WindowStyle = 7
Shortcut.WorkingDirectory = "C:\Users\Unicorn\AppData\Local\hermes"
Shortcut.Save

' 8788 → agentrouter
Set Shortcut = WshShell.CreateShortcut(startup & "\Headroom-8788.lnk")
Shortcut.TargetPath = python
Shortcut.Arguments = """C:\Users\Unicorn\AppData\Local\hermes\headroom_8788_launcher.py"""
Shortcut.Description = "Headroom proxy 8788 → agentrouter"
Shortcut.WindowStyle = 7
Shortcut.WorkingDirectory = "C:\Users\Unicorn\AppData\Local\hermes"
Shortcut.Save
```

Run with: `cscript //nologo create_headroom_links.vbs`

## Verification

```bash
# Health check — verify upstream URLs are set
curl -s http://127.0.0.1:8787/health | python -c "import sys,json; d=json.load(sys.stdin); print(d['config']['anthropic_api_url'], d['config']['openai_api_url'])"

# Model list — must match upstream (headroom does NOT modify /v1/models)
curl -s -H "Authorization: Bearer $KEY" http://127.0.0.1:8787/v1/models | python -c "import sys,json; d=json.load(sys.stdin); [print(m['id']) for m in d['data'][:5]]"

# Check .lnk files exist
ls ~/AppData/Roaming/Microsoft/Windows/Start\ Menu/Programs/Startup/ | grep -i headroom
```

## Deploying

1. Create/update Python bootstrap scripts in `C:\Users\Unicorn\AppData\Local\hermes\`
2. Run `cscript //nologo C:\Users\Unicorn\AppData\Local\hermes\create_headroom_links.vbs` to create `.lnk` files
3. Verify `.lnk` files exist in Startup folder
4. To test: double-click the `.lnk` or run the Python script directly
5. After a 30-60s wait, verify with `curl http://127.0.0.1:8787/health`

### Recreating after updates

```bash
rm -f ~/AppData/Roaming/Microsoft/Windows/Start\ Menu/Programs/Startup/Headroom-*.lnk
cscript //nologo C:\Users\Unicorn\AppData\Local\hermes\create_headroom_links.vbs
```