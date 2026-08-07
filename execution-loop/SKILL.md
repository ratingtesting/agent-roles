---
name: execution-loop
description: Use when agent risks stopping early, drifting from task, claiming completion without verification, running long autonomous sessions, or when performing iterative modification loops (modify-verify-decide) — provides the full loop system with persistence, verification, stability checks, escalation ladder, and cross-run learning
version: 2.1.0
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [workflow, execution, loop, autonomous, adaptation]
---

# Execution Loop (Hermes Edition) — Full Loop System

Adapted for Hermes Agent from 4 ClawHub sources:
- `@lanyasheng/execution-loop` v2.4.0 — Ralph, Doubt Gate, Task Completion, Drift Re-anchor, Adaptive Triage
- `@rocketship4545-a11y/match-loop` v1.0.0 — Generator ↔ Visual Analyst vibe-coding loop
- `@leostehlik/autoresearch-loop` v0.2.1 — Bounded modify-verify-decide loop with rollback proof, escalation ladder, lessons
- `@zhaobod1/huo15-autoresearch-loop` v1.0.3 — Karpathy Modify→Verify→Keep/Discard→Repeat

Plus:
- Loop Stability Check — 5 named failure modes (dead retry, oscillation, drift, amplification, feedback starvation)
- Phoenix Loop — cross-run learning from repeated failures

**These are not separate tools. They are layers of one system applied depending on task type.**

## CRITICAL RULE: Read Source Documentation Before Adapting

Before adapting ANY skill for Hermes:
1. **Read the full ClawHub/GitHub source page** — description, patterns, workflow, scripts, references. The original author's documentation is authoritative.
2. **Test the deps** — old configs break. Graphify API changed in v0.9.12, Cloudflare hit 429 daily limit. Always probe before declaring working.
3. **Use browser for web inspection** — `browser_navigate` to error URLs. Don't guess from curl or web_extract output. The browser toolset (navigate, snapshot, vision, console) exists for interactive inspection.
4. **High-star projects are not dangerous** — GitHub stars are a better trust signal than a local scanner. 252k ⭐ superpowers is a legitimate project. Use --force when the scanner is wrong.
5. **Never dismiss tools or repos as "not needed" / "not priority"** without reading what they actually do. Every OpenClaw script and skill on ClawHub had a purpose documented in the original page. Read first, then decide. Saying "not a priority" before reading = dismissal, not triage.
6. **Clean reinstall, never cache restore** — when reinstalling something that was removed, install fresh from the original source. Never restore from backup, trash, or desktop-attachments cache — those are stale copies that produce unexplained bugs.
7. **Test models comparatively, not sequentially** — when choosing between two models, run them on the same prompt, measure both quality and latency side by side. A single "it works" test doesn't tell you which is better.
8. **Matrix thinking, not linear** — when the user asks for an inventory or table of all components, list everything in one structured table. Don't trickle-feed partial answers per turn.

Pattern: DOC → TEST → ADAPT → VERIFY.

## Structure: 5 Layers, Selected by Task Type

