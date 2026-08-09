---
name: agent-authoring
description: Use when creating a new Hermes agent/skill from scratch, adapting an existing agent (agency-agents or skills hub), or writing a prompt for a role-based agent under pressure to skip structure. Applies to any task where the deliverable is a reusable agent definition (SKILL.md + prompt), not a one-off answer.
---

# Agent Authoring — создание и адаптация агентов

## Overview
Скилл для написания агентов (Hermes skills), которые решают конкретную задачу.
Базируется на `writing-skills` (структура SKILL.md, SDO, Iron Law тестирования) и
Anthropic Prompt Engineering Best Practices (роль, context-блоки, пример вывода, итеративность).
Обязателен при любом создании/правке агента.

## When to Use
- Создаёшь нового агента под задачу (Founder, Product, Economy, Flutter-architect и т.п.).
- Берёшь готового агента из `agency-agents` / skills hub и адаптируешь под проект.
- Пишешь промпт ролевому агенту в kanban / delegate_task.
- Агент под давлением (срок, объём) игнорирует структуру — принуди к recipe-форме.

## Core Pattern (recipe, not prohibition)

### 1. SKILL.md frontmatter
```yaml
---
name: agent-name-with-hyphens
description: Use when <конкретные триггеры/симптомы>   # только КОГДА звать
---
```
- `description` = условия вызова, НЕ описание процесса (иначе агент пойдёт по shortcut).
- Макс 1024 символа, третье лицо.

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

### 3. Промпт агента (Anthropic context-engineering)
- Явная роль + планка (аналогия).
- Context-блоки: `<context>...</context> <task>...</task> <constraints>...</constraints>`.
- Один пример вывода (silver bullet).
- Границы: что агент НЕ делает.
- Итеративность: v1 → Chief Simplicity → правка.

## Обязательное правило (неукоснительно)
**При создании скилла на НЕЗНАКОМУЮ тему — обязателен `web_search` лучших практик + факт-чек.**
1. `web_search` по теме (Anthropic, академия, официальные docs).
2. Проверь факты — не по памяти, не догадкой.
3. Только после подтверждения — пиши скилл.
4. Не уверен на 100% — скажи "не знаю", не выдумывай научную базу.

## Hard Rules (red-flags)
- Description суммирует процесс → агент не читает тело. Исправь на trigger-only.
- Prohibition вместо recipe для shaping-задач → агент договаривается. Дай слоты.
- Пропущен web_search на чужой теме → догадка = ложь. Блокируй.
- Скилл без теста (Iron Law) → удали, начни с baseline-прогона.

## Output Example (фрагмент SKILL.md агента)
```markdown
---
name: founder-visionary
description: Use when нужно сформулировать миссию/North Star платформы цифровых активов
---
# Founder Visionary
## Role: сооснователь уровня Paul Graham + Brian Chesky
## Context: MANIFEST.md, 00_Founder/Brief.md (раздел 1)
## Task: Vision.md — Mission / Vision 10 лет / North Star / Anti-Goals
## Hard Rules: не код; удалить при нарушении; противоречить манифесту нельзя
```

## Dependencies
- Требует: `writing-skills` (структура, Iron Law), `test-driven-development` (цикл RED-GREEN-REFACTOR).
- Читает: MANIFEST.md проекта (общий контекст).
- Пишет: `~/AppData/Local/hermes/profiles/<profile>/skills/<agent>/SKILL.md`.

## Common Mistakes
- Description = "агент пишет Vision.md" (summary) вместо trigger.
- Hard Rules мягкие ("желательно") → под давлением игнорируются.
- Нет Output Example → агент угадывает форму.
- Взял чужого агента, не адаптировал под MANIFEST → противоречие.

## Iron Law (из writing-skills)
НЕТ СКИЛЛА БЕЗ ПАДАЮЩЕГО ТЕСТА СНАЧАЛА.
RED: прогони subagent БЕЗ скилла на давление (время+объём) → запиши рационализации.
GREEN: напиши минимальный скилл → прогони снова → агент comply.
REFACTOR: новая рационализация → явный контр-приём → ре-тест.

## Sources (verified)
- `writing-skills` SKILL.md (локально) — структура, SDO, Iron Law.
- Anthropic Prompting Best Practices: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
- Anthropic Effective Context Engineering: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
