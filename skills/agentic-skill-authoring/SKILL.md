---
name: agentic-skill-authoring
description: Use when authoring a paid skill with license, sources.
version: 0.1.0
author: Петр (ratingtesting), Hermes Agent
license: MIT-0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [skill-authoring, agent-authoring, license-compliance, anthropic-patterns, commercial]
    related_skills: [writing-skills, hermes-agent-skill-authoring, test-driven-development]
---

# Agentic Skill Authoring (commercial-grade)

## Overview
Скилл для создания переиспользуемых агентов/скиллов, которые идут в **коммерческий продукт** (resale, без атрибуции). Объединяет три источника:
1. Структуру SKILL.md и Iron Law тестирования из `writing-skills`.
2. Лицензионную дисциплину (MIT-0 по умолчанию, белый список, clean-room переписывание).
3. Проверенные паттерны Anthropic (building effective agents, context engineering, prompt best practices).

Обязателен при любом создании/адаптации агента, чей результат покидает этот чат (дашборд, релиз, репозиторий клиента).

## When to Use
- Создаёшь нового агента под задачу (Founder, Product, Economy, Flutter-architect, swarm-monitor роли и т.п.).
- Адаптируешь готового агента из `agent-roles` / skills hub под коммерческий проект.
- Пишешь промпт ролевому агенту в kanban / `delegate_task`.
- Агент под давлением (срок, объём) игнорирует структуру — принуди к recipe-форме.
- Результат будет интегрирован в продукт третьей стороны или продаваться.

**Don't use for:** личных одноразовых ответов без артефакта; чисто метафизических рассуждений без вывода-деливерабла.

## Core Recipe (output slots — not prohibitions)

При создании скилла агент производит ровно этот набор артефактов:

### 1. SKILL.md frontmatter
```yaml
---
name: agent-name-with-hyphens        # lowercase, hyphens, ≤64
description: Use when <конкретные триггеры/симптомы>   # ТОЛЬКО КОГДА звать, не что делает
version: 0.1.0
author: <Человек (handle)>, Hermes Agent
license: MIT-0                      # по умолчанию
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Short, Descriptive]
    related_skills: [existing-in-repo-skill]
---
```
- `description` ≤ 60 символов, третье лицо, начинается с "Use when". Описывает УСЛОВИЕ ВЫЗОВА, а не процесс (иначе агент пойдёт по shortcut и не прочитает тело).
- `author` — человек первым, затем "Hermes Agent". Никогда только "Hermes Agent".
- `related_skills` — только существующие в этом дереве.

### 2. Тело (слоты вывода)
```markdown
# <Agent Name>
## Role — якорь уровня: "Ты <эксперт уровня X + Y>"
## Context — что прочитать ДО: MANIFEST.md, свой раздел Brief.md, зависимые доки
## Task — контракт вывода (слоты, не запреты):
  1. <Раздел A>
  2. <Раздел B>
## Hard Rules — жёсткие с red-flags:
  - Не писать код → удали документ и начни заново
  - Русский; ссылки на зависимые доки обязательны
## Output Example — один реальный кусок
## Dependencies — от кого ждёт документ
```

### 3. License & Sources (ОБЯЗАТЕЛЬНЫЙ СЛОТ — см. ниже)

## Anthropic Patterns (verified, 2024-2026)

Интегрируй релевантные при проектировании агента:

**Workflow-паттерны (предсказуемые пути):**
- **Prompt chaining** — задача декомпозируется в последовательность шагов; между шагами программные gate-проверки.
- **Routing** — классификация входа → специализированный follow-up. Разделяй задачи по типам.
- **Parallelization** — sectioning (независимые подзадачи параллельно) + voting (несколько прогонов для уверенности).
- **Orchestrator-workers** — центральный LLM динамически дробит задачу, делегирует воркерам, синтезирует. Для задач, где подзадачи непредсказуемы (код-агенты).
- **Evaluator-optimizer** — один генерирует, другой оценивает в цикле. Когда есть чёткие критерии качества.

**Agents (автономные):** LLM в цикле с инструментами, ground truth из среды на каждом шаге, stopping conditions (макс. итераций). Используй когда шаги предсказать нельзя и есть доверие к решениям модели.

**3 принципа (Anthropic):** (1) Simplicity — добавляй сложность только когда она измеримо улучшает результат; (2) Transparency — показывай шаги планирования; (3) ACI (Agent-Computer Interface) — документируй и тестируй инструменты так же тщательно, как промпты (poka-yoke аргументы, примеры использования, абсолютные пути).