```
                              ┌──────────────────────────────┐
                              │     Task Arrives              │
                              └────────┬─────────────────────┘
                                       │
                          ┌────────────▼────────────┐
                          │    COMPLEXITY TRIAGE     │
                          │  (Adaptive Complexity)   │
                          └────────────┬─────────────┘
                    ┌──────────────────┼──────────────────┐
                    ▼                  ▼                  ▼
              ┌──────────┐     ┌───────────┐      ┌──────────┐
              │ Trivial  │     │ Standard  │      │ Complex  │
              │ (Express)│     │ (Loop)    │      │ (Full)   │
              └──────────┘     └───────────┘      └──────────┘
                                      │                  │
                    ┌─────────────────▼──────┐    ┌──────▼──────────┐
                    │  Layer 2: PERSISTENCE  │    │ Layer 2–5 FULL │
                    │  (Ralph/Doubt/Drift)   │    │   STACK        │
                    └─────────────────┬──────┘    └──────┬──────────┘
                                      │                  │
                              ┌───────▼───────┐  ┌───────▼───────┐
                              │ Layer 3:      │  │ Layer 3:      │
                              │ STABILITY     │  │ STABILITY     │
                              │ (5 failure    │  │ + PHOENIX     │
                              │  modes scan)  │  │ (cross-run)   │
                              └───────┬───────┘  └───────┬───────┘
                                      │                  │
                              ┌───────▼───────┐  ┌───────▼───────┐
                              │ Layer 4:      │  │ Layer 4:      │
                              │ PHOENIX       │  │ AUTORESEARCH  │
                              │ (lightweight) │  │ (full loop)   │
                              └───────┬───────┘  └───────┬───────┘
                                      │                  │
                                      └──────────────────┘
                                                  │
                                          ┌───────▼───────┐
                                          │ Layer 5:       │
                                          │ MATCH          │
                                          │ (visual QA)    │
                                          └───────┬───────┘
                                                  │
                                          Done ───┘
```

## Layer 1: Adaptive Complexity Triage

Before ANY loop, classify the task. This picks the mode for all subsequent layers.

| Level | Criteria | Layers Active | Mode |
|---|---|---|---|
| **Trivial** | 1 file, typo/rename/comment fix | None (no loop) | Express: fix + commit + done |
| **Low** | 1-2 files, trivial feature/bug | Layer 2 only (Ralph basic) | Light: persistence + check |
| **Standard** | 2-5 files, feature/bug | Layers 2-3 | Loop: persistence + stability |
| **High** | 5+ files, architecture change | Layers 2-4 | Full: persistence + stability + phoenix |
| **Critical** | Security, data loss, production | Layers 2-5 | Full+Match: all + visual QA |

**Default is Standard** — never assume Express when unsure (Express skips gate checks).

## Layer 2: Persistence (Ralph + Doubt + Drift + Task Completion)

Adapted from `@lanyasheng/execution-loop`. Don't stop early, don't hedge, don't drift.

### Tools (no bash hooks — Hermes builtins)

| Original OpenClaw Hook | Hermes Builtin |
|---|---|
| `ralph-init.sh` + `ralph-stop-hook.sh` | **`/goal`** — sets persistent task goal injected into every system prompt |
| `doubt-gate.sh` | **SOUL.md caveman rule** — forbidden words: "likely", "probably", "maybe", "should work", "looks like" |
| `task-completion-gate.sh` | **`todo` tool** — create checklist, mark completed, never claim done with items pending |
| `drift-reanchor.sh` | **`/goal`** — re-anchoring is built-in (every turn has goal in context) |
| `ralph-cancel.sh` | **User says stop** — that's the cancel signal |
| `iteration-aware-messaging.sh` | Structured feedback: iteration awareness via AGENTS.md format |

### Rules

1. **Start every task:** create `todo` with ordered subtasks. Mark done as you complete.
2. **Before claiming done:** check `todo` has all items completed. Check `/goal` — does the output match the goal?
3. **No hedging:** If you're unsure, run the test/verify command — report real result. Not "it should work".
4. **Safety valves** (always respected, override all persistence):
   - Context >= 80% — stop gracefully
   - Auth failures (401/403) — stop and report
   - 3 consecutive identical errors — STOP, write counterfactual explanation, escalate
   - User says "stop" or changes topic — stop
5. **Iteration limit:** max 3 attempts per problem, then escalate (from AGENTS.md)

## Layer 3: Stability Check (5 Failure Modes)

Adapted from OpenClaw Loop Stability Check concept.

Every 3 iterations (or before any progress claim), scan for these 5 named failure modes:

### 1. Dead Retry
Each iteration does the same thing.
- **Signal:** same error message, same fix, same result
- **Action:** switch approach fundamentally (not a variation)
- **Escalate after:** 3 consecutive dead retries

