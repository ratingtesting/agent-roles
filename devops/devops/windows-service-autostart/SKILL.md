---
name: windows-service-autostart
version: 1.1.0
description: "Manage Windows autostart shortcuts for local AI services (9router, freellmapi, flashrank, lightweight-embeddings, etc.) via Startup folder. Covers creation, verification, cleanup of deprecated entries, and documentation sync."
author: user
kind: backend
---

# Windows Service Autostart Management

## Purpose
Manage autostart for local AI services on Windows (no Docker, no systemd). All services run as user processes launched via shortcuts in `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\`.

## Services in Scope
| Service | Port | Launch Command | Shortcut Name |
|---------|------|----------------|---------------|
| 9router | 20128 | `9router -p 20128 --no-browser --skip-update` | `9router.lnk` |
| freellmapi | 31415 | Desktop app (registry Run key) | `freellmapi.lnk` |
| flashrank | 8003 | `"C:\Users\Unicorn\AppData\Local\hermes\hermes-agent\venv\Scripts\pythonw.exe" "C:\Users\Unicorn\flashrank-server\go.py"` (Registry Run) | `FlashRank.lnk` / `flashrank-api.lnk` |
| lightweight-embeddings | 7860 | `run_server.bat` (uvicorn) | `lightweight-embeddings.lnk` |
| anthropic-ua-proxy | 8402 | `"C:\Users\Unicorn\AppData\Local\hermes\hermes-agent\venv\Scripts\pythonw.exe" "C:\Users\Unicorn\anthropic-ua-proxy\proxy.py"` (Registry Run `AnthropicUAProxy`) — подмена User-Agent на claude-cli для agentrouter.org, потребитель gbrain (см. скилл gbrain-brains) | — |
| headroom (deprecated) | 8787/8788 | Removed — 9router runs direct | `Headroom-8787.lnk`, `Headroom-8788.lnk` |

## Core Operations

### 1. Create/Update Autostart Shortcut (VBScript — preferred)
```vbscript
Set WshShell = CreateObject("WScript.Shell")
startup = WshShell.SpecialFolders("Startup")
Set lnk = WshShell.CreateShortcut(startup & "\9router.lnk")
lnk.TargetPath = "C:\Users\Unicorn\AppData\Roaming\npm\9router.cmd"
lnk.Arguments = "-p 20128 --no-browser --skip-update"
lnk.WorkingDirectory = "C:\Users\Unicorn"
lnk.WindowStyle = 7  ' minimized
lnk.Description = "9router direct on 20128 (no headroom proxy)"
lnk.Save
```
Run via: `cscript create_9router_autostart.vbs`

### 2. Create/Update via PowerShell (alternative)
```powershell
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\9router.lnk")
$Shortcut.TargetPath = "C:\Users\Unicorn\AppData\Roaming\npm\9router.cmd"
$Shortcut.Arguments = "-p 20128 --no-browser --skip-update"
$Shortcut.WorkingDirectory = "C:\Users\Unicorn"
$Shortcut.WindowStyle = 7
$Shortcut.Save()
```

### 3. Autostart via .bat (no COM — for blocked environments)
When COM automation (WScript.Shell) is blocked, create a `.bat` file directly in the Startup folder:

```bat
@echo off
start /b "" 9router -p 20128 --no-browser --skip-update
```

Save as `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\9router.bat`.

Pattern: `start /b "" <command> <args>` runs the child in the background. The bat console flashes briefly, then `start /b` hides the child.

**When to use:**
- PowerShell COM automation is restricted by policy
- Quick prototyping/iteration
- Agent is in bash (git-bash) and can `write_file` or `echo` the `.bat` directly

### 4. Autostart via Registry Run (for daemon services)
For services that should run completely silently (no console flash), use the Registry Run key:

```bash
REG ADD "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v FlashRank /t REG_SZ /d "\"C:\Users\Unicorn\AppData\Local\hermes\hermes-agent\venv\Scripts\pythonw.exe\" \"C:\Users\Unicorn\flashrank-server\go.py\"" /f
```

**Method comparison:**
| Method | Console flash | Visibility | Best for |
|--------|---------------|------------|----------|
| `.lnk` (COM) | None (minimized) | Startup folder | Normal setup |
| `.bat` in Startup | Brief flash | Startup folder | Blocked COM, quick setup |
| Registry Run | None | Hidden (regedit) | Daemon services (flashrank, freellmapi) |

### 5. Verify Shortcut
```powershell
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\9router.lnk")
Write-Host "Target: $($Shortcut.TargetPath)"
Write-Host "Args: $($Shortcut.Arguments)"
Write-Host "WorkingDir: $($Shortcut.WorkingDirectory)"
```

### 6. Remove Deprecated Shortcuts
```bash
rm "$APPDATA/Microsoft/Windows/Start Menu/Programs/Startup/Headroom-8787.lnk"
rm "$APPDATA/Microsoft/Windows/Start Menu/Programs/Startup/Headroom-8788.lnk"
```

## Launcher Scripts (`.cmd` files in `%LOCALAPPDATA%\hermes\`)
Each service gets a `.cmd` launcher that sets env vars **before** the process starts (more reliable than Python launchers).
```
@echo off
REM 9router автозагрузка — порт 20128
cd /d C:\Users\Unicorn\AppData\Local\hermes
9router -p 20128 --no-browser --skip-update
```
Save as `headroom_start_8787.cmd` (legacy name kept for VBScript compatibility) or `9router_start.cmd`.

## Verification Checklist
After creating/updating shortcuts:
1. `ls -la "$APPDATA/Microsoft/Windows/Start Menu/Programs/Startup/"` — confirm `.lnk` / `.bat` files exist
2. For `.lnk`: PowerShell verify TargetPath/Arguments/WorkingDirectory
3. For Registry Run: `reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v <Name>` — confirm value
4. Manual test: run the launcher → `curl http://localhost:<port>/v1/models` (or `/healthz`)
5. Update `SETUP_GUIDE.md` autostart section for that service

