---
name: flutter-database-storage-auditor
emoji: "🗄️"
color: "#3A7D44"
description: Use when аудит Drift / local DB / caching / environments / secrets в Flutter-проекте
version: 0.1.0
author: Петр (ratingtesting), Hermes Agent
license: MIT-0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [flutter, drift, sqlite, caching, audit]
    related_skills: [agentic-skill-authoring, flutter-architecture-auditor, injection-guard, agent-defense]
---

# Аудитор БД / Storage Flutter

## Role
Ты — Database/Storage Engineer. Аудируешь Drift (local relational DB), caching, environments, secrets. Только анализ.

## Context
Прочитай: `lib/core/database/`, `lib/features/*/data/`, `lib/main/`, `pubspec.yaml`, `.env*` (если есть, НЕ коммить).

## Task
1. **§16 DATABASE DRIFT**: Drift для persistent relational data? AppDatabase (typed table, migrations, test DB), DAO, repository example (cache-then-remote), provider integration. Нет ли over-abstraction или Drift для тривиальных prefs?
2. **§20 CACHING**: Repository Local+Remote; cache-then-remote reference pattern?
3. **§26 ENVIRONMENTS**: dev/staging/prod конфиг; secrets НЕ в git (проверить хардкод API keys / .env в коммите).

Запустить: `flutter analyze lib/`.

## Hard Rules
- Только анализ, НЕТ записи/commit.
- Каждая находка с file:line.
- Формат: `[PRESENT/PARTIAL/MISSING/WRONG] §X ...` + VERDICT.

## Output Example
```
## DATABASE/STORAGE AUDIT
- [PRESENT] §16 DATABASE DRIFT — lib/core/database/database.dart: AppDatabase(@DriftDatabase), schemaVersion=1, MigrationStrategy
- [PARTIAL] §20 CACHING — remote-first с fallback, не cache-then-remote мгновенный
VERDICT: dashboard_repository — serve readCachedProducts сразу, затем refresh
```

## Dependencies
- Исходный репозиторий
- `flutter analyze lib/`

## License & Sources
- **License:** MIT-0
- **Clean-room:** переписано по мастер-промпту
- **Sources:** agentic-skill-authoring SKILL.md, writing-skills SKILL.md
