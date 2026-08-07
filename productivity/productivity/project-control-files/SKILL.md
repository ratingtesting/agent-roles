---
name: project-control-files
description: Index a project setup file so other chats find it.
---

# Project Control Files — Cross-Chat Discoverability

## Trigger
The project has a single source-of-truth setup/env file (commonly `SETUP_GUIDE.md` at repo root)
that other chat agents / subagents must find. User signals: "other chats don't know this file",
"save its path to your controlling files", "not just memory".

## Rule (explicit user correction — embed, don't just memorize)
Do NOT store the setup file's location in agent memory ONLY. Also write it to the project's
**controlling markdown files** so any chat/agent that loads the repo's AGENTS.md / CLAUDE.md finds it:
1. **AGENTS.md** (Hermes agents) — add a top-level "ГЛАВНЫЙ ФАЙЛ СЕТАПА" block NEAR THE TOP with the absolute path.
2. **CLAUDE.md** (Claude / Codex / generic agents) — mirror the same pointer; these agents read
   CLAUDE.md, not AGENTS.md.
3. **Memory** — save the path too, for the current agent's own future sessions.

Keep each pointer MINIMAL: absolute path + one line on what it contains. Do NOT paste the whole setup.

## Why
Subagents and other chat sessions do NOT inherit the parent chat's memory or conversation. A path
buried only in memory is invisible to them. AGENTS.md / CLAUDE.md load at the start of every session
in that repo, so they are the durable cross-chat index.

## Example pointer (TOP of AGENTS.md)
```
## 📍 ГЛАВНЫЙ ФАЙЛ СЕТАПА (ЧИТАТЬ ПЕРВЫМ)
**Путь:** `C:\Projects\lazy-unicorn\SETUP_GUIDE.md` (корень монорепо)
Вся конфигурация среды — там. При вопросе «где лежит X» — читай этот файл, не гадай.
```

## Pitfalls
- Don't bury the pointer deep (e.g. section 23) — other agents skim the top.
- Don't put it ONLY in memory — not loaded by sibling chats.
- Write BOTH AGENTS.md and CLAUDE.md (different agents read different files).
- Don't paste full config into the pointer files; just path + one-line scope.
