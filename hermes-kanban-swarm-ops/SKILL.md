---
name: hermes-kanban-swarm-ops
description: "Use when running `hermes kanban swarm` with role-agents — isolated boards, cron-limited watchdog, worker recovery."
version: 1.2.0
author: emelya-agent, Hermes Agent
license: MIT-0
platforms: [linux, macos, windows]
emoji: "🛡️"
color: "slate"
metadata:
  hermes:
    tags: [kanban, swarm, multi-agent, debugging, recovery]
    related_skills: [master-model-orchestration, semantic-corpus-cleaning, keelwright, agentic-skill-authoring]
---

# Hermes Kanban Swarm Ops

Launch and operate multi-agent swarms via `hermes kanban swarm` (workers → verifier →
synthesizer). This skill captures the failure modes that are NOT in the happy-path
docs — learned from real swarms that crashed on launch and took multiple fixes.

## КРИТИЧЕСКИЕ ПРАВИЛА (из TASK_REQUIREMENTS-STANDART.md §A.12, §F.29-33б, §O.7-9, SOUL.md)

### 🛡️ ИЗОЛЯЦИЯ ДОСКИ (ЖЁСТКО, НАРУШЕНИЕ = РАБОТА НА ЧУЖОЙ ДОСКЕ)
- **Каждый агент работает на СВОЕЙ доске** (одна доска = один проект). Другие агенты в любой момент переключают глобальную активную доску на свою (`hermes kanban boards switch`), поэтому полагаться на «текущую» доску НЕЛЬЗЯ.
- **ЗАПРЕЩЕНО** вызывать голый `hermes kanban ...` без `--board <slug>` — это ударит по глобально-активной доске, которую мог переключить другой агент.
- **Правильный вызов:** `hermes kanban --board <МОЯ_ДОСКА> <команда>` — всегда явно.
- **Своя обёртка:** создать скрипт `~/bin/<префикс>` с уникальным префиксом (пример для vibe-board: `~/bin/hkv` = `hermes kanban --board v2-g3-os-swarm`), чтобы не конфликтовать с чужими алиасами в общем ~/.bashrc.
- **Определение СВОЕЙ доски:** доска проекта = slug из `hermes kanban boards list`; на старте работы ОДИН раз определить и запомнить свою доску (в памяти агента/в контексте), дальше всегда явный `--board`.
- **Проверка перед ЛЮБОЙ работой:** `hermes kanban --board <МОЯ_ДОСКА> list` — если заголовок `Board:` не совпадает с ожидаемым — СТОП.
- **НЕ использовать** `hermes kanban boards switch` без необходимости — глобальное переключение вредит другим агентам; при работе всегда явный `--board`.
- **Чужие алиасы/обёртки** в ~/.bashrc (hkb*, hkv* и т.п.) могут принадлежать другим агентам — использовать ТОЛЬКО свою, с уникальным именем.
- env var `HERMES_KANBAN_BOARD=<slug>` тоже работает (штатный механизм Hermes) — выставлять per-процесс, не глобально в ~/.bashrc (иначе сломает других агентов).

### 🚫 ЗАПРЕТ КРОНОВ ДЛЯ ДОСОК (ЖЁСТКИЙ ПРИОРИТЕТ, урок 05.09.2026 — 8 часов переустановок!)
> **Никогда, НИ ПРИ КАКИХ УСЛОВИЯХ не создавать cron для диспатча/мониторинга доски роя.**

**ПОЧЕМУ (факты):**
- Cron хранится ПОСТОЯННО в профиле и исполняется gateway'ом при старте Windows/Hermes (Hermes_Gateway.vbs в автозапуске).
- После перезагрузки/обрыва связи gateway поднимает ВСЕ активные кроны → крон диспатчит доску → воркеры запускаются → грузят CPU → система висит. Рой как процесс умер, а крон-диспетчер — НЕТ («восстаёт из пепла»).
- Реальный ущерб: 2 крона-двойника v2-g3-os-swarm-watchdog (каждые 10 мин) сожгли пользователю 8 часов на переустановки системы.

