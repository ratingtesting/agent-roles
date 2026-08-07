---
name: litellm-custom-router-bridge
description: Bridge LiteLLM clients to a custom router via proxy.
---

# LiteLLM ↔ Custom Router Bridge

Connect any **LiteLLM-backed client** to a **custom OpenAI-compatible router** that uses its own
provider/model namespace (e.g. 9router's `oc/...`, `opencode/...`).

## When this applies
- Client throws `litellm.BadRequestError: LLM Provider NOT provided. You passed model=oc/deepseek-v4-flash-free`
- Client is OpenHands / Agent Canvas / litellm SDK / LangChain-with-litellm
- Upstream is 9router, freellmapi, Headroom, a local vLLM, or any OpenAI-compatible server routing
  by its OWN namespace (not LiteLLM's `openai/`, `anthropic/`, … prefixes)

## Root cause
LiteLLM validates the provider prefix **client-side** before sending. A bare `oc/...` is an unknown
provider → it refuses with "LLM Provider NOT provided". But the upstream router needs exactly
`oc/...` — it does NOT know an `openai/` prefix. A single model string cannot satisfy both sides.

## The fix (verified 2026-07-27, OpenHands → 9router)
Two parts:

1. **In the client**, present the model as `openai/<upstream-namespace>/<model>`:
   - `openai/oc/deepseek-v4-flash-free`
   - `openai/oc/mimo-v2.5-free`
   LiteLLM sees `openai/` → uses the OpenAI-compatible client → OK. It forwards everything AFTER
   `openai/` as the model name to `api_base`.

   Official LiteLLM (OpenAI-Compatible Endpoints):
   > Put `openai/` in front of your model name so litellm knows you're calling an openai
   > `/chat/completions` endpoint; LiteLLM routes via the openai client and forwards the rest of
   > the name to `api_base`. Example: `model: openai/google/gemma` → sends `google/gemma`.

2. **Run a tiny streaming proxy** between the client and the router that strips the leading
   `openai/` from the request body. The client's Base URL points at the proxy, NOT the router.

   ```
   Client (LiteLLM) → http://localhost:20129/v1 (proxy) → router :20128
   model: openai/oc/deepseek-v4-flash-free
   proxy rewrites → oc/deepseek-v4-flash-free  (sent to router)
   ```

## Proxy requirements (PITFALLS)
- **MUST stream (pipe) SSE**, not buffer the whole response. Buffering breaks OpenHands' live token
  stream; a trailing `data: [DONE]` frame can also break strict JSON parsers. Use
  `proxyRes.pipe(res)` and delete `content-length` so the client uses chunked transfer.
- **Only rewrite the request body** (`json.model` startsWith `openai/` → slice it). Pass everything
  else (headers, SSE) through verbatim.
- **Proxy must be running** before the client is used — it does NOT auto-start. If it died, the
  client either hits a dead port, or (if Base URL was flipped to the router directly) sends a bare
  `oc/...` and gets the same "Provider NOT provided" error. Verify: `netstat -ano | grep 20129`.
- Make it persistent via the Windows Startup folder (see `windows-service-autostart`) so it survives
  reboots — same treatment as 9router/freellmapi/flashrank.
- **Register as a Windows scheduled task (`schtasks /Create /TN 9router-proxy /TR "node <path>\proxy.js" /SC ONLOGON /F`)** — a Startup-folder `.lnk` is unreliable for node daemons; a logon task is more robust.

## OpenHands / Agent Canvas profile-file trap (PITFALL — separate from the prefix bug)
Even with the proxy + `openai/oc/...` model, OpenHands can still throw `litellm.BadRequestError: ... You passed model=` (model is **empty**, not just missing prefix). Root cause is NOT LiteLLM — it's OpenHands's **on-disk profile JSON**, which the UI onboarding silently corrupts.

- Profiles live under `%USERPROFILE%\.openhands\`:
  - `agent-profiles\default.json` → `llm_profile_ref: "v1"` names the active LLM profile.
  - `profiles\v1.json` → **the active LLM profile the backend reads on STARTUP**. Fields:
    `model`, `base_url`, `api_key` (encrypted blob), `stream`, etc.
- **Failure mode seen 2026-07-27:** `v1.json` had `model` and `base_url` SWAPPED
  (`"model": "http://localhost:20129/v1"`, `"base_url": "openai/freellmapi/auto"`), so the client sent
  an empty/garbage model. The UI onboarding ("Set up your LLM") does NOT show this swap and can
  overwrite the file with broken values on every attempt.
- **Fix:** edit `profiles\v1.json` directly (do not rely on the UI):
  ```json
  { "model": "openai/oc/deepseek-v4-flash-free",
    "base_url": "http://localhost:20129/v1",
    "api_key": "<encrypted blob from profiles/deepseek-v4-flash-free.json>",
    "stream": true }
  ```
  Reuse the valid encrypted `api_key` from a sibling profile (e.g. `deepseek-v4-flash-free.json`) so you
  never retype the secret. Keep a `v1.json.fixed.bak` backup.
- **Backend caches the profile in memory** — after editing `v1.json`, RESTART Agent Canvas (kill the
  ingress + agent-server PIDs, confirm ports `:8000`/`:18000` free, relaunch with `PYTHONPATH=`). A
  live UI "save" is not enough; the running backend keeps old values until restarted.
- **GUI will not launch from a headless/background terminal** (no Windows desktop session). Have the
  USER open Agent Canvas from the Start menu / double-click; the agent terminal can only manage the
  proxy + profile files.

## Reusable artifacts
- Known-good Node proxy: `scripts/9router-bridge-proxy.js` (edit `UPSTREAM` / `LISTEN_PORT`).
- Verification recipe: `references/verify.md`.

## Verification (what "working" looks like)
- Hit the proxy `/v1/chat/completions` with model `openai/oc/...`.
- A **429 Rate limit** (or a real completion) from the upstream = SUCCESS: `openai/` was stripped and
  `oc/...` reached the router. The prefix problem is solved.
- A `litellm.BadRequestError: LLM Provider NOT provided` = STILL BROKEN (prefix not stripped / client
  hitting router directly).
- Proxy log prints `[bridge] rewrote model -> oc/deepseek-v4-flash-free` per request.
