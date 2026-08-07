---
name: headroom-proxy-setup
description: >-
  Configure and debug Headroom proxy on Windows with multiple upstreams
  (9router, agentrouter, freellmapi, etc.). Covers startup, routing
  configuration, health verification, and Windows-specific troubleshooting.
trigger: >-
  User asks to set up a proxy, install headroom, create a passthrough for AI
  providers, configure multiple upstreams, or debug headroom startup failures.
  Load this whenever the user mentions "headroom proxy", "лёгкий прокси",
  "компрессия трафика", or asks to route through 9router/agentrouter.
replaces: []
---

# Headroom Proxy Setup (Windows)

## ⚠️ Methodology: Always Check Docs First

Before touching any headroom config, read the OFFICIAL documentation:
- **README:** https://github.com/headroomlabs-ai/headroom/blob/main/README.md
- **Docs site:** https://headroom-docs.vercel.app/docs
- **Proxy help:** `headroom.exe proxy --help` (lists all flags + env vars)

Do NOT guess CLI flags, do NOT read source code to figure out params. The docs are the source of truth. If you have a specific question about a feature, search the docs first.

## ⚠️ Critical: Correct PYTHONPATH on this Windows machine

Headroom is installed **user-wide** under Python 3.14 at:
```
C:\Users\Unicorn\AppData\Roaming\Python\Python314\site-packages
```

The system site-packages (`C:\Python314\Lib\site-packages`) is **EMPTY** (only pip).
**NEVER** point PYTHONPATH at `C:\Python314\Lib\site-packages` — imports will fail.
Always use the **user site-packages** path above.

## Quick Start — Two Approaches

### Approach A: `.py` launcher + minimal `.cmd` caller (RECOMMENDED)

This session established the most reliable Windows pattern: put **all** required env vars inside a `.py` launcher **before** `from headroom.cli import main`, and have a minimal `.cmd` caller set `PYTHONPATH` then invoke that `.py`.

**Why not `python -c "..."` inside `.cmd`?** On Windows, `cmd.exe` can misparse one-liners with quotes/semicolons/non-ASCII, causing silent import failures. A `.py` file avoids that completely.

**headroom_8787_launcher.py**
```python
import os, sys

os.environ["HEADROOM_OUTPUT_SHAPER"] = "1"
os.environ["HEADROOM_VERBOSITY_AUTOTUNE"] = "1"
os.environ["OPENAI_TARGET_API_URL"] = "http://localhost:20128/v1"
os.environ["ANTHROPIC_TARGET_API_URL"] = "http://localhost:20128/v1"

# 8787 → 9router (localhost:20128)
# Дефолтный backend (anthropic) — НЕ ставить HEADROOM_BACKEND!
#   /v1/messages         → ANTHROPIC_TARGET_API_URL     (нативный Anthropic)
#   /v1/chat/completions → OPENAI_TARGET_API_URL         (нативный OpenAI)
os.environ["OPENAI_TARGET_API_URL"] = "http://localhost:20128/v1"
os.environ["ANTHROPIC_TARGET_API_URL"] = "http://localhost:20128/v1"
os.environ["OPENAI_API_KEY"] = os.environ.get("API_9ROUTER_KEY", "")

os.environ["PYTHONPATH"] = r"C:\Users\Unicorn\AppData\Roaming\Python\Python314\site-packages"

from headroom.cli import main
sys.argv = ["headroom", "proxy", "--port", "8787"]
main()
```

**headroom_start_8787.cmd**
```batch
@echo off
set PYTHONPATH=C:\Users\Unicorn\AppData\Roaming\Python\Python314\site-packages
C:\Python314\python.exe C:\Users\Unicorn\AppData\Local\hermes\headroom_8787_launcher.py
```

Mirror for 8788 with agentrouter URLs/port.

### Approach B: `headroom.exe` directly (simpler, but PyInstaller-bundled)

