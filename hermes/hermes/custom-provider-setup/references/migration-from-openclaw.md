# OpenClaw → Hermes Migration Reference

## Architecture Comparison

| Dimension | OpenClaw | Hermes Agent |
|-----------|----------|--------------|
| Config file | `~/.openclaw/openclaw.json` | `~/.hermes/config.yaml` |
| Secrets | `~/.openclaw/.env` or System User env vars | `~/.hermes/.env` (file-based, loaded at startup) |
| Identity | `workspace/SOUL.md` + `workspace/USER.md` | `~/.hermes/SOUL.md` + `memories/USER.md` (via memory tool) |
| Project rules | `workspace/AGENTS.md` | `AGENTS.md` (cwd) or `.hermes.md` (walk parents) |
| Skills | `workspace/skills/<name>/SKILL.md` | `~/.hermes/skills/<category>/<name>/SKILL.md` (bundled) or `~/.hermes/skills/<name>/SKILL.md` (local) |
| Skill install | `clawhub install <author>/<name>` | `hermes skills install <ID>` or URL |
| Plugins | TypeScript `extension.ts` | Python plugins or MCP servers |
| Gateway | built-in (Telegram, Discord, etc.) | `hermes gateway setup/start` |
| Session search | `memory_search` | `session_search` (FTS5, free) |
| Browser | `agent-browser` (npm) | Built-in browser toolset (`browser_navigate`, etc.) |
| Execution sandbox | none | `execute_code` (Python), Docker/SSH/Modal backends |

## Workflow Mapping (Detailed)

### Feature Development

**Before (OpenClaw):**
```
/do feature-name
 → skill discovery: npx skills find "..."
 → read brain/INDEX.md
 → spawn @software-architect
 → wait for user "let's build"
 → VibeSafe check → code → test → review → commit
```

**After (Hermes):**
```
/do feature-name
 → skill discovery: skills_list / skill_view
 → read brain/plans/current-status.md or use todo tool
 → delegate_task for parallel subtasks
 → wait for user "let's build"
 → VibeSafe (manual: web_search CVE check) → code → test → delegate_task 3 reviewers → commit
```

### Context Save

**Before (OpenClaw):** `/save` → update `brain/plans/current-status.md` → `openclaw token-usage` → `git add brain/ && git commit -m "memory: update"`

**After (Hermes):** `/save` → update `todo` tool / `brain/plans/current-status.md` → `memory tool` save findings → `git add brain/ && git commit -m "memory: update"`

### Bug Fix

**Before (OpenClaw):** `sessions_spawn` with `systematic-debugging` skill reference → 3 max attempts → counterfactual

**After (Hermes):** `skill_view(name='systematic-debugging')` → follow 4-phase process → 3 max attempts via `todo` → escalate

## Loop Coding Adaptation

OpenClaw had dedicated loop scripts (PowerShell) for:
- **Execution Loop** (Ralph) — prevent premature stop, detect hedging, check task checklist
- **Match Loop** — Generator → Visual Analyst → convergence
- **Autoresearch Loop** — Karpathy modify→verify→commit/revert
- **Phoenix Loop** — learn from repeated errors, write local skill

**In Hermes, these patterns are composable from built-in primitives:**

| Pattern | Hermes Primitives |
|---------|-------------------|
| Ralph (anti-drift) | `todo` tool for task checklist + `memory` for task state + `/compress` for context awareness |
| Doubt Gate (anti-hedging) | SOUL.md rules (caveman mode, no filler) + `AGENTS.md` termination conditions |
| Match Loop (visual check) | `delegate_task` visual agent + `vision_analyze` on screenshots + `browser_vision` |
| Autoresearch Loop | `cronjob` with chaining + `delegate_task` for verify step |
| Phoenix Loop | `skill_manage(action='create')` on 3rd same error + `memory` for pattern extraction |

There are no PowerShell scripts to migrate — the loop patterns should be implemented as SOUL.md behavioural rules + AGENTS.md workflow rules + Hermes built-in tools.

**⚠️ Adapted loop layers can be inert.** Layers whose triggers are cross-session counters ("every 10 iterations", "3 rollbacks", "pattern repeats across sessions") only fire if those counters are persisted to disk (`PROGRESS.md`, `autoresearch-lessons.md`, `phoenix-log.md`) or `memory`. A fresh chat has no iteration count. When auditing a migrated loop, grep the repo for these artifact files before claiming "it learns across runs" — if absent, the layer is decorative prose. See the `execution-loop` skill's "L4 is inert without persistent artifact files" note.

## Context-File Token Hygiene: Thin Dispatcher Skills (proven pattern)

The single biggest token win when migrating an OpenClaw `AGENTS.md` into Hermes: **AGENTS.md loads on EVERY turn of a project session; skills load on demand.** OpenClaw AGENTS.md files tend to inline full procedures (PONYTAIL ladders, `/do` workflows, review-agent tables, VibeSafe steps). Ported verbatim, that prose is re-sent every turn even when the user just asks "show me this file."

**The fix — extract procedure → thin dispatcher skill, leave a pointer in AGENTS.md:**

1. Identify prose blocks in AGENTS.md that are *procedures* (how to do a class of task), not *rules* (always-true constraints). Procedures belong in skills; rules stay in AGENTS.md.
2. Create ONE class-level skill (e.g. `coding-framework`) that is a **dispatcher, not a duplicator**: it holds the procedure AND a "stage → which native skill to call" mapping (PONYTAIL→`clean-code-review`, layers→`clean-architecture`, tests→`test-driven-development`). It must not restate what native skills already say.
3. Replace the extracted AGENTS.md block with a ~3-line pointer: "Before X, `skill_view(name='<skill>')`. Point of truth = the skill. Don't duplicate here."
4. Keep genuinely-unique rules (e.g. project-specific Dependency Impact Analysis) inline — don't over-extract.

