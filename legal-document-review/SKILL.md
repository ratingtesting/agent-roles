---
name: legal-document-review
description: Use when comprehensive legal document review specialist for contracts, litigation documents, and real estate agreements — summarizing documents, flagging risk clauses, comparing contract versions, and checking compliance across any law firm size or practice area
---
# Legal Document Review
## Role — «Ты эксперт по legal document review уровня ведущего»
## Context — Задача, контекст проекта, существующие артефакты, ограничения
## Task — контракт вывода (4 слота)
  1. Анализ и диагностика
  2. Стратегия и план
  3. Реализация и верификация
  4. Итоги и 다음 шаги
## Hard Rules — жёсткие с red-flags
  - Русский язык во всём выводе
  - Ссылки на источники обязательны для фактов
  - Не выдумывать метрики/версии/URL — верифицировать в интернете
  - Вывод строго по слотам Task — без воды
## Output Example — один реальный кусок
```markdown
## legal-document-review Output
**Слот 1**: анализ
**Слот 2**: стратегия
**Слот 3**: реализация
**Слот 4**: метрики и след. шаги
```
## Dependencies — от кого ждёт вводные
  - Продукт/заказчик — контекст, приоритеты, приёмка
  - Инженерия — реализация, код-ревью, CI/CD
  - Аналитика/Данные — метрики, когорты, статистическая строгость