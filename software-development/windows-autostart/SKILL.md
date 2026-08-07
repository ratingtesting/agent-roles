---
name: windows-autostart
description: Create a Windows "run at login" autostart entry for a local app or script. Covers startup folder `.lnk` creation, alternative registries, and VBS/PowerShell quoting, with Python server pitfalls.
---

## Windows Autostart

Create a `.lnk` in the user's `Startup` folder or use the Registry `Run` key so an app/script starts at Windows login.

## When to use

- A service, proxy, daemon, or watcher that must start with the OS
- A GUI app that should re-launch after a reboot
- A background Python server (note: see Python-specific pitfalls below)

## Preferred method: Startup folder `.lnk` via VBS

```vbscript
Set WshShell = CreateObject("WScript.Shell")
Set Shortcut = WshShell.CreateShortcut("C:\Users\USERNAME\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\APPNAME.lnk")
Shortcut.TargetPath = "C:\Path\To\app.exe"
Shortcut.Arguments = "--flag value"
Shortcut.Description = "App description"
Shortcut.WindowStyle = 7              ' 7 = minimized, 1 = normal, 3 = maximized
Shortcut.WorkingDirectory = "C:\Path\To"
Shortcut.Save
```

Run with: `cscript //nologo path\to\make-link.vbs`

## Alternative: Registry `Run` key

For entries that don't need a visible `.lnk`:

```
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v APPNAME /t REG_SZ /d "C:\Path\To\app.exe --args"
```

## Python-specific pitfalls

### `pythonw.exe` breaks long-running servers

`pythonw.exe` (no console window) causes uvicorn/FastAPI-based services to exit silently — uvicorn needs stdout/stderr and fails without a console. **Do not use `pythonw.exe` for Python server processes.** Use `python.exe` with `WindowStyle = 7` (minimized) in the `.lnk` instead. The window stays hidden in the taskbar but the process lives.

### `sys.path` contamination from Hermes venv

When a Python interpreter from a user-local installation (e.g. `C:\Python314\python.exe`) runs, `sys.path` may pick up Hermes venv site-packages (`...\hermes-agent\venv\Lib\site-packages`). If Hermes has stale or incompatible packages (e.g. `pydantic_core` without the native extension), imports fail. Fix: sanitize `sys.path` early in the entry script:

```python
import sys, os
sys.path = [p for p in sys.path if 'hermes' not in p.lower() and 'venv' not in p.lower()]
sys.path.insert(0, r'C:\Python314\Lib\site-packages')
os.environ['PYTHONPATH'] = r'C:\Python314\Lib\site-packages'
```

#### `start "" /MIN` NOT `start /B` for long-lived Python servers

`start /B "" python.exe` shares the parent console. When the parent cmd.exe (wrapping the `.lnk` target) exits, the console may be destroyed, taking the Python server with it. Use `start "" /MIN "python.exe" path\to\script.py` (WITHOUT `/B`) to create a new minimized console window.

### Toggle services via config.yaml (user preference)

User prefers all Hermes configuration through `config.yaml` only — no GUI toggles, no settings panels. For a proxy like Headroom that sits between Hermes and providers:

```yaml
# In config.yaml
headroom_proxy:
  enabled: true
  port: 8787
```

A small startup script reads this flag and rewrites `base_url` of all `custom_providers` to point at the proxy (`http://127.0.0.1:8787/v1`) when enabled, or restores original URLs when disabled. No GUI, pure config-driven toggle.

### `.bat` wrapper breaks multi-line Python `-c`

Writing multi-line Python code inside a `.bat` file via `-c "..."` is fragile — batch quoting rules mangle quotes, newlines, and special characters. **Prefer**: `.lnk` → `python.exe path\to\script.py` directly, with the Python code in a `.py` file. Skip the `.bat` wrapper entirely when launching Python scripts.

### Env vars must be set before import

If the script reads an env var at module level (e.g. `HEADROOM_OUTPUT_SHAPER`), setting it after `import` has no effect. Set `os.environ['VAR'] = 'value'` as the **first** Python statement in the bootstrap script.

## Troubleshooting

- If the app doesn't start after login, check Event Viewer under Windows Logs → Application for .NET errors, or run the target path manually from a command prompt to verify it works independently.
- `.lnk` files that launch Python scripts may fail silently if the Python environment isn't fully initialized at login time. Use a short `timeout /t 5` in a wrapper `.bat` to introduce a startup delay.
- Windows Defender or other AV may quarantine unknown `.exe` or `.bat` files in the Startup folder. Add an exclusion if needed.

## Proven Headroom launcher pattern on Windows

Tested on Windows 11, Python 3.14 user site-packages, headroom 0.31.0.

Use a `.cmd` that only sets `PYTHONPATH`, then calls a `.py` launcher. Do **not** use `python -c "..."` inside `.cmd`: semicolons and multiline quoting break under `cmd.exe` and can cause `import` to be interpreted as a command. `python.exe` path must be Windows-style absolute; bash `/c/...` paths produce bad sys.path entries.

### `headroom_start_8787.cmd`

```cmd
@echo off
set PYTHONPATH=C:\Users\Unicorn\AppData\Roaming\Python\Python314\site-packages
C:\Python314\python.exe C:\Users\Unicorn\AppData\Local\hermes\headroom_8787_launcher.py
```

### `headroom_8787_launcher.py`

```python
import os, sys

os.environ["HEADROOM_OUTPUT_SHAPER"] = "1"
os.environ["HEADROOM_VERBOSITY_AUTOTUNE"] = "1"
os.environ["OPENAI_TARGET_API_URL"] = "http://localhost:20128/v1"
os.environ["ANTHROPIC_TARGET_API_URL"] = "http://localhost:20128/v1"

# Critical for custom OpenAI-compatible providers like 9router:
# without these, headroom uses litellm credentials/default provider routing.
os.environ["HEADROOM_BACKEND"] = "anyllm-openai"
os.environ["HEADROOM_ANYLLM_PROVIDER"] = "openai"
os.environ["OPENAI_API_KEY"] = os.environ.get("API_9ROUTER_KEY", "")

os.environ["PYTHONPATH"] = r"C:\Users\Unicorn\AppData\Roaming\Python\Python314\site-packages"

from headroom.cli import main
sys.argv = ["headroom", "proxy", "--port", "8787"]
main()
```

### Auth/routing rules

- `HEADROOM_BACKEND=anyllm-openai` + `HEADROOM_ANYLLM_PROVIDER=openai` → headroom uses `any-llm-sdk` OpenAI-compatible transport and sends requests to `OPENAI_TARGET_API_URL` / `ANTHROPIC_TARGET_API_URL` without litellm provider credential checks.
- Model name is relayed as-is. If upstream cannot resolve a model, the error comes from upstream, not headroom.
- `HEADROOM_OUTPUT_SHAPER=1` and `HEADROOM_VERBOSITY_AUTOTUNE=1` must be set **before** importing `headroom.cli`; setting them after import is ignored.

## Support files

- `references/headroom-proxy.md` — full walkthrough of setting up Headroom AI Proxy as a startup item, including bootstrap script, VBS lnk creator, verification commands, and all the pitfalls above documented with real errors.
