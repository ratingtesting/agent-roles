---
name: windows-software-install
description: Windows software install via PowerShell+curl resume.
---

# Windows Software Install via PowerShell + curl Resume

## Trigger

Installing large SDKs/tools on Windows 11 from ZIP archives hosted on Google Storage or similar — especially downloads that may be interrupted (network drops, session timeouts, user closes terminal). The user explicitly requested a **script**, not an active download.

## Verified Method

Key insight: `Invoke-WebRequest -Resume` does NOT work reliably with Google Storage (infinite `Network error` retries). Use `curl.exe -C -` via `Start-Process` in PowerShell.

### Pattern

```powershell
$Url = "https://storage.googleapis.com/..."
$Zip = "$env:TEMP\tool.zip"
$Dest = "C:\dev\tools\tool-name"
$BinDir = "$Dest\bin"

New-Item -ItemType Directory -Force -Path $Dest | Out-Null

# Download with resume
for ($i = 1; $i -le 50; $i++) {
    $curlArgs = @("-L", "-C", "-", "--retry", "5", "--retry-delay", "3",
                  "--connect-timeout", "30", "-o", $Zip, $Url)
    $p = Start-Process -FilePath "curl.exe" -ArgumentList $curlArgs -NoNewWindow -Wait -PassThru
    if ($p.ExitCode -eq 0) { break }
    Start-Sleep -Seconds 3
}

# Integrity check
$size = (Get-Item $Zip).Length
if ($size -lt 100MB) { throw "Archive too small — corrupt" }

# Extract
Expand-Archive -Path $Zip -DestinationPath $Dest -Force

# Path
$userPath = [Environment]::GetEnvironmentVariable("Path","User")
if ($userPath -notlike "*$BinDir*") {
    [Environment]::SetEnvironmentVariable("Path","$userPath;$BinDir","User")
}

# Verify
& "C:\dev\tools\flutter\bin\flutter.bat" doctor -v
```

## When npm Is Too Slow: Prefer GitHub Release Assets

For complex packages with hundreds of npm dependencies (e.g. `@openhands/agent-canvas` with React + Monaco Editor + 600+ subdeps), `npm install -g` can timeout or hang on slow or lossy connections. **Check GitHub Releases first** — many projects publish standalone installers (`.exe`, `.msi`) or platform-specific archives.

**Pattern:**
1. Visit `https://github.com/<owner>/<repo>/releases/latest`
2. Look for platform-specific assets (`.exe`, `.msi`, `.dmg`, `-win.zip`)
3. Download via `curl.exe -L -o` (GitHub delivers at ~3–5 MB/s, much faster than npm registry)
4. Install silently: `start /wait installer.exe /S` or `Expand-Archive`

**Example — Agent Canvas (OpenHands UI):**
```powershell
# npm was too slow (timeout at 600s). GitHub Release was 38s:
curl.exe -L -o "$env:TEMP\Agent-Canvas-Setup.exe" `
  "https://github.com/OpenHands/agent-canvas/releases/download/v1.6.1/Agent-Canvas-Setup-1.6.1.exe"
Start-Process -FilePath "$env:TEMP\Agent-Canvas-Setup.exe" -ArgumentList '/S' -Wait -NoNewWindow
```
Installs to `%LOCALAPPDATA%\Programs\Agent Canvas\` as an Electron desktop app (224 MB).

## Known Working Instances

| Tool | Size | Method |
|---|---|---|
| **Flutter 3.44.8** | 1.77 GB | Script: `C:\Projects\lazy-unicorn\scripts\install_flutter.ps1` |
| **Android cmdline-tools** (14742923) | 143 MB | Script: `C:\Projects\lazy-unicorn\scripts\install_android_sdk.ps1` |
| **Bun 1.3.14** (Win baseline) | 36 MB | `curl -L -o bun.zip https://github.com/oven-sh/bun/releases/latest/download/bun-windows-x64-baseline.zip` → `Expand-Archive` to `~\\.bun\\bin\\`. **Must use baseline** on CPUs without AVX2 (Xeon E5 v3 etc.). Regular build crashes with `Illegal instruction` or `STATUS_STACK_BUFFER_OVERRUN`. |
| **Agent Canvas 1.6.1** (OpenHands UI) | 135 MB | `curl.exe -L -o` from GitHub Release → silent install (`/S`). Electron desktop app, no Docker required. |

Scripts live at the project root under `scripts/` where applicable. Run from PowerShell 7:
```powershell
powershell -ExecutionPolicy Bypass -File C:\Projects\lazy-unicorn\scripts\install_<tool>.ps1
```

## Pitfalls

### Do NOT
- **Use `Invoke-WebRequest -Resume`** — fails on Google Storage HTTP ranges.
- **Use `bash` in PowerShell** — `bash` in PS = WSL (may not be installed).
- **Put Cyrillic/Russian text in `.ps1`** — PowerShell encoding breaks, ParserError.
- **Use `-NoProfile` on `Start-Process`** — that flag belongs to `pwsh.exe`, not `Start-Process`.
- **Start the download yourself** — the user asked for a script, not execution. Write, describe, STOP.

### PowerShell 7 Syntax Notes
- Ternary operator `$cond ? $a : $b` is supported in PowerShell 7+.
- `[ScriptBlock]::Create((Get-Content 'file.ps1' -Raw))` parses syntax without execution (safe for verification).
- `Start-Process -NoNewWindow -Wait -PassThru` captures exit code from external programs.

### Bun on Windows (Older CPUs)
- **Xeon E5 v3 (Haswell) and similar pre-2016 CPUs** do NOT support AVX2 — Bun's regular Windows binary crashes with `Illegal instruction` (exit code 132) or `STATUS_STACK_BUFFER_OVERRUN` (0xC0000409).
- Always use **baseline** build: `bun-windows-x64-baseline.zip` from GitHub Releases.
- Detection: `powershell -Command "[CPU]::HasAVX2()"` returns `False` on affected CPUs.
- Baseline build is slightly slower but fully functional.

### Android SDK Specifics
- `cmdline-tools` zip extracts to `cmdline-tools/` → must be moved to `cmdline-tools/latest/` for `sdkmanager.bat` to find itself.
- Set `ANDROID_HOME` as user environment variable.
- `sdkmanager --sdk_root=SdkDir ...` — always pass `--sdk_root` or it looks in the wrong place.
- Accept licenses via `$("y" * 100) | & sdkmanager.bat --licenses`.
