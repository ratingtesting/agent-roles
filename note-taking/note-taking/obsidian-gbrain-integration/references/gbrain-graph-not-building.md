# Граф памяти gbrain не строится: источник `federated` без `local_path`

Диагностика «поиск работает, а граф пуст» для мозгов PGLite, изолированных
по профилям Hermes (personal / app / marketplace). Проверено 2026-08-07.

## Симптом
- `gbrain status`: `Sync: [UNKNOWN] default never`, `Last full cycle: never run`
  даже после прямого `gbrain dream`.
- `gbrain dream`: фазы `sync`, `extract`, `patterns` падают строкой
  `requires a local brain directory; this brain has no on-disk checkout
  (postgres/remote engine); pass --dir <path>`; остальные фазы проходят ПУСТО
  → 0 связей, 0 фактов, 0 takes, граф памяти пуст.
- `gbrain doctor --json`: `cycle_freshness = fail` («Source 'vault' has never
  completed a full cycle»).
- `gbrain search` ПРИ ЭТОМ работает (страницы в БД, эмбеддинги 100%).

## Корень
Источник `default` создан `federated=true` БЕЗ `local_path`. gbrain различает две
оси: **brain = какая БД**, **source = какой репозиторий в ней**. Файловые фазы
(`sync`/`extract`/`patterns`) читают markdown с диска через источник с
`local_path`. У федеративного источника диска нет → связи `[[wikilinks]]` не
строятся. Это НЕ проблема модели — смена nemotron→deepseek не чинит.

CLI не даёт привязать путь к существующему `default`:
- `sources add default --path X` → «already registered» (даже с `--force`).
- `sources remove default --confirm-destructive` → «cannot remove the "default"
  source (it backs the pre-v0.17 brain)».
- `sources attach default --path X` ИГНОРИРУЕТ `--path` — привязывает текущую
  папку (пишет `.gbrain-source` в CWD). Откат: `rm .gbrain-source`.
- Править `local_path` напрямую в `brain.pglite` — не делать (риск повредить).

## Решение: второй источник `vault` поверх git-репозитория
gbrain требует, чтобы `--path`-источник был **git-репо с закоммиченными
файлами** (walker читает через git objects; untracked невидимы). Obsidian-vault
по умолчанию не git → сначала git-init.

```bash
# на каждый мозг (personal/app/marketplace)
export GIT_AUTHOR_NAME="GBrain" GIT_AUTHOR_EMAIL="gbrain@local"
export GIT_COMMITTER_NAME="GBrain" GIT_COMMITTER_EMAIL="gbrain@local"

V="C:\\Users\\Unicorn\\Documents\\Obsidian-Profiles\\<brain>"
(cd "$HOME/Documents/Obsidian-Profiles/<brain>" \
  && git init && git add -A && git commit --allow-empty -m "brain initial")

bash ~/brains/gb.sh <brain> sources add vault --path "$V"
bash ~/brains/gb.sh <brain> sources default vault
bash ~/brains/gb.sh <brain> config set link_resolution.global_basename true
bash ~/brains/gb.sh <brain> sync --source vault
bash ~/brains/gb.sh <brain> extract all --source fs --dir "$V"   # backfill связей
bash ~/brains/gb.sh <brain> dream --source vault                 # КЛЮЧ: не голое dream!
```

### Почему `dream --source vault`, а не голое `dream`
Голое `dream` не покрывает источник `vault` — `cycle_freshness` остаётся fail.
`dream --source <id>` проходит файловые фазы. Для полного покрытия запускать оба
(`dream --source vault`, затем `dream`), как в `~/brains/brains-maintain.sh`.

### basename-резолвер (Obsidian-стиль)
Obsidian использует «bare» `[[note-name]]`; gbrain по умолчанию резолвит только
path-qualified `[[path/page]]`. Без `link_resolution.global_basename true` связи
между папками не строятся. Включить + повторный `extract links`.

## Ловушки
- MSYS `$b` в одинарных кавычках пути не раскрывается → `C:\...\$b` буквально.
  Пути для `--path` передавать ЯВНО, не через переменную в кавычках (slug прошлого
  прогона `Obsidian-Profiles$b`).
- `sync` может падать на embed 503 (перегрузка сервиса) — транзиент; retry/
  `--skip-failed`.
- Автоматика: cron 3:00 `brains-maintain.py` (embed + dream --source vault по
  `~/brains/brains.json`), cron 9:00 `brains-watchdog.py`. Обёртки — Python,
  вызывают bash-скрипты через полный Git-bash (cron не гоняет `.sh` без WSL-bash).
- Новый профиль одним вызовом: `bash ~/brains/new-profile.sh <имя>` (профиль +
  мозг + hook + vault + git + источник + basename).

## Архитектурное правило (SETUP_GUIDE §6, решено 2026-08-07)
Брейн для кода НЕ создавать. graphify = граф кода (AST, бесплатно);
gbrain = память решений. 3 мозга — personal/app/marketplace — изолированы по
профилям, границы не пересекаются, каждый привязан к своему vault.