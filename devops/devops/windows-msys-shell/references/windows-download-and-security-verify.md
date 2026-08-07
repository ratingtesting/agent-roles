# Windows: large downloads + local security verification (verified patterns)

Reusable, task-focused patterns confirmed working on Pëtr's Windows host (2026-07-25).
Not session narrative — these are durable techniques.

## 1. Resume-safe large download (GB-scale, slow link)

Slow/unstable connections make a single `curl` of a ~1.7 GB file (e.g. Flutter) time out
or take hours. Use `curl -C -` (resume from byte offset) inside a retry loop, then verify
integrity before extracting.

Template (`scripts/install_flutter.sh` in lazy-unicorn):
```bash
FLUTTER_VERSION="3.44.8"
URL="https://storage.googleapis.com/flutter_infra_release/releases/stable/windows/flutter_windows_${FLUTTER_VERSION}-stable.zip"
ZIP="/tmp/flutter_${FLUTTER_VERSION}.zip"
DEST="/c/dev/tools"

for i in $(seq 1 50); do
  if curl -L -C - --retry 5 --retry-delay 3 --connect-timeout 30 -o "$ZIP" "$URL"; then
    break
  fi
  sleep 3
done

# Integrity gate — never extract a possibly-truncated archive
unzip -tq "$ZIP" >/dev/null 2>&1 || { echo "corrupt, delete and rerun"; exit 1; }

rm -rf "$DEST/flutter"
unzip -q "$ZIP" -d "$DEST"
# add to PATH (bashrc + Windows user env via powershell.exe)
```
Run from **git-bash** (Trap 8), not PowerShell `bash`.

### PowerShell variant (when user runs from PowerShell, not WSL)

When the user has PowerShell 7 and **no WSL**, a `.sh` script is useless — `bash` in
PowerShell resolves to WSL, which fails. Use `.ps1` with `curl.exe -C -` via `Start-Process`
(instead of `Invoke-WebRequest -Resume`, which fails on Google Storage).

Key differences from the bash template:
- `curl.exe -C -` retired inside a PowerShell loop
- Size gate: `$size -lt 100MB` (PowerShell `(Get-Item).Length`)
- Extract via `Expand-Archive -Path $Zip -DestinationPath $Dest`
- PATH via `[Environment]::SetEnvironmentVariable("Path",...,"User")`

**Use English-only strings in .ps1** — Cyrillic produces ParserError due to UTF-8/codepage mismatch on Windows.

Working example (`scripts/install_flutter.ps1`):
```powershell
$Version = "3.44.8"
$Url = "https://storage.googleapis.com/.../flutter_windows_${Version}-stable.zip"
$Dest = "C:\dev\tools"
$Zip = "$env:TEMP\flutter_${Version}.zip"

for ($i = 1; $i -le 50; $i++) {
    $p = Start-Process -FilePath "curl.exe" -ArgumentList @("-L","-C","-","--retry","5","--retry-delay","3","--connect-timeout","30","-o",$Zip,$Url) -NoNewWindow -Wait -PassThru
    if ($p.ExitCode -eq 0) { break }
    Start-Sleep -Seconds 3
}

if (-not (Test-Path $Zip) -or (Get-Item $Zip).Length -lt 100MB) { exit 1 }
Remove-Item -Recurse -Force "$Dest\flutter" -ErrorAction SilentlyContinue
Expand-Archive -Path $Zip -DestinationPath $Dest -Force

$userPath = [Environment]::GetEnvironmentVariable("Path","User")
if ($userPath -notlike "*$BinDir*") {
    [Environment]::SetEnvironmentVariable("Path","$userPath;$BinDir","User")
}
```

Also works for Android SDK (143 MB `commandlinetools-win-*.zip`):
- URL: `https://dl.google.com/android/repository/commandlinetools-win-14742923_latest.zip`
- Extract to `C:\dev\tools\android-sdk\cmdline-tools\latest\`
- Install components: `& "$CmdlineDir\bin\sdkmanager.bat" --sdk_root=$SdkDir "platforms;android-35" "build-tools;35.0.0" "platform-tools"`
- Accept licenses: `$yes = "y" * 100; $yes | & $sdkmanager --sdk_root=$SdkDir --licenses`

## 2. Gitleaks config gotcha (Windows)

`[extend]` with an `https://...` path does NOT work — gitleaks fails to open the URL on
Windows ("volume label syntax is incorrect"). Either:
- drop `[extend]` and write self-contained `[[rules]]` (the repo's custom rules cover
  service_role + provider API keys), or
- keep only the standard built-in rules (gitleaks loads them by default).

Verified working `.gitleaks.toml` (repo root, `lazy-unicorn`):
```toml
title = "lazy-unicorn gitleaks config"
[[rules]]
id = "LazyUnicorn-Supabase-Service-Role"
description = "Supabase service_role key (full access)"
regex = '''(?i)(supabase|sb)-(?:\w*-)?service[-_]?role[-_]?key['\s:=]+['"]?([a-zA-Z0-9\-_]{40,})'''
keywords = ["service_role", "supabase"]
severity = "CRITICAL"
[[rules]]
id = "LazyUnicorn-API-Key"
description = "API keys (9router/freellmapi/agentrouter)"
regex = '''(?i)(API_9ROUTER_KEY|API_FREELLMAPI_KEY|API_AGENTROUTER_KEY)['\s:=]+['"]([a-zA-Z0-9\-_]{20,})'''
keywords = ["API_9ROUTER_KEY", "API_FREELLMAPI_KEY", "API_AGENTROUTER_KEY"]
severity = "HIGH"
[allowlist]
paths = [ '''(?i)(\.git|node_modules|\.dart_tool|build|\.venv|\.obsidian|graphify-out|brain|\.storage)''', ]
```
Run: `gitleaks detect --config .gitleaks.toml --source . --no-banner`

## 3. Semgrep regex gotcha (keys with underscores)

A pattern like `(service_role_key)["'\s:=]+...` FAILS to match `service_role_key` because
the key itself contains an underscore and the separator class consumes the `=`/`:` boundary
but the capture anchor is off. The working form:

```yaml
- id: lu-hardcoded-secret
  pattern-regex: |
    (service_role_key|SERVICE_ROLE|API_9ROUTER_KEY|API_FREELLMAPI_KEY|API_AGENTROUTER_KEY)["\s:=]+["']([a-zA-Z0-9\-_.]{20,})["']
  severity: ERROR
  languages: [dart, yaml, json]
```
Note: `["\s:=]+` (double-quote inside the class) matches `"service_role_key": "..."`.
Verify with a temp fixture containing a fake secret; expect 1 blocking finding (exit 1).

Semgrep first run is slow on Windows (cold start ~30-60s). Run via git-bash, not WSL.

## 4. Verify-before-claim (Petr's standing expectation)

After writing any config/script, actually execute it (ad-hoc verify / real invocation)
before saying "works". `write_file` lint = syntax only; it does NOT prove runtime behavior.
The two bugs above (gitleaks extend URL, semgrep underscore regex) both passed `write_file`
cleanly and only surfaced at runtime.