**ПРАВИЛЬНАЯ СХЕМА (одобрена Петром 05.09.2026, делать ТОЛЬКО так):**
1. Рой запускается ТОЛЬКО по явной команде пользователя.
2. Диспатч — вручную в текущей сессии: `hermes kanban --board <B> dispatch --max N` (или фоновый процесс сессии, который умирает вместе с Hermes).
3. Мониторинг — вручную в сессии (раз в 10 мин `list`), НЕ через крон.
4. Новый запуск роя = чистый старт: старых кронов нет → нечему восставать. Перезагрузка/обрыв убивает и рой, и диспатчер — вместе.
5. `hermes kanban daemon` — DEPRECATED (диспатчер встроен в gateway), НЕ использовать.

**ПРЕДУПРЕЖДЕНИЕ ПОЛЬЗОВАТЕЛЯ:** Если пользователь просит «поставь крон на доску» — ОБЯЗАТЕЛЬНО предупредить: «Крон переживёт перезагрузку и будет диспатчить доску автоматически — после обрыва связи/перезагрузки он воскресит рой и может повесить систему. Это запрещённая схема (урок 05.09.2026). Рекомендую ручной диспатч в сессии. Делать всё равно крон?» — и только при явном «да, делай» — создавать, но с одноразовым поведением и записью о риске.

### КРОН С ОГРАНИЧЕННЫМ СРОКОМ ЖИЗНИ (ОДОБРЕН Петром 06.09.2026 — решает проблему «воскресает»)
**Проблема запрета выше:** крон `every 10m` без срока живёт вечно → после перезагрузки воскресает рой. Демон-бесконечный цикл — профанация (все равно требует ручного пробуждения).

**РЕШЕНИЕ (только для проверки статуса, НЕ диспатча):**
1. Крон **проверяет доску** (list), НЕ диспатчит.
2. **`--repeat N`** — жёсткий срок жизни: `N = (1.5 × ожидаемое время роя) / интервал`. Крон сам умирает через 1.5×, даже если забыли выключить — НЕ воскресает после перезагрузки (истёк).
3. Пример: рой ~40 мин → интервал 3 мин → `repeat = 40*1.5/3 = 20` → крон умрёт через 60 мин.
4. **Оценка времени:** брать фактическое время из прошлых прогонов (не «предположить»).
5. Убить вручную при done: `hermes cron remove <id>`.
6. **ВАЖНО:** крон требует запущенного gateway (`hermes gateway start`) — без него крон создаётся, но не fires.

**Формула:** `repeat = ceil(1.5 × оценочное_время_минут / интервал_минут)`.

**ПРОТИВОРЕЧИЕ разрешено:** старый запрет (05.09) — про **вечный** крон-диспатчер (воскресает). Новое — про **ограниченный по времени** крон-проверку (сам умирает). Ограничение срока жизни снимает риск воскресания.

**ЧЕК-ЛИСТ ЗАКРЫТИЯ РОЯ (обязателен после каждого роя):**
1. `hermes kanban --board <B> block` всех задач (не оставлять ready/running)
2. Проверить ВСЕ профили: `hermes --profile <p> cron list` для p in marketplace swarm default → удалить ЛЮБОЙ крон, упоминающий доску роя
3. Убедиться, что нет запущенных воркеров (процессы python/hermes с kanban в cmdline)
4. Только потом сообщать «рой завершён»

