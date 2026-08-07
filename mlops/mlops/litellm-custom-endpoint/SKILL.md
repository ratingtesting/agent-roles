---
name: litellm-custom-endpoint
description: Fix LiteLLM "Provider NOT provided" for custom endpoints.
---

# LiteLLM → Custom OpenAI-Compatible Endpoint

## Trigger
A tool wrapping LiteLLM (OpenHands / Agent Canvas, LangChain, etc.) rejects a model from your
self-hosted / custom OpenAI-compatible endpoint with:
`litellm.BadRequestError: LLM Provider NOT provided.`
and your endpoint routes by its own prefix (`oc/`, `opencode/`, `local/`, …) LiteLLM does not know.

## Root cause
LiteLLM requires a KNOWN provider prefix (`openai/`, `anthropic/`, …) or throws "LLM Provider NOT provided"
at validation (before any HTTP call). But the upstream endpoint routes by ITS OWN namespace and does
NOT recognize `openai/`. So `oc/deepseek-...` (LiteLLM rejects) and `openai/oc/deepseek-...`
(endpoint rejects `openai/`) both fail.

## Solution (two parts)

### 1. Tell LiteLLM the provider, hide the real prefix
Tool model field: `openai/<endpoint-model>`. Example: `openai/oc/deepseek-v4-flash-free`.
- LiteLLM sees `openai/` → uses OpenAI-compatible client → validation passes.
- LiteLLM forwards the name WITH `openai/` stripped to `api_base`.

Officially documented (LiteLLM "OpenAI-Compatible Endpoints"): "Put `openai/` in front of your model
name so litellm knows you're calling an openai `/chat/completions` endpoint; LiteLLM routes via the
openai client and forwards the rest of the name to `api_base`." Example: `openai/google/gemma` →
upstream receives `google/gemma`. (See `references/litellm-openai-compatible.md`.)

### 2. Strip `openai/` in a local proxy before it hits the endpoint
Tiny reverse proxy between tool and endpoint rewrites `openai/oc/deepseek-...` → `oc/deepseek-...`
in the request body, forwards to the real endpoint.
Tool → proxy(:LISTEN_PORT) → real endpoint(:UPSTREAM_PORT).
See `templates/proxy.js` (Node, streaming/SSE passthrough, strips only the leading `openai/`).

Tool config: Base URL = `http://localhost:LISTEN_PORT/v1`, Model = `openai/oc/deepseek-v4-flash-free`.
Other endpoint models: `openai/oc/<any-model>`.

### OpenHands / Agent Canvas specifics
- LLM profiles are NOT UI-only — JSON on disk:
  `~/.openhands/profiles/v1.json` (active; `agent-profiles/default.json` → `llm_profile_ref` points to it).
  UI onboarding can SCRAMBLE these (observed: `model` and `base_url` SWAPPED → `You passed model=` empty).
  If tool errors with empty model, edit `v1.json`:
  ```json
  { "model": "openai/oc/deepseek-v4-flash-free", "base_url": "http://localhost:LISTEN_PORT/v1", "api_key": "<key>", "stream": true }
  ```
  Backend caches profile in memory — RESTART the tool after editing.
- Proxy must run whenever the tool calls the LLM. Autostart it (Startup folder / systemd).

## Pitfalls
- **Windows git-bash path mangling (CRITICAL when launching proxy):** `node C:\Projects\...\proxy.js`
  from git-bash turns `\` into escape → path collapses → `MODULE_NOT_FOUND` → proxy dies exit 1.
  ALWAYS use forward slashes in bash: `node C:/Projects/lazy-unicorn/9router-proxy/proxy.js`.
  In `.bat`/cmd/PowerShell `\` is fine.
- Don't put the real endpoint URL in the tool's Base URL — point at the proxy, or LiteLLM sends
  `openai/oc/...` straight to the endpoint, which rejects `openai/`.
- **`429` from endpoint = PASS for routing:** means `openai/` stripped and real model reached it
  (free-tier limit). `litellm.BadRequestError` "Provider NOT provided" = prefix still wrong/missing.

## Verification
1. Proxy listening: `netstat -ano | findstr LISTEN_PORT` (Win) / `ss -ltnp | grep LISTEN_PORT` (Linux).
2. End-to-end: POST `http://localhost:LISTEN_PORT/v1/chat/completions` with
   `{"model":"openai/oc/...","messages":[...],"stream":false}` → `200 OK` + JSON; log shows `rewrote model -> oc/...`.
3. Raw-socket probe beats `curl` here (curl can misreport chunked SSE as `000`).
