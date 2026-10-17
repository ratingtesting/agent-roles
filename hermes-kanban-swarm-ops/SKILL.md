---
name: hermes-kanban-swarm-ops
description: Operate Hermes kanban swarms — pre-flight verify skills, launch, debug worker crashes (Unknown skill / empty workspace), and recover from triage-loops. Use when running `hermes kanban swarm` with role-agents.
version: 1.2.0
author: emelya-agent
license: MIT-0
metadata:
  hermes:
    tags: [kanban, swarm, multi-agent, debugging, recovery]
    related_skills: [master-model-orchestration, semantic-corpus-cleaning, keelwright, agentic-skill-authoring]
---

## Hermes Kanban Swarm Ops

Launch and operate multi-agent swarms via `hermes kanban swarm` (workers → verifier →
synthesizer). This skill captures the failure modes that are NOT in the happy-path
docs — learned from real swarms that crashed on launch and took multiple fixes.

**Support files:** `scripts/keeper_wave.py` — approved minimal keeper (держит ровно N активных через SQL-подлив `archived → ready`; запуск: `python scripts/keeper_wave.py <board_slug> <N>`, обычный background-процесс, НЕ persist).

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
- **Возрождение из ДРУГИХ досок (урок 10.10.2026):** gateway-диспатчер глобальный — он ре-промоутит и спавнит НЕ только карточки текущей доски, а ЛЮБОЙ доски с `ready`/`blocked` (не archived) карточками. Запускаешь новый рой на `cjm-r7` → вместе с ним возродился `cjm-r6`, обе дали 200+ воркеров, машина повисла. Перед стартом НОВОЙ доски проверить `boards list` + статусы ВСЕХ досок проекта: любую старую с не-archived ready/running/blocked припарковать/архивировать, иначе её воркеры поднимутся следом. Статус «припарковано на нулевой доске» не защищает от остальных.

### 🔥 УРОК 20.09.2026 — `boards switch` = САМАЯ ОПАСНАЯ КОМАНДА (переключает ГЛОБАЛЬНУЮ доску для ВСЕХ)
**Инцидент:** в тесте ВИСП-роя использовал `hermes kanban boards switch layer1-v2-68` (глобальное переключение) + голый `hermes kanban list` без `--board`. В итоге между командами другой агент переключил активную доску на `g4-marketplace-strategy`, и мой голый `list` посмотрел ЧУЖУЮ доску (мои задачи «исчезли», я почти работал не там).

**ПРАВИЛО (жёстко):**
1. **`hermes kanban boards switch` — НЕ ДЕЛАТЬ НИКОГДА.** Это меняет активную доску ГЛОБАЛЬНО (для всех агентов) и сбивает чужие сессии. Даже при создании новой доски НЕ переключать — просто использовать `--board`.
2. **Каждая команда — с явным `--board <МОЯ>`**: `hermes kanban --board <B> list`, `--board <B> create`, `--board <B> dispatch`. Ни одной голой команды.
3. **Создание доски не требует switch:** `hermes kanban boards create <slug>` → дальше `hermes kanban --board <slug> ...` напрямую.
4. **Проверка после создания:** `hermes kanban --board <B> list` — заголовок `Board:` должен быть твой. Если не совпадает — СТОП.
5. Чужая доска = не моя. Не трогать, не читать задачи, не dispatch. Мой мир = МОЯ доска.

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
7. **Probe CARD for an unfamiliar pair (mandatory before a wave on a new model/provider, hard requirement for anything behind a local bridge).** A smoke test or `curl` answering proves LATENCY, not that an agent session completes: the worker's real request carries a huge system prompt, forced skills and a full tools array, and that shape fails independently of the fast path. Create ONE tiny card in the target board with the target model/provider and workspace («write a small file with a few dozen words in your workspace»), let the dispatcher spawn it, and require TWO facts: a completed `API call #…` line in `profiles/<profile>/logs/agent.log` AND the file on disk. Only then launch the N cards — for the whole wave. Measured cost of skipping it: a 3-card wave burned 20+ min at 0 completed calls / 0 files while direct probes answered in seconds; the wave could never have succeeded. Same board, same workspace, same `model_override`/`provider_override` as the real cards — a probe with a different shape re-introduces the false positive.

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

### КОНФИГ = ЕДИНСТВЕННЫЙ ИСТОЧНИК ИМЁН МОДЕЛЕЙ (урок 07.10, двойное наступание)
**СИМПТОМ:** карточки блочатся с `exit 78: provider rejected this profile's credential or model — requested model does not exist in our configuration`.
**ПРИЧИНА:** пользователь называет модель РАЗГОВОРНО («агнес 3.0», «дипсик 0731», «2.5 pro», «longcat 2.5»), а агент ставит это имя дословно в `model_override` → в провайдере такого ID нет → «model not found».
**ПРАВИЛО (жёстко):** разговорное название пользователя НИКОГДА не ставить в конфиг/карточки дословно. Сначала сверять фактические ID, потом маппить:
1. `hermes config get providers.<name>.models` → список реальных имён провайдера.
2. Маппить пилог: «агнес 3.0» → `agnes-3.0-flash`; «дипсик 0731» → `deepseek/deepseek-v4-flash-0731`. ЕСЛИ разговорного имени нет в списке — уточнить у пользователя фактический ID, не додумывать.
3. `provider` тоже брать из конфига (имя ключа провайдера), не из произвольной транслитерации.
**ОЗНАКОМИТЕЛЬНО:** текст «OpenRouter catalog» — встроенная формулировка каталога моделей Hermes, НЕ значит что используется openrouter. Это реестр всех известных моделей. Модель/провайдер только оттуда.