```bash
export OPENAI_TARGET_API_URL="http://localhost:20128/v1" && \
export ANTHROPIC_TARGET_API_URL="http://localhost:20128/v1" && \
export HEADROOM_OUTPUT_SHAPER=1 && \
/c/Users/Unicorn/AppData/Roaming/Python/Python314/Scripts/headroom.exe proxy --port 8787
```

**Note on `headroom.exe`:** It is a PyInstaller/shiv bundle with **frozen imports** — it does NOT read `PYTHONPATH`. It works standalone as long as its bundled deps are intact. Use Approach A when you need to control which Python/site-packages are used.

### ⚠️ `.py` launcher caveat

Earlier guidance said env vars from `os.environ` inside a `.py` launcher were unreliable. This session found the real failure mode was the **caller**, not the `.py` file itself: when `.cmd` used `python -c "..."`, Windows/non-ASCII/quoting broke startup silently. The recommended pattern is now:

- `.cmd` = only `PYTHONPATH` + invocation of `.py`
- `.py` = all headroom env vars, including backend/auth

**Both** `OPENAI_TARGET_API_URL` AND `ANTHROPIC_TARGET_API_URL` must be set — setting only one breaks the other protocol's routing.

### Debugging Backend Selection

If you see `Set credentials for your provider (e.g., OPENAI_API_KEY, MISTRAL_API_KEY)` in the proxy banner — backend is NOT using `anyllm-openai`. Verify:

1. `HEADROOM_BACKEND=anyllm-openai` is set before `from headroom.cli import main`
2. `HEADROOM_ANYLLM_PROVIDER=openai` is set
3. `OPENAI_API_KEY` env var is set inside the `.py` launcher from a Windows-visible env var such as `%API_9ROUTER_KEY%`
4. `ANTHROPIC_TARGET_API_URL` is also set, even if both URLs point to the same upstream

### How it works internally

When `backend: "anyllm-openai"` is set, `create_proxy_backend()` in `registry.py` creates an `AnyLLMBackend` with:
- `provider="openai"`
- `api_base=OPENAI_TARGET_API_URL` (or `ANTHROPIC_TARGET_API_URL` for anthropic routes)
- `api_key=OPENAI_API_KEY` env var

The backend then calls `AnyLLM.create("openai", api_base=..., api_key=...)` which wraps the upstream as a plain OpenAI-compatible endpoint.

## Configuration Pattern

Headroom 0.31.x supports one upstream per process. For multiple upstreams, run separate processes on different ports:

| Port | Upstream | OpenAI URL | Anthropic URL |
|------|----------|-----------|---------------|
| 8787 | 9router | `http://localhost:20128/v1` | `http://localhost:20128/v1` |
| 8788 | agentrouter | `https://agentrouter.org/v1` | `https://agentrouter.org` |

### Persistent Configuration via Settings GUI

Per https://headroomlabs-ai.github.io/headroom/configuration/#settings-gui:

1. Start headroom with minimal flags: `headroom.exe proxy --port 8787`
2. Open `http://127.0.0.1:8787/dashboard/settings` in a browser
3. Set the upstream URLs under the **Endpoints** section (`ANTHROPIC_TARGET_API_URL` / `OPENAI_TARGET_API_URL`)
4. Click "Save" to persist without restart, or "Apply & Restart" to take effect immediately
5. Settings are saved to `~/.headroom/settings.json` and loaded at startup

**Precedence** (highest to lowest):
1. Explicit shell `export` (env vars)
2. Settings from `~/.headroom/settings.json`
3. Code default

## Routing Behavior

- `/v1/chat/completions` → forwarded to `openai_api_url`
- `/v1/messages` → forwarded to `anthropic_api_url`
- `/v1/models` → forwarded to upstream **as-is** (no modification — verified in code: `proxy_routes.py` does not filter/reorder the model list)
- Other paths → catch-all passthrough based on auth headers
- `/health`, `/livez`, `/readyz` → headroom's own health endpoints

### `/v1/models` Passthrough