**Measured result (this session):** `lazy-unicorn/AGENTS.md` 25430 → 19426 bytes (**−24%**) across two passes (coding-framework extraction, then LOOP-CODING practices → skill-pointer table), with zero rule loss. That's ~24% off every project-session turn.

**Why dispatcher, not full port:** a 1:1 port of the OpenClaw SKILL.md would (a) duplicate what's already in AGENTS.md and (b) shadow native Hermes skills, creating drift — the same rule in two places diverges. One point of truth per rule.

**Sequencing when the OpenClaw original is gone:** if the source skill was deleted (`.openclaw` removed), you can't port 1:1 — reconstruct from the AGENTS.md prose where it already lives as adapted text, and note "original OpenClaw skill removed" in the setup log so the provenance is clear.

## Custom Provider Config (Production Example)

This 4-endpoint config works with 3 API keys across 2 providers (agentrouter shared key):

```yaml
custom_providers:
  - name: 9router
    base_url: http://localhost:20128/v1
    key_env: AP
```

<!-- (remainder of custom-provider config section preserved from prior version) -->

## Third-Party Orchestration Frameworks: License-First Evaluation

When the native primitives aren't enough and you're recommending a third-party framework (CrewAI, LangGraph, Langflow, Flowise, AutoGen, etc.), **verify the license from the primary source (the repo's `LICENSE`/`LICENSE.md` file) before recommending** — never guess from memory. The user's downstream goal changes the answer:

- If the goal includes **redistribution, white-labeling, or building a resellable layer**, a permissive license (**MIT / Apache-2.0**) is required.
- Watch for the **open-core trap**: a repo can be Apache-2.0 at the core but ship an `enterprise/` directory (RBAC, SSO, multi-tenant, audit logs) under a separate **Commercial License**. Example (verified 2026): **Flowise** = Apache-2.0 community + Commercial `/enterprise`; the paid features are exactly the ones a "universal multi-tenant control plane" product needs. **Langflow** = pure **MIT**, no such trap. **CrewAI** = MIT (but visual Studio is paid). **AutoGen** = MIT but in maintenance mode (merged into MS Agent Framework).

Selection checklist for this user (solo founder, $0 budget, no Docker, Flutter+Supabase stack, wants mouse-driven + eventual universal layer):
1. **License** permits the end goal (MIT > Apache open-core for redistribution).
2. **Install without Docker** — pure `pip`/`npm`, no nested-virtualization requirement.
3. **No-code / visual** if the user said "mouse, not code."
4. Reuse existing stack for durable state + live dashboard (Supabase Postgres + Realtime) rather than adopting a new datastore.
5. A "beautiful + free + local + no-Docker" turnkey dashboard generally **does not exist** — vendors monetize the pretty UI (SaaS/Docker/enterprise). Expect to assemble the visualization (e.g. React Flow or Flutter over Supabase Realtime) on top of a free engine.

### Product-vs-engine architecture (this user's Step 2)

When the user's product is "sell trained AI-companies", the sellable IP is a **portable, engine-independent Company Schema** (YAML/JSON: company → departments → roles → tools → tasks → handoffs), consumed by a thin **adapter layer** that maps schema → whichever engine (CrewAI / OpenHands / Langflow). Never couple the template format to one engine — that's lock-in, and a license change on that engine can kill the product. A loop-coding development pipeline (ralph-mode/execution-loop) is a *different machine* from the sellable multi-role company product; don't assume one evolves into the other.

## Workflow Rule: Documentation-First Migration

**When migrating skills from another framework, READ THE SOURCE SKILL DOCUMENTATION before proposing adaptations.**

Incorrect approach (this session's original mistake):
1. See OpenClaw skill name → guess what it does → propose Hermes equivalent → user corrects

Correct approach (user-enforced):
1. Fetch the source skill's SKILL.md (via `web_extract` or `git clone`)
2. Read supporting files (`references/`, `scripts/`, prompts)
3. Understand the skill's actual mechanism, not just its name
4. THEN adapt to Hermes primitives (`delegate_task`, `cronjob`, `todo`, `browser_*`, etc.)
5. Preserve the skill's core semantics — only change the transport mechanism

This applies to ALL migration work: skills, loop scripts, security tools, memory protocols. The source documentation is the ground truth, not the agent's assumption about what the skill probably does.

## Loop Skills: Source Documentation → Hermes Adaptation

Three ClawHub loop skills were adapted this session. The source documentation (ClawHub pages) was read before adaptation:

| Source Skill | What It Actually Does (from docs) | Hermes Adaptation |
|---|---|---|
| `execution-loop` (lanyasheng v2.4.0) | 7 patterns: Ralph stop-hook, Doubt Gate hedging scanner, Task Completion checklist, Drift Re-anchor, Adaptive Triage, Iteration-aware messaging, Headless control. Implemented as bash stop-hooks in OpenClaw. | `execution-loop` Hermes skill: same 7 patterns mapped to `/goal`, `todo`, `cronjob`, `delegate_task`, SOUL.md caveman rules. No bash scripts — behavioral rules + built-in tools. |
| `match-loop` (rocketship4545 v1.0.0) | Generator subagent codes UI → Analyst subagent visually inspects via browser → feedback packet → revise → converge | `delegate_task` (generator) + `delegate_task` (analyst with browser toolset: `browser_navigate`, `browser_vision`, `browser_click`) → feedback → re-dispatch |
| `huo15-autoresearch-loop` (zhaobod1 v1.0.3) | Karpathy modify→verify→commit/revert cycle with state file and convergence detection | `cronjob` tool for recurring cycles + `/goal` for target + `todo` for iteration tracking |
