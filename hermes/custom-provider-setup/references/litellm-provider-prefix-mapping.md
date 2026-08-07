# LiteLLM Provider Prefix Mapping (Third-Party Tools)

## Problem

Tools that embed LiteLLM internally — such as **OpenHands** (via OpenHands SDK / Agent Canvas Desktop App) — determine the LLM provider by the **prefix** of the model name:

- `openai/...` → OpenAI-compatible provider
- `anthropic/...` → Anthropic provider
- `huggingface/...` → HuggingFace provider
- `oc/...` → ❌ UNKNOWN — LiteLLM rejects with `LLM Provider NOT provided`

This is a problem when your router (e.g. 9router) exposes models **with its own provider prefixes** (`oc/deepseek-v4-flash-free`, `kr/claude-sonnet-5`, `freellmapi/glm-5`), because LiteLLM doesn't know the `oc/`, `kr/`, or `freellmapi/` prefixes.

## Solution 1: Proxy Bridge (Recommended)

**Important caveat:** LiteLLM does **NOT** always strip the `openai/` prefix before sending the model name to the upstream API. When tested with 9router, the full model string `openai/oc/deepseek-v4-flash-free` was sent as-is, causing 9router to fail with `"No active credentials for provider: openai"`.

The reliable solution is a **local proxy** that intercepts LiteLLM's requests, strips the `openai/` prefix, and forwards to the actual router:

```
OpenHands/LiteLLM → Proxy (:20129) → 9router (:20128)
   model: openai/oc/...        model: oc/...
```

### Architecture

| Component | Port | Purpose |
|-----------|------|---------|
| **9router** | `:20128` | Actual LLM router with provider prefixes |
| **Bridge Proxy** | `:20129` | Strips `openai/` prefix, forwards to 9router |
| **Agent Canvas / OpenHands** | `:8000` | UI that embeds LiteLLM, sends to proxy |

### Configuration in Agent Canvas

| UI Field | Value |
|----------|-------|
| **Base URL** | `http://localhost:20129/v1` (proxy endpoint) |
| **Custom Model** | `openai/oc/deepseek-v4-flash-free` |
| **API Key** | Your 9router API key |

The proxy is at `scripts/9router-litellm-proxy.js` under this skill.

### Proxy Features

- Strips `openai/` prefix from model name before forwarding to 9router
- Strips trailing SSE termination markers (`data: [DONE]\n\n`) that 9router appends even to non-streaming responses (would otherwise break JSON parsing)
- Recalculates Content-Length headers after modifications
- Returns proper HTTP error codes on upstream failures

### Starting the Proxy

```bash
node <skill-dir>/scripts/9router-litellm-proxy.js
```

For permanent operation, add to a Windows startup script or run as a background process in Hermes.

### Proxy Behaviour

| Incoming Model | Forwarded Model | Result |
|---|---|---|
| `openai/oc/deepseek-v4-flash-free` | `oc/deepseek-v4-flash-free` | ✅ 9router routes via `oc` provider |
| `openai/kr/claude-sonnet-5` | `kr/claude-sonnet-5` | ✅ 9router routes via `kr` provider |
| `openai/freellmapi/glm-5` | `freellmapi/glm-5` | ✅ 9router routes via `freellmapi` provider |

## Solution 2: Prefix Nesting (Only if LiteLLM strips the prefix)

Some LiteLLM versions DO strip the known prefix. In that case, nest the router's provider prefix inside `openai/`:

```text
Known prefix / Actual provider prefix / Model name
      ↓                    ↓                    ↓
  openai/                 oc/            deepseek-v4-flash-free
```

**This only works if LiteLLM sends the model WITHOUT the `openai/` prefix.** Test with:

```bash
# Send model WITH openai/ prefix directly to the router
curl -s -X POST http://localhost:20128/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"openai/oc/deepseek-v4-flash-free","messages":[{"role":"user","content":"hi"}],"max_tokens":5}'
```

If this returns `"No active credentials for provider: openai"` — the router receives the prefix as-is, and only Solution 1 (proxy bridge) will work.

If it returns a valid completion — LiteLLM strips the prefix, and Solution 2 (nesting only) is sufficient.

### Verification

```bash
# Test that the actual model name works against 9router directly
curl -s -X POST http://localhost:20128/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_9ROUTER_KEY" \
  -d '{"model":"oc/deepseek-v4-flash-free","messages":[{"role":"user","content":"hi"}],"max_tokens":10}'

# Test through the proxy
curl -s -X POST http://localhost:20129/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_9ROUTER_KEY" \
  -d '{"model":"openai/oc/deepseek-v4-flash-free","messages":[{"role":"user","content":"hi"}],"max_tokens":10}'
```

## Known Affected Tools

- **OpenHands** (OpenHands SDK v1.37.0+) via **Agent Canvas Desktop App**
- Any tool that embeds LiteLLM for LLM routing and exposes a "Custom Model" / "Base URL" field
- Tools where the Base URL points to a router/proxy, not the final provider

## Pitfalls

- **Don't use the router's own prefix directly** (e.g. `oc/model`). LiteLLM rejects unknown prefixes with `BadRequestError: LLM Provider NOT provided`.
- **Don't assume LiteLLM strips the prefix.** Test with a direct curl to the router using the `openai/prefixed-model` format. If the router returns an error, LiteLLM is NOT stripping the prefix and you need the proxy.
- **9router appends `data: [DONE]\n\n`** to all responses, even non-streaming ones. The proxy handles this, but direct LiteLLM → 9router connections may fail on JSON parsing. Ensure streaming is disabled in the tool's settings if using direct connection.
- **The API Key field** in the tool is the router's API key, not a session/generated key. Agent Canvas Desktop App may auto-fill a session key — overwrite it with the real router key.
- **Restart the tool** after saving settings if it hangs on a previous config. Agent Canvas's onborading wizard may reset on each reload if the LLM config is invalid.