Headroom does NOT modify the `/v1/models` response. The upstream's response is returned verbatim. Tested with 9router — the model list passes through unchanged (189 models). For providers that reject unauthenticated `/v1/models` (agentrouter returns `unauthorized_client_error`), use `discover_models: false` in Hermes provider config.

### Credentials Forwarding

Headroom reads the `Authorization` header from the incoming request and forwards it to the upstream. Hermes's existing API key config works transparently — no extra auth setup needed.

---

### ⚠️ Backend Selection — Use DEFAULT (`anthropic`) for Both Proxies

**User-confirmed rule (2026-07-17):** Both 8787 (→9router) and 8788 (→agentrouter) must use the **default backend** (`anthropic`). Do NOT set `HEADROOM_BACKEND` at all.

**Why default backend is correct:**
- Default `anthropic` backend routes **natively** by path:
  - `/v1/messages` (Anthropic format) → `ANTHROPIC_TARGET_API_URL` — sent as-is, no conversion
  - `/v1/chat/completions` (OpenAI format) → `OPENAI_TARGET_API_URL` — sent as-is, no conversion
- This is what you want for upstreams that accept **both** protocols natively (9router on :20128, agentrouter.org).
- Verified: 8788 with default backend routes `/v1/messages → https://agentrouter.org` and `/v1/chat/completions → https://agentrouter.org` — both shown correctly in the startup banner. `agentrouter-claude` (Anthropic Messages API) works through it.

**The `anyllm-openai` backend is WRONG for dual-protocol proxies — PITFALL:**
- `anyllm-openai` forces ALL traffic through the OpenAI provider path. `/v1/messages` (Anthropic) gets **converted to OpenAI format** and sent to `OPENAI_TARGET_API_URL/v1/chat/completions`.
- This BREAKS `agentrouter-claude` — Hermes sends Anthropic Messages API, headroom converts it to OpenAI format, agentrouter receives the wrong format. The user caught this: *"опенаи!!! шлет на антропик. Что ты там настроил?"*
- `anyllm-openai` only makes sense for a single-protocol OpenAI-only upstream. Do not use it when the proxy must serve both `/v1/messages` and `/v1/chat/completions`.

**Default backend `.py` launcher (correct — no HEADROOM_BACKEND set):**
```python
import os, sys
os.environ["HEADROOM_OUTPUT_SHAPER"] = "1"
os.environ["HEADROOM_VERBOSITY_AUTOTUNE"] = "1"
os.environ["OPENAI_TARGET_API_URL"] = "http://localhost:20128/v1"
os.environ["ANTHROPIC_TARGET_API_URL"] = "http://localhost:20128/v1"
os.environ["OPENAI_API_KEY"] = os.environ.get("API_9ROUTER_KEY", "")
os.environ["PYTHONPATH"] = r"C:\Users\Unicorn\AppData\Roaming\Python\Python314\site-packages"
from headroom.cli import main
sys.argv = ["headroom", "proxy", "--port", "8787"]
main()
```

**When `anyllm-openai` might still be needed (rare):** only if the upstream is OpenAI-only AND the default backend's litellm credential check rejects your custom model name. This was a red herring in earlier sessions — the real issue was the `SuperCombo_256k` vs `SuperCombo_256k_100` model name mismatch, not the backend. If you see `No active credentials for provider: openai` with the default backend, first verify the model name is correct via `/v1/models`, then consider `anyllm-openai` as a last resort for single-protocol OpenAI-only upstreams only.

---

### Model names — user-defined groups, passthrough-safe

Inside 9router, your `SuperCombo_*` names are **group/model-list labels**, not fixed global IDs. Headroom passes the `model` parameter **unchanged** to upstream, so this setup is resilient to renames inside 9router.

**Rule:** headroom does not need changes when you rename groups inside 9router. The only thing that must stay in sync is Hermes `config.yaml` `model.default.model` with the current group/model name exposed by 9router.

**If requests fail with `model_not_found`**, list current IDs from the proxy:
```bash
curl -s -H "Authorization: Bearer $API_9ROUTER_KEY" http://127.0.0.1:8787/v1/models | jq '.data[].id'
```

