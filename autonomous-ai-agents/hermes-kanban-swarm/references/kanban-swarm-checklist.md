# Kanban Swarm Runbook — проверенный сценарий (Proof Pack, 2026-08)

Проверенный end-to-end сценарий оркестрации роя на board `proof-pack` профиля app.

## Результат
15 карточек (W1–W6), 5 волн + аудит-фикс, 46 документов, все `done`.
Проект: `C:\Projects\lazy-unicorn\Digital Unlock Platform\`.

## Команды-шпаргалка
```bash
# board
hermes --profile app kanban boards create proof-pack --name "Proof Pack" --icon 🐝 --switch
hermes --profile app kanban init

# карточка волны (родитель = зависимость)
hermes --profile app kanban --board proof-pack create "<title>" \
  --assignee app --workspace "dir:C:\Projects\lazy-unicorn\Digital Unlock Platform" \
  --max-retries 3 --created-by founder --json --parent <parent_id> --body "<ctx>"

# gateway (диспетчер, тик ~60с)
hermes --profile app gateway run                      # фон
hermes --profile app gateway status
hermes --profile app config set platforms.api_server.port 8643   # при конфликте порта

# контроль
hermes --profile app kanban --board proof-pack stats  # счётчики по статусам
hermes --profile app kanban --board proof-pack list
hermes --profile app kanban --board proof-pack log <id>   # лог воркера
hermes --profile app kanban --board proof-pack show <id>  # body + события
hermes --profile app kanban --board proof-pack comment <id> "..."  # эскалация
```

## Схема волн (работает)
- W1 Vision/Research (нет родителей) → W2 Product/Unlock/Campaign (родители W1)
- W2 → W3 Economy/Domain/Flutter (родители W2)
- W3 → W4 Growth/Risk/MVP (родители W3)
- W4 → W5 Simplicity + Devil's Advocate (родители W4)
- Аудит-фикс (W6) — волна, добавленная после проверки структуры.

## Тело карточки (проверенный шаблон)
```
## РОЛЬ
Первым делом вызови skill_view(name='<skill>') и работай строго в этой роли.
<конкретная задача: какие файлы, какие разделы из 00_Founder/Brief.md>

## Обязательный контекст (прочитать ДО генерации)
1. `00_Founder/Brief.md` — свой раздел (промпт основателя).
2. `MANIFEST.md` — единый манифест. Противоречить нельзя.
3. `PROGRESS.md` — Termination Conditions и журнал итераций.

## Правила
- Язык — русский. Никакого кода.
- Все обязательные разделы из Brief.md. Ссылки на зависимые документы.
- Лимит 3 итерации. После каждой — запись в PROGRESS.md (попытка N/3, результат, причина, шаг).
- 3/3 ❌ → kanban comment "🛑 ЭСКАЛАЦИЯ: ..." и СТОП.
- De-Sloppify перед завершением: убрать воду, повторы, противоречия манифесту.
```

## Ошибки, которые реально случились (и как вышли)
1. `--skill founder-visionary` → воркер падал `Unknown skill(s)` (3 краха). Фикс: skill_view в body.
2. `--priority P1` → `invalid int value`. Фикс: `--priority 1`.
3. Gateway `8642 already in use` (default-профиль держит порт). Фикс: `config set platforms.api_server.port 8643`.
4. `gbrain think` НЕ сохраняет (Pages:0) — пишет только `put`. Экспорт: `bash ~/brains/gb.sh app export --dir "$(cygpath -w "$HOME/Documents/Obsidian-Profiles/app")"`.
5. graphify semantic (9router 502 ResourceExhausted / freellmapi 429) — упало честно, AST-граф оставлен рабочим (`graphify update .`).
6. Скрипт создания карточек: имена файлов с пробелами в bash-циклах ломают `for f in $(find ...)` — использовать `-print0 | while read -d ''`.
7. Вложенные дубли папок скиллов (`skills/X/X/SKILL.md`) → `Ambiguous skill name`. Дедуп: переместить идентичные в бэкап-папку.

## Аудит после волн (Definition of Done)
- Полная сверка структуры против Brief (папка за папкой).
- Поиск TODO/FIXME/placeholder — только осознанные «заглушки» (TON-порт в MVP) допустимы.
- Проверка битых относительных .md-ссылок (python-скриптом, не grep — имена с пробелами).
- Проверка нумерации разделов (у воркеров дрейфует: 5→7, внутри 7.x при разделе 6).
- Проверка дублей: Risks §6 ≠ Devils Advocate.md (это фильтр + полный разнос — архитектура валидна).
