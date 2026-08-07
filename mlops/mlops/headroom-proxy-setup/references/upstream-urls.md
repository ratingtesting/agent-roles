# Upstream URLs + Backend Selection Reference

## KEY FINDING: Default Backend Breaks Custom Upstreams

Headroom's default `backend: "anthropic"` routes to Anthropic API **directly**.
For 9router (OpenAI-compatible) this fails with `No active credentials for provider: openai`.

**Fix**: Set `HEADROOM_BACKEND=anyllm-openai` + `HEADROOM_ANYLLM_PROVIDER=openai` + `OPENAI_API_KEY=<upstream_key>`.

## 9router — Port 8787

```bash
export OPENAI_TARGET_API_URL="http://localhost:20128/v1"
export ANTHROPIC_TARGET_API_URL="http://localhost:20128/v1"
export HEADROOM_BACKEND=anyllm-openai
export HEADROOM_ANYLLM_PROVIDER=openai
export OPENAI_API_KEY=$API_9ROUTER_KEY
headroom.exe proxy --port 8787
```

**Dependencies** (any-llm-sdk for Python 3.14):
```bash
C:\Python314\python.exe -m pip install "any-llm-sdk[openai]"
```

Verify import works:
```bash
PYTHONPATH="C:\Users\Unicorn\AppData\Roaming\Python\Python314\site-packages" \
  C:\Python314\python.exe -c "import any_llm; print('ok')"
```

## agentrouter — Port 8788

```bash
export OPENAI_TARGET_API_URL="https://agentrouter.org/v1"
export ANTHROPIC_TARGET_API_URL="https://agentrouter.org"
export HEADROOM_BACKEND=anyllm-openai
export HEADROOM_ANYLLM_PROVIDER=openai
export OPENAI_API_KEY=$API_AGENTROUTER_KEY
headroom.exe proxy --port 8788
```

Note the different paths: OpenAI-style requests go to `/v1`, Anthropic-style
requests go to the root. This is because agentrouter uses different path
structures per protocol.

### AgentRouter 401 `unauthorized_client_error`

If both OpenAI and Anthropic format requests return:
```json
{"error":{"message":"unauthorized client detected, contact support for assistance at https://discord.gg/aYq5B4RW3","message":"UNAUTHENTICATED","success":false,"type":"unauthorized_client_error"}}
```

This is **not a headroom bug** — hitting AgentRouter directly produces the same response.
Headroom correctly forwards the upstream rejection. Fix: update `API_AGENTROUTER_KEY` in `.env`.

## When `backend: "anthropic"` (default) works

Only when the upstream IS Anthropic's API (api.anthropic.com) OR an Anthropic-compatible proxy that accepts `x-api-key` auth. 9router is OpenAI-compatible, not Anthropic-compatible — hence the need for `anyllm-openai`.

## Model Names for 9router

9router returns a list of models via `/v1/models` that includes:
- `SuperCombo_1M`, `SuperCombo_256k_100`, `SuperCombo_131k_66-67`, etc. (composite)
- `kr/claude-opus-4.8`, `kr/claude-sonnet-5`, etc. (kr/* namespace)
- `openrouter/...` (prefixed OpenRouter models)
- `freellmapi/...` (prefixed freellmapi models)
- `agentrouter-claude/...` (AgentRouter Claude models)
- `cf/...` (Cloudflare Workers AI models)
- `qd/...` (other namespaces)

**Use exact model IDs from the list**. Requesting an unknown model returns
`{"error":{"message":"No active credentials for provider: openai","type":"invalid_request_error","code":"model_not_found"}}`
— this error originates from 9router itself, not from headroom.

## Settings GUI (Alternative to env vars)

Instead of env vars, use the web UI:
1. Start headroom: `headroom.exe proxy --port 8787`
2. Open `http://127.0.0.1:8787/dashboard/settings`
3. Set upstream URLs in the **Endpoints** section
4. Settings persist to `~/.headroom/settings.json`

**Note**: Backend selection may not be available through the GUI — use env vars for `HEADROOM_BACKEND`.

## Hermes Integration

### Provider Config (`~/.hermes/config.yaml`)

When using Headroom as the main provider for Hermes:

```yaml
custom_providers:
  - name: 9router
    base_url: http://127.0.0.1:8787/v1
    key_env: API_9ROUTER_KEY
    api_mode: chat_completions
  - name: agentrouter-openai
    base_url: http://127.0.0.1:8788/v1
    key_env: API_AGENTROUTER_KEY
    api_mode: chat_completions
    discover_models: false
  - name: agentrouter-claude
    base_url: http://127.0.0.1:8788
    key_env: API_AGENTROUTER_KEY
    api_mode: anthropic_messages
    discover_models: false
```

Headroom forwards `/v1/models` — no direct-provider bypass needed.
Use `discover_models: false` for providers that reject unauthenticated model listing (agentrouter does).

### PYTHONPATH Requirement

When Headroom runs under Python314 (non-default Python install), set PYTHONPATH:

```bash
PYTHONPATH="C:\Users\Unicorn\AppData\Roaming\Python\Python314\site-packages"
```

Without this, `headroom.exe` may fail with `ModuleNotFoundError: No module named 'headroom'`.

## Headroom Version

```
Python 3.14.6
headroom 0.31.0
uvicorn 0.51.0
any-llm-sdk 1.21.0
```

## Verify health

```bash
# After waiting 60s for startup
curl -s http://127.0.0.1:8787/health
```

Check that `backend` shows `anyllm-openai` in the response:
```json
{"config": {"backend": "anyllm-openai", ...}}
```

If `"backend": "anthropic"` — backend env vars not propagated, requests will fail with `No active credentials`.