When running two headroom proxies (8787→9router, 8788→agentrouter), point `custom_providers` at the proxies. Use `discover_models: false` for providers that reject unauthenticated `/v1/models` calls (agentrouter returns `unauthorized_client_error`):

```yaml
custom_providers:
  - name: 9router
    base_url: http://127.0.0.1:8787/v1    # headroom proxy → upstream localhost:20128
    key_env: API_9ROUTER_KEY
    api_mode: chat_completions
  - name: freellmapi                        # direct, no proxy
    base_url: http://127.0.0.1:31415/v1
    key_env: API_FREELLMAPI_KEY
    api_mode: chat_completions
  - name: agentrouter-openai
    base_url: http://127.0.0.1:8788/v1    # headroom proxy → upstream agentrouter.org/v1
    key_env: API_AGENTROUTER_KEY
    api_mode: chat_completions
    discover_models: false
  - name: agentrouter-claude
    base_url: http://127.0.0.1:8788      # headroom proxy → upstream agentrouter.org (Anthropic)
    key_env: API_AGENTROUTER_KEY
    api_mode: anthropic_messages
    discover_models: false
```

**Note:** `model.default.base_url` in config.yaml can override the provider's `base_url` for the main model. If Hermes is configured to use 9router as `model.default`, set both `model.default.base_url` AND `custom_providers[9router].base_url` to the same proxy URL to avoid conflict.

### Dual-Protocol Routing with DEFAULT Backend

The **default** `anthropic` backend handles both protocols natively (no conversion):
- `/v1/messages` (Anthropic format) → `ANTHROPIC_TARGET_API_URL` — forwarded as-is
- `/v1/chat/completions` (OpenAI format) → `OPENAI_TARGET_API_URL` — forwarded as-is

One headroom instance serves both Hermes providers (agentrouter-openai and agentrouter-claude) pointing at the same proxy port. This is why BOTH 8787 and 8788 use the default backend — no `HEADROOM_BACKEND` env var.

**Do NOT use `anyllm-openai` for dual-protocol proxies** — it converts `/v1/messages` to OpenAI format, breaking Anthropic-native upstreams (see "Backend Selection" above).

### AgentRouter Auth

AgentRouter (`https://agentrouter.org`) returns `unauthorized_client_error` (401) for both protocol formats when the API key is invalid/expired. This error comes from the **upstream**, not from headroom — verified by hitting AgentRouter directly and getting the identical response. Headroom correctly forwards the upstream rejection.

Fix: update `API_AGENTROUTER_KEY` in `.env`, not headroom config.

### Model Listing Works

Headroom correctly forwards `/v1/models` to the upstream without modifying the response. Verified with 9router: 189 models pass through unchanged. No special bypass or model list workaround is needed. For providers that reject `/v1/models` without auth (agentrouter), use `discover_models: false` in the provider config.

### Credentials Forwarding

Headroom reads the `Authorization` header from the incoming request and forwards it to the upstream. Hermes's existing API key config works transparently — no extra auth setup needed.

## Windows-Specific Pitfalls

See `references/windows-pitfalls.md` for details on:

- **Stale SQLite WAL files** after `taskkill /F` — remove `~/.headroom/ccr_store.db-shm` and `~/.headroom/ccr_store.db-wal`
- **Very slow startup (60-100s)** — headroom prints the banner immediately, but uvicorn takes 60-100 seconds to bind the port on this Windows machine (Kompress ML model loading). This is normal behavior, not a hang. Wait before connecting.
- **`headroom.exe` is PyInstaller-bundled** — has frozen imports, does NOT read `PYTHONPATH`. Works standalone but you can't add packages to it. Use `python.exe -c "from headroom.cli import main"` (Approach A) when you need to control site-packages.
- **System site-packages is EMPTY** — `C:\Python314\Lib\site-packages` only contains pip. Headroom and all deps (fastapi, uvicorn, etc.) are in **user** site-packages: `C:\Users\Unicorn\AppData\Roaming\Python\Python314\site-packages`. NEVER point PYTHONPATH at system site-packages.
- **`headroom.exe` vs `python -m headroom.cli`** — both work. `headroom.exe` spawns a child uvicorn process (different PID). `python -m` runs in the parent process directly.
- **Curl unreliability on MSYS** — `curl` may fail with "Connection refused" even when the server is running; use Python sockets or httpx for reliable checks
- **`&` shell backgrounding** — not allowed in Hermes terminal; always use `terminal(background=true, notify_on_complete=false)` for long-lived servers
- **PYTHONPATH required for `python.exe` approach** — when running Headroom via `python.exe -c` or `.py` launcher, set `PYTHONPATH` to user site-packages (see above). Not needed for `headroom.exe`.

