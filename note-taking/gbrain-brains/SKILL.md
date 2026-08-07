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
| chat / models.default | `openai:oc/deepseek-v4-flash-free` (через OPENAI_BASE_URL=http://localhost:20128/v1 = 9router). Сменён с `oc/nemotron-3-ultra-free` 2026-08-06: у nemotron доставка ответа 2/5 против 5/5 у deepseek на строгом JSON (бенчмарк — см. скилл `graphify-setup`). |
| embeddings | `openai:lightweight-embeddings/bge-m3`, dimensions **1024** |
| rerank | `llama-server-reranker:ms-marco-MultiBERT-L-12`, base URL `http://127.0.0.1:8000/v1` (FlashRank — нативно совместим, адаптер НЕ нужен) |
| models.think / expansion_model | `anthropic:claude-opus-4-8` через UA-прокси `ANTHROPIC_BASE_URL=http://127.0.0.1:8402` |
| search.mode | `balanced` |

### Смена модели мозга (проверено 2026-08-06)
`models` может ОТСУТСТВОВАТЬ в `.gbrain/config.json` — тогда значение берётся из дефолта, а
предупреждение всё равно пишет `resolved to "..." via "models.default"`, будто ключ задан.
Не редактируй JSON руками — ставь командой (ключ создастся):
```bash
cp ~/brains/<brain>/.gbrain/config.json ~/brains/<brain>/.gbrain/config.json.bak.$(date +%Y%m%d-%H%M%S)
bash ~/brains/gb.sh <brain> config set models.default "openai:oc/deepseek-v4-flash-free"
bash ~/brains/gb.sh <brain> status | head -3   # первая строка покажет новую модель
```
Мозгов несколько (`~/brains/brains.json`: personal/app/marketplace) — смена в одном НЕ
затрагивает остальные. Побочный эффект не-Anthropic модели: `BUDGET_METER_NO_PRICING ...
Budget gate disabled` — у gbrain прайсинг только для Anthropic, т.е. бюджетный лимит цикла
отключается (на free-модели расходов нет, но защиты от разгона тоже нет).

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
12. **DURABLE FACTS → GBRAIN, NEVER built-in `memory`.** Built-in `memory` tool
   can fail in a hard loop (observed 4× failure in one turn, "consolidation failed").
   When a cross-session fact must persist, write it to the isolated project brain via
   `bash ~/brains/gb.sh <brain> put "<slug>"` (markdown on stdin), then `get` to confirm.
   This is the user's explicit preference (2026-07-28): "у тебя память гигабрейн
   есть ... и межсессионная память keelwright" — use GBrain, not the agent's MEMORY.md.
13. **`think` does NOT persist; `put` does.** `gb.sh <brain> think "..."` synthesizes an
    answer with LLM+citations but writes NO page — output shows `Pages: 0` (observed
    repeatedly this session). To RECORD a fact/decision for later sessions use
    `put "<slug>"` (markdown on stdin, as in #12), then `get` to confirm. Read/synthesis =
    `think`/`search`/`query`/`ask`; write = `put`/`capture`. In the verification block below,
    use `capture` (not `think`) when the intent is a persistent record.
14. **СТРОГАЯ ИЗОЛЯЦИЯ МОЗГОВ = СТРОГАЯ ИЗОЛЯЦИЯ ПРОЕКТОВ.** `lazy-unicorn` — это
   СРЕДА РАЗРАБОТКИ (инструменты: Flutter, провайдеры, прокси), НЕ общий мешок проектов.
   `app`, `marketplace`, `personal` — отдельные изолированные силосы: свой Git, своя Supabase,
   свой GBrain-мозг, свои графы Graphify. Пользователь ЗАПРЕТИЛ называть `lazy-unicorn`
   «монорепо/общим мешком». Коммиты/пуш проекта `app` идут в его собственный репозиторий,
   не в `lazy-unicorn`. Пиши факт про проект `app` именно в мозг `app`, чтобы не нарушать изоляцию.

15. **«Мозг работает?» — проверяй ЦИКЛ, а не только ответ на запрос.** `search` может
   отдавать результаты, пока мозг фактически не собран. Диагностика по `status`:
   `Last full cycle: never run` + `Sync: [UNKNOWN] default never` означают, что связи между
   страницами никогда не строились — это поиск, а не «мозг». Полный цикл = `gb.sh <brain> dream`
   (фазы: extract_facts → resolve_symbol_edges → recompute_emotional_weight → consolidate →
   propose_takes). Прерывание после `consolidate` безопасно.
16. **`extract` даёт 0 связей — это чаще всего НЕ модель.** `extract all --source fs` падает с
   «No brain directory configured» пока не выполнен `gbrain sources add default --path <brain-dir>`;
   обходной путь — `--source db`. Но если и `--source db` возвращает `0 links, 0 timeline` при
   N страницах, причина в контенте: в заметках нет wikilinks `[[...]]`, связывать нечего.
   Смена модели это НЕ чинит — нужен экспорт с перекрёстными ссылками.
17. **Obsidian показывает граф ЗАМЕТОК (gbrain), а не граф КОДА (graphify).** Частый вопрос
   пользователя «почему не вижу графы в Obsidian». В vault
   `Documents/Obsidian-Profiles/<profile>/` попадает только то, что экспортировал gbrain;
   graphify пишет в `<project>/graphify-out/` и в vault не заходит никогда.
18. **`sources attach --path <p>` ИГНОРИРУЕТ `--path` и привязывает ТЕКУЩУЮ папку.** Ловушка
   с побочным эффектом в чужом репозитории: команда создаёт файл-маркер `.gbrain-source`
   (содержимое — id источника) в CWD и печатает «Attached <CWD> to source "default"».
   Это НЕ задание пути источника, а пометка «команды из этой папки идут в этот источник».
   Если сработало не там — просто `rm .gbrain-source`. Всегда проверяй `pwd` перед `attach`.
   Переопределить путь существующего источника CLI НЕ даёт: `sources add default --path ...`
   отвечает «already registered ... use sources remove --confirm-destructive», и `--force`
   этого не обходит (`--force` пропускает только проверку наличия закоммиченных файлов).
   Команды `sources set-path` не существует — список подкоманд смотреть в
   `~/.bun/install/global/node_modules/gbrain/src/commands/sources.ts` (блок `case`), т.к.
   `gbrain sources --help` выдаёт лишь заглушку «run gbrain --help».
19. **Прежде чем чинить «мозг не собирается» — посмотри, ЕСТЬ ЛИ ЧТО собирать.** Модель тут
   почти никогда не виновата (см. #16). Мантра из документации gbrain:
   *brain = какая БД, source = какой репозиторий в ней*. На этой машине папки
   `~/brains/{personal,app,marketplace}/` содержат ТОЛЬКО `.gbrain/` с базой — ни одного `.md`.
   Поэтому файловые фазы `dream` честно рапортуют
   `requires a local brain directory; this brain has no on-disk checkout` и пропускаются
   (`sync`, `extract`, `patterns`), а `Last full cycle: never run` остаётся даже после
   успешного `dream` с exit 0 — счётчик привязан к синхронизированному источнику.
   Указывать `local_path` физически не на что, и это РАЗВИЛКА С ПОТЕРЕЙ ДАННЫХ
   (переучреждение источника = `remove --confirm-destructive` = удаление страниц).
   НЕ решай сам: варианты — пустая `~/brains/<name>`, Obsidian-vault (риск цикла
   «экспорт→импорт») или репозиторий проекта (смешает память с кодом, для кода есть graphify).
   Спроси пользователя, тем более что изоляция мозгов у него жёсткое правило.

20. **РАЗДЕЛЕНИЕ РОЛЕЙ (УТВЕРЖДЕНО ПЕТРОМ 2026-08-07): graphify vs gbrain.** НЕ создавать
   отдельный мозг (brain) для кода. Чёткое разделение:
   - **graphify** = граф КОДА (как устроен код): AST-парсер, классы/импорты/вызовы/сообщества.
     Пишет в `<project>/graphify-out/` (коммитить в git). Бесплатно, `graphify update .` без API.
   - **gbrain** = память РЕШЕНИЙ (почему так решили): факты, gap-анализ, связи между решениями.
     Пишет в `~/brains/<profile>/.gbrain` + vault `Documents/Obsidian-Profiles/<profile>/`.
   - **Code-brain НЕ заводим** — это дубликат graphify, дороже (LLM на каждый цикл) и хуже по
     точности (пересказ vs парсинг). gbrain README упоминает «indexing a codebase as a queryable
     code brain», но для этого окружения избыточно и противоречит воле пользователя.
   - Изоляция: 3 мозга gbrain (personal/app/marketplace) по профилям Hermes, границы не
     пересекаются. Каждый привязан к своему vault (personal vault отсутствует — привязывать не к чему).
   - Решение ЗАФИКСИРОВАНО в `C:\Projects\lazy-unicorn\SETUP_GUIDE.md` §6 (раздел
     «Разделение ролей: graphify (код) vs gbrain (память)») — эталон для будущих сессий.
     При сомнении «нужен ли брейн для кода?» отвечать НЕТ и ссылаться на SETUP_GUIDE §6.
   - Опционально (ручная привычка, не автосвязь): выводы graphify (god nodes, архитектурные
     выводы) можно класть в gbrain как заметки (`put`), но это не обязательно.

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
