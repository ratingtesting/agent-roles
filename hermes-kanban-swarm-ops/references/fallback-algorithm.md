# Fallback-алгоритм для rate-limited моделей

## Приоритет провайдеров
nous > freellmapi > opencode-free > openrouter (openrouter — только последний)

## Алгоритм при 429/502/504
1. Зафиксировать время блокировки
2. Ждать 3 минуты
3. Retry той же модели/провайдера
4. Если снова 429 → следующий провайдер той же модели (nous→freellmapi)
5. Если все провайдеры исчерпаны → следующая модель по таблице
6. Openrouter — только если все выше не помогли

## Частые ошибки
- Переключение всех задач на одну fallback-модель (унификация)
- Мгновенный fallback без ожидания 3 минут
- Использование openrouter как основного провайдера
- Использование stepfun/step-3.7-flash:free для QA вместо nemotron-3.5-lightning

## Рабочие пары моделей/провайдеров (2026-09-06)
|- poolside/laguna-s-2.1:free → nous (Coder)
|- poolside/laguna-s-2.1:free → freellmapi (fallback)
|- nemotron-3-ultra:free → opencode-free (Strategist)
|- nemotron-3-ultra-550b → freellmapi (Orchestrator)
|- nemotron-3-super-120b → freellmapi (Architect)
|- meituan/longcat-2.0:free → nous (fallback для всех)

## Критические ошибки и lessons
- **Gateway должен быть запущен** (`hermes gateway start`) чтобы cron срабатывал. Без gateway крон создаётся, но НЕ fires — статус показывает "Gateway is not running".
- При 429 на poolside/laguna-s-2.1 через freellmapi — retry с тем же провайдером после 3 минут, не переключать сразу на другую модель.
