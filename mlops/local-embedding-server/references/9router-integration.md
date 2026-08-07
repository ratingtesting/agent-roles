# 9router Integration — Custom Embedding Provider

> **⚠️ HARD RULE: NEVER edit 9router's SQLite DB.** All connectivity fixes go on the server (lightweight-embeddings), not on 9router. See SKILL.md → Proxy Compatibility.

## Database Schema (read-only reference)

9router stores providers in SQLite at `%APPDATA%/9router/db/data.sqlite`:

### `providerNodes` — provider type definitions

| Column | Value for lightweight-embeddings |
|--------|----------------------------------|
| id     | `custom-embedding-<uuid>` |
| type   | `custom-embedding`        |
| name   | `lightweight-embeddings`  |
| data   | `{"prefix":"lightweight-embeddings","baseUrl":"http://localhost:7860/v1"}` |

`type` MUST be `custom-embedding`. Using `openai-compatible` will route it to chat completions executor and fail.

### `providerConnections` — credentials & state

| Column | Value |
|--------|-------|
| id         | uuid |
| provider   | references `providerNodes.id` |
| authType   | `apikey` |
| name       | `lightweight-embeddings` |
| isActive   | `1` |
| data       | JSON with `apiKey`, `providerSpecificData` containing `prefix`, `baseUrl`, `connectionProxyEnabled` etc. |

## How 9router routes embedding requests

9router strips `/v1` from upstream base URLs. With `baseUrl=http://localhost:7860`, it sends requests to `http://localhost:7860/embeddings` (no `/v1`). The server must handle this path — see SKILL.md → Proxy Compatibility for the fix (mirror routes without `/v1`).

## Model Name

`lightweight-embeddings/bge-m3` — format: `{data.prefix}/{model_name}`.

Available models are fetched from `GET /v1/models` on the baseUrl.

## Testing

```bash
# Direct — should work
curl http://localhost:7860/v1/embeddings -H "Content-Type: application/json" -d '{"input":"test"}'

# Without /v1 — works after adding mirror routes
curl http://localhost:7860/embeddings -H "Content-Type: application/json" -d '{"input":"test"}'

# Via 9router
curl http://localhost:20128/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{"model":"lightweight-embeddings/bge-m3","input":"test"}'
```

## Debug flow when 9router returns 404

1. Check the lightweight-embeddings server logs — see what path 9router is hitting
2. If 9router hits `/embeddings` (no `/v1`), add mirror routes on the server
3. **DO NOT touch 9router's SQLite** — the user manages 9router
4. Update `SETUP_GUIDE.md` with any new server endpoints
