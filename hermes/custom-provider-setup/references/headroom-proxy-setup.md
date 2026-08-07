### Headroom 0.31.0 Proxy Setup for Windows (Python 3.14)

## Architecture

Two proxy instances, each serving different upstreams with different backends.
**8788 currently disabled** — commented out in the unified launcher but preserved for manual start.

| Port | Upstream | Backend | Format | Status |
|------|----------|---------|--------|--------|
| 8787 | `localhost:20128/v1` (9router) | `anyllm-openai` | OpenAI-only | ✅ Active |
| 8788 | `agentrouter.org` (both APIs) | default `anthropic` | both (auto-routed) | ❌ Disabled |

**Backend rule:**
- `anyllm-openai` — forwards EVERYTHING as OpenAI `/v1/chat/completions` to `OPENAI_TARGET_API_URL`. Breaks Anthropic `/v1/messages` requests (converts to OpenAI). Use ONLY for OpenAI-only upstreams.
- Default (`anthropic`) — auto-routes `/v1/messages` → `ANTHROPIC_TARGET_API_URL`, `/v1/chat/completions` → `OPENAI_TARGET_API_URL`. Skips litellm credential validation. Use for upstreams serving both formats.

## Required Environment

- Python 3.14 with headroom 0.31.0 installed in user site-packages:
  `C:\Users\Unicorn\AppData\Roaming\Python\Python314\site-packages`
- headroom.exe (PyInstaller binary) at:
  `C:\Users\Unicorn\AppData\Roaming\Python\Python314\Scripts\headroom.exe`
- **headroom.exe ignores system PYTHONPATH** — must be set explicitly via `set PYTHONPATH=...` in .cmd launcher, or headroom crashes with missing deps
- Windows User env vars: `API_9ROUTER_KEY`, `API_AGENTROUTER_KEY`

## Launcher: `headroom_start.bat` (primary)

Unified launcher for both proxies. 8788 is currently commented out but can be enabled by uncommenting its section.

```batch
@echo off
set PYTHONPATH=C:\Users\Unicorn\AppData\Roaming\Python\Python314\site-packages

REM ─── 8787 — 9router (anyllm-openai) ─────────────────────────
set OPENAI_TARGET_API_URL=http://localhost:20128/v1
set ANTHROPIC_TARGET_API_URL=http://localhost:20128/v1
set OPENAI_API_KEY=%API_9ROUTER_KEY%
set ANTHROPIC_API_KEY=%API_9ROUTER_KEY%
set HEADROOM_OUTPUT_SHAPER=1
set HEADROOM_VERBOSITY_AUTOTUNE=1
set HEADROOM_OUTPUT_HOLDOUT=0.1
set HEADROOM_BACKEND=anyllm-openai
set HEADROOM_ANYLLM_PROVIDER=openai
start "" /MIN "C:\Users\Unicorn\AppData\Roaming\Python\Python314\Scripts\headroom.exe" proxy --port 8787

REM ─── 8788 — agentrouter (отключён) ──────────────────────────
REM set OPENAI_TARGET_API_URL=https://agentrouter.org/v1
REM set ANTHROPIC_TARGET_API_URL=https://agentrouter.org
REM set OPENAI_API_KEY=%API_AGENTROUTER_KEY%
REM set ANTHROPIC_API_KEY=%API_AGENTROUTER_KEY%
REM set HEADROOM_BACKEND=anthropic
REM start "" /MIN "C:\Users\Unicorn\AppData\Roaming\Python\Python314\Scripts\headroom.exe" proxy --port 8788
```

**Legacy separate files** (still on disk, not used):
- `headroom_start_8787.cmd` — old 8787-only launcher
- `headroom_start_8788.cmd` — 8788 separately, start command commented out

## Autostart (survives Hermes restart)

```
Registry (HKCU\...\Run) → wscript.exe //B → headroom_8787.vbs → headroom_start.bat
```

**VBS wrapper** (silent, no console flash) at `C:\Users\Unicorn\AppData\Local\hermes\headroom_8787.vbs`:
```vb
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "C:\Users\Unicorn\AppData\Local\hermes\headroom_start.bat", 7, False
```