### Роли и модели
- **Роли берутся ТОЛЬКО из локального репо** `C:\Projects\agent-roles` (278+ ролей, репо ratingtesting/agent-roles)
- **Модели — СТРОГО из** `C:\Projects\_master-1000-articles\strategy\MODEL_TABLE.md` **и** `C:\Projects\_master-1000-articles\strategy\JTBD_TASK.md`
- JTBD-рои: заголовки — **ТОЛЬКО** `inclusionai/ling-3.0-flash-sante:free` (nous) или `inclusionai/ling-3.0-flash-fin:free` (nous). **NE ver shablon!** (см. Pitfall 15)
- Step-3.7 для заголовков — ЗАПРЕЩЁН (калька-шаблон «фраза = заголовок»)
- Новые роли: если роли нет в репо → создать через скилл `agentic-skill-authoring` + **WEB GUARD** (п.33б) + push в `ratingtesting/agent-roles` (п.19)
- **Установка ролей для канбана:** скопировать из `C:\Projects\agent-roles\\<role>\` в `C:\Users\Unicorn\AppData\Local\hermes\skills\\<role>\` (default skill dir). `profiles/swarm/skills/` НЕ достаточно.
- **Zero-swarm V2:** создание стратегических файлов `G2-Runtime` на основе ФАКТИЧЕСКИХ результатов V1 (не плана)
- **Graphify для кода** — при поиске/анализе кода ОБЯЗАТЕЛЬНО использовать graphify (экономия токенов, точный поиск)
- **Документирование кода** — по SOUL.md: doc-комментарии ТОЛЬКО для сложных бизнес-правил и публичных API, НЕ для очевидного

### Скилл ДОЛЖЕН быть универсальным (урок 04.09.2026 — пользовательская директива)
- Этот скилл используют РАЗНЫЕ агенты в РАЗНЫХ проектах на СВОИХ досках. ЗАПРЕЩЕНО зашивать конкретный slug доски/проекта в правила и команды как единственно-верный — только как пример (`<B>` = своя доска, пример `hkv`/v2-g3-os-swarm для vibe-board).
- Каждый агент на старте определяет свою доску (slug из `hermes kanban boards list` по своему проекту), запоминает и дальше всегда явный `--board`.
- Если глобальная active-доска сменилась другим агентом: НЕ вызывать `boards switch` назад (глобальное переключение вредит другим), НЕ пересоздавать cron «на актуальной» доске — просто продолжать через явный `--board <B>`. `hkv list` (или эквивалент) всегда показывает свою доску.

### Модель-на-роль СТРОГО из таблицы (не унифицировать!)
- Каждая роль имеет СВОЮ модель из `C:\Projects\_master-1000-articles\strategy\MODEL_TABLE.md`.
- НЕЛЬЗЯ ставить всем одну рабочую модель (напр. poolside/laguna) даже если она стабильна.
- Пользователь ПРОВЕРЯЕТ модель каждой задачи (`hermes kanban --board <B> show <id> | grep model:`).

### Приоритет провайдеров (жёстко)
1. `nous`
2. `freellmapi`
3. `opencode-free` — только для моделей, где он реально работает; если провайдер возвращает `401/not supported` — сразу переходить к `nous`/`freellmapi` по fallback-строке таблицы.
4. `openrouter` — **только последним** в запасных.

### Модельная матрица (MODEL_TABLE.md 2026-09-06)
| № | Роль | Основная модель (провайдер) | Запасные модели (провайдеры) |
|---|------|----------------------------|------------------------------|
| 1 | Стратег | nvidia/nemotron-3-ultra:free (opencode-free) | nemotron-3-ultra-550b (freellmapi), nemotron-3-super (freellmapi), meituan/longcat-2.0:free (nous) |
| 2 | Оркестратор | nemotron-3-ultra-550b (freellmapi) | nemotron-3-super (freellmapi), minimax-m3 (freellmapi), meituan/longcat-2.0:free (nous) |
| 3 | Архитектор | nemotron-3-super-120b (freellmapi) | nemotron-3-ultra-550b (freellmapi), nemotron-3-super (freellmapi), meituan/longcat-2.0:free (nous) |
| 4 | Кодер-исполнитель | poolside/laguna-s-2.1:free (nous) | poolside/laguna-s-2.1:free (openrouter), poolside/laguna-s-2.1 (freellmapi), poolside/laguna-xs-2.1:free (nous), meituan/longcat-2.0:free (nous) |
| 5 | Ревьюер кода | stepfun/step-3.7-flash:free (nous) | nemotron-3-super (freellmapi), meituan/longcat-2.0:free (nous) |
| 6 | Маркетолог | stepfun/step-3.7-flash:free (nous) | inclusionai/ling-3.0-flash-fin:free (nous), nvidia/nemotron-3-super-120b:free (openrouter) |
| 7 | Писатель (SEO-контент) | meituan/longcat-2.0:free (nous) | stepfun/step-3.7-flash:free (nous), inclusionai/ling-3.0-flash-fin:free (nous) |
| 8 | Экономист (финансы) | inclusionai/ling-3.0-flash-fin:free (nous) | stepfun/step-3.7-flash:free (nous) |
| 9 | Биржевой трейдер | nvidia/nemotron-3.5-lightning:free (opencode-free) | poolside/laguna-s-2.1:free (freellmapi), poolside/laguna-xs-2.1:free (nous) |
| 10 | Тестировщик (QA) | nvidia/nemotron-3.5-lightning:free (opencode-free) | poolside/laguna-s-2.1:free (freellmapi), poolside/laguna-xs-2.1:free (nous) |

**ВАЖНО:** Опенроутер (`openrouter`) в основной таблице НЕ используется — провайдер `openrouter` только в крайних запасных, если все остальные исчерпаны. Бесплатные модели через `nous` и `freellmapi` чаще всего доступны без очереди.

## Pre-flight (run BEFORE launching)
1. **Repo state check** — run `git log --oneline -10` in project dir BEFORE creating tasks. The repo may have been updated by another session with significant code changes (new features, bug fixes, new deps). Do NOT create tasks for code that already exists. Update task bodies to reflect actual state.
2. **Skill resolution check** — for EACH role, run:
   `hermes chat --profile swarm -Q -q "say one word" --skills <role>`
   If `Error: Unknown skill(s): <role>` → role NOT installed in `~/.hermes/skills/`. Fix (Pitfall 1) before launch.
3. **Model check** — verify profile config has correct model from MODEL_TABLE.md for each role.
4. **Data path check** — workers run in isolated board workspace; they do NOT see project dir. Put ABSOLUTE paths in goal text (Pitfall 2).
5. **Web guard check** — if any role requires web, verify `verify_web_guard.py` passes.
6. **Model health check** — run quick test per role before swarm: `hermes chat --profile swarm -Q -q "say ok" --model <MODEL> --provider <PROV>`; if 502/504 → switch to fallback.

## Pitfall 1 — Worker crashes: `Error: Unknown skill(s): <role>`
Root cause: role folder in `C:\Projects\agent-roles\<role>\` is NOT a Hermes-installed skill. Workers resolve skills from default skill dir `~/.hermes/skills/`.
Fix:
```bash
SRC=/c/Projects/agent-roles
DST="C:/Users/Unicorn/AppData/Local/hermes/skills"
for r in backend-architect software-architect senior-developer api-platform-engineer frontend-developer qa-test-engineer test-automation-engineer swarm-runner-engineer agents-orchestrator identity-access-engineer data-visualization-engineer; do
  rm -rf "$DST/$r"; mkdir -p "$DST/$r"; cp -r "$SRC/$r/." "$DST/$r/"
