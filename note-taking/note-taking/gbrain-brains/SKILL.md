---
name: gbrain-brains
description: "GBrain memory: per-profile brains, config, pitfalls."
version: 1.0.0
---

# GBrain — изолированные мозги на профиль Hermes (Windows)

Утверждённая схема Петра (2026-07): один глобальный `gbrain` CLI (bun), отдельный
PGLite-мозг на каждый профиль Hermes в `~/brains/<имя>` (default→personal, app, marketplace).
Источник истины по конфигурации: `C:\Projects\lazy-unicorn\SETUP_GUIDE.md` §6.

## Быстрый доступ

```bash
bash ~/brains/gb.sh <brain> <gbrain-cmd...>   # напр.: gb.sh app think "вопрос"
```
`gb.sh` сам ставит GBRAIN_HOME + ключи (9router/agentrouter) + base URLs.

## Эталонная конфигурация (шаблон всех мозгов)

| Роль | Значение |
|---|---|
| chat / models.default | `openai:oc/nemotron-3-ultra-free` (через OPENAI_BASE_URL=http://localhost:20128/v1 = 9router) |
| embeddings | `openai:lightweight-embeddings/bge-m3`, dimensions **1024** |
| rerank | `llama-server-reranker:ms-marco-MultiBERT-L-12`, base URL `http://127.0.0.1:8000/v1` (FlashRank — нативно совместим, адаптер НЕ нужен) |
| models.think / expansion_model | `anthropic:claude-opus-4-8` через UA-прокси `ANTHROPIC_BASE_URL=http://127.0.0.1:8402` |
| search.mode | `balanced` |

## Ключевые уроки / питфоллы

1. **agentrouter.org режет все User-Agent кроме `claude-cli/...`** («unauthorized client»).
   gbrain/AI SDK не умеет кастомные заголовки на native-anthropic пути → нужен
   UA-прокси на :8402 (stdlib Python, `C:\Users\Unicorn\anthropic-ua-proxy\proxy.py`,
   автозапуск Registry Run `AnthropicUAProxy`). См. `references/agentrouter-ua-proxy.md`.
2. **`gbrain think` берёт модель из `models.think`**, НЕ из `chat_model`. Без установки
   падает на дефолтный anthropic:claude-opus-4-7. Ставить оба: `models.default` и `models.think`.
3. **nemotron через 9router на длинных structured-ответах** иногда отдаёт multi-chunk
   JSON → gbrain «Invalid JSON response». Для think использовать opus через прокси;
   nemotron ок для chat/dream. `oc/hy3-free` не существует; `oc/mimo-v2.5-free` нестабилен (500-ки).
4. **Баг #1917**: `gbrain skillpack ...` не находит корень при bun-установке.
   Фикс: `cd ~/.bun/install/global/node_modules/gbrain` перед командой.
5. **MSYS искажает пути в bun-CLI**: `--workspace ~/brains/x` может создать `/c/c/Users/...`.
   После scaffold проверять, куда реально легли файлы (`find /c/c -maxdepth 6 ...`), переносить.
6. **PGLite database_path абсолютный** — после переноса/rename папки мозга поправить
   `database_path` в `.gbrain/config.json`, иначе БД продолжит писаться по старому пути.
7. **Кириллица через curl в MSYS ломается** (encoding) — тесты LLM API писать
   Python-скриптом (urllib, ensure_ascii=False, utf-8), не inline curl -d.
8. **9router может отвечать SSE/конкатенированным JSON** даже при stream:false —
   парсер тестов должен уметь склеивать чанки.
9. Проверка провайдеров: `gbrain models doctor` (реальные probe всех touchpoints).
   **Ложная тревога**: chat-probe имеет таймаут ~5с, а 9router после простоя отвечает 5–25с →
   «unknown» для рабочих моделей. Истина — боевой цикл capture→search→think.
   Аналогично health-curl к :20128 с `-m 5` даёт ложный отказ — повторять с `-m 15`.
10. **`gbrain config get` может зависать** (db plane) — не звать в цикле по многим ключам;
   читать `.gbrain/config.json` напрямую python-ом.
11. **Кодовое-слово-тест** проверяет всю цепочку одним заходом:
   `capture "…кодовое слово изумруд-42…"` → `think "какое кодовое слово?"` → ответ с цитатой
   [inbox/...]; затем search того же слова в чужом мозге → «No results» (изоляция).

## Агенты используют мозг по умолчанию (схема 1+2, без MCP)

Само существование мозга НЕ заставляет агентов им пользоваться — нужно правило в двух слоях:
- **Память каждого профиля** (`~/AppData/Local/hermes/profiles/<p>/memories/MEMORY.md`;
  default — основная память): «вопросы о прошлом → `gb.sh <мозг> search`; ценные новые
  факты/решения → `gb.sh <мозг> capture`». Дописывать `printf ... >> MEMORY.md` с `§`.
- **AGENTS.md**: корень монорепы (раздел «GBrain — использовать по умолчанию») +
  `app/AGENTS.md` + `marketplace/AGENTS.md` — так правило видят и Claude Code/Codex.
- Скиллы gbrain (43) — НЕ Hermes-скиллы: агенты открывают `~/brains/skills-workspace/skills/`
  по указателю из памяти/AGENTS.md (вход `_AGENT_README.md` → `RESOLVER.md`).
- `gbrain mcp` (publish_skills=true) — вариант нативных tool calls, но постоянный
  токен-оверхед на каждый вызов модели; включать только по явному запросу.

## Автосоздание мозгов (идемпотентность — железно)

- `~/brains/ensure-brain.sh <имя>`: существует → exit 0 без записи; битый → ALERT, НЕ трогать;
  создание атомарное через `.tmp-<имя>` → `gbrain doctor` → rename → фикс database_path.
- Hook `ensure-brain` на `session:start` в hooks/ каждого профиля (BRAIN= меняется per-profile).
- Вотчдог `brains-watchdog.sh` (cron 9:00, no_agent): сканирует profiles/, оснащает новые,
  ведёт `~/brains/brains.json`; молчит без изменений.
- Обслуживание `brains-maintain.sh` (cron 3:00): embed --stale + dream по реестру.

## Верификация после установки/изменений

```bash
bash ~/brains/gb.sh personal doctor            # Overall health score
bash ~/brains/gb.sh app capture "тест"         # запись
bash ~/brains/gb.sh app search "тест"          # retrieval
bash ~/brains/gb.sh marketplace search "тест"  # изоляция: НЕ должен найти
bash ~/brains/gb.sh app think "вопрос"         # полная LLM-цепочка (opus через прокси)
```

## Support files
- `references/agentrouter-ua-proxy.md` — детали UA-блокировки agentrouter и рабочий прокси.
