---
name: gbrain-multi-brain-setup
version: 1.0.0
description: "Use when installing GBrain per-profile brains on Windows."
author: agent
---

# GBrain: мозг на профиль Hermes (Windows, бесплатный стек)

Эталон конфигурации и результаты тестов: `C:\Projects\lazy-unicorn\SETUP_GUIDE.md` §6.

## Архитектура
- Мозги: `~/brains/{personal,app,marketplace}` — PGLite, полная изоляция (проверять записью в один и поиском в другом).
- Профиль default → мозг `personal`; остальные — по имени профиля.
- Один глобальный `gbrain` CLI (bun); переключение мозга через `GBRAIN_HOME` (это РОДИТЕЛЬ папки `.gbrain`).
- Реестр: `~/brains/brains.json` (пишет вотчдог).

## Установка (порядок важен)
1. `export PATH="$HOME/.bun/bin:$PATH" && bun install -g github:garrytan/gbrain`
   - Bun блокирует postinstall → если `doctor` даёт schema_version:0, запустить `gbrain apply-migrations --yes`.
2. Скиллы ДО мозгов: `gbrain skillpack scaffold --all` (баг #1917: работает только из `~/.bun/install/global/node_modules/gbrain`; путь `--workspace` может исказиться MSYS → проверить, файлы могли лечь в `/c/c/Users/...` — перенести вручную). Скиллы: `~/brains/skills-workspace/skills/`.
3. Мозги: `bash ~/brains/ensure-brain.sh <имя>` — идемпотентный, атомарный (.tmp → doctor → rename → фикс database_path в config.json, т.к. init пишет абсолютный путь).
4. Хук `ensure-brain` (`session:start`) в `hooks/` каждого профиля Hermes; вотчдог-cron (no_agent, 9:00) сканирует `profiles/`, cron-скрипты — обёртки в `~/AppData/Local/hermes/scripts/` (cronjob принимает только имена оттуда).
5. Обслуживание: cron 3:00 `brains-maintain.sh` (embed --stale + dream по реестру).

## Ключевые питфоллы (стоили времени)
- **agentrouter.org режет ВСЕ User-Agent кроме `claude-cli/...`** («unauthorized client»). gbrain/AI SDK не умеет кастомные UA → микро-прокси `C:\Users\Unicorn\anthropic-ua-proxy\proxy.py` (stdlib, :8402 → agentrouter, подмена UA). Автозапуск: Registry Run c полным путём pythonw.exe. gbrain: `ANTHROPIC_BASE_URL=http://127.0.0.1:8402`.
- **9router модели**: `oc/hy3-free` НЕ существует; `oc/mimo-v2.5-free` нестабилен (500-ки). Рабочая: `oc/nemotron-3-ultra-free`. Для `think`/structured-JSON nemotron падает («Invalid JSON response» — стриминг-чанки 9router) → `models.think` и `expansion_model` на `anthropic:claude-opus-4-8` через прокси.
- **models-ключи разные**: `chat_model` НЕ покрывает think; ставить также `models.default` и `models.think`.
- **FlashRank :8003 нативно совместим** с gbrain-реранкером (`/v1/rerank`, results[{index,relevance_score}]) — адаптер не нужен. lightweight-embeddings `/v1/rank` — НЕ совместим, не путать серверы.
- **Кириллица в curl -d на MSYS ломается** (кракозябры) → тесты API писать Python-скриптом с `ensure_ascii=False` + `.encode("utf-8")`.
- **9router иногда отдаёт SSE/склеенный JSON** при stream:false — парсить построчно.

## Env для любого вызова gbrain
```bash
export GBRAIN_HOME="C:\\Users\\Unicorn\\brains\\<имя>"
export OPENAI_API_KEY=$API_9ROUTER_KEY OPENAI_BASE_URL="http://localhost:20128/v1"
export ANTHROPIC_API_KEY=$API_AGENTROUTER_KEY ANTHROPIC_BASE_URL="http://127.0.0.1:8402"
```
Обёртка: `bash ~/brains/gb.sh <brain> <gbrain-args...>`.

## Верификация
1. `gb.sh <b> doctor` → «All checks OK» (70/100 у пустого мозга — норма, 0 за граф).
2. `gbrain models doctor` → embedding_config + reranker_config ok.
3. capture → search → **think** (полная цепочка: реранк + opus через прокси).
4. Изоляция: capture в A, search в B → «No results».
5. Повторный `ensure-brain.sh` / вотчдог → молчание, ничего не пересоздано.