### 2. Oscillation
Fix A → breaks B → fix B → breaks A.
- **Signal:** reverting last iteration's change
- **Action:** stop and ask user for guidance, or write a plan that addresses both
- **Escalate after:** 2 oscillations

### 3. Drift
Original task is forgotten.
- **Signal:** working on tangents, improving unrelated code, "while I was at it..."
- **Action:** re-read `/goal`, re-read task description, discard tangent work
- **Counter:** every 5 turns, re-state the original goal

### 4. Amplification
Each change makes things worse.
- **Signal:** more errors after each iteration, metrics degrade
- **Action:** `git revert` to last good state, ask for help
- **Escalate after:** 2 amplifications

### 5. Feedback Starvation
Tests pass, lint passes, but UI is broken / feature doesn't work.
- **Signal:** green checkmarks but user reports something is wrong
- **Action:** launch Match Loop (Layer 5) — visual inspection
- **Escalate after:** 1 round of visual QA still fails

## Layer 3b: Autoresearch Loop (Bounded Modify→Verify→Decide)

Adapted from `@leostehlik/autoresearch-loop` v0.2.1 and `@zhaobod1/huo15-autoresearch-loop` v1.0.3.

Use when the user explicitly asks for iterative improvement toward a measurable metric.

### Run Contract

DO NOT start without explicit confirmation of ALL of:

| Field | Description | Example |
|---|---|---|
| **Goal** | One sentence, measurable | "Reduce widget render time under 200ms" |
| **Metric** | Number, direction, baseline, target | "render_time: 350ms → <200ms" |
| **Verify command** | Exact command to measure metric | `flutter test --benchmark` |
| **Guard command** | Command that must keep passing | `flutter test` (all unit tests) |
| **Scope** | Files allowed to change | `lib/widgets/` |
| **Forbidden scope** | Files NEVER changed | `lib/auth/`, `supabase/` |
| **Rollback** | How to revert failed attempts | `git revert HEAD` (per commit) |
| **Iteration cap** | Max iterations | 20 |
| **Run mode** | foreground (default) or background/unattended | foreground |
| **External research** | Web search allowed? | No |

Show the contract as a table. Get explicit approval before starting.

### Core Loop

```
1. Confirm approved run contract
2. Read lessons file (autoresearch-lessons.md)
3. Pick ONE hypothesis
4. Make ONE atomic change inside scope
5. COMMIT/SNAPSHOT before verification (so rollback is clean)
6. Run VERIFY command
7. Run GUARD command
8. Decision: keep / discard / rework
   - Verify+Guard PASS — keep, extract lesson
   - Verify PASS + Guard FAIL — rework (max 2 attempts), then discard
   - Verify FAIL — discard using approved rollback
9. Log the result in iteration log
10. Read original goal every 10 iterations (anti-drift)
11. Repeat until: goal met, cap reached, user stops, blocker hits
```

### Escalation Ladder

| Trigger | Action |
|---|---|
| 3 consecutive discards | REFINE — adjust within same strategy |
| 5 consecutive discards | PIVOT — abandon strategy, try fundamentally different approach |
| 2 PIVOTs without improvement | Ask user before web search |
| 3 PIVOTs without improvement | SOFT BLOCKER — stop, report to user |

A single successful keep **resets all counters**.

### Safety (CRITICAL)

- Default: foreground mode only. Background = explicit user approval + iteration cap
- Never modify guard files
- Never reset unrelated user work
- Never push, deploy, publish, touch production unless explicitly approved
- Never expose private code, secrets, logs to external sources

### Lessons File

Extract structured lessons after every:
- Kept iteration (what worked, why)
- PIVOT decision (what failed, why)
- Run completion

Store: `autoresearch-lessons.md` in repo root (DO NOT commit unless user says so).
Consult at run start. Keep about 50 entries, summarise older ones.