**Registry add** (from cmd):
```
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v Headroom /t REG_SZ /d "wscript.exe //B C:\Users\Unicorn\AppData\Local\hermes\headroom_8787.vbs" /f
```

## Compression Flags

| Env Var | Value | Effect |
|---------|-------|--------|
| `HEADROOM_OUTPUT_SHAPER` | `1` | Enable output token shaping (compression) |
| `HEADROOM_VERBOSITY_AUTOTUNE` | `1` | Auto-tune verbosity level per request |
| `HEADROOM_OUTPUT_HOLDOUT` | `0.1` | Reserve 10% tokens for fallback (safety margin) |

## Proxy Config Pitfalls

### Golden rule: never make unauthorized changes

**Only modify files the user explicitly asks for.** Do NOT:
- Unify separate `.cmd` files into a new `.bat` without asking
- Update VBS wrappers or Registry entries unless told
- Rewrite files with truncated/placeholder values (breaks working setup)
- Delete or recreate files — prefer `patch` or restore-as-was approach
- Make "helpful" improvements the user didn't request

When user says "закомментируй старт 8788": do EXACTLY that — comment out that one line, nothing else.

### `proxy_error` on `/v1/chat/completions` with default backend:**
- Default `anthropic` backend routes OpenAI requests through litellm
- Litellm checks credentials for unknown models → fails if `OPENAI_API_KEY` not set or provider not recognized
- Fix: set `HEADROOM_BACKEND=anyllm-openai` + `HEADROOM_ANYLLM_PROVIDER=openai` for OpenAI-only upstreams

**`headroom.exe` fails with "FastAPI required":**
- Cause: `PYTHONPATH` not set or set incorrectly — headroom.exe can't find its own site-packages
- Fix: always `set PYTHONPATH=C:\Users\Unicorn\AppData\Roaming\Python\Python314\site-packages` in .cmd before calling headroom.exe

**`cmd /c` with inline python fails:**
- `cmd /c python -c "..."` with semicolons in code breaks on Windows cmd
- Fix: use .cmd + .py launcher pattern or start /B on .cmd file directly

**`anyllm-openai` breaks Anthropic `/v1/messages`:**
- This backend converts ALL requests to OpenAI format → `/v1/chat/completions`
- Anthropic models get corrupted responses
- Fix: use separate port with default `anthropic` backend for multi-format upstreams

## Agentrouter quirks

- Agentrouter.org blocks curl (User-Agent detection) but passes Python OpenAI SDK requests
- Health check via curl will show 401 — this is expected and does NOT affect Hermes
- Two custom_providers entries needed in Hermes config.yaml (one per api_mode):
  ```yaml
  - name: agentrouter-openai
    base_url: https://agentrouter.org/v1
    key_env: API_AGENTROUTER_KEY
    api_mode: chat_completions
    discover_models: false
  - name: agentrouter-claude
    base_url: https://agentrouter.org
    key_env: API_AGENTROUTER_KEY
    api_mode: anthropic_messages
    discover_models: false
  ```
- `discover_models: false` prevents Hermes from hammering agentrouter with discovery requests

## Verification

```bash
# Health check
curl -s http://127.0.0.1:8787/health | python -c "import sys,json; d=json.load(sys.stdin); print('ready:',d['ready'],'| backend:',d['config']['backend'])"

# Models passthrough (verify upstream models are NOT filtered)
curl -s http://127.0.0.1:8787/v1/models | python -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('data',[])), 'models')"

# Chat completions (OpenAI format)
curl -s -X POST http://127.0.0.1:8787/v1/chat/completions \
  -H "Authorization: Bearer %API_9ROUTER_KEY%" \
  -H "Content-Type: application/json" \
  -d '{"model":"SuperCombo_256k_100","max_tokens":10,"messages":[{"role":"user","content":"ping"}]}'

# Chat completions (Anthropic format)
curl -s -X POST http://127.0.0.1:8788/v1/messages \
  -H "x-api-key: %API_AGENTROUTER_KEY%" \
  -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json" \
  -d '{"model":"claude-opus-4-8","max_tokens":10,"messages":[{"role":"user","content":"ping"}]}'
```
