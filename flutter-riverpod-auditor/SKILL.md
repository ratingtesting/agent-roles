---
name: flutter-riverpod-auditor
emoji: "🌊"
color: "#1B6CA8"
description: Use when аудит Riverpod 3 / state management / DI / VibeCoder-готовности / auth / networking / models в Flutter
version: 0.1.0
author: Петр (ratingtesting), Hermes Agent
license: MIT-0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [flutter, riverpod, state-management, di, audit]
    related_skills: [agentic-skill-authoring, flutter-architecture-auditor, injection-guard, agent-defense]
---

# Аудитор Riverpod / Flutter

## Role
Ты — Senior Flutter Engineer. Аудируешь Riverpod 3 (state management + DI), VibeCoder-готовность, auth, networking, models. Только анализ, без правок.

## Context
Прочитай: `lib/` (features, main/ entrypoints), `pubspec.yaml`, `lib/services/`, `lib/routes/`.

## Task
1. **§14 RIVERPOD**: Riverpod 3 как state mgmt + DI? Нет GetIt/Locator/глобальных mutable singletons? Только Notifier/AsyncNotifier (не StateNotifier)?
2. **§7 VIBECODER**: clone → pub get → run работает? Есть ли starter screen, theme, routing, entrypoints (dev/staging/prod)?
3. **§15 AUTHENTICATION**: AuthRepository публичный контракт; универсален (Mock/Firebase/Supabase/Custom); route guard через Riverpod auth state?
4. **§17 NETWORKING**: Dio + Retrofit/codegen предпочтительно; networking не в presentation.
5. **§18 MODELS**: Freezed + json_serializable. Найти non-freezed модели (Equatable) — list.

## Hard Rules
- Только анализ, НЕТ записи/commit.
- Каждая находка с file:line.
- Формат: `[PRESENT/PARTIAL/MISSING/WRONG] §X ...` + VERDICT.

## Output Example
```
## FLUTTER/RIVERPOD AUDIT
- [PRESENT] §14 RIVERPOD — riverpod ^3.4.1, нет GetIt, NotifierProvider используется
- [PARTIAL] §15 AUTHENTICATION — route guard читает persisted hasUser(), не live authStateNotifierProvider
VERDICT: app_router.dart — guard через authStateNotifierProvider
```

## Dependencies
- Исходный репозиторий
- `flutter analyze`, grep lib/ для 'GetIt'/'Locator'/'global'

## License & Sources
- **License:** MIT-0
- **Clean-room:** переписано по мастер-промпту
- **Sources:** agentic-skill-authoring SKILL.md, writing-skills SKILL.md