done
hermes skills list   # role must show as local/enabled
```

## Pitfall 2 — Worker reports empty workspace / "data isn't in the board"
Root cause: workers execute in `C:\Users\<u>\AppData\Local\hermes\kanban\boards\<board>\workspaces\<task_id>\` (NOT project dir).
Fix: in swarm GOAL, state absolute input paths explicitly, e.g. `Read V1 results at C:\Projects\vibe-board\... and C:\Projects\_master_vibe-board\handoffs\V1-Runtime\MASTER_HANDOFF_V1.md; write G2-Runtime files to C:\Projects\_master_vibe-board\СТРАТЕГИЯ_TS\PROJECT\G2-Runtime\`.

## Pitfall 10 — Worker status is `running` but worker is dead (log staleness)
**Symptom:** Task shows `running` for hours but no log updates, worker process died silently after gateway restart.
**Diagnosis:** Check `stat -c '%y %n' logs/<task_id>.log` — if mtime is > 5 minutes old during expected active work, the worker is dead. Also check `ps aux | grep -i "hermes\|python" | grep -v grep` — dead worker won't appear.
**Fix:** `hermes kanban --board <B> archive <id>` (force-archive stuck task), then `hermes kanban --board <B> create` a NEW task with same body + correct model.

## Pitfall 11 — Task archived with run still active (orphaned run)
**Symptom:** After `unblock` + `dispatch`, old run's PID is still alive and fighting with new run for workspace. Logs show "task archived with run still active" or multiple PIDs spawning/crashing in events.
**Fix:** Kill orphaned worker PID first: `taskkill /F /PID <pid>` (from events log), THEN archive + create fresh task. Check `ps aux | grep python | grep -v grep` for orphaned hermes workers.

## Pitfall 12 — Cron requires running gateway to fire
**Symptom:** `hermes cron create` succeeds with "Next run: ..." but never fires. `hermes cron status` says "Gateway is not running."
**Diagnosis:** `hermes gateway status` — if "No gateway process detected", cron is dormant.
**Fix:** `hermes gateway start` to start immediately. Note: direct spawn dies with the spawning shell on Windows — for persistence use `hermes gateway install` (requires admin/UAC).

## Pitfall 13 — Code Review completed but reviewed WRONG code
**Symptom:** Code Review task marked `done` but its findings are invalid because it reviewed code generated by workers running on INCORRECT models (e.g., minimax-m3 for all tasks instead of per-role models per MODEL_TABLE.md).
**Fix:** **Archive and re-create Code Review task ONLY after all worker tasks are verified running on correct MODEL_TABLE.md models.** Use model `stepfun/step-3.7-flash:free` via `nous` per MODEL_TABLE.md.

## Pitfall 14 — Repo already has new code from another session
**Symptom:** After session restart, board shows 7/8 done but actual repo has NEW commits fixing issues that were blocking workers. Creating duplicate work or creating tasks that reference stale code.
**Diagnosis:** Run `git log --oneline -10` in project dir after EVERY session restart. Compare board task bodies with actual code state.
**Fix:** Update task bodies to reflect actual repo state. If task already has a working solution in repo, archive the board task and mark as done.

## Zero-swarm V2: создание G2-Runtime файлов
**Задача:** на основе фактических результатов V1 (MASTER_HANDOFF_V1.md, git diff, тесты, сборка) обновить/создать файлы в `C:\Projects\_master_vibe-board\СТРАТЕГИЯ_TS\PROJECT\G2-Runtime\`:
- README.md — актуальный снапшот V1 (что построено, что нет)
- 01-architecture.md — фактическая архитектура (Payload коллекции, DTF, Runner, Web)
- 02-api-contracts.md — реальные API endpoints
- 03-data-model.md — реальная схема БД
- 04-roadmap-V2.md — план V2 (G3 OS) на основе того, что реально есть
- 05-risks-V2.md — риски V2
- 06-stack-V2.md — стек V2 (добавления к V1)
- 09-adr/ — новые ADR за V1

Каждый файл = измеримый критерий DONE (файл существует, содержит реальные данные, не плановые).

## Канбан команды (Hermes 2026-09-01) — ВСЕГДА через `--board <СВОЯ_ДОСКА>`
- **ЗАПРЕЩЕНО** `hermes kanban` без `--board` (чужая доска может быть активной). Ниже `<B>` = твоя доска (или своя обёртка, напр. `hkv` для vibe-board = `hermes kanban --board v2-g3-os-swarm`).
- Create card: `hermes kanban --board <B> create --skill <ROLE> --priority <N> --json "<TITLE>"`
- **Create with output dir (ПРАВИЛЬНЫЙ синтаксис):** `hermes kanban --board <B> create "Title" --skill <ROLE> --model <MODEL> --provider <PROV> --workspace "dir:C:/путь/к/проекту"`. Флаг называется `--workspace dir:<path>` — НЕ `--dir` (unrecognized argument, exit 2). Без него workers пишут в scratch-папку и файлы теряются
- Assign: `hermes kanban --board <B> assign <task_id> swarm`
- **Set model override:** `hermes kanban --board <B> set-model <task_id> "<model_id>" --provider "<provider>"`
- List: `hermes kanban --board <B> list --json`
- Show: `hermes kanban --board <B> show <task_id>`
- Board delete: `hermes kanban --board <B> boards rm <B>` — только СВОЮ доску, чужие НЕ трогать
- Timeout: may return exit 124 after 10-40s even on success. Retry once, check list. Max 3 retries.

## Verified Working Models (session 2026-09-04, updated 2026-09-06)
| Role (MODEL_TABLE.md) | Model ID | Provider | Status |
|----------------------|----------|----------|--------|
| Strategist | nvidia/nemotron-3-ultra:free | opencode-free | ✅ works |
| Orchestrator | nemotron-3-ultra-550b | freellmapi | ✅ works |
| Architect | nemotron-3-super-120b | freellmapi | ✅ works |
| Coder (TS/React/Payload) | poolside/laguna-s-2.1:free | nous | ✅ works (Z2-Z8, T2.x success) |
| Reviewer/QA | nvidia/nemotron-3.5-lightning:free | opencode-free | ⚠️ 401 not supported on opencode-free → fallback poolside/laguna-s-2.1:free (freellmapi) |
| Humanities/Writer | stepfun/step-3.7-flash:free | nous | ✅ works |
| Economist | inclusionai/ling-3.0-flash-fin:free | nous | untested |
| Trader | nvidia/nemotron-3.5-lightning:free | opencode-free | untested |
| Helper | upstage/solar-pro4:free | nous | ✅ works |
| Helper-alt | meituan/longcat-2.0:free | nous | ✅ works |

**Fallback rule:** If primary provider fails (400/401/429/502/504), switch provider first per MODEL_TABLE.md fallback chain, then model after all providers exhausted. Priority: `nous` → `freellmapi` → `opencode-free` → `openrouter`.

**DEPRECATED models (do not use):**
- `tencent/hy3:free` via `nous` — free period ended (HTTP 404)
- `nvidia/nemotron-3-super-120b:free` via `openrouter` — HTTP 400 invalid model ID
- `nemotron-3-ultra:free` via `openrouter` — use `nemotron-3-ultra-free` via `opencode-free` instead

## Critical Task Body Requirement
**The task body MUST explicitly require file creation:** `MUST create/update C:\\Projects\...\G2-Runtime\FILENAME.md with: ... Use write_file tool.` — skill instructions alone do NOT enforce output. Workers read but don't write without this directive.

## WATCHDOG & MONITORING

### Cron-ворддог (ограниченный по сроку, формула в § КРОН С ОГРАНИЧЕННЫМ СРОКОМ)
- Создавать при запуске роя с `--repeat N` по формуле: `N = ceil(1.5 × оценочное_время_роя / интервал_мин)`
- Команда: `hermes cron create --name <имя> --schedule "every 3m" --repeat <N> --skill hermes-kanban-swarm-ops --deliver origin "Check board <B> status..."`
- Крон проверяет статус (list), НЕ диспатчит. Диспатч — только вручную: `hermes kanban --board <B> dispatch --max N`
- Если глобальная доска меняется другим агентом — cron НЕ пересоздавать: явный `--board <B>` в команде уже указывает на свою доску.

### Проверка доски — КАЖДЫЕ 10 МИНУТ (не эскалация, помощь рою)
```
hermes kanban --board <B> list --json
```
Что искать:
- `triage` / `blocked` — воркер застрял, нужен unblock / model switch
- `running` > 30 мин без прогресса — possible hang, проверить логи
- `ready` не подхватываются — нет свободных слотов или dispatcher issues
- `error` в логах — API 502/504, skill missing, workspace empty

### 2-минутная проверка ПОСЛЕ КАЖДОГО ДЕЙСТВИЯ
После:
- создания доски / карточек
- назначения (assign)
- смены модели (`set-model`)
- разблокировки (`unblock`)
- dispatch
- перезапуска cron

**Ждать 2 минуты**, потом `hermes kanban --board <B> list` — проверить, что задача перешла в `running` / не упала в `triage`.

### Watchdog для долгих задач (3-4x expected time)
- Ожидаемое время задачи оценить заранее (из опыта: Z-tasks ~5-15 мин, T2.x implementation ~20-60 мин)
- Если `running` > 3-4x ожидаемое время:
  - Отдельный `watch` на этого воркера (проверять каждые 2-3 мин)
  - Проверить логи: есть ли реальный прогресс или только "working..."
  - Если висит на одном месте > 10 мин без tool calls — `block` + `set-model` на fallback / `unblock` + `dispatch`

### Проверка живости воркеров после обрывов связи / падений
- Статус `running` ≠ воркер жив: после обрыва связи процесс мог умереть, а задача висеть в `running`.
- Проверка живости: `stat -c %y "logs/<task_id>.log"` (или `date` рядом) — если лог не обновлялся > 3-5 мин при ожидаемой активной работе — воркер завис/умер.
- Свежие сессии в логе (строки `Title: ... #N`, `Duration:`) + недавний mtime = жив.
- Живых воркеров НЕ перезапускать: `dispatch` может их «crashed/auto-blocked» и пересоздать зря.

