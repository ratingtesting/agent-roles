# AgentRouter Dual-API Setup (Named Custom Providers)

AgentRouter exposes two different API formats on the same account — requires **two named custom providers** in `config.yaml`.

---

## Config

```yaml
custom_providers:
  - name: agentrouter-messages
    base_url: https://agentrouter.org       # NO /v1
    key_env: API_AGENTROUTER_KEY
    api_mode: anthropic_messages            # Claude format
  - name: agentrouter-completions
    base_url: https://agentrouter.org/v1    # WITH /v1
    key_env: API_AGENTROUTER_KEY
    api_mode: chat_completions              # OpenAI format
```

## Env var

```env
API_AGENTROUTER_KEY=sk-***
```

## Switching

```
/model custom:agentrouter-messages:claude-opus-4-8
/model custom:agentrouter-completions:gpt-5.5
```

## Key Differences

| | Messages | Completions |
|--|----------|-------------|
| **api_mode** | `anthropic_messages` | `chat_completions` |
| **base_url** | `https://agentrouter.org` | `https://agentrouter.org/v1` |
| **Auth** | `x-api-key` header | `Authorization: Bearer` |
| **Models** | claude-opus-4-6/7/8 | gpt-5.5, glm-5.2 |

## Why Two Entries?

A single entry exposes one API format. AgentRouter serves two incompatible formats on different base URLs, so two entries are needed — one per `api_mode`.
