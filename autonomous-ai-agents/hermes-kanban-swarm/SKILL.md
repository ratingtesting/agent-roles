---
name: hermes-kanban-swarm
description: Orchestrate agent swarms via native Hermes Kanban.
---

# Hermes Kanban Swarm Orchestration

Orchestrate a *рой* of specialized worker agents through the native Hermes Kanban instead of
prompting each agent. The dispatcher (hosted by the gateway) promotes `todo→ready` only when a
task's parents are `done`, and runs workers in isolated workspaces. The founder stays out of
the loop unless something escalates.

## When to use
- "Собери рой агентов" / "proof pack" / "волна специалистов" — multi-agent doc/code production.
- Any multi-wave batch with dependency gating (wave N waits for wave N−1) where the founder must NOT be a bottleneck.
- Reusing named specialist agents/skills (founder-visionary, unlock-architect, economy-designer, strategy-duel-agent, growth-hacker, ...) per task.

## Steps

### 1. Board + init (per profile)
```bash
hermes --profile app kanban boards create <slug> --name "..." --icon 🐝 --switch
hermes --profile app kanban init
```

### 2. Shared context (MUST, in project root)
- `MANIFEST.md` — compressed manifesto every worker must obey (what we build, platform, MVP goal).
- `PROGRESS.md` — loop-coding log: per-task Termination Conditions DONE/FAILED, attempt N/3, result, reason, next step; escalate at 3/3 ❌ via a kanban comment, NOT to the founder.
- `00_Founder/Brief.md` holds each worker's section pointer.

### 3. Cards per dependency wave (`--parent` = dependency)
```bash
hermes --profile app kanban --board <slug> create "<title>" \
  --assignee <profile> --workspace "dir:<abs project path>" \
  --max-retries 3 --created-by founder --json \
  --parent <parent_task_id> ... --body "<full instruction ctx>"
```
- `--priority` takes an INT, not a flag string (`P1` errors).
- Dispatcher promotes a child only after all its parents are `done`.

### 4. Skill loading — CRITICAL pitfall
`--skill` on `kanban create` (and `-s` on `chat`) is UNRELIABLE in profile app — often
"Unknown skill: <name>" even when `skills list` shows it; nested-duplicate skill folders
compound it. Do not depend on it. Instead put **in the card body**:
> **РОЛЬ:** First call skill loaded with `skill_view(name='<skill>')` and act strictly in that role.
> <task instruction> <shared context>

Workers loading the skill in-session works.

### 5. Dispatcher = gateway
```bash
hermes --profile app gateway run   # background; ticks ~60s
hermes --profile app config set platforms.api_server.port 8643   # if port clash
```
No gateway → tasks stay in `ready` forever. Recovery pass: `kanban --board X dispatch` (manual one-shot).

### 6. Monitor
```bash
hermes --profile app kanban --board X stats | list | log <id>  # status counts, task view, worker log
```

## Pitfalls
- **Skill preload `--skill` unreliable** → embed "call skill_view" in the card body (step 4).
- **Duplicated nested skill folders** `skills/X/X/SKILL.md` cause "Ambiguous/Unknown skill". Dedupe by moving identical copies to a backup dir — do NOT touch user-owned skills (e.g. keelwright, kept separate v1.5.5 vs v1.4.1). Note keelwright's nested copy is a NEWER version — verify before dedupe.
- **Gateway port clash** by another profile → bump `platforms.api_server.port`.
- **Tasks created `running` before gateway** → dispatcher cleans up on startup; rebuild via `reclaim` + recreate.
- **Semantic graph / gbrain may fail at wave boundaries** — record in PROGRESS.md, do NOT fake success.

## Definition of Done (audit)
- `kanban stats` → all `done`, 0 `running`/`blocked`.
- Files exist at expected paths — non-empty, valid markdown, structure per Brief, references to deps, no TODO/FIXME, no contradiction with MANIFEST.
- Fix worker numeric-naming/link defects (e.g. Risk-§6 numbering + ADR-005 link mismatch).

## Support files
- `references/kanban-swarm-checklist.md` — repeatable runbook + command cheat-sheet.