### Не менять модели у РАБОТАЮЩИХ воркеров без реальной причины (директива 04.09.2026)
- «Стратег будет работать на той модели, которая сейчас установлена» / «Если будут проблемы с моделями и их ответом — сообщи»: не перебирать модели на уже-работающих задачах по наитию.
- Менять модель ТОЛЬКО при конкретном сбое: задача в triage/blocked, в логе HTTP 4xx/5xx, «free period ended», «model not found».
- Сначала сверить с MODEL_TABLE.md, потом сообщить пользователю о проблеме/плане, не крутить set-model веером.

### Что сработало в сессии 2026-09-04 (ЗАФИКСИРОВАТЬ)
- `--workspace "dir:C:/Projects/.../G2-Runtime"` — КРИТИЧЕСКОЕ: без этого workers пишут в scratch workspace (temp), файлы теряются. НЕ `--dir`, а `--workspace dir:`
- `poolside/laguna-s-2.1:free` via `nous` — самая надёжная модель для кодинга (Z2-Z8 все success, T2.x running)
- `minimax/minimax-m3:free` via `nous` — работает для orchestrator
- `nemotron-3-ultra-free` via `opencode-free` — работает для strategist
- openrouter модели (`nvidia/nemotron-3-super-120b:free`, `nemotron-3-ultra:free`) — частые 400/502/504, использовать ТОЛЬКО как primary с быстрым fallback на nous
- 2-min check после каждого действия — поймал 3 зависших задачи до того как они ушли в глубокий triage
- Cron every 10m — поймал 2 зависших воркера на Z7/Z8
- Анализ логов (`cat logs/<task_id>.log`) — показывает реальную причину (model error, skill missing, workspace empty) быстрее чем status
- **Dispatcher bug**: при ретрае/рестарте сбрасывает `model_override` на `hy3:free`/`nous`. ЛЕЧЕНИЕ: `archive` старой задачи + `create` новой с правильной моделью изначально (не `set-model` + `unblock`)
- `tencent/hy3:free` — free period ended (HTTP 404), полностью исключить из fallback
- Задачи в `ready` могут висеть бесконечно без `dispatch`

