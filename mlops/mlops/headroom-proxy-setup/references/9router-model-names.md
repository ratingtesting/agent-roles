# 9router Model Names Reference

## The Error: "No active credentials for provider: openai"

This error **originates from 9router itself**, not from headroom. It means:
1. Headroom correctly forwarded the request to 9router
2. 9router received the request but didn't recognize the model
3. 9router fell back to its default OpenAI provider routing which requires credentials you don't have

## Working Model IDs (from 9router's /v1/models)

```
SuperCombo_1M
SuperCombo_256k_100
SuperCombo_131k_66-67
SuperCombo_256k_66-67
SuperCombo-Architect
SuperCombo-Orchestrator
kr/claude-opus-4.8
kr/claude-opus-4.8-thinking
kr/claude-opus-4.8-agentic
kr/claude-opus-4.8-thinking-agentic
kr/claude-opus-4.7
... (more kr/* models)
kr/claude-sonnet-5
kr/claude-sonnet-4.5
kr/claude-haiku-4.5
kr/deepseek-3.2
kr/qwen3-coder-next
kr/glm-5
kr/MiniMax-M2.5
kr/gpt-5.6-sol
kr/gpt-5.6-terra
kr/gpt-5.6-luna
... (more)
qd/ultimate
openrouter/google/lyria-3-pro-preview
openrouter/nvidia/nemotron-3-ultra-550b-a55b:free
... (more openrouter/*)
freellmapi/kimi-k2.6
freellmapi/kimi-k2.7-code
freellmapi/qwen3-coder-480b
... (more freellmapi/*)
agentrouter-claude/claude-opus-4-8
```

## Common Mistakes

| Request Model | Result | Why |
|--------------|--------|-----|
| `SuperCombo_256k` | ❌ 404 `model_not_found` | Not in 9router's list — use `SuperCombo_256k_100` |
| `SuperCombo_1M` | ✅ Works | Exact match |
| `gpt-4o` | ❌ `model_not_found` | Not a 9router model ID |
| `kr/claude-opus-4.8` | ✅ Works | Exact from list |
| `claude-opus-4-8` | ❌ 404 | Missing `kr/` prefix |

## How to List Available Models

```bash
# Through headroom proxy (port 8787)
curl -s -H "Authorization: Bearer $API_9ROUTER_KEY" \
  http://127.0.0.1:8787/v1/models | jq '.data[].id'

# Direct to 9router (port 20128)
curl -s -H "Authorization: Bearer $API_9ROUTER_KEY" \
  http://localhost:20128/v1/models | jq '.data[].id'
```

## Testing a Working Request

```bash
# Use a model ID from the actual list
curl -sv -X POST http://127.0.0.1:8787/v1/chat/completions \
  -H "Authorization: Bearer $API_9ROUTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"SuperCombo_256k_100","max_tokens":10,"messages":[{"role":"user","content":"hi"}]}'
```

## Key Insight

**Headroom is working correctly** — it passes `/v1/models` and `/v1/chat/completions` through without modification. The error is purely a 9router-side model name mismatch. Always use exact model IDs from 9router's `/v1/models` endpoint.

---

## New Session Insights (2026-07-17)

### SuperCombo Model Family

The `SuperCombo_*` models are 9router's **internal composite models** that route requests to multiple providers. They're not prefixed because they're 9router-native:

- `SuperCombo_256k_100` — most general-purpose, 256k context, 100% routing
- `SuperCombo_1M` — 1M context composite
- `SuperCombo_131k_66-67` — 131k context, ~66% routing
- `SuperCombo_256k_66-67` — 256k context, ~66% routing
- `SuperCombo-Architect` / `SuperCombo-Orchestrator` — persona-tuned composites

**Use `SuperCombo_256k_100` as default** for Hermes `model.default.model` — it's the most general-purpose composite.

### Provider-Prefixed Models

| Prefix | Provider | Notes |
|--------|----------|-------|
| `kr/` | Kiro (Anthropic-compatible) | Many Claude variants, thinking/agentic modes |
| `openrouter/` | OpenRouter | Free and paid models |
| `freellmapi/` | FreeLLMAPI | Free models, some with reasoning |
| `cf/` | Cloudflare Workers AI | Meta, Mistral, Moonshot, Qwen, etc. |
| `agentrouter-claude/` | AgentRouter (Anthropic) | Only works via 8788 proxy with auth |

### litellm Routing Logic

9router uses **litellm** internally. When it receives a model name:
1. Tries to match against known provider patterns (prefixes like `kr/`, `openrouter/`, etc.)
2. **Falls back to `openai` provider** if no pattern matches
3. The `openai` provider requires `OPENAI_API_KEY` credentials → fails with "No active credentials for provider: openai"

**This is why `SuperCombo_256k` fails** — it doesn't match any known pattern, so litellm defaults to openai provider. But `SuperCombo_256k_100` IS in 9router's model registry, so it routes correctly.

**Rule**: Always use exact model IDs from `/v1/models`. Never guess or assume shorter names work.