# agent-roles

Коммерческий пул скиллов-ролей (агентов) для перепродажи. Все роли — clean-room
переписывание исходников `agency-agents` (MIT, AgentLand Contributors) в формат
Hermes, лицензия выходных скиллов **MIT-0**. Шаблон создания ролей —
`skills/agentic-skill-authoring/`.

## Обязательная защита при веб-походах

Каждый агент, ходящий в интернет (`web_search` / `web_extract` / `browser_navigate` /
`fetch_url` / `vision_analyze`), обязан использовать два скилла защиты:

1. **`injection-guard`** — Hermes-плагин (hook `transform_tool_result`), классификатор
   DeBERTa на входе веб-тулов. Автор: gweber, MIT.
2. **`agent-defense`** — Hermes-скилл (scastile, MIT), многослойная защита
   (память, egress, anti-cloaking).

Оба указаны в `related_skills` каждого агента и в шаблоне `agentic-skill-authoring`.

### ⚠️ КРИТИЧНО: плагин injection-guard требует зависимостей

Без зависимостей плагин **молча не работает** (no-op) — веб-контент НЕ сканируется,
и ты думаешь, что защищён, хотя нет. Это реальная проблема на чистой машине.

Установи в venv Hermes (где исполняется `hermes-agent`):

```bash
# найди venv (пример для Windows):
# C:\Users\<user>\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe
<venv>/Scripts/python -m pip install "transformers>=4.40" torch sentencepiece
```

После установки — **перезапусти gateway**:

```bash
hermes gateway restart
```

Проверить, что классификатор грузится: в логе gateway при первом веб-запросе НЕ должно
быть сообщения `injection-guard: 'transformers' not installed — the hook is a no-op`.
Пойманные атаки пишутся в `~/.hermes/injection-guard/caught_attacks.jsonl`.

### Инфраструктурные требования (уже в твоём Hermes)

- `SOUL.md` PRE-EXEC GATE п.6: перед веб-походом — загрузить `injection-guard` + `agent-defense`.
- `hermes-web-configuration` SKILL.md: раздел `MANDATORY WEB-GUARD`.
- `config.yaml` (всех профилей): `plugins.enabled` содержит `injection-guard` + `security-guidance`.

## Лицензии

| Что | Лицензия | Примечание |
|-----|----------|-----------|
| Роли (269 агентов) | MIT-0 | clean-room из MIT-исходника |
| `injection-guard` | MIT | gweber/hermes-injection-guard |
| `agent-defense` | MIT | scastile/hermes-agent-defense |
| `agentic-skill-authoring` | MIT-0 | шаблон (собственный) |

Исходник ролей `agency-agents` — MIT (AgentLand Contributors). Clean-room применён
избыточно (MIT разрешает использование с атрибуцией); решение по атрибуции —
за владельцем репозитория.

## Реестр источников

`SOURCES_REGISTRY.md` — реестр всех внешних источников (защита, исходники, практики)
со ссылками и видами лицензий.