## Health Verification

Use Python sockets (not curl) for reliable health checks on Windows:

```python
import socket, json

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(5)
s.connect(('127.0.0.1', 8787))
s.sendall(b'GET /health HTTP/1.0\r\nHost: 127.0.0.1\r\n\r\n')
data = b''
while True:
    chunk = s.recv(4096)
    if not chunk: break
    data += chunk
s.close()

body = data.split(b'\r\n\r\n', 1)[1]
d = json.loads(body)
print('openai_api_url:', d['config']['openai_api_url'])
print('anthropic_api_url:', d['config']['anthropic_api_url'])
print('ready:', d.get('ready'))
```

### Verify model list passthrough

```python
key = "your-api-key"
s = socket.socket(...)
s.connect(('127.0.0.1', 8787))
req = f'GET /v1/models HTTP/1.0\r\nHost: 127.0.0.1\r\nAuthorization: Bearer {key}\r\n\r\n'
s.sendall(req.encode())
data = b''
while True:
    chunk = s.recv(4096)
    if not chunk: break
    data += chunk
s.close()

body = data.split(b'\r\n\r\n', 1)[1]
d = json.loads(body)
models = [m['id'] for m in d.get('data', [])]
print(f'{len(models)} models')
```

## Launcher Files

### `.cmd` caller + `.py` launcher (RECOMMENDED — one pair per instance)

Create `headroom_8787_launcher.py` and `headroom_start_8787.cmd` in `C:\\Users\\Unicorn\\AppData\\Local\\hermes\\`.

**Why this split?** This session found the previous `python -c "..."` one-liner in `.cmd` was unreliable on Windows because `cmd.exe` can misparse quotes, semicolons, and non-ASCII. A real `.py` file avoids that completely.

**headroom_8787_launcher.py** — owns all headroom env vars (DEFAULT backend, no HEADROOM_BACKEND):
```python
import os, sys

os.environ["HEADROOM_OUTPUT_SHAPER"] = "1"
os.environ["HEADROOM_VERBOSITY_AUTOTUNE"] = "1"
os.environ["OPENAI_TARGET_API_URL"] = "http://localhost:20128/v1"
os.environ["ANTHROPIC_TARGET_API_URL"] = "http://localhost:20128/v1"
os.environ["OPENAI_API_KEY"] = os.environ.get("API_9ROUTER_KEY", "")

os.environ["PYTHONPATH"] = r"C:\Users\Unicorn\AppData\Roaming\Python\Python314\site-packages"

from headroom.cli import main
sys.argv = ["headroom", "proxy", "--port", "8787"]
main()
```

**headroom_start_8787.cmd** — only sets `PYTHONPATH` then invokes `.py`:
```batch
@echo off
set PYTHONPATH=C:\Users\Unicorn\AppData\Roaming\Python\Python314\site-packages
C:\Python314\python.exe C:\Users\Unicorn\AppData\Local\hermes\headroom_8787_launcher.py
```

Mirror for 8788 with agentrouter URLs/port.

### Autostart: `.lnk` in Startup folder pointing to `.cmd`

Use VBS to create `.lnk` files (see `references/windows-pitfalls.md` and `windows-autostart` skill). Point the `.lnk` at the `.cmd` file, NOT at the `.py` launcher — the `.cmd` approach is more reliable.

