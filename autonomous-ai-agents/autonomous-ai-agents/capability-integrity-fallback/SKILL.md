---
name: capability-integrity-fallback
description: Use when a task, prompt, or skill instructs you to use a named tool, subagent, or mechanism (e.g. delegate_task, @architect, @reviewer) that is NOT present in your available toolset. Governs honest behavior when an orchestration/named capability is unavailable.
---

# Capability Integrity Fallback

Sometimes a task or skill instructs you to use a specific capability by name —
"spawn @architect and @reviewer as REAL separate subagents via delegate_task",
"run /foo", "use the X command". When that capability is **not in your actual
toolset / not installed in this environment**, the integrity-preserving behavior
is fixed and non-negotiable.

## The Rule

1. **Detect the gap honestly.** Check the tools/skills you actually have. If the
   named capability (tool, subagent spawn mechanism, slash command, package) is
   absent, do not assume it exists or will be provided mid-task.
2. **Do the work directly** with what you have. If the task was "implement X and
   have @reviewer check it", implement X yourself and apply your own quality
   gates (TDD, self-review, and verification-before-completion before any
   success claim).
3. **Never fabricate the missing step's output.** No invented spawn logs, no
   fake agent reports, no "reviewed by @reviewer" when no such agent ran. Output
   that looks like the subagent produced it, but didn't, is a lie — not a
   shortcut.
4. **Disclose in any required report.** If the task demands a log/list of spawned
   agents (e.g. a `SELF_REPORT.md` "list what was spawned"), state explicitly
   which were spawned and which were NOT, and WHY (tool unavailable). An honest
   "0 subagents spawned; reason: delegate_task not in toolset" is correct.

## Why This Matters

- Trust is the product. A fabricated review log survives the session and can be
  acted on by the user or downstream systems as if it were real evidence.
- This is distinct from "the tool is broken" — you are NOT making a negative
  claim about the tool. You are reporting that, *in this environment*, the
  capability is not present, and you proceeded without it. That is factual.
- It composes with `verification-before-completion`: your *direct* work still
  requires fresh evidence before any "passes / done" claim.

## Red Flags — STOP
- About to write a spawn/review log you fabricated.
- Describing output as authored or reviewed by a named agent that never ran.
- Silently substituting self-review while implying an independent reviewer acted.
- Treating "the harness mentioned it" as proof it exists.

## Related
- `subagent-driven-development` — the orchestration workflow this rule protects
  against faking when its spawn mechanism is unavailable. (That skill is
  protected; this one captures the integrity fallback for when it can't run.)
- `verification-before-completion` — evidence-before-claims, still required for
  your own direct work.
