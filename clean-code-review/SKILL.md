---
name: clean-code-review
description: Pragmatic coding standards for writing clean, maintainable code — naming, functions, structure, anti-patterns, and pre-edit safety checks.
---

# Clean Code

> Be **concise, direct, and solution-focused**. Clean code reads like well-written prose — every name reveals intent, every function does one thing, and every abstraction earns its place.

## Core Principles

| Principle | Rule | Practical Test |
| --- | --- | --- |
| **SRP** | Single Responsibility — each function/class does ONE thing | "Can I describe what this does without using 'and'?" |
| **DRY** | Don't Repeat Yourself — extract duplicates, reuse | "Have I written this logic before?" |
| **KISS** | Keep It Simple — simplest solution that works | "Is there a simpler way to achieve this?" |
| **YAGNI** | You Aren't Gonna Need It — don't build unused features | "Does anyone need this right now?" |
| **Boy Scout** | Leave code cleaner than you found it | "Is this file better after my change?" |

## Naming Rules

Names are the most important documentation. A good name eliminates the need for a comment.

| Element | Convention | Bad | Good |
| --- | --- | --- | --- |
| **Variables** | Reveal intent | `n`, `d`, `tmp` | `userCount`, `elapsed`, `activeUsers` |
| **Functions** | Verb + noun | `user()`, `calc()` | `getUserById()`, `calculateTotal()` |
| **Booleans** | Question form | `active`, `flag` | `isActive`, `hasPermission`, `canEdit` |
| **Constants** | SCREAMING_SNAKE | `max`, `timeout` | `MAX_RETRY_COUNT`, `REQUEST_TIMEOUT_MS` |
| **Classes** | Noun, singular | `Manager`, `Data` | `UserRepository`, `OrderService` |

**Rule:** If you need a comment to explain a name, rename it.

## Function Rules

| Rule | Guideline | Why |
| --- | --- | --- |
| **Small** | Max 20 lines, ideally 5-10 | Fits in your head |
| **One Thing** | Does one thing, does it well | Testable and nameable |
| **One Level** | One level of abstraction per function | Readable top to bottom |
| **Few Args** | Max 3 arguments, prefer 0-2 | Easy to call correctly |
| **No Side Effects** | Don't mutate inputs unexpectedly | Predictable behavior |

### Guard Clauses

Flatten nested conditionals with early returns. Never nest deeper than 2 levels.

```typescript
// GOOD — guard clauses flatten the structure
function processOrder(order: Order) {
  if (!order) throw new Error('No order');
  if (!order.items.length) throw new Error('No items');
  if (!order.customer) throw new Error('No customer');
  if (!order.customer.isVerified) throw new Error('Customer not verified');
  return submitOrder(order);
}
```

**Cardinal rule: guard clauses must come BEFORE side effects.**

A guard clause that fires *after* a mutation has already happened is not a guard — it's a rollback that doesn't roll back. The system is left in a corrupt state even though the error is returned.

```python
# BAD — side effect before guard: target is already promoted when permission fails
def promote_to_admin(current_user, target_user_id):
    user = users_db.get(current_user)
    # BUG: mutation happens here...
    users_db[target_user_id] = {"role": "admin"}
    # ...guard fires here, too late — state is already corrupted
    if user.get("role") != "admin":
        return {"error": "Permission denied"}

# GOOD — guard before side effect: clean rejection
def promote_to_admin(current_user, target_user_id):
    user = users_db.get(current_user)
    if user.get("role") != "admin":
        return {"error": "Permission denied"}
    # Only reach here if permission is confirmed
    users_db[target_user_id] = {"role": "admin"}
```

**Checklist when writing guards:**
- Are all permission/precondition checks at the *top* of the function, before any mutations?
- Could a guard clause fire after a side effect has already happened?
- Does the function's happy path assume state is clean when it starts? (It should — guards guarantee that.)

### Parameter Objects

When a function needs more than 3 arguments, use an options object.

## Code Structure Patterns

| Pattern | When to Apply | Benefit |
| --- | --- | --- |
| **Guard Clauses** | Edge cases at function start | Flat, readable flow |
| **Flat > Nested** | Any nesting beyond 2 levels | Reduced cognitive load |
| **Composition** | Complex operations | Small, testable pieces |
| **Colocation** | Related code across files | Easier to find and change |
| **Extract Function** | Comments separating "sections" | Self-documenting code |

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
| --- | --- | --- |
| Comment every line | Noise obscures signal | Delete obvious comments; comment _why_, not _what_ |
| Helper for one-liner | Unnecessary indirection | Inline the code |
| Factory for 2 objects | Over-engineering | Direct instantiation |
| `utils.ts` with 1 function | Junk drawer file | Put code where it's used |
| Deep nesting | Unreadable flow | Guard clauses and early returns |
| Magic numbers | Unclear intent | Named constants |
| God functions | Untestable, unreadable | Split by responsibility |
| Side-effect before guard | Mutation happens before permission check; state corrupted even on failure | Check preconditions BEFORE any mutation |
| Commented-out code | Dead code confusion | Delete it; git remembers |
| TODO sprawl | Never gets done | Track in issue tracker, not code |
| Premature abstraction | Wrong abstraction is worse than none | Wait for 3+ duplicates before abstracting |
| Copy-paste programming | Duplicated bugs | Extract shared logic |
| Stringly-typed code | Typos and missed cases | Use enums or union types |

## Pre-Edit Safety Check

Before changing any file, answer:
- What imports this file? (Dependents might break)
- What does this file import? (Interface changes ripple)
- Can I do this with a smaller diff? (Less risk)

## Pink Flag (запах кода → стоп)

Если **ощущается неправильным** — это сигнал, не шум.

1. **Стоп** — не продолжай писать код поверх запаха
2. **Вызови этот скилл** → `skill_view(name='clean-code-review')`
3. **Диагностика:** сравни с таблицами выше (Naming Anti-Patterns, Function Rules, Anti-Patterns)
4. **Реши:** рефакторить сейчас (high-tier) или залогировать в todo (medium/low)
5. **Только потом** — продолжай

Типичные запахи (каждый — причина остановиться):
- Функция делает 2 вещи ("и" в описании) → нарушение SRP
- Имя требует комментария для объяснения → rename it
- Вложенность > 2 уровней → guard clauses
- Параметров > 3 → options object
- Комментарий описывает "что", а не "почему" → delete, rename, or explain why
- Копируешь код второй раз → DRY violation
- "Это временное решение" → будет permanent, исправь сейчас
- Функция > 20 строк → split

## Как это связано с другими скиллами

| Скилл | Решает | Когда вызывать |
|---|---|---|
| `clean-code-review` (этот) | КАК писать (стиль, naming, структура) | Когда решил писать + любой Pink Flag |
| `clean-architecture` | ГДЕ писать (слои data/domain/presentation) | Перед созданием файла |
| `vibe-loop` | ДВИЖОК луп-кодинга: 3 фазы, backpressure, Stability, security-гейты, автономия | Луп-кодинг, автономная итерация |
| jscpd + lizard/scc (в `vibe-loop`) | МЕХАНИЧЕСКАЯ чистка: дубли + сложность | Перед коммитом (см. vibe-loop/writing-code.md) |