## Watchdog cron (autonomous recovery)
Script: `hermes kanban --board <B> list --json` → count statuses → print status line + WAKE markers.
Cron: `no_agent=false` + `deliver='origin'`. Diffs stdout against previous tick; change wakes orchestrator.
Schedule: `every 10m` (adjustable per board complexity).

## Диспатчер баг — контрольный список
- После `set-model` + `unblock` + `dispatch` — ВСЕГДА ждать 2 мин и проверять `list`
- Если задача ушла в `triage`/`blocked` с `model_override` — `archive` + `create` новой с правильной моделью изначально
- `dispatch --max N` где N = количество задач для параллельного запуска
- `ready` задачи могут висеть бесконечно без `dispatch`
- Log analysis: `cat logs/<task_id>.log` | grep -E "HTTP|Error|Failed|API call failed"

## License & Sources
- **License:** MIT-0 (no attribution required, commercial use allowed).
- **Whitelist of source licenses:** MIT-0, MIT, Apache-2.0, ISC, Unlicense, 0BSD.
- **Excluded:** CC-BY*, GPL (all), Proprietary, anything requiring attribution/share-alike.
- **Clean-room:** rewritten from scratch in our own words; no verbatim copying of third-party text/structure.
- **Sources (verified):**
  - hermes-kanban-swarm-ops SKILL.md (local, emelya-agent) — operational patterns, failure recipes, cron-limited watchdog
  - Hermes Agent documentation — https://hermes-agent.nousresearch.com/docs