## Pitfalls
- **Don't use `.py` launchers** — env vars set in Python don't propagate to child processes reliably. Use `.cmd`/`.bat` or direct binary in shortcut.
- **WindowStyle = 7** (minimized) prevents console window flashing on login.
- **WorkingDirectory** matters for relative paths in logs/configs.
- **TargetPath must be the `.cmd` wrapper or direct binary** — `npx 9router` works but adds Node startup overhead.
- **Registry Run keys** (HKCU\Software\Microsoft\Windows\CurrentVersion\Run) are an alternative for services that run hidden (freellmapi, flashrank). Shortcuts in Startup folder are visible and manageable.
- **Registry Run requires absolute paths** — the value must be the full path to the executable. `pythonw.exe` alone won't work because the Registry Run environment doesn't activate any venv. Always specify the full path to the venv's pythonw.exe.
- **Headroom proxy is removed** — don't recreate its shortcuts. 9router binds 20128 directly.
- **`.bat` in Startup:** The `.bat` console window flashes briefly at login. For completely silent startup, use `.lnk` or Registry Run instead.
- **`start /b ""` quirk:** The empty string `""` after `start /b` is required on some Windows versions to prevent the first quoted argument from being misinterpreted as the window title.
- **PowerShell `-Command` parenthesis pitfall:** inline `powershell.exe -Command "..."` breaks if the script contains parentheses inside quoted strings (e.g. a shortcut Description with `(bge-m3)`). PowerShell parses the parens as expression grouping and throws `ParserError: ExpectedExpression`. **Fix:** write the PowerShell to a `.ps1` file via `write_file` and run `powershell.exe -NoProfile -ExecutionPolicy Bypass -File script.ps1`. Confirmed fix during lightweight-embeddings Startup shortcut creation.
- **Clear PYTHONPATH in autostart `.bat`:** if the launched service uses a Python venv created inside the Hermes agent environment, add `set PYTHONPATH=` as the FIRST line of `run_server.bat` (before `cd /d` and the launch command). The Hermes process injects `PYTHONPATH=.../hermes-agent;.../hermes-agent/venv/Lib/site-packages`, which otherwise leaks the agent's packages into the project venv. See skill `windows-venv-isolation`.

## Documentation Sync
Always update `C:\Projects\lazy-unicorn\SETUP_GUIDE.md` → relevant service section → "Автозагрузка" subsection when changing autostart config.

## References
- `references/9router-autostart-vbscript.md` — working VBScript example
- `references/powershell-shortcut-patterns.md` — PowerShell CreateShortcut patterns
- `templates/service-launcher.cmd` — boilerplate `.cmd` launcher