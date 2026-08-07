---
name: ralph-mode
description: Autonomous development loops with iteration, backpressure gates, hats (personas), and completion criteria. Use for sustained coding sessions requiring multiple iterations, test validation, and structured progress tracking. Replaces 7 PowerShell loop scripts (ralph-init, ralph-cancel, ralph-stop-hook, doubt-gate, task-completion, drift-reanchor, auto-loop).
---

# Ralph Mode — Autonomous Development Loops (Hermes Edition)

Adapted for Hermes Agent from `@richginsberg/ralph-mode` v1.2.0 (ClawHub).

Replaces the 7 PowerShell loop scripts that were removed from ClawHub (references/scripts.md → 404).

## Core Principles

### Three-Phase Workflow

1. **Phase 1: Requirements Definition** — Document specs in `specs/` (one file per topic), define acceptance criteria
2. **Phase 2: Planning** — Gap analysis, create `IMPLEMENTATION_PLAN.md` with prioritized tasks
3. **Phase 3: Building (Iterative)** — One task per iteration, implement → validate → plan → commit

### Backpressure Gates

Hermes equivalents:

| Gate | OpenClaw PS1 | Hermes |
|---|---|---|
| Tests | ralph-stop-hook + test runner | `terminal('[test command]')` before declaring done |
| Typecheck | doubt-gate | `terminal('[typecheck]')` |
| Lint | task-completion checklist | `terminal('[lint command]')` |
| Build | auto-loop → rebuild | `terminal('[build]')` |

### Hats (Personas via delegate_task)

- **@architect** — high-level design, data modeling
- **@implementer** — write code, one file per iteration
- **@tester** — test authoring, edge cases
- **@reviewer** — code review, quality

Usage:
```
Spawn a sub-agent with @implementer hat to fix lib/db.ts line 27
```

### Loop Mechanics

**Outer Loop (you coordinate via /goal + todo):**
1. Don't allocate work to main context — spawn sub-agents
2. Let Ralph Ralph — LLM self-identifies and self-corrects
3. Plan is disposable — regenerate when stale
4. Move outside the loop — observe, don't micromanage

**Inner Loop (sub-agent via delegate_task):**
1. Study → Select → Implement → Validate → Update PROGRESS.md → Exit

### Mandatory PROGRESS.md

After each iteration, sub-agent writes to PROGRESS.md:
```markdown
## Iteration [N] - [Timestamp]
### Status: Complete | Blocked | Failed
### What Was Done
- [changes]
### Validation
- [results]
### Next Step
- [what next]
```

### Stopping Conditions
- All tasks completed
- All acceptance criteria met
- Tests passing, no blocking issues
- Max iterations reached (configured limit)
- Manual `/goal reset`

## Hermes-specific adaptation

| OpenClaw construct | Hermes equivalent |
|---|---|
| `ralph-init.ps1` | Write goal to `/goal`, create todo list |
| `ralph-cancel.ps1` | `/goal reset` + `todo` mark cancelled |
| `ralph-stop-hook.ps1` | `notify_on_complete=true` on `terminal(background=true)` |
| `doubt-gate.ps1` | AGENTS.md rules + terminal command check |
| `task-completion.ps1` | `todo` tool with verify command |
| `drift-reanchor.ps1` | `/goal` re-read (system prompt injection) |
| `auto-loop.ps1` | `execution-loop` skill + `cronjob` |
| `sessions_spawn` → sub-agent | `delegate_task(goal=...)` |
| `IMPLEMENTATION_PLAN.md` | `todo` tool (structured checklist) |
| `PROGRESS.md` | Sub-agent writes to `PROGRESS.md` in project root |
