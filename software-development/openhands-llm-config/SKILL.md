---
name: openhands-llm-config
description: Configure OpenHands LLM to a custom router endpoint.
---

# OpenHands / Agent Canvas LLM backend config (LiteLLM)

OpenHands (and the Agent Canvas desktop GUI built on it) routes ALL LLM calls through **LiteLLM**, which
requires a known provider prefix on the model name. This collides with custom routers that own their own
model namespace. The fix is a small local proxy that strips the LiteLLM prefix before the request reaches
the router.

## When this skill applies
- Error: `litellm.BadRequestError: LLM Provider NOT provided. Pass in the LLM provider you are trying to call. You passed model=<x>`
- Error variant: `You passed model=` (empty) — the active profile file is corrupted (see Pitfall 1).
- You are wiring OpenHands to 9router / freellmapi / any `/v1` OpenAI-compatible server that is NOT a stock LiteLLM provider.
- Agent Canvas shows "Set up your LLM" onboarding but the connection never sticks.

## Core rule (LiteLLM)
LiteLLM validates the model string client-side. Without a known prefix (`openai/`, `anthropic/`, …) it
throws before any HTTP call. So the model OpenHands sends MUST carry `openai/`.

Official LiteLLM backing (docs "OpenAI-Compatible Endpoints"):
> Put `openai/` in front of your model name so litellm knows you're calling an openai `/chat/completions`
> endpoint; LiteLLM routes via the openai client and forwards the rest of the name to `api_base`.
> Example: `model: openai/google/gemma` → forwards `google/gemma` to the custom base.

So `openai/` is STRIPPED by LiteLLM and only the remainder is sent on the wire to `api_base`.

## The collision
- Router (e.g. 9router) owns its own namespace: `oc/deepseek-v4-flash-free`, `opencode/...`. It does NOT know `openai/`.
- `oc/deepseek-v4-flash-free` → LiteLLM rejects (no prefix).
- `openai/oc/deepseek-v4-flash-free` sent directly to the router → router rejects `openai/`.
- Resolution: a local proxy sits between OpenHands and the router. OpenHands sends `openai/oc/...` (LiteLLM happy), the proxy strips `openai/` and forwards `oc/...` to the router.

## Working pattern (verified)
```
OpenHands (LiteLLM) ──model: openai/oc/deepseek-v4-flash-free──▶ PROXY :20129 ──strips openai/──▶ 9router :20128
                                                                   Base URL: http://localhost:20129/v1
```
- OpenHands Base URL = `http://localhost:20129/v1` (the PROXY, not the router directly).
- OpenHands Custom Model = `openai/<router-namespace>/<model>` (e.g. `openai/oc/deepseek-v4-flash-free`).
- API Key = the router's key.

Generic, reusable proxy: `templates/proxy-strip-prefix.js` (streaming passthrough, configurable prefix/ports).

## Pitfall 1 — config lives in a FILE, not the UI (CRITICAL)
OpenHands stores LLM settings in JSON on disk, NOT in the onboarding UI:
```
~/.openhands/
├── agent-profiles/default.json   # active agent; field "llm_profile_ref": "v1"
└── profiles/
    ├── v1.json                    # ← ACTIVE LLM profile (read by backend at startup)
    └── <name>.json                # saved copies
```
- The UI onboarding ("Set up your LLM") can OVERWRITE `v1.json` and HIDE corruption. Seen in the wild:
  `model` and `base_url` fields were SWAPPED (`"model": "http://localhost:20129/v1"`,
  `"base_url": "openai/freellmapi/auto"`) → error `You passed model=` (empty/garbage).
- Fix: edit `v1.json` directly. Set `"model"`, `"base_url"`, keep the existing (encrypted) `"api_key"`.
  Working shape:
  ```json
  { "model": "openai/oc/deepseek-v4-flash-free",
    "base_url": "http://localhost:20129/v1",
    "api_key": "<encrypted, reuse from a known-good profile .json>",
    "stream": true }
  ```
- After editing, RESTART Agent Canvas — the backend caches the profile in memory and will keep sending
  the old (corrupt) values until restarted.

## Pitfall 2 — Agent Canvas is a GUI; it won't start from the agent terminal
Agent Canvas is an Electron GUI. It does NOT start reliably from an agent's background terminal (no
interactive desktop session there). The USER must launch it (double-click / Start menu). A background
process the agent spawns is killed when the agent command returns, so long-lived servers (the proxy)
must auto-start via the Windows Startup folder (.lnk) or a scheduled task — not be launched by the agent.

## Pitfall 3 — proxy must be streaming passthrough
OpenHands streams tokens via SSE. A proxy that BUFFERS the whole response before sending will break the
UI stream. The proxy must `pipe()` the upstream response through (chunked). See `templates/proxy-strip-prefix.js`.

## Verification (scripts/verify-proxy.js)
- `node --check proxy.js` (syntax).
- Unit-test the strip logic: `openai/oc/x` → `oc/x`; `oc/x` → `oc/x` (untouched); other prefixes untouched.
- Live: confirm `netstat -ano | grep <port>` LISTEN; send a test chat completion; check the proxy log
  shows `rewrote model -> <router>/<model>` and the router responds (even HTTP 429 proves routing worked).

## Reference
`references/9router-openhands.md` — condensed knowledge bank: exact working config, v1.json structure,
LiteLLM doc excerpt, and the real error transcripts from the 2026-07-27 session.
