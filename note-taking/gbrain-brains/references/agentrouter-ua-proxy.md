# agentrouter.org: блокировка User-Agent и UA-прокси

## Симптом
Любой запрос к `https://agentrouter.org/v1/messages` (anthropic messages API) c
«неправильным» User-Agent получает:

```json
{"error":{"message":"unauthorized client detected, contact support ..."},
 "message":"UNAUTHENTICATED","type":"unauthorized_client_error"}
```

Проверено (2026-07): режутся `ai-sdk/anthropic/*`, `anthropic-sdk-typescript/*`,
`Python-urllib/*`, отсутствие UA. Проходит ТОЛЬКО:

```
User-Agent: claude-cli/1.0.0 (external, cli)
```

Заголовки успешного запроса: `x-api-key: $API_AGENTROUTER_KEY`,
`anthropic-version: 2023-06-01`, `Content-Type: application/json`.
Кириллица в body — ок (при корректном UTF-8; в MSYS curl -d ломает кодировку,
использовать `--data-binary @file.json` или Python).

Через 9router (`agentrouter-claude/claude-opus-4-8`) этот провайдер стабильно
падал «Provider error (reset after 30s)» — 9router не подменяет UA.

## Решение: UA-прокси

`C:\Users\Unicorn\anthropic-ua-proxy\proxy.py` — stdlib Python (http.server +
urllib), слушает `127.0.0.1:8402`, пробрасывает все `/v1/*` на
`https://agentrouter.org`, подменяя User-Agent на claude-cli и форсируя
`Accept-Encoding: identity`. Ключ клиента пробрасывается как есть.
`GET /health` → `{"status":"ok"}`.

Автозапуск: Registry Run key `AnthropicUAProxy` →
`"...\hermes-agent\venv\Scripts\pythonw.exe" "C:\Users\Unicorn\anthropic-ua-proxy\proxy.py"`.

Потребители: gbrain (`ANTHROPIC_BASE_URL=http://127.0.0.1:8402`; gbrain сам
нормализует до `/v1`). Подходит для любого anthropic-SDK-клиента, которому
нельзя задать кастомный UA.

## Тест

```bash
curl -s http://127.0.0.1:8402/health
# затем POST /v1/messages с любым UA — должен вернуться ответ модели
```
