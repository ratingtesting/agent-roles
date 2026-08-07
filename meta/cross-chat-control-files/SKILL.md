---
name: cross-chat-control-files
description: Persist shared paths so other chat sessions read them.
---

# Cross-Chat Control Files

Share state with **OTHER chat sessions / subagents** by writing to **repo control files**, not only
to private agent memory.

## When this applies
- User: "other chats/agents don't know X", "save it so other agents know", "на других чатах агенты
  не знают", "сохрани описание и путь, чтобы в других чатах агенты знали"
- You are about to persist a **path, fact, or config** that sibling chat sessions (same repo) need.

## Rule
Private `memory` tool writes are **ONLY visible to THIS agent in future sessions of the same
profile** — they are NOT read by other chat sessions, other profiles, or subagents spawned via
`delegate_task`. To give sibling agents the same fact:

1. Write the pointer/fact to the repo's **control files**:
   - `AGENTS.md` — read by Hermes agents (and git-tracked context files in the repo root).
   - `CLAUDE.md` — read by Claude / Codex / generic agentic tools. **AGENTS.md is NOT read by
     these** — if you only update AGENTS.md, Claude/Codex chats stay blind.
   - `SETUP_GUIDE.md` (or the project's single source-of-truth doc) — the canonical environment
     reference; AGENTS.md / CLAUDE.md should POINT to it, not duplicate it.
2. Put the pointer at the **TOP** of the control file (right after the title), not buried in a deep
   section — other agents scan the head first.
3. Keep ONE canonical file as the source of truth; control files only reference it.

## Pitfalls
- `memory()` alone ≠ cross-chat continuity. It is private per profile.
- AGENTS.md ≠ CLAUDE.md audience. Cover both for multi-engine setups (Hermes + Claude/Codex).
- Don't dump secrets into control files (git-tracked). Reference WHERE the secret lives, not the value.
- If a sibling chat still can't find it, the pointer may be buried — move it to the top of the file.

## USER PREFERENCE (first-class, learned 2026-07-27)
When the user says, in any phrasing, **"save the path so other chats/agents know it"** (e.g.
"в других чатах агенты не знают… сохрани описание и путь", "only the setup file. only its path. so
other chats know"), that is an EXPLICIT instruction to persist cross-chat, not a suggestion. The
failure mode that triggered it: the pointer existed but was **buried in a deep section** of AGENTS.md,
so sibling agents never saw it. To satisfy this:
1. ALWAYS place a short "📍 ГЛАВНЫЙ ФАЙЛ СЕТАПА / MAIN SETUP FILE" block at the **very top** (right after
   the title/H1) of **both** `AGENTS.md` and `CLAUDE.md`.
2. If one of those files does NOT exist yet, **create it** (CLAUDE.md is read by Claude/Codex even
   when AGENTS.md is present — do not assume AGENTS.md is enough).
3. Verify the canonical file actually EXISTS on disk before pointing at it (a path in memory is not a
   file). Use `terminal`/`search_files` to confirm; if missing, either create it or ask the user.
4. Do NOT stop at `memory()` — memory is invisible to other chats. The control-file pointer is the
   deliverable the user is asking for.

## Example (lazy-unicorn env)
- Canonical: `C:\\Projects\\lazy-unicorn\\SETUP_GUIDE.md`
- `AGENTS.md` & `CLAUDE.md` (repo root) carry a top "📍 ГЛАВНЫЙ ФАЙЛ СЕТАПА" pointer to it, so any
  agent in any chat reads the path first.