**Context Engineering (для long-horizon):** compaction (сжатие истории с сохранением решений), structured note-taking (NOTES.md / memory вне контекста), sub-agent architectures (воркеры возвращают 1-2k токенов сводки), just-in-time retrieval (лёгкие ссылки вместо предзагрузки всего корпуса). Контекст — конечный ресурс с убывающей отдачей.

**Prompt Best Practices:** будь чётким и прямым (golden rule: покажи промпт коллеге без контекста — если он запутается, запутается и модель); давай контекст/мотивацию; few-shot примеры (канонические, не список всех edge-case); XML-теги/`##` для секций; минимальный набор high-signal токенов.

## License & Sources (MANDATORY SLOT)

Каждый скилл/агент завершается блоком:

```markdown
## License & Sources
- **License:** MIT-0 (по умолчанию). Альтернативы для коммерции БЕЗ атрибуции: MIT, Apache-2.0, ISC, Unlicense, 0BSD.
- **Белый список лицензий исходников:** MIT-0, MIT, Apache-2.0, ISC, Unlicense, 0BSD.
- **Исключены (НЕ используем чужой код/текст):** CC-BY*, GPL (все), Proprietary, любые требующие атрибуции/share-alike.
- **Clean-room правило:** если взятый за основу материал имеет лицензию вне белого списка — НЕ копируй текст и структуру. Перепиши своими словами с нуля («чтобы не найти концов»): перескажи идею, измени формулировки, перестрой структуру, укажи источник-вдохновитель без цитирования.
- **Sources (verified):**
  - writing-skills SKILL.md (локально) — структура, SDO, Iron Law
  - hermes-agent-skill-authoring SKILL.md (локально) — frontmatter-стандарты
  - Anthropic — Building Effective Agents (https://www.anthropic.com/engineering/building-effective-agents)
  - Anthropic — Effective Context Engineering (https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
  - Anthropic — Prompting Best Practices (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
```

## Obsidian/agent-roles Compatibility
Скиллы предназначены для интеграции в дашборд (не «лазание по папкам»). Структура SKILL.md совместима с форматом `agent-roles` (role/context/task/hard-rules/output-example/dependencies). При адаптации роли из `agent-roles` сохраняй эти слоты, но добавляй License & Sources.

## Hard Rules (red-flags)
- Description суммирует процесс → агент не читает тело. Исправь на trigger-only.
- Prohibition вместо recipe для shaping-задач → агент договаривается. Дай слоты вывода.
- Пропущен web_search на чужой теме → догадка = ложь. Блокируй, ищи практики.
- Скилл без теста (Iron Law) → удали, начни с baseline-прогона.
- **Нет блока License & Sources** → скилл некоммерчепригоден, допиши.
- **Чужая лицензия исходника скопирована как есть** → нарушение. Clean-room перепиши.

## Iron Law (из writing-skills)
НЕТ СКИЛЛА БЕЗ ПАДАЮЩЕГО ТЕСТА СНАЧАЛА.
RED: прогони subagent БЕЗ скилла на давление (время+объём) → запиши рационализации.
GREEN: напиши минимальный скилл → прогони снова → агент comply.
REFACTOR: новая рационализация → явный контр-приём → ре-тест.

## Verification Checklist

### A. Структура из agent-authoring (6 слотов тела — ОБЯЗАТЕЛЬНЫ)
- [ ] `# <Agent Name>` — заголовок
- [ ] `## Role` — якорь уровня (эксперт X + Y)
- [ ] `## Context` — что прочитать ДО (MANIFEST, Brief, зависимые доки)
- [ ] `## Task` — контракт вывода (слоты, не запреты)
- [ ] `## Hard Rules` — жёсткие с red-flags
- [ ] `## Output Example` — один реальный кусок
- [ ] `## Dependencies` — от кого ждёт вводные

### B. Добавлено мной (commercial-grade)
- [ ] Frontmatter: name/description(≤60, trigger-only)/version/author(человек first)/license(MIT-0)/platforms/metadata.hermes.{tags,related_skills}
- [ ] description начинается с "Use when", не summary процесса
- [ ] `## License & Sources` — обязательный слот: лицензия в белом списке, clean-room для чужих, Sources с проверенными ссылками
- [ ] Чужие лицензии — clean-room переписаны (не цитаты, не структура)
- [ ] Интегрирован релевантный Anthropic-паттерн (workflow/agent/context/ACI)

### C. Iron Law (TDD для скиллов)
- [ ] baseline-прогон (RED) зафиксирован ДО написания
- [ ] Скилл протестирован на comply (GREEN пройден)
