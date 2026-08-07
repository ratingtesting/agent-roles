---
name: import-agent-collection
description: Use when installing a markdown agent repo as Hermes skills.
---

# Import Agent Collection → Hermes Skills

## Overview
External repos like `msitarzewski/agency-agents` ship hundreds of specialized agents as standalone `.md` files with YAML frontmatter. Hermes consumes skills as `<skill>/SKILL.md` with a different, stricter frontmatter. This skill is the repeatable pipeline to turn one into the other — and to fill role gaps the repo doesn't cover with purpose-built custom skills.

## When to Use
- User points at a GitHub agent-collection repo and says "install these agents" / "set them up as skills".
- You need a swarm of role agents (founder, architect, growth, etc.) and want to reuse a maintained community collection instead of authoring from scratch.
- After import, you must author platform/vision-specific agents the collection lacks.

## Core Pipeline

### 1. Clone (shallow) + inventory
Clone to a stable local path, then list agent files. In this Windows/MSYS env, `search_files(target='files', pattern='*.md')` returns 0 — use terminal `find` instead:
```bash
git clone --depth 1 https://github.com/msitarzewski/agency-agents.git
cd agency-agents && find . -name '*.md' -not -path './.git/*' | sort
```

### 2. Map names → repo files
Build an explicit mapping of the requested agent names to their source `.md` paths. Watch for:
- **Name collisions**: two requested names pointing at ONE file (e.g. `software-architect` and `engineering-software-architect.md` are the same file). Install it under both names as aliases.
- **Missing in repo**: if a requested role isn't in the repo, DON'T fabricate — note it for custom authoring (step 4).
- **Ambiguous matches**: confirm exact filename before writing.

### 3. Convert frontmatter → write SKILL.md
agency-agents frontmatter has fields: `name, description, color, emoji, vibe, tools`. Hermes SKILL.md frontmatter accepts: `name, description` (required), plus optional `license, compatibility, metadata, allowed-tools`.

Conversion rule: **keep `name` + `description`, drop `color/emoji/vibe/tools`**, move the markdown body (everything after the closing `---`) verbatim.

Write each to `~/AppData/Local/hermes/skills/<skill-name>/SKILL.md`.

See [references/agency-agents-format.md](references/agency-agents-format.md) for the exact field mapping and a ready-to-adapt conversion script (run via `execute_code`; note the MSYS→Windows path fix in `wpath()`).

### 4. Author missing role-specific custom skills
The collection rarely has vision-only, platform-specific, or meta roles your project needs. For each gap, author a custom skill following `writing-skills` (study the official `agentskills.io/specification` + a rich example agent first — the user expects rigour, not guesswork). Patterns that worked this session:
- **Vision-only agent** (`founder-visionary`): explicit "NO CODE" hard rule; delivers Vision/NorthStar/AntiGoals docs.
- **Platform-specific architect** (`flutter-architect`): Clean Architecture + plugin-system + TON/Telegram; specifies, does not implement.
- **Meta/editor role** (`chief-simplicity-officer`): scope-cutting review template.
- **Mechanic/campaign architects** (`unlock-architect`, `campaign-architect`): plugin-contract so core never branches on type.

A good custom skill body: Identity & Mindset → Core Mission (with a deliverable template) → Critical Rules → Red Flags. Keep frontmatter `description` trigger-focused (what+when, keywords), body <500 lines.

### 5. Verify
Run `skill_view(name='<each>')` for every installed/created skill. Confirm `readiness_status: available` and valid frontmatter. List the skills dir to confirm one `SKILL.md` per entry.

## Critical Rules
1. **Never fabricate an agent that isn't in the repo.** Missing role → custom-author, don't fake a conversion.
2. **Preserve `description` quality.** Copy the repo's `description` verbatim (it's already trigger-focused); don't summarize the workflow in it.
3. **Skill `name` = directory name**, lowercase-hyphen, ≤64 chars, no `--`.
4. **Plugin contracts over switches** — when authoring custom mechanic/campaign/architect skills, mandate that core loads by id/registration, never `if (type == …)`.
5. **Custom skills must respect the manifest** of the project they serve (e.g. virality-is-product) — don't cut the core thesis.

## Common Mistakes
- Using `search_files` glob on this host → returns 0; use terminal `find`.
- Forgetting MSYS `/c/...` paths break when passed to the natively-Windows Hermes python in `execute_code` → convert with `wpath()` (see references).
- Installing a name-collision file only once → the second alias silently missing.
- Authoring custom agents that write code when the role should only produce specs/docs.

## References
- [references/agency-agents-format.md](references/agency-agents-format.md) — frontmatter field map + runnable conversion snippet.
