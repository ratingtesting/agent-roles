# Named Custom Providers — Field Reference

Full reference for the `custom_providers:` section in `~/.hermes/config.yaml`.

---

## Syntax

```yaml
custom_providers:
  - name: <provider-name>          # canonical id for /model
    base_url: <endpoint-url>       # e.g. http://localhost:20128/v1
    key_env: <ENV_VAR>             # env var name for API key
    api_mode: <api-mode>           # optional: chat_completions | anthropic_messages | codex_responses
```

---

## Field Details

### `name` (required)
Used in the triple syntax `/model custom:<name>:<model-id>`. Lowercase, hyphens allowed. Must be unique.

### `base_url` (required)
Full endpoint URL. **No trailing slash.**
- OpenAI-compatible: usually ends in `/v1` (e.g. `http://localhost:11434/v1`)
- Anthropic Messages: NO `/v1` (e.g. `https://agentrouter.org` or `https://api.anthropic.com`)

### `key_env` (required)
Name of the environment variable in `~/.hermes/.env`. Do NOT prefix with `$`, `%`, or `process.env.`.

### `api_mode` (optional, defaults to `chat_completions`)
| Value | Protocol | Example |
|-------|----------|---------|
| `chat_completions` | OpenAI `/v1/chat/completions` | 9router, vLLM, Ollama |
| `anthropic_messages` | Anthropic Messages API (POST) | AgentRouter Claude, Anthropic proxy |
| `codex_responses` | OpenAI Codex Responses API | xAI Grok via OpenAI compat |

---

## Complete Examples

### 4-endpoint multi-router setup

```yaml
custom_providers:
  - name: 9router
    base_url: http://localhost:20128/v1
    key_env: API_9ROUTER_KEY
    api_mode: chat_completions
  - name: freellmapi
    base_url: http://127.0.0.1:31415/v1
    key_env: API_FREELLMAPI_KEY
    api_mode: chat_completions
  - name: agentrouter-completions
    base_url: https://agentrouter.org/v1
    key_env: API_AGENTROUTER_KEY
    api_mode: chat_completions
  - name: agentrouter-messages
    base_url: https://agentrouter.org
    key_env: API_AGENTROUTER_KEY
    api_mode: anthropic_messages
```

### Local + remote + Anthropic proxy

```yaml
custom_providers:
  - name: local
    base_url: http://localhost:8080/v1
    key_env: LOCAL_API_KEY
    api_mode: chat_completions
  - name: gpu-server
    base_url: https://gpu.internal.corp/v1
    key_env: CORP_API_KEY
    api_mode: chat_completions
  - name: claude-proxy
    base_url: https://proxy.example.com/anthropic
    key_env: ANTHROPIC_PROXY_KEY
    api_mode: anthropic_messages
```

---

## Switching Commands

```text
/model custom:9router:supercombo
/model custom:freellmapi:auto
/model custom:agentrouter-completions:gpt-5.5
/model custom:agentrouter-messages:claude-opus-4-8
```

---

## Model Discovery

Named custom providers auto-fetch models from `{base_url}/models` (OpenAI-compatible) on first use. The results are cached.

For Anthropic Messages endpoints (`api_mode: anthropic_messages`), there is no `/models` endpoint — model discovery relies on the `fallback_models` tuple in Python plugin profile, or the models you manually specify.

---

## Per-Provider extra_body

```yaml
custom_providers:
  - name: gemma-local
    base_url: http://localhost:8080/v1
    key_env: GEMMA_API_KEY
    extra_body:
      enable_thinking: true
```

---

## Key Differences from TypeScript Plugin Format

| | TypeScript extension.ts (AgentRouter format) | Named Custom Providers (Hermes format) |
|--|-----------------------------------------------|----------------------------------------|
| Location | `~/.hermes/plugins/<name>/extension.ts` | `~/.hermes/config.yaml` |
| Loading | Plugin system (per-process) | Config-based (per-process) |
| Model list | Hardcoded in `models[]` array | Auto-fetched from `/v1/models` |
| Multiple per user | Unclear/experimental | Yes — unlimited `- name:` entries |
| Hermes official | ❌ Documented by AgentRouter, NOT Hermes | ✅ Hermes official docs |