```vbscript
Set WshShell = CreateObject("WScript.Shell")
startup = WshShell.SpecialFolders("Startup")
Set lnk = WshShell.CreateShortcut(startup & "\Headroom-8787.lnk")
lnk.TargetPath = "C:\\Users\\Unicorn\\AppData\\Local\\hermes\\headroom_start_8787.cmd"
lnk.WorkingDirectory = "C:\\Users\\Unicorn\\AppData\\Local\\hermes"
lnk.WindowStyle = 7  ' minimized
lnk.Save
```

**Ready-to-use template**: See `templates/create_headroom_autostart.vbs`

Run with: `cscript //nologo create_headroom_autostart.vbs`

## ⚠️ Process Persistence — Surviving Hermes Session Cleanup

**Problem:** Headroom started via Hermes `terminal(background=true)` gets killed by SIGTERM when:
- The Hermes session ends or is reset (`/new`)
- A network error / stream timeout occurs mid-conversation
- The parent terminal session is cleaned up

This is **not** a headroom bug — Hermes background processes are lifecycle-bound to the session that spawned them. When that session dies, all its `terminal(background=true)` children get SIGTERM.

### Solution: Detach headroom from Hermes entirely

**Pattern A — `start /B` (works from Hermes terminal, survives session end):**
```bash
cmd /c "start /B C:\Users\Unicorn\AppData\Local\hermes\headroom_start_8787.cmd"
cmd /c "start /B C:\Users\Unicorn\AppData\Local\hermes\headroom_start_8788.cmd"
```
`start /B` launches a detached process that is NOT a child of the Hermes terminal. Hermes cannot SIGTERM it. Verified: processes survive after the Hermes session that started them is gone.

**Pattern B — Registry Run (survives reboot + login, most durable):**
```bash
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "Headroom-8787" /t REG_SZ /d "wscript.exe //B \"C:\Users\Unicorn\AppData\Local\hermes\headroom_8787.vbs\"" /f
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "Headroom-8788" /t REG_SZ /d "wscript.exe //B \"C:\Users\Unicorn\AppData\Local\hermes\headroom_8788.vbs\"" /f
```
Where `headroom_8787.vbs` is:
```vbscript
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "C:\Users\Unicorn\AppData\Local\hermes\headroom_start_8787.cmd", 7, False
```
`wscript //B` runs silently (no console window). The `.vbs` → `.cmd` → `.py` chain starts headroom minimized and detached.

**Recommendation:** Use BOTH — `start /B` for immediate launch during a session, Registry Run for post-reboot persistence. The Startup `.lnk` is a third redundant layer.

### Restart after a crash (manual)
```bash
cmd /c "C:\Users\Unicorn\AppData\Local\hermes\headroom_start_8787.cmd"
cmd /c "C:\Users\Unicorn\AppData\Local\hermes\headroom_start_8788.cmd"
```

### Verifying processes are truly detached
```bash
# Should show PIDs even after Hermes session reset
netstat -ano | grep -E ":8787|:8788" | grep LISTENING
curl -s http://127.0.0.1:8787/health
curl -s http://127.0.0.1:8788/health
```

## ⚠️ Compression Visibility — Models Not in Headroom Dashboard

**Symptom:** A model (e.g., `glm-5.2` on agentrouter) works through the proxy, but does NOT appear in headroom's dashboard and shows no compression in `/stats`.

**Cause:** Headroom's compression (Output Shaper, Kompress) only activates for models it recognizes as compressible. Unknown/custom model names may be passed through without compression. The `mode: "cache"` setting means prefix-freezing for cache alignment, which may show `requests_compressed: 0` with `prefix_frozen` in the uncompressed breakdown — this is normal for short or cache-aligned requests.

**Not a bug:** The proxy is transparent — it forwards requests correctly. Compression depends on headroom's internal model registry and request-size heuristics. For custom model names, verify via `/stats` that traffic is flowing; compression may engage on larger contexts.