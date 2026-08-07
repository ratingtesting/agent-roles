# 9router ↔ OpenHands (LiteLLM) — condensed knowledge bank

Source session: 2026-07-27, lazy-unicorn project, Windows 11, Agent Canvas v1.6.1 (OpenHands SDK v1.37.0).

## Working config (verified end-to-end)
```
OpenHands (LiteLLM) ──model: openai/oc/deepseek-v4-flash-free──▶ PROXY :20129 ──strips openai/──▶ 9router :20128
```
- OpenHands Base URL: `http://localhost:20129/v1`  (the proxy, NOT 9router directly)
- OpenHands Custom Model: `openai/oc/deepseek-v4-flash-free`
- API Key: 9router key (env `API_9ROUTER_KEY`; in OpenHands UI paste the literal key, e.g. `sk-913…1473`)
- Other models: `openai/oc/<model>` (e.g. `openai/oc/mimo-v2.5-free`)

9router itself: OpenAI-compatible `/v1`, listens on `:20128`, owns namespace `oc/` (provider Opencode).
`curl -X POST localhost:20128/v1/chat/completions -H "Authorization: Bearer <key>" -d '{"model":"oc/deepseek-v4-flash-free",...}'`
→ succeeds (300ms in test). 9router accepts ANY model string and routes via its configured provider.

## LiteLLM doc excerpt (official, "OpenAI-Compatible Endpoints")
> Put `openai/` in front of your model name so litellm knows you're calling an openai `/chat/completions`
> endpoint; LiteLLM routes via the openai client and forwards the rest of the name to `api_base`.
> Example: `model: openai/google/gemma` → forwards `google/gemma` to the custom base.
Conclusion: LiteLLM strips ONLY the leading `openai/` token; the remainder is the wire model name.

## Error transcripts seen
1. `litellm.BadRequestError: LLM Provider NOT provided. ... You passed model=oc/deepseek-v4-flash-free`
   → model had no `openai/` prefix. Fix: add prefix (via proxy).
2. `You passed model=openai/oc/deepseek-v4-flash-free` (router rejected) — happened only when Base URL
   pointed at 9router directly (no proxy to strip). Fix: point Base URL at the proxy.
3. `You passed model=` (EMPTY) — active profile `v1.json` had `model` and `base_url` SWAPPED. The UI
   onboarding hid this. Fix: edit `v1.json` directly (see below).

## ~/.openhands profile layout
```
C:\Users\Unicorn\.openhands\
├── agent-profiles\default.json      # "llm_profile_ref": "v1"
└── profiles\
    ├── v1.json                       # ACTIVE — read by backend at startup
    ├── 9Router.json                  # saved copy (oc/mimo-v2.5-free)
    └── deepseek-v4-flash-free.json   # saved copy (oc/deepseek-v4-flash-free, valid api_key)
```
Working `v1.json`:
```json
{
  "model": "openai/oc/deepseek-v4-flash-free",
  "base_url": "http://localhost:20129/v1",
  "api_key": "<encrypted, reuse from deepseek-v4-flash-free.json>",
  "stream": true
}
```
After editing `v1.json` you MUST restart Agent Canvas — backend caches the profile in memory.

## Proxy auto-start (Windows)
- Startup shortcut: `C:\Users\Unicorn\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\9router-proxy.lnk`
  → runs `C:\Projects\lazy-unicorn\9router-proxy\9router-proxy.bat` (guards against double-launch).
- Scheduled task `NineRouterProxy` (ONLOGON) as a duplicate.
- NOTE: agent terminal (Hermes) cannot keep the proxy alive — background procs are killed on command
  return. The USER must launch Agent Canvas + proxy from an interactive desktop session.

## Why a proxy (not just openai/ in model name)
Sending `openai/oc/...` directly to 9router fails: 9router sees the `openai/` prefix and has no such
provider. The proxy is the minimal seam that satisfies LiteLLM's prefix requirement while speaking 9router's
native `oc/` namespace on the wire. Alternative (not used): register a custom OpenAI-compatible provider in
LiteLLM via `litellm.register_model` / a custom LLM handler — heavier, requires code in OpenHands SDK.