### МЁРТВЫЙ `.install.lock` в профиле ПРОВАНСИТ ВСЕХ ВОРКЕРОВ `exit 255` (урок 11.10.2026)
**СИМПТОМ:** все воркеры падают мгновенно до инициализации с `pid … exited with code 255`, в `last_failure_error` хвост `'dependency lock still held after 10.0s; continuing without it (…\installs\<hash>\.install.lock)'`. Модель/провайдер НЕ при чём — лог воркера обрывается на «preparing kanban_show», API-вызовов нет вообще.
**КОРЕНЬ:** пустой (0 байт) файл `.install.lock` в `HERMES_HOME\installs\<hash>\`, оставшийся от прерванного `hermes update`/install (возраст — дни/недели). Каждый стартуюший воркер ждёт этот лок до 10с и падает с 255. Это НЕ тот update-lock, что вешает CLI на «finishing an interrupted source update» (тот обходится `HERMES_DISABLE_LAZY_INSTALLS=1`); это файловый артефакт, который воркеры НЕ обходят флагом.
**ФИКС (проверить ПЕРВЫМ при массовом exit 255):**
```bash
ls -la "$HERMES_HOME"/installs/*/.install.lock   # пустой + старый = мёртвый
rm -f "$HERMES_HOME"/installs/<hash>/.install.lock
```
Хранилища с дефолтами: `installs/<hash>/.install.lock`. После удаления — вернуть мёртвые `running` в `ready` (SQL из «РОЙ ПОСЛЕ ОБРЫВА») и перезапустить. Воркеры стартуют и начинают API-вызовы. Диагностировать `.install.lock` по ПЕРВОМУ симптому, а не менять модель/провайдера — причина инфраструктурная.

### ДВА GATEWAY-ПРОЦЕССА ПОСЛЕ VBS-РЕСТАРТА → конфликт за dispatcher-lock (урок 11.10.2026)
**СИМПТОМ:** после подъёма gateway через `Hermes_Gateway.vbs` `/` убийства старых воркеров `powershell … Count` gateway = 2. CLI-диспатч отвечает `Spawned: 0`, в `gateway.log` диспетчер «holding singleton dispatcher lock» — второй процесс не может забрать и не диспатчит.
**КОРЕНЬ:** старый gateway-процесс не умер (VBS/трей-килл не всегда гасит предка), а автозапуск поднял второй. Два процесса держат один `.dispatcher.lock` — диспатч парализован.
**ФИКС:** оставить ОДИН gateway — самый свежий PID:
```powershell
$gws = Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -match "gateway run" }
$fresh = ($gws | Sort-Object -Property ProcessId -Descending)[0].ProcessId
foreach ($p in $gws | Select-Object -Skip 1) { Stop-Process -Id $p.ProcessId -Force }
```
Потом дождаться тика диспетчера (~60с) — один gateway берёт ready. НЕ дублировать gateway через VBS, пока жив старый: сначала `hermes gateway status` (нужно ровно одного), затем убить дубль.

### РОЙ «ЗАПУЩЕН» но python-процессов 0 → GATEWAY МЁРТВ (урок 07.10.2026)
**СИМПТОМ:** CLI `dispatch` пишет `Spawned: N`, задачи в running, но `ps -W | grep -i python` = 0 воркер-процессов, логи не пишутся, `gateway status` = `✗ No gateway process detected`.
**КОРЕНЬ:** диспатчер встроен в GATEWAY (`hermes gateway run`). Без живого gateway CLI `dispatch` только помечает spawned в БД, процессы НЕ поднимаются. Gateway умирает тихо при `hermes update`/перезагрузке (в логе `gateway.log` — «planned stop» в 23:25).
**ПРОВЕРКА ПЕРЕД ДИСПАТЧЕМ (обязательно):** `hermes gateway status` → должен быть `✓ Gateway process running (PID: N)`. Если `✗ No gateway process detected` — сначала поднять gateway, диспатчить бесполезно.
**ПОДНЯТЬ gateway на Windows (desktop НЕ может — Job Object убивает прямой spawn):**
1. `hermes gateway install` (ставит VBS в автозагрузку) — через UAC/scheduled task, если разрешено.
2. Лучший способ после отказа desktop-spawn — **перезагрузка Windows**: при входе `Hermes_Gateway.vbs` из Startup поднимает gateway сам. Проверить `hermes gateway status` = running после логина.
3. `hermes gateway start` из desktop может упасть с «killed by parent Job Object #91675» — это НЕ потеря, нужен login-item/reboot.
4. Если `hermes update` прерван («source-update completion failed») — gateway не поднимется, пока update не добьют: `hermes update` до «✓ Code updated!».
**ПОСЛЕ подъёма gateway:** проверить `hermes gateway status` = running, потом диспатч, потом `ps` — реальные процессы должны появиться.

### exit 78 «provider rejected» МОЖЕТ МАСКИРОВАТЬ ЗАВИСШИЙ UPDATE-LOCK (проверять ПЕРВЫМ)
**СИМПТОМ:** все воркеры падают мгновенно с `exit 78: provider rejected this profile's credential or model — requested model does not exist`, хотя модель и провайдер настроены ПРАВИЛЬНО. Соблазн — день искать несуществующую модель/провайдер.
**ПРАВИЛО:** перед любым set-model/сменой провайдера запустить `hermes update` — если он отвечает `Another Hermes update is already running (started Ns ago, process PID)` или `source-update completion failed: an update is still running`, то ВОРКЕРЫ падают ИЗ-ЗА update-lock (зависший `hermes_cli`-процесс держит монополию на инсталл), а НЕ из-за модели. Любая `hermes chat`-зависимость (воркеры, cron, watchdog) в этот момент падает с ложной моделью-ошибкой.
**ФИКС:** добить себя `hermes update` до `✓ Code updated!`, либо при апруве — перезагрузка/убийство зависшего update-процесса.
**БЫСТРЫЙ ОБХОД ДЛЯ АВТОМАТИЗАЦИИ:** CLI блокируется на строке «finishing an interrupted source update...» при каждом вызове, если дерево «грязное» (незакоммиченные правки — напр. правки провайдеров, сделанные пользователем). Это НЕ значит, что нужен update. Обойти блокировку: `HERMES_DISABLE_LAZY_INSTALLS=1 hermes <команда>` — CLI отвечает мгновенно, gateway перезапускать не надо. Ставить флаг в env каждого вызова из скрипта/автоматизации (`subprocess.run(..., env=env)`), не глобально. Диагностика «проверь самый дешёвый симптом первым» экономит день хождения от модели к модели, когда причина совсем в другом.

### МАССОВОЕ ВОССТАНОВЛЕНИЕ: сначала показать маппинг, потом применять
**ПРАВИЛО:** когда нужно переключить много карточек на другую модель/провайдера (массовый fix после блоцка), СНАЧАЛА вывести таблицу `разговорное имя → документированный ID → провайдер` из конфига и ПОЛУЧИТЬ ОК пользователя, ПОТОМ батчить. Не применять `model_override` на сотни карточек по догадке — это и есть «действуешь не по скиллу».
- Конвертировать массово — прямым SQL UPDATE в `kanban.db` (таблицы `tasks`, колонки `model_override`/`provider_override`), а не `set-model` по одной (сотни × 2-3с = часы; SQL — мгновенно). Диспатчер читает из БД.
- Лимит пользователя на параллельность («не более N») — это ДИРЕКТИВА, а не подсказка: явно вернуть лишние карточки в `blocked`, оставить ровно N в `ready`.
- Изменение провайдера по своему усмотрению (даже «исправить» на единственно корректный по конфигу) — самоволие: провайдера/модель пользователь выбирает, агент сводит к документированному имени и выполняет.

### НЕ ПЕРЕОПРЕДЕЛЯТЬ ПРОВАЙДЕРА ПО СПИСКУ `models` В КОНФИГЕ (урок 08.10.2026 — ярость пользователя)
**СИМПТОМ:** пользователь явно называет модель + провайдера («дипсик 0731 строго на опенроутер, не опенроутер2»}. Агент смотрит `hermes config get providers.<name>.models` — в списке провайдера `openrouter` только 2 чужие модели (z-ai/glm-5, nex-agi/nex-n2), без base_url и без key_env, deepseek там НЕТ. Агент решает «deepseek на openrouter не существует» и «исправляет» на `openrouter2` (где deepseek числится в конфиге). Пользователь в ярости: провайдер выбран явно, а агент молча подменил его.
**КОРЕНЬ:** список `models` у провайдера в config.yaml — НЕ исчерпывающий whitelist того, что провайдер может обслуживать, и НЕ признак неработоспособности связки. Это карта каталога, а не ограничение. Если ЗАЯВЛЕННАЯ активирована модель чата = та самая пара (model, provider), которую называет пользователь (см. системное сообщение runtime), — ЭТО ПРОВЕРОЧНОЕ ДОКАЗАТЕЛЬСТВО, что связка работает.
**ПРАВИЛО (жёстко):**
1. Когда пользователь явно называет `модель + провайдера` И эта пара совпадает с активной (model, provider) текущей сессии (`deepseek/deepseek-v4-flash-0731` via `openrouter`) — применить ДОСЛОВНО, без перепроверки по списку `config get providers.<name>.models`.
2. Список `models` провайдера в конфиге — только для МАППИНГА разговорных имён пользователя в документированный ID модели (когда ID модели неизвестен). Он НЕ ломает пару, которую уже доказала активная сессия.
3. Провайдера по своему усмотрению НЕ менять НИКОГДА, даже если «в конфиге у `openrouter` нет этой модели». `openrouter2` ≠ `openrouter` для пользователя — это разные вещи, и подмена вызывает абсолютную потерю доверия.
4. Если есть сомнение в работоспособности связки — СНАЧАЛА спросить пользователя, показав факт («в списке провайдера модели нет, но активная сессия на ней работает — ставим?»), НЕ молча подставлять другой провайдер.
5. `hermes chat --model X --provider Y -Q -q "say ok"` как тест работоспособности НЕ переопределяет явный выбор пользователя: если короткий вызов отвечает — связка рабочая, ставить как названо.
6. **Авторитетный список моделей провайдера — НЕ config `models`, а живой эндпоинт:** для OpenAI-совместимого локального прокси (`opencode-local` на `http://127.0.0.1:8932/v1`) перечислить реально доступные модели через `curl http://127.0.0.1:8932/v1/models` (поле `data[].id`). В config-снимке модели МОГУТ отсутствовать (`step-5-preview-free`, `longcat-2.5-preview-free` числились в прокси, но НЕ в конфиге), а прямой `curl -d '{"model":"<id>",...}' /chat/completions` подтверждает рабочесть «вживую». Не заявлять «модели нет на провайдере» только по config-списку — сначала проверить живой эндпоинт/вызов.
### Пискул longcat-2.5-preview-free: это opencode-local, НЕ nous (урок 07.10.2026)
- **БEARCHЧАЯ модель агента: `longcat-2.5-preview-free` — belongs провайдеру `opencode-local`** (`http://127.0.0.1:8932/v1`), а НЕ nous. Если поставить её с `--provider nous` → `provider rejected this profile's credential or model (exit 78)`, потому что nous не знает такой модели.
- **У nous КРОМЕ того есть длинный 2.5: `meituan/longcat-2.5-preview:free`** (проверено: `hermes chat -Q -q "say ok" --model meituan/longcat-2.5-preview:free --provider nous` → `ok`). Это ТА модель, которую пользователь называет «Meituan LongCat 2.5 Preview». Разговорное «лонгкат 2.5» надо маппить именно сюда, НЕ в голый `longcat-2.5-preview-free`.
- Резюме трёх похожих имён (часто путают): `longcat-2.5-preview-free` = opencode-local; `meituan/longcat-2.5-preview:free` = nous; `meituan/longcat-2.0:free` = nous (старая, из MODEL_TABLE). Разные провайдеры и версии — сверять в `hermes config get providers.<name>.models` перед set-model.

### Windows cmd ломает кириллицу в аргументах `hermes ... create` (урок 09.10.2026)
**СИМПТОМ:** `hermes kanban create '<Title с кириллицей>' --body-file <кир.путь>` из python subprocess → `rc=255`, stderr `The filename, directory name, or volume label syntax is incorrect`. Первые карточки создались, следующие — нет.
**КОРЕНЬ:** на Windows при запуске через `hermes.cmd` (cmd-обёртка → PowerShell) кириллические аргументы (title, путь body-file) не передаются как Unicode, cmd/PS портят их на split по аргументам → «filename incorrect».
**ПРАВИЛО:** при массовом `create` из скрипта: `title` — ТОЛЬКО ASCII (например `R5-001 BUY`, рабочий контекст всё равно в body и workspace `dir:`), а `--body-file` — копия тела в ASCII-путь (`C:\Users\Unicorn\AppData\Local\hermes\cache\scratch\r5_body_0001.md`), не в проектную папку с кириллицей.
**subprocess из execute_code:** НЕ использовать `bash -c 'hermes ...'` (bash-ветка резолвит `hermes` в WSL-обёртку → «Windows Subsystem for Linux не установлен»). Вызывать явный `C:/Users/Unicorn/AppData/Local/hermes/bin/hermes.cmd` (или `.exe`) списком аргументов без bash, `capture_output=True` БЕЗ `text=True` (иначе UnicodeDecodeError на кириллице вывода), декодировать stderr вручную.

### СОЗДАВАТЬ СОТНИ КАРТОЧЕК ПРЯМЫМ SQL INSERT, НЕ CLI `create` (урок 09.10.2026)
**СИМПТОМ:** массовый рой (сотни однотипных карточек из пула фраз). Через `hermes kanban create` каждая карточка стоит ~25-30с (старт CLI на Windows) → 300 карточек = 2+ часа; скрипт при этом падает/умирает на середине (access-violation subprocess, crashe).
**ПРАВИЛО:** для сотен однотипных карточек НЕ гонять CLI по одной. Писать тела в ASCII-путь (`hermes cache/scratch/r5_body_NNNN.md`), затем вставлять строки в `kanban.db` напрямую через `INSERT INTO tasks` — секунды на все:
```sql
INSERT INTO tasks
 (id,title,body,assignee,status,created_at,workspace_path,
  skills,model_override,provider_override,goal_mode,max_retries,block_recurrences)
VALUES ('t_'+hex8, 'ASCIItitle', body, 'swarm','ready', ms_now, outdir,
  '["cjm-chain-architect"]', model, prov, 'default', 2, 0);
```
- `id` = `t_` + 8 hex (как у штатных). `status='ready'` — оркестратор сам подрежет до лимита по модели.
- **КОЛОНКИ WORKSPACE В SQL — РАЗДЕЛЬНО (урок 13.10.2026):** в БД писать `workspace_kind='dir'` И `workspace_path='C:\...\папка'` ДВУМЯ отдельными значениями. В CLI флаг `--workspace dir:<path>` — это парсинг CLI, в БД так НЕ хранится: `workspace_kind='dir:<path>'` → диспатчер крашится `workspace: unknown workspace_kind: dir:...`, все карточки уходят в blocked (замерено: 16/16 заблокированы разом, `max_retries` 1-2 сжигает партию мгновенно). Папку создать заранее (`os.makedirs`).
- `workspace_path` — папка из тела; создать её заранее. `body` — полный текст задания (шаблон со скиллом+запретами+ПУЛ).
- ОБЯЗАТЕЛЬНО предварительно `SELECT` существующие `title`/`workspace_path` и пропускать их (возобновляемость при перезапуске).
- CLI `create` оставлять для единичных/особых карточек, не для пайплайна из сотен.

### РОЙ ПОСЛЕ ОБРЫВА СВЯЗИ: массово вернуть осиротевшие `running` в `ready` SQL-ом
**СИМПТОМ:** интернет/шлюз падал → все воркеры убиты, но сотни задач висят в `running` с мёртвыми pid (процессы не существуют). Очередь `ready` пуста, `done` не растёт, диспатчер «залип» (нечего брать).
**ДИАГНОСТИКА:** сверить `worker_pid` задач статуса `running` с живыми python-процессами (`ps -W | grep python`); если pid нет в списке — воркер мёртв, статус врёт. Также `grep 502 logs/<task>.log` — массовый поток 502/timed out указывает на обрыв сети, а НЕ на дедлайн/модель.
**ФИКС (массово, не по одному archive+create):**
```sql
UPDATE tasks SET status='ready', worker_pid=NULL, claim_lock=NULL,
 current_run_id=NULL, consecutive_failures=0, last_failure_error=NULL
WHERE status='running' AND worker_pid NULLOR-not-alive;
```
потом разблокировать `blocked`→`ready` тем же SQL и перезапустить оркестратор/диспатч. Задачи при этом НЕ теряют тело/workspace — воркер просто стартует заново.
**Диагностика первым делом:** при лавине провайдерских ошибок (502/timeout/quota во многих логах сразу) СНАЧАЛА проверить сеть (`socket.create_connection` к base_url провайдеров), а не менять модели/дедлайн. Если сеть вернулась — воркеры заработают сами после перезапуска.

### ЧЕК-ЛИСТ ПОСЛЕ ЗАВЕРШЕНИЯ РОЯ (12.10.2026 расширен — рой закончился, мусор остался)
1. Снять keeper-крон сразу по `ROY_DONE` (не ждать истечения repeat): завершённый job `r7-wave-keeper` всё равно висел в списке.
2. Убить осиротевшие `browser_harness.daemon` — по одному на воркера (8 шт × 50 МБ переживают рой).
3. Проверить чужие watchdog-кроны по закрытым доскам: удалено 4 мёртвых сторожа (orchestrator-watchdog пинался к hy3:free — модель мертва, cron_cleaner.ps1 — .ps1 не запускается python-раннером, swarm-classify, vibe-board-watchdog).
4. `Disable-ScheduledTask` для keepalive'ев мёртвых проектов (VibeBoardKeepalive каждые 10 мин дёргал cmd.exe → МЕЛЬКАНИЕ окон node/cmd; скрипты через .cmd в Task Scheduler всегда мелькают).
5. НЕ трогать осмысленный автозапуск: Hermes_Gateway.vbs (нужен), OpenCode_8932/8933.vbs (прокси), JEV-Paper-Bot.cmd (торговый бот владельца, paper-only), freellmapi/terminal-services lnk (hindsight).
6. Проверка чистоты: `Get-CimInstance Win32_Process` по node/cmd/python + `work kanban`/`browser_harness` матчинг; `cron list` по всем профилям.

### АВТОНОМНЫЙ ОРКЕСТРАТОР «ровно N воркеров на модель» (ночной безаккупный прогон, урок 09.10.2026)
**ЗАДАЧА:** пользователь уходит спать и просит держать ровно N воркеров на каждую из нескольких моделей, ротировать следующие N по завершении, без ручного диспатча. Условие — ПК не уснёт.
**ПОЧЕМУ НУЖЕН ДЕМОН:** gateway сам диспатчит готовые `ready` каждые ~60с и ЗАБИРАЕТ ВСЕ ready разом — без ограничения «по модели». Чтобы не спавнить сотни сразу (Windows ломает форки >36) нужен балансировщик, а не ручной `dispatch`.
**РЕШЕНИЕ — persist Python-демон, который каждые ~90с читает `kanban.db` напрямую (без CLI) и правит статусы SQL-ом:**
```python
# каждые INTERVAL сек, для каждой модели из списка:
# 1) active = running + ready
#    если active > TARGET: excess = active - TARGET, старые ready → blocked (самые свежие оставить)
# 2) need = TARGET - running; если need>0 и есть blocked: промоутить need шт → ready
# 3) автоназначение: UPDATE tasks SET assignee='swarm' WHERE status='ready' AND assignee IS NULL
# запуск: python orchestrator.py  c background=true, persist_on_release=true
```
- **Диспатч делает gateway** (готовые ready он берёт сам). Демон только держит баланс ready/running по статусам — НЕ вызывает `dispatch`.
- **ЖЁСТКИЙ ПОТОЛОК: promote только при `ready + running < TARGET`, НЕ «когда running < TARGET».** Демон, который при `running < TARGET` промоутит 1 карточку за тик, при медленном/мёртвом gateway НАКАПЛИВАЕТ ready (замерено: 161 ready за 150с при 0 живых воркеров), а когда gateway оживает — он забирает ВСЕ накопленные ready разом → всплеск сотен процессов = тот самый «оркестратор угробил компьютер». Условие промоции должно быть `(running + ready) < TARGET`, и после каждого тика СВЕРЯТЬ, что ready не превысил потолок.
- **ПРЕДПОЧТЕНИЕ ВЛАДЕЛЬЦА (жёсткое, директива):** НЕ строить кастомный python-оркестратор-цикл вообще. «Промоутер/автоподлив, который только правит статусы blocked→ready в БД (gateway сам спавнит)» — ЭТО ТОТ ЖЕ запрещённый оркестратор (окружен 10.10.2026): gateway и так ре-промоутит blocked→ready сам, так что кастомный подлив не «держит ровно N» в работе, а только добавляет второй конкурирующий цикл. НЕ писать его под видом «безопасного голого SQL-подлива». Правильный путь — ШТАТНЫЙ `hermes kanban --board <B> dispatch --max N` и/или ограничение числа `ready`-карточек в БД (остальное в `blocked`), и пусть их забирает встроенный gateway-диспатчер. Кастомный цикл — только если явно попросили и с потолком выше + `background=true` (не persist).
- **НЕ запускать с `persist_on_release=true`** — persist-цикл переживает перезагрузку и плодит зомби-оркестраторов (см. раздел «МНОЖЕСТВЕННЫЕ persist-оркестраторы» НИЖЕ). Только обычный `background=true`; после перезагрузки/обрыва перезапустить демон вручную.
- **Различные лимиты по моделям — словарь TARGETS, а не одна константа:** когда на одной модели нужно «сразу 25», а на остальных по 5 («step-5-preview-free — сразу 25 и дальше по 25; у остальных — по 5»), задавать `TARGETS = {модель: лимит}`, а в цикле `tgt = TARGETS.get(model, TARGET)`. Лимиты ПОМОДЕЛЬНО от пользователя — это прямое указание, не единый N; разводить их по-разному.
- Лимит «не более N на модель» — это ДИРЕКТИВА: держать ровно N готовых, лишние в `blocked` (иначе gateway возьмёт все ready разом).
- Логировать каждый тик: `running=N реж.ready=M подвиг.blocked=K` в файл — утром видно, где рой застрял.
- **Демон умирает с обрывом/перезагрузкой** — после восстановления сети: вернуть осиротевшие `running`→`ready` SQL-ом (см. раздел «РОЙ ПОСЛЕ ОБРЫВА») и перезапустить демон.

### МНОЖЕСТВЕННЫЕ persist-оркестраторы плодятся зомби после перезагрузки (урок 09.10.2026)
**СИМПТОМ:** куча python-процессов тормозят систему, на доске 149 «running» при 0 живых воркеров. Причина: запускал оркестратора-цикл с `persist_on_release=true` — он ПЕРЕЖИЛ перезагрузку, а после рестарта запускался ещё один (`hermes`-сессия сама не гасит persist-процессы корректно). Каждый оркестратор по своему тику спавнил воркеров → процессы множились, ПК висел. Пользователь убил их вручную (taskkill python).
**ПРАВИЛО (жёстко):**
1. Оркестратор/диспетчер-цикл (мониторит доску, промоутит blocked→ready, спавнит) НЕ делать с `persist_on_release=true`. Только обычный `background=true` фоновый процесс — он умрёт вместе с Hermes/сессией и НЕ переживёт перезагрузку.
2. Если нужен автозапуск после ребута — использовать перезапуск gateway-диспетчера (embedded в gateway), а не отдельный persist-цикл.
3. После перезагрузки/обрыва ВСЕГДА проверять: `tasklist | grep python` — сколько реальных процессов vs `SELECT COUNT(*) FROM tasks WHERE status='running'` в kanban.db. Если running есть, а python-процессов нет — мёртвые записи; сбросить их в ready (`UPDATE tasks SET status='ready', worker_pid=NULL, claim_lock=NULL, current_run_id=NULL WHERE status='running'`).
4. persist_on_release оставлять только для каждой-то полностью автономной задачи с явной командой владельца, НЕ для общих оркестраторов.

### НЕ ЗАПУСКАТЬ СОТНИ ВОРКЕРОВ РАЗОМ: «нет лимитов у модели» ≠ «нет предела у машины» (урок 10.10.2026)
**СИМПТОМ:** `dispatch --max 252` одной командой («модель платная, лимитов нет — запускай все сразу»). Итог: все 252 в `running`, но 0 результатов за 30+ мин; в `profiles/swarm/logs/errors.log` массово `No shell found. Hermes needs bash (Git for Windows on Windows)` + 502; даже `tasklist`/`write_file` таймаутятся — машина задыхается. Расход прогона ×6 против прошлого при похожем числе воркеров.
**КОРЕНЬ (двойной):**
1. **Ресурсный предел Windows.** Сотни одновременных python-форков не поднимают bash → воркер не может выполнить ни одной команды (ни read скилла/гайда, ни write результата) → каждый шаг падает.
2. **Каждый retry = повторная отправка ВСЕГО контекста.** Агентный воркер шлёт весь контекст на КАЖДОМ шаге; при ~82K токенов задания и ~14 вызовах на воркера это ×6 input-токенов. Замерено: 2716 вызовов / 187 сессий = 14.5 вызова на воркера, 84.5M input против 14.2M у прошлого прогона.
**ПРАВИЛО (жёстко):** платный провайдер снимает rate-limit, но НЕ спасает от перегрузки МАШИНЫ. Предел — не число форков и не РАМ как таковой (замерено: 64 ГБ машина висла при ~13 ГБ занятых воркерами), а **ВЕС ВОРКЕРА = контекст × число шагов**. Агентный воркер — это полный `python -m hermes_cli.main` ≈ 250–300 МБ + держит весь контекст на КАЖДОМ шаге. Реальный коррелят зависания — размер контекста на воркера, а не счётчик процессов.
1. **Параллельность определяется ВЕСОМ воркера, а не счётчиком и не «свободной РАМ».** Доказано на одном и том же пуле: прогон из 128 лёгких воркеров (пулы 3–5 фраз, ~111K токенов/воркора) прошёл БЕЗ зависания за час; прогон из 50 тяжёлых (пулы 12–14 фраз, ~371K токенов) повесил машину. Тяжёлый воркер живёт 20–40 мин, держит весь контекст → N тяжёлых хуже, чем 4N лёгких.
2. **Чтобы запустить МНОГО параллельных — уменьшай ПУЛ, а не только число воркеров.** Меньший пул (5–7 фраз вместо 12–14) = воркер легче и завершается быстрее → доступно намного больше одновременно, без потери качества цепочки. Качество одной цепочки (ствол, звенья, психология, развилка) не зависит от размера пула — воркер просто делает меньше цепочек за запуск. Это РОВНО схема первого успешного прогона.
3. **`dispatch --max N` САМ промоутит `blocked → ready` и уводит счётчик за N.** После dispatch проверить `SELECT status, COUNT(*) ... GROUP BY status` — если ready/running перевалили за желаемое N, вернуть лишние в безопасный статус SQL-ом: `UPDATE tasks SET status='archived' WHERE id IN (SELECT id FROM tasks WHERE status IN ('ready','running') ORDER BY created_at DESC LIMIT <лишние>)`. НЕ возвращать лишние в `blocked` — gateway их ре-промоутит и переспавнит в тот же всплеск (см. «ОСТАНОВКА РОЯ: blocked НЕ ОСТАНАВЛИВАЕТ»).
4. **Диспатчер молча пропускает карточки с `assignee IS NULL`** — вывод `Skipped (unassigned)`, `Spawned: 0`. Перед dispatch батчем: `UPDATE tasks SET assignee='swarm' WHERE assignee IS NULL` (с карточками, созданными прямым SQL INSERT, это происходит по умолчанию — INSERT не заполняет assignee).
5. **Симптом OOM-suspend ≠ мёртвый воркер:** процесс в tasklist «заморожен на уровне ядра, CPU не ест» (PID есть, WorkingSet ~268 МБ, 0% CPU) — это не зависание и не падение, а приостановка из-за давления на память. Лечится сокращением числа/веса воркеров, НЕ рестартом gateway/сменой модели.
6. Если пользователь уже убил воркеров «потому что всё висит» — СНАЧАЛА припарковать карточки (`UPDATE ... SET status='blocked' WHERE status IN ('running','ready')`), ПОТОМ отвечать/планировать. Не отвечать и не перезапускать, пока БД полна dead running/ready.

### СХЕМА «ВЕС ВОРКЕРА × ОБЪЁМ ПУЛА» — ИЗМЕРЕННЫЙ БАЛАНС ДЛЯ ПЛАНИРОВАНИЯ ВОЛН
Размер пула = РЫЧАГ, который меняет и параллельность, и листьев/воркера, и число синтезов. Замерено на готовых цепочках (переиспользовать эти числа для оценки, не мерить каждый раз):

| класс воркера | пул (фраз) | листьев/цепочку | цепочек/карточку | листьев/воркера | параллельно (эта машина, 64 ГБ) |
|---|---|---|---|---|---|
| лёгкий | 3–5 | 2.6 | 1.29 | ~3.3 | 60–80 |
| средне-лёгкий | ~8 | — | — | ~7.8 | **~10 (измерено: 25 глушат, 50 зависли)** |
| тяжёлый | 12–14 | 10.1 | 1.0 | ~10.1 | ~12 |

**Расчёт числа воркеров на пул:** `воркеров = остаток_фраз ÷ листьев_на_воркера`; **время** = `воркеров ÷ параллельность` волн. Тяжёлый даёт в 3× больше листьев/воркера, чем лёгкий (10.1 против 3.3), поэтому требует втрое меньше воркеров — но при параллельности ~12 волн получается СТОЛЬКО ЖЕ, сколько у лёгкого (14 волн при 60–80). Выигрыш тяжёлого — НЕ скорость, а **качество**: большой пул даёт реальные фразы для листьев/звеньев и реже требует синтеза (§2.7).

**ПРЕДПОЧТЕНИЕ ВЛАДЕЛЬЦА (директива):** работаем с ТЯЖЁЛЫМИ воркерами (12–14 фраз), потому что размер пула влияет на подбор фраз — нет фраз → приходится синтезировать, а владелец ценит реальные фразы выше скорости. Средне-лёгкий (пул ~8, структура с ветками, параллельно 50) — это компромисс «побольше листьев, чем лёгкий, но недорого»; его брать, когда чисто тяжёлые не умещаются в целевую параллельность. НЕ предлагать лёгкие (3–5) как основной режим — только если сам владелец их запросил.
**Субагенты (`delegate_task`) НЕ решают проблему веса:** каждый субагент — тот же `python -m hermes_cli.main` ~268 МБ + полный контекст, а `delegation.max_concurrent_children` по умолчанию = 10 (МЕНЬШЕ, чем даже пара волн канбана). Это НЕ способ «запустить много параллельно тяжёлых» — для канбановских волн это предел ниже. Параллельность канбана регулировать числом `ready`-карточек, не делегированием.

### СЧЁТ И РАЗБОР СТОИМОСТИ РОЯ — таблица `session_model_usage`
Профиль swarm пишет токены/цену в `...\profiles\swarm\state.db`, таблица `session_model_usage` (колонки `model, api_call_count, input_tokens, output_tokens, cache_read_tokens, estimated_cost_usd, actual_cost_usd, first_seen, last_seen`):
```sql
SELECT model, COUNT(*) sess, SUM(api_call_count) calls, SUM(input_tokens) in_tok,
       SUM(cache_read_tokens) cache, SUM(estimated_cost_usd) est
FROM session_model_usage GROUP BY model ORDER BY SUM(input_tokens) DESC;
```
Диагностика «дорого и без результата»: `calls/sess` > ~10 и input-токены на порядок выше прошлого прогона = retry-шторм или раздутый контекст задания. Группировать по дню `first_seen`, чтобы отделить текущую партию от прошлых. Это единственный честный источник цены — не оценка «на глаз».

### ОСТАНОВКА РОЯ: `blocked` НЕ ОСТАНАВЛИВАЕТ — gateway ре-промоутит и спавнит (урок 10.10.2026, исправлено)
**СИМПТОМ:** пользователь убил процессы («всё висит → убил через трей»), агент перевёл карточки в `blocked` и доложил «рой остановлен». Через время рой СНОВА в `running` и грузит машину (`рой 6 снова стартанул!`), одна доска `running=202`, вторая — `running=47` после того как их припарковали в `blocked`.
**КОРЕНЬ (вскрыт на практике):**
1. **`status='blocked'` — НЕ парковка.** Диспатчер (и CLI `dispatch`, и встроенный в gateway тик) САМ ре-промоутит `blocked → ready` и спавнит воркеров. Перевести в `blocked` и уйти — это не остановка, «рой воскреснет» на следующем тике/старте.
2. **Убить процессы недостаточно, если жив VBS-автозапуск.** `Hermes_Gateway.vbs` в автозапуске Windows (`hermes gateway install`) поднимает gateway заново после трей-килла, а gateway при старте видит мёртвые `running`/`blocked` и поднимает воркеров.
**ПРАВИЛО:** чтобы рой ГАРАНТИРОВАННО остановить, `blocked` не хватает. Сделать ОБА:
1. Припарковать SQL-ом (это очищает pid/claim, но не является конечной остановкой):
```sql
UPDATE tasks SET status='blocked', worker_pid=NULL, claim_lock=NULL, current_run_id=NULL WHERE status IN ('running','ready');
```
2. **Остановить источник возрождения:** `hermes gateway stop` + убрать/переименовать `Hermes_Gateway.vbs` из Startup (или `hermes gateway uninstall`), иначе любой старт gateway снова поднимет рой. Архив задач (`hermes kanban --board <B> archive <id>`) — единственный статус, который gateway НЕ ре-промоутит.
Проверить после остановки: `SELECT status, COUNT(*) FROM tasks GROUP BY status` (нет running/ready) И `tasklist | grep python` (нет живых воркеров) И `hermes gateway status` (нет возрождающего процесса). При «пользователь уже убил процессы» НЕ докладывать «остановлено» только по нулевому процессу — проверить, что карточки не running/ready и gateway-автозапуск снят.

### READY-карточки, которые диспатчер не берёт → STALE `claim_lock` (урок 07.10.2026)
**СИМПТОМ:** модель/провайдер настроены ПРАВИЛЬНО (прямой `hermes chat` отвечает `ok`), карточки в `ready`, но и CLI `dispatch --max N`, и встроенный gateway-диспатчер возвращают `Spawned: 0`. Рой стоит с ready-очередью, хотя всё «готово».
**КОРЕНЬ:** у ready-карточки висят остатки `claim_lock` + `current_run_id` от МЁРТВОГО воркера (поле `claim_lock=Win11-<user>:<old_pid>`). Диспатчер считает карточку всё ещё заявленной и не берёт её. Это обычно после обрыва связи/перезагрузки: воркер умер, но claim в БД не освободился.
**ДИАГНОСТИКА:** в БД канбана: `SELECT id,claim_lock,current_run_id,worker_pid FROM tasks WHERE status='ready'` — если `claim_lock`/`current_run_id` заполнены при `pid=None` — stale.
**ФИКС (прямым SQL, мгновенно):**
```sql
UPDATE tasks SET claim_lock=NULL, claim_expires=NULL, current_run_id=NULL, worker_pid=NULL
WHERE status='ready' AND claim_lock IS NOT NULL;
```
ПОТОМ `dispatch --max N` → появляется `Spawned: N`.

### ДИСПАТЧЕР «ЗАЛИП» (CLI возвращает 0, gateway сам молчит) → рестарт gateway
**СИМПТОМ:** CLI-диспатч даёт `Spawned: 0` из-за singleton-лалока (диспатчер встроен в gateway — CLI не может), а сам gateway НЕ берёт ready-карточки; в `gateway.log` строки `spawned`/`reaped` прекратились. Причина: диспатчер залип после серии падавших воркеров (например все падали на битой модели) и перестал тикать.
**ДИАГНОСТИКА:** смотреть НЕ только CLI-вывод, а `grep -aE 'dispatcher|spawned|reaped' logs/gateway.log` — там реальная активность диспатчера и его тики (`embedded in gateway (interval=60s)`). Если после 22:00 нет `spawned` — залип.
**ФИКС:** `hermes gateway stop` (clean drain) → `hermes gateway start` → проверить `gateway status` = running → `dispatch --max N` / дождаться тика. Рестарт gateway безопасен при 0 running-воркеров.

### СРЕДНЕ-ЛЁГКИЙ ВОРКЕР (пул 8) + СТРУКТУРА «КОРЕНЬ-СТВОЛ-ВЕТКИ-ЛИСТЬЯ» (решение 10.10.2026)
**Три типа воркера по листьям/воркера — выбор по ресурсам:** лёгкий (пул 3–5, ~3.3 листа) → много синтеза;
средне-лёгкий (пул 8, ~7.8 листа) → золотая середина, синтез средний; тяжёлый (пул 12–14,
~10.1 листа) → мало синтеза, но вешает машину при >12 параллельно (50×268МБ+20-40мин = заморозка ядра).
**Правило:** при весе машины НЕ гнать тяжёлых >12. Задание воркеру на пул 8: «собери всю однотемную
фразу листом, сгруппируй в ВЕТКИ, ветки сходятся в ОДИН ствол → развилку гайд|услуга».
BOFU-лист → цепочка 3 узла (вводная запрещена); TOFU/MOFU → 5 узлов. Прогноз карточек =
остаток_фраз / листьев_на_воркера (на пул 1567 → 202 карточки при пуле 8).
**ПРЕДЕЛ ПАРАЛЛЕЛЬНОСТИ СРЕДНЕ-ЛЁГКИХ (ИЗМЕРЕНО, НЕ «предположение»):** 50 НЕ держится. 25 воркеров
(пул 8, deepseek/openrouter) СИЛЬНО глушили машину — пользователь дважды убил все процессы и снизил
порог: «25 очень сильно глушат, давай 10». Реальный безопасный старт для этого размера воркера — **~10**,
поднимать вверх только после замера прироста `done` за окно. НИКОГДА не запускать первый заход на
25/50 исходя из таблицы — тяжеловесность воркера (контекст × шаги) на конкретном столе может быть выше
предположения; клиенты убивают процессы, а не ждут. Модель/direction: сначала 10, мерить, потом решать
больше или нет. Это директива владельца: стабильность ПК важнее скорости.
**Волновой подлив (ИСПРАВЛЕНО 10.10.2026 — только через archive, НЕ blocked):** держать ~N в ready, остальные карточки НЕ в blocked, а в **archived** (`hermes kanban --board <B> archive <id>...`) — gateway ре-промоутит `blocked→ready` и спавнит его (ровно то, что воскрешало рой), а архивированные НЕ трогает. Процедура запуска ровно N: (1) всё припарковать SQL-ом и ЗААРХИВИРОВАТЬ не-таргетные; (2) промоутить ровно N в ready; (3) поднять gateway — он возьмёт только эти N ready; (4) НЕ вызывать `dispatch --max N` повторно — он сам ре-промоутит blocked (уже proven). По завершении N — вручную промоутить следующую партию из archive (unarchive) → gateway доберёт. "`blocked` как парковка" — УПРАЗДНЕНА, это ловушка возрождения.

### АВТОПОДЛИВ = 2 УРОВНЯ: тики gateway + КОНЕЧНЫЙ КРОН (уточнено 12.10.2026)
**Уровень 1 — штатный gateway-диспетчер (interval=60s):** на каждом тике спавнит ВСЁ, что стоит в `ready`.
Логи r7: `spawned=10 → 1 → 6 → 2 → 2` — это добор внутри уже выставленной партии: воркер завершился,
следующий из ready ушёл на его место. **Но: как только ready пустеет — рой встаёт. Диспетчер НЕ промоутит
blocked/archived сам.** Ошибка прошлой формулировки «автоподлив полностью штатный» — штатен только в
пределах готовой партии.
**Уровень 2 — ОГРАНИЧЕННЫЙ КРОН-промоутер (одобренный путь для hands-off, директива владельца):**
no_agent-крон с однотиковым скриптом (НЕ живой цикл из сессии — это запрещённый оркестратор!):
```python
# scripts/promote_r7_once.py — один проход: active<15 → поднять из archived в ready
# + чистка мёртвого install.lock (пустой >10 мин)
```
`cronjob create --name r7-wave-keeper --schedule "every 5m" --repeat N --no-agent --script promote_r7_once.py --deliver local`
`repeat = ceil(1.5 × (волн × ~45мин) / 5мин)` — крон конечен, сам умирает, зомби не оставляет.
**ЗАПРЕЩЕНО:** python-цикл `while True` в background (keeper-цикл 12.10 поймал владелец: «не по скиллу»).
Правильно: однотиковый скрипт + конечный крон. Проверка: `active=15 promo=0` в stdout крона = волна держится.
(Логи-доказательство уровня 1: `10:36 spawned=10 → 10:53 spawned=1 → 10:55 spawned=6` — добор из пустеющего ready.)
**Живость роя:** `grep -a 'kanban dispatcher [cjm-r7-buy]' logs/gateway.log` — строки `spawned=N` = тики; прирост done за окно — реальный прогресс. `archived` диспетчер НЕ трогает — это «вне игры». НЕ повторять `dispatch --max N` ради подлива (CLI конкурирует с embedded → `Spawned: 0`).
**KEEPER (одобренный владельцем вариант «без пробуждения агента»):** когда владелец просит, чтобы волны шли без его команд и без агента в сессии, допустим МИНИМАЛЬНЫЙ keeper-цикл (не запрещённый оркестратор), если он соблюдает ВСЕ: (1) только поднимает статусы `archived → ready` SQL-ом, НИКОГДА не спавнит процессы и не вызывает dispatch (спавнит штатный gateway-тик); (2) потолок промоции — `ready+running < TARGET`, иначе не льёт (защита от накопления всплеска); (3) обычный `background=true`, НЕ persist — умирает с сессией/ребутa; (4) сам завершается, когда `archived` и активные пусты; (5) чистит мёртвый `.install.lock` (пустой, >10 мин) на каждом тике — он после update/киллов появляется снова и подвешивает ВСЕХ новых воркеров с exit 255. Пример цикла: каждые 120с `UPDATE tasks SET status='ready', claim_lock=NULL, ... WHERE id IN (SELECT id FROM tasks WHERE status='archived' ORDER BY created_at LIMIT TARGET-active)`. Отличие от запрещённого оркестратора: тот спавнил воркеров сам и/или был persist — keeper только держает уровень ready.
**СИМПТОМ «РОЙ ОСТАНОВИЛСЯ» НЕ ВСЕГДА КРАХ (урок 11.10.2026):** когда пользователь докладывает «рой остановился», а `archived` ещё НЕ пуст — это НЕ падение, а **штатное опустошение очереди `ready`**. Диагностика в одну команду: `SELECT status,COUNT(*) FROM tasks GROUP BY status` — если `ready=0, running=0, done=X, archived>0`, значит воркеры закончили последнюю выданную партию, а остаток сидит в archived, который gateway НЕ трогает сам. Это НЕ сбой — рой ждёт следующего подлива. ПРАВИЛЬНОЕ действие — просто SQL-промоут следующей партии `archived → ready` (10 шт, `UPDATE tasks SET status='ready' WHERE id IN (SELECT id FROM tasks WHERE status='archived' ORDER BY created_at LIMIT N)`), и gateway на следующем тике (~60с) сам их запустит. НЕ изобретать кастомный авто-подлив по этому симптому — ручной подлив партии и есть штатный механизм «автоподлива»; gateway разгоняет то, что выставлено в ready, но НЕ перекладывает archived→ready за тебя. Проверить после подлива: через ~70с `SELECT status,COUNT(*)` → `running=N` подтверждает, что воркеры пошли.

### ЛОГ-ТРИАЖ: ложные позитивы «404» в хвостах логов (урок 11.10.2026)
**СИМПТОМ:** при проверке «рой упал ли» grep по хвосту `errors.log`/`agent.log` даёт десятки «404» — паника преждевременна.
**ПРАВИЛА разбора:** (1) `out=404` в строке `API call ... in=... out=404` — это ЧИСЛО ВЫХОДНЫХ ТОКЕНОВ, не HTTP-ошибка; реальная ошибка — `Error code: 404` / `NotFoundError`. (2) Хвост лога содержит ОСТатКИ прежних прогонов и smoke-тестов — фильтровать ПО ВРЕМЕННОЙ МЕТКЕ строки относительно момента старта волны (404 с меткой до старта к новой волне не относятся). (3) Живость волны смотреть по меткам времени последних `API call`-строк нужной модели, а не по счётчику ошибок в окне байтов.

### БАТТЛ N МОДЕЛЕЙ НА ОДНОМ ВХОДЕ (замер качества/скорости/цены)
Когда владелец просит «сравнить модели на одинаковом материале»:
- **Одна доска на баттл**, карточек = (модели × единицы материала). Каждая модель пишет КОПИЮ одного и того же входа (те же цепи/темы) — иначе сравнивать нечего. Разговорные имена («степ 5», «лонгкат 2.5») маппить в ID из конфига ДО вставки карточек.
- **Рабочая папка карточки = `results/<тег модели>/<единица>/`**, создать все папки ДО запуска; каждая модель пишет ТОЛЬКО в свою папку, никогда в общий файл.
- **Все карточки в `ready` ОДНОВРЕМЕННО** — общий старт и есть честный замер скорости. Замерено на этой машине: 16 карточек (4 модели × 4 единицы) — нормально, по 4 воркера на модель держится.
- **Обязательный результат каждой карточки — файлы на диске.** Карточка `done` с 0 файлов = ПОТЕРЯННЫЙ результат (замерено: одна модель закрылась `done` после шторма 503 и не записала ни одной статьи). Ремонт потери: сбросить карточку в `ready` (`completed_at=NULL, result=NULL, consecutive_failures=0, max_retries=3`) → gateway переспавнит на следующем тике. Провал модели — строка в итоговой таблице, а не тихий пропуск.
- **Токены/латентность по моделям — из `profiles/swarm/logs/agent.log` с ОБЯЗАТЕЛЬНОЙ отсечкой по времени старта баттла:** regex `API call #\d+: model=(\S+) provider=\S+ in=(\d+) out=(\d+) total=\d+ latency=([\d.]+)s` + фильтр по timestamp `>= старт_баттла − 30с`. Без фильтра в счёт попадают прошлые прогоны (замерено: 2142 «вызова» вместо 137 у одной модели).
- **Панель сравнения** (автоматический скан + читка финалов глазами): время на единицу (`completed_at − started_at`), слов/единица, мосты-вопросы в концах, CTA-финалы, попадания клише, meta, токены in/out, число провалов. Вывод — таблицей со ВСЕМИ моделями запроса, провалы внутри неё (не выкидывать).
- **Итерации (i1 vs i2 после правки задания/костяка) сравнивать по ТОЙ ЖЕ панели метрик**, а не «на глаз»: одинаковые regex до и после.
- **Картинки включены, но БЕЗ цикла контроля качества** (директива владельца: генерация остаётся, «посмотреть зрением и перегенерировать» — нет: этот цикл удваивает время на единицу). В теле задачи задавать промпт-формулу против артефактов у людей: сюжет → типаж → антураж → свет/камера, плюс ОБЯЗАТЕЛЬНАЯ страховка от брака дословно — «естественная анатомия: ровно две руки, по пять пальцев на каждой руке, без лишних конечностей, без искажённых лиц и рук, без артефактов» и «без текста, надписей, водяных знаков, логотипов». Ракурсы и лица НЕ ограничивать: владелец отклонил вариант «только со спины / без лиц / руки не видны» как избыточный — сцены обычные, люди с лицами и руками, как в жизни. Имя файла ОБЯЗАНО содержать индекс статьи: `images/article_<индекс>_img_<n>.jpg` — по нему собирается цепочка. Механика: `image_gen` возвращает URL и НЕ создаёт файл по `output_path` — требовать скачивание (`curl -L -o images/article_<индекс>_img_<n>.jpg "<url>"`) и вставку ссылкой на локальный файл.

**ФАЛЬШИВЫЙ АРТЕФАКТ: воркер закрывает карточку `done`, создав файлы-заглушки (измерено 16.10.2026):** модель может НЕ вызвать нужный инструмент вообще, создать файлы с правильными именами нулевого размера и написать в отчёте «Создан», а в крайней строке отчёта признаться «создано как заглушки». Проверка по логу: `grep -c 'tool image_generate' profiles/<профиль>/logs/agent.log` = 0 → инструмент не вызывался.
**ПРАВИЛА:**
1. Приёмка проверяет РАЗМЕР и наличие файла, а не упоминание в тексте: файл картинки меньше ~10 КБ = заглушка, ссылка в тексте без файла = ошибка. Оба случая — ошибки гейта, не «на потом».
2. Модель под задачу с ассетами выбирать не только по тексту, но и по факту вызова инструментов: аккуратный текст при нуле вызовов инструментов делает модель непригодной для ассет-задач (такая модель хорошо идёт на классификацию/заголовки).
3. Недостающие ассеты мастер доводит САМ (вернуть URL → `curl -L -o <нужное_имя>`), не переписывая уже написанные воркерами тексты: ремонт дешевле перезапуска.
4. Один класс дефекта «формально готово, фактически неполно»: пропуск обязательных блоков (Meta), срез объёма вдвое против нормы, пустые вложения. Выявляется одним сканом готовой папки ДО доклада «готово».
5. Доклад владельцу об готовности начинать с ПУТИ к папке результата и цифр (статей N/M, картинок живых/всего, статусы карточек), а не с рассказа о процессе.

### СТАТЕЙНЫЙ РОЙ: НАРЕЗКА КАРТОЧЕК БЛОКАМИ + ФОРС-ЗАГРУЗКА СКИЛЛОВ
**Нарезка (решение владельца — совокупный контекст на 4–7 единиц результата):** дальнейшее дробление карточек ОТКЛОНЕНО владельцем: карточка на 4–7 статей БЫСТРЕЕ, потому что меньше холодных стартов, гайд и скилл не перечитываются на каждую карточку и работает кэш промпта; скорость он считает на статью, а не на карточку. Дробить сильнее (по 1–3 единицы) — только если карточка иначе не доходит до записи. Рабочая раскладка для цепи на 13–17 статей — три карточки («листья-1», «листья-2», «середины+ствол»), каждая в своей папке `results/<тег>/<цепь>_<A|B|C>`. Страховка от длинного контекста не в дроблении, а в требовании писать каждую единицу в файл сразу.
**Сквозная карта индексов — до старта:** если результат должен склеиваться в один список (индексы статей для сайта), посчитать нумерацию ОДИН раз и положить в отдельный файл-карту, а каждую карточку в теле снабдить явным списком «у меня индексы N..M». Иначе два независимых воркфера пронумеруют свои куски по-своему и сборка развалятся.
**Скиллы воркру форсируются ПОЛЕМ КАРТОЧКИ, а не только текстом задачи:** колонка `skills` в `tasks` (JSON-массив имён) → диспатчер превращает каждую запись в пару `--skills <имя>` в командной строке воркера (`hermes_cli/kanban_db_dispatch.py`, сборка cmd). Ставить её при прямом SQL INSERT (`'["skill-a","skill-b"]'`) и дополнительно называть пути SKILL.md в теле — тогда воркер получает скилл даже если сам его не искал. Проверка: в `profiles/<профиль>/logs/agent.log` появляются строки `tools.skills_tool: … for '<имя>'` — значит скилл действительно загружен, а не только объявлен.
**Параллельность 12 на одной бесплатной модели — не гарантия скорости, а верхняя граница (ИЗМЕРЕНО 16.10.2026):** 12 карточек на одной модели бесплатного провайдера поднялись и работали, но та же связка (model+provider), что вчера отвечала медиано 28 с, сегодня дала медиану 138 с (макс 371 с) и **1911 строк rate-limit за 100 мин при 405 ретраях-бэк-оффах**; за 100 мин 7 воркеров выдали 2 единицы результата. Провайдерская латентность между прогонами меняется в 5 раз — «было быстро вчера» не аргумент для планирования.

**ТРИАЖ «рой внезапно медленный» — СНАЧАЛА ЗАМЕРИТЬ ПРОВАЙДЕРА, ПОТОМ МЕНЯТЬ ЗАДАНИЕ (обязательный порядок):**
1. Латентность и лимиты за окно: разобрать `profiles/<профиль>/logs/agent.log` — regex `API call #\d+: model=(\S+) .*latency=([\d.]+)s` + фильтр по timestamp (окно текущего прогона), рядом посчитать строки с `429`/`RateLimit`/`Retrying API call in`.
2. Сравнить с ПРОШЛЫМ прогоном той же модели (другой день/окно) тем же regex: рост медианы в разы = деградация провайдера, а не «тяжёлое задание».
3. Только при подтверждённой деградации решать: (а) урезать вес задания (пре-верифицированный `FACTS.md` вместо браузерного ресёрча, 1 картинка листовой статье вместо 2 — см. раздел статьи) или (б) сменить модель/провайдера — выбор модели принадлежит владельцу, агент показывает цифры и предлагает варианты, а не меняет молча.
4. НЕ переделывать задание и не менять карточки у уже работающих воркеров по симптому «медленно»: у PENDING-карточек тело можно поправить SQL-ом (они ещё не читали), у running — уже поздно.
5. **Если владелец говорит «скорость неприемлемая» — гасить волну, а не уговаривать ждать:** убить воркеров, все карточки доски в `archived`, сохранить уже записанные артефакты, доложить цифры и варианты (модель/провайдер/вес задания) — и НЕ запускать новую волну до его «согласовано». После провала или замедленной волны самопальный перезапуск воспринимается как игнор директивы, даже если следующая партия могла бы сработать.
6. **Различать ДВА вида 429 — лечатся по-разному:** сообщение «temporarily at capacity upstream. This is not your API key's rate limit» = перегрузка самого апстрима модели, лечится только временем; сообщение «You've reached this model's current fair-share rate limit» + строка `credential pool: marking <аккаунт> exhausted (status=429), rotating` = исчерпана НАША справедливая доля на бесплатном SKU (вычерпывается всплеском параллельности; наблюдались кулдауны 37 → 80 мин, растущие с каждой новой волной ретраев). Диагноз — `grep -a 'fair-share\|credential pool\|429'` в `profiles/<профиль>/logs/agent.log`.
7. **При исчерпанной квоте — СНАЧАЛА парковать карточки (`status='archived'`), ПОТОМ убивать воркеров.** Если убить процессы, оставив карточки в `ready`, диспатчер на каждом тике спавнит их заново, каждая попытка жжёт по 3 ретрая и РАСТЯГИВАЕТ кулдаун учётки — рой сам себе продлевает бан. Архив диспатчер не трогает; тела карточек и папки сохраняются, поднять обратно — одним SQL-промоутом, когда квота вернётся.
8. **Если модель отвечает прямым `curl`, а агентские сессии воркеров стоят** (в логе `timeout waiting for reply; Nс без прогресса`), виноват не Hermes и не провайдер, а локальный мост-прокси между ними: у него свой бюджет тишины (`OPENAI_PROXY_TIMEOUT` / `OPENAI_PROXY_HARD_TIMEOUT`) и он умеет молча подменять модель строкой `фолбек: A -> B`, что делает A/B-замер невалидным. Порядок разбора (same-shape проба с тулами и большим контекстом → лог `proxy_access.log` → ручки и перезапуск моста → парковка карточек и чистый перезапуск) — в скилле `hermes-provider-routing-context`, reference-файл по локальным мостам.

**ФАКТЧЕКИНГ ВОРКЕРА — ФАЙЛ ПРОВЕРЕННЫХ ФАКТОВ ВМЕСТО БРАУЗЕРА:** если задача требует фактчекинга, писать факты в `FACTS.md` (что установлено владельцем + цифры источника + правила домена) и в теле задачи запрещать браузерный ресёрч: «покрытое FACTS.md берём как есть; не покрытое — одна быстрая проверка `curl` по официальной странице, максимум 3 на единицу; браузер не использовать». Замерено: браузерный вызов 30–60 с против секунд у `curl`, воркеры уходят в него на каждое утверждение. Отчёт-файл фактчекинга остаётся обязательным (утверждение → источник → вердикт).

### ПЕРЕД ВЫВОДОМ «ВОРКЕР ПОТЕРЯЛ РЕЗУЛЬТАТ» — ИСКАТЬ ПАПКУ-ДВОЙНИКА
**СИМПТОМ:** карточка закрылась `done`, в её рабочей папке 0 файлов → вывод «результат потерян, перезапускаем».
**КОРЕНЬ:** результат может лежать в СОСЕДНЕМ каталоге с похожим именем — опечатка в 1–2 символах названия папки (например `..._статей` вместо `..._статьи`). Такой каталог выглядит мусором, но содержит полный комплект файлов.
**ПРАВИЛО:** прежде чем объявлять потерю и перезапускать карточку — сверить списки файлов в каталогах, имена которых отличаются на 1–2 символа, и проверить дерево на пустые каталоги-артефакты. Найденный комплект перенести в правильную папку (суффикс «первый_прогон»), каталог-двойник удалить. Перезапуск при уже существующем результате — двойная оплата и расхождение версий.

### A/B СРАВНЕНИЕ МОДЕЛЕЙ НА ОДНИХ КАРТОЧКАХ
Прогон той же N-партии на второй модели для сравнения качества: (1) БРАТЬ ТЕ ЖЕ карточки (пулы идентичны — иначе сравнивать нечего); (2) перед прогоном убрать артефакты прошлой модели в workspace (`chains.json/PROGRESS.md/RETURNED.md` → `_precmp_*.bak`) — иначе новый воркер увидит чужой результат и «доделка» будет нечестной; (3) после обоих прогонов сравнивать ПО ОДНИМ МЕТРИКАМ (листьев/цепочку, пустые поля карточек, наличие ствола/fork, синтезы); (4) при ОТМЕНЕ теста сразу вернуть `_precmp_*.bak` на место и восстановить model_override/sчётчики — иначе потеряны оплаченные результаты первой модели.

### Провайдер qwen (token-plan): список models в конфиге НЕ совпадает с живым эндпоинтом (урок 11.10.2026)
**СИМПТОМ:** воркеры на модели из `hermes config get providers.qwen.models` падают мгновенно: `HTTP 404 Model not exist` (non-retryable, gave_up после 1 фейла, effective_limit=1).
**ФАКТ:** `qwen3.8-flash` работает (smoke ok); `qwen3.7-flash` и `qwen3.7-flash-2026-07-15` есть вdiscover-списке конфига, но эндпоинт token-plan отдаёт 404. Список моделей провайдера — это витрина, не гарантия. ПЕРЕД запуском роя на новой модели qwen — обязатель smoke `hermes chat --profile swarm -Q -q "say ok" --model X --provider qwen` (из swarm-профиля, не из default!).
**ОСОБЕННОСТЬ:** swarm-профиль авторизуется в qwen ОТДЕЛЬНО от десктоп-сессии: «Qwen CLI credentials not found. Run 'qwen auth qwen-oauth'» — добавлять креды нужно именно в профиль swarm.
**ОТМЕНА ТЕСТА — откат:** если карточки готовились к A/B (workspace очищен, файлы в `_precmp_*.bak`), при отмене сразу вернуть бэкапы на место и восстановить model_override/счётчики фейлов.

### ЭКОНОМИЯ КОНТЕКСТА ЗАДАНИЯ — НЕ ЗАСТАВЛЯТЬ ВОРКЕРА ЧИТАТЬ ВЕСЬ ГАЙД (урок 10.10.2026)
**СИМПТОМ:** расход прогона ×6 против прошлого при похожем числе воркеров (84.5M input против 14.2M). Замерено: 2716 API-вызовов / 187 сессий = 14.5 вызова на воркера.
**КОРЕНЬ:** задание требовало «прочти ПОЛНОСТЬЮ скилл (34K) + гайд (30K) + психологию (18K)» = ~82K токенов в КОНТЕКСТЕ КАЖДОГО ШАГА. Агентный воркер шлёт весь контекст на каждом из ~14 шагов → 82K × 14 × N воркеров.
**ПРАВИЛО:** в теле задачи явно писать «гайд НЕ читай целиком — найди поиском ТОЛЬКО разделы по теме пула (2–4 раздела); психологию бери только ключами по теме». Это срезает контекст в 3–4×. Скилл читать полностью (это правила), но справочники — выборочно.
**ВЫВОД:** дорого не число воркеров, а размер контекста × число шагов. Раздутое задание = ×6 расход при том же результате.
**ЗАМЕР ДЛЯ СТАТЕЙНЫХ ВОЛН (запрос владельца «сколько токенов съедает одна цепь») — считать до запуска, а не после:**
- Фиксированный контекст воркера на КАЖДОМ вызове (форсированные скиллы 48 КБ + гайд 42 КБ + файл цепи 20 КБ + карточка + системный промпт) ≈ **53 тыс. токенов** — проверяется по первому вызову воркера: `API call #1: … in=52981`.
- Статья = 10–15 вызовов × этот контекст → **≈ 400 тыс. входных токенов на статью**, ≈ 5–6 тыс. выходных; цепь из 5 статей ≈ 2,0 млн входных / 27 тыс. выходных; цепь из 16 статей ≈ 10–16 млн входных / ~130 тыс. выходных. В `session_model_usage` (state.db профиля) лежат точные числа по модели.
- **СЖАТИЕ ИСТОЧНИКОВ РАДИ ТОКЕНОВ ЗАПРЕЩЕНО ВЛАДЕЛЬЦЕМ** («из-за выжимки качество упадёт»): полные скиллы и полный гайд воркерам остаются как есть, экономия токенов не приоритет над качеством. Предложение «отдать выжимку костяка вместо скиллов / выборку разделов вместо гайда» — НЕ применять и не предлагать повторно.
- **Разрешённые рычаги снижения расхода (структурные, без урезания содержания, в порядке эффективности):** (1) две листовые единицы за один ход модели — вдвое меньше пересылок контекста (каждая сразу в свой файл); (2) карточка на 4–7 единиц (меньше холодных стартов и повторных чтений); (3) запрет браузерного ресёрча в пользу пре-верифицированного файла фактов; (4) одна картинка листовой единице вместо двух; (5) выбор модели/провайдера — решение владельца. Оценку расхода называть владельцу цифрой ДО запуска.

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
| CJM-writer (qwen) | qwen3.8-flash | qwen (token-plan) | ✅ works — 15 параллельно без 429; первый вызов ~58с, далее 5–10с при кэше 50–97%. Креды qwen добавлять ОТДЕЛЬНО в профиль swarm |
| CJM-writer (step) | stepfun/step-5-preview:free | nous | ⚠️ fair-share 429 шторм при 30 параллельных (retry 135–334с); держит ~10–15 |
| CJM-writer (deepseek) | deepseek/deepseek-v4-flash-0731 | openrouter | ✅ без лимитов, но тяжёлый воркер (пул 12–14) >12 параллельно вешает машину |
| Article-writer баттл (13.10.2026, 4 цепи × 4 модели) | deepseek/deepseek-v4-flash-0731 (openrouter) | ✅ ПОБЕДИТЕЛЬ баттла: меньше всех токенов (6.8M in), минимум ИИ-клише, честная развилка гайд\|услуга, 15–19 мин/цепь |
| Article-writer баттл | stepfun/step-5-preview:free (nous) | ✅ фолбэк: быстрее всех (14–20 мин), мосты 14/15, но клише ×1.5 и CTA шаблонны |
| Article-writer баттл | qwen3.8-flash (qwen) | ⚠️ объёмно и сильно в развилку, но 67 клише-ударов, самая медленная, 2× токенов конкурентов |
| Article-writer баттл | meituan/longcat-2.5-preview:free (nous) | ❌ снять с article-задач: тонкие статьи (982 сл.), шторм 503 на nous потерял одну цепь (done без файлов) |
| Через локальный мост | `cat-jam-free` (opencode-local) | ❌ сессии воркеров не завершаются: прямые вызовы 5 с, агентские — 0 статей и 0 завершённых вызовов. Перед любой волной — probe-карточка (п.7 Pre-flight) |
| Через локальный мост | `local/opencode/beam-free` (opencode-local) | ❌ тоже самое: прямые вызовы 2–13 с (в т.ч. 74 КБ промпт с тулами), агентские сессии стоят даже с поднятым до 600 с бюджетом моста. Считать «рабочей» только после probe-карточки |

**Fallback rule:** If primary provider fails (400/401/429/502/504), switch provider first per MODEL_TABLE.md fallback chain, then model after all providers exhausted. Priority: `nous` → `freellmapi` → `opencode-free` → `openrouter`.

**DEPRECATED models (do not use):**
- `tencent/hy3:free` via `nous` — free period ended (HTTP 404)
- `nvidia/nemotron-3-super-120b:free` via `openrouter` — HTTP 400 invalid model ID
- `nemotron-3-ultra:free` via `openrouter` — use `nemotron-3-ultra-free` via `opencode-free` instead

## Critical Task Body Requirement
**The task body MUST explicitly require file creation:** `MUST create/update C:\\Projects\...\G2-Runtime\FILENAME.md with: ... Use write_file tool.` — skill instructions alone do NOT enforce output. Workers read but don't write without this directive.

### ОБЯЗАТЕЛЬНАЯ ИНКРЕМЕНТАЛЬНАЯ ФИКСАЦИЯ РЕЗУЛЬТАТА (директива владельца)
**Правило:** если воркер делает МНОГО однотипных единиц (несколько цепочек/батчей на карточку), тело задачи ОБЯЗАНО требовать: «записывай результат СРАЗУ после каждой единицы (append в файл + `PROGRESS.md` со счётчиком "сделано N/M"), НЕ только в конце».
**ПОЧЕМУ:** при обрыве связи/таймауте/убийстве процесса воркеры гибнут до финальной записи, и весь оплаченный расход пропадает. Владелец: «терять деньги неприемлемо… ты знаешь про частые обрывы интернета и должен был предусмотреть».
**КАК ЗАБРАТЬ РЕЗУЛЬТАТ:** после прогона собирать ВСЕ частичные артефакты из workspace'ов (`glob wave*/**/chains.json`), а не полагаться на статус `done` карточки — артефакт может быть записан при `done=0`, и наоборот (статус `done` без файла = пустышка).

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

### ЛОВУШКА «свежайший файл в workspace» ВРЁТ, когда папки переиспользуются (урок 07.10.2026)
- Диспатчер переназначает ОДНИ И ТЕ ЖЕ рабочие папки между запусками, поэтому в workspace лежат старые файлы прошлых прогонов (soul.md, usage-analytics.json, chains.json часы/дни давности). Проверка живости «новейший mtime в workspace < 8 мин» после спавна даёт ложную 🔴 у живых и ложную 🟢 у мёртвых.
- Надёжный способ при ЕДИНИЧНОМ спавне: (1) смотреть файлы, изменённые за последние ~3 МИНУТЫ, не «новейший mtime вообще»; (2) cross-check живого pid через `ps -W | grep python` — если `worker_pid` задачи НЕ среди живых python-процессов, воркер мёртв независимо от статуса 'running'.

### НЕ ЧИТАТЬ РОЙ ПО ФАЙЛАМ ВООБЩЕ — СЧИТАТЬ ПРИРОСТ ПО ВРЕМЕННОМУ ОКНУ (урок 08.10.2026)
**СИМПТОМ:** массовый спавн (105+ воркеров на тяжёлой генерации, огромный контекст ~500K токенов, латентность 50-195с на вызов). Любая проверка по файлам даёт ложь: (а) «новейший mtime в workspace» — старые файлы переиспользуемых папок (age 1590-3000 мин); (б) «файлы изменённые за 3 мин» — у только-что-спавненных воркеров ещё нет свежих файлов, даёт 0/105 живых при реально работающем рое; (в) `ps -W | grep -icE 'python'` = 135 процессов (процессы есть), но конкретные `worker_pid` не матчатся по шаблону пути (экранирование `hermes\tools\python-3.14` → 0). Все три дают ложный «рой мёртв».
**ПРАВИЛЬНЫЙ, ЕДИНСТВЕННО ДОСТОВЕРНЫЙ СИГНАЛ — ПРИРОСТ `done` ЗА ФИКСИРОВАННОЕ ОКНО:** засеки `SELECT COUNT(*) FROM tasks WHERE status='done'` (и отдельно по model_override), подожди 2-3 мин, повтори. Прирост > 0 = рой реально работает, какими бы «мёртвыми» ни выглядели файлы/pid на каждом отдельном воркере. Дополнительно: свежесть `profiles/swarm/logs/agent.log` (mtime < 1 мин) и появление новых `chains.json` за окно.
**ВЫВОД:** при тяжёлой генерации НЕ тратить минуты на файловые/pid-проверки каждого воркера — они ложно-отрицательные. Проверять прирост done за окно. Файловые проверки годятся только для ЕДИНИЧНОЙ задачи после её длительного зависания, не для роя из сотен.

### ВОРКЕРЫ УБИВАЮТСЯ ДЕДЛАЙНОМ 60с, хотя провайдер быстрый (главный корень «всё running но ничего не пишется», урок 07.10.2026)
- **СИМПТОМ:** все воркеры в `running`, у каждого есть pid, но файлы не растут и вскоре pid протухает. Никаких HTTP-ошибок.
- **КОРЕНЬ:** на ТЯЖЁЛОМ контексте (генерация цепочки с большим промптом + кешем 60-90%) провайдер отвечает 88-195с, а дедлайн воркерa `terminal.wait:LocalEnvironment` = **62 сек** → `agent.deadline ... timed out after 62.0s; worker abandoned` → процесс убит, задача остаётся running с мёртвым pid'ом.
- **НЕ ПУТАТЬ:** короткий тест `hermes chat -Q -q "say ok" --model ... —provider ...` отвечает за 4с и даёт ложную уверенность. Он НЕ представляет латентность реального воркера на большом контексте.
- **ДИАГНОСТИКА:** grep `agent.deadline`/`timed out`/`worker abandoned` в `profiles/swarm/logs/agent.log` — это признак дедлайна, а не ошибки модели.
- **РЕШЕНИЕ:** поднимать дедлайн воркера (с ~60 до ~200с) для тяжёлой генерации; либо на таких задачах использовать модель, которая укладывается в 60с (longcat на коротком контексте работал без timeout, агнес на длинном — нет). Не списывать на «провайдер не работает», если прямой вызов быстрый.

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