## Layer 4: Phoenix Loop (Cross-Run Learning)

Adapted from OpenClaw Phoenix Loop concept. Layer on top of Execution Loop that converts repeated errors into durable knowledge.

**Trigger:** When Layer 3 detects a failure mode that repeats >=2 times across sessions.

### Protocol

```
1. DIAGNOSE: What specific pattern is failing?
   (Exact error message? Exact scenario? Exact rationalization?)
2. EXTRACT: Write a structured lesson either in autoresearch-lessons.md or as a durable memory record:
   - Pattern: what triggers the failure
   - Root cause: why it happens
   - Fix: how to avoid it next time
   - Example: the actual error
3. CRYSTALLISE: If pattern repeats 3+ times across sessions:
   - Propose a new skill (via skill_manage)
   - Or update AGENTS.md / TOOLS.md with a new rule
4. VERIFY: In next session, check: does the fix prevent recurrence?
```

**Phoenix does not replace the failure mode scanner. It fires AFTER the scanner detects recurrence.**

## Layer 5: Match Loop (Visual QA)

Adapted from `@rocketship4545-a11y/match-loop` v1.0.0. For vibe-coding where one-shot generation isn't enough.

### Pattern: Generator ↔ Analyst Loop

1. **Define target** — what "perfect" means, must-have features, visual/style expectations
2. **Spawn Generator** (`delegate_task`) — codes the artifact
3. **Spawn Analyst** (`delegate_task` with browser toolset) — reviews code + visually inspects UI
4. Analyst produces **feedback packet**: what works, what's broken, screenshots, prioritized changes
5. Generator revises → repeat until convergence

### Analyst Responsibilities (NON-NEGOTIABLE for frontend)

The analyst MUST visually inspect the frontend. Code review alone is insufficient.

**Order of browser tools:**
1. `browser_navigate` to open the app
2. `browser_vision` for screenshots
3. `browser_click` / `browser_type` for interactions
4. `browser_console` for runtime errors
5. `browser_snapshot` for DOM structure

**Check for:**
- Text cut off, overlapping, low contrast, misaligned
- Mobile/desktop layout problems
- Broken spacing, hierarchy, visual balance
- Forms that look fine in code but fail in UI
- Loading/error states that look broken
- Silent API failures (check console)
- Buttons that do nothing

### Convergence Rule

Analyst accepts ONLY after:
- Code review passes for task scope
- Frontend visually inspected (if applicable)
- Key interactions tested
- Major visual/functional defects resolved

Stop when: analyst accepts, trashing (revisions don't improve), blocked, or user says stop.

## Complete Workflow: Putting It All Together

```
User: "Implement user profile page with avatar upload"
  |
  +-- Layer 1: Triage
  |   > 5 files, feature -> Standard mode
  |
  +-- Layer 2: Persistence
  |   > /goal "Implement user profile..."
  |   > todo: [create avatar widget, upload logic, profile form, tests]
  |   > Execute tasks one by one
  |
  +-- Layer 3: Stability Check (every 3 iterations)
  |   > No oscillation detected -> OK
  |
  +-- Layer 4: Phoenix (check if this pattern failed before)
  |   > First time -> skip
  |
  +-- Layer 5: Match Loop
  |   > Generator codes avatar widget
  |   > Analyst opens app in browser, checks both mobile+desktop
  |   > "Avatar crops wrong on mobile, file picker doesn't close on cancel"
  |   > Generator fixes -> Analyst re-checks -> accepted
  |
  +-- Done -> finishing-a-development-branch
```

## Integration

Load alongside:
- `skill_view(name='writing-plans')` — task decomposition
- `skill_view(name='executing-plans')` — batch execution
- `skill_view(name='test-driven-development')` — RED-GREEN-REFACTOR
- `skill_view(name='systematic-debugging')` — when stuck
- `skill_view(name='requesting-code-review')` — final review
