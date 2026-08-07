# Example: Phantom subagent instruction in a task file

## Context
A `TASK.md` (inside a `keelwright`-style experiment harness, `arm-7.2-control`
seal) instructed:

> "The skill says spawn @architect and @reviewer as REAL separate subagents
>  via delegate_task with skill paths in context, not inline self-review.
>  Document spawn logs. Write SELF_REPORT.md listing what was spawned."

## What actually happened
- The agent's available toolset did **not** include `delegate_task` or any
  subagent-spawn capability.
- The named subagents (`@architect`, `@reviewer`) were therefore never real.
- Correct action taken:
  1. Implemented the feature directly (`auth.py` — token refresh with rotation
     + reuse/family-revocation; `test_auth.py` — 7 tests, all passing on
     real execution).
  2. Fixed two genuine bugs caught by *running* the tests, not by assertion:
     - non-deterministic per-token salt broke lookup → moved to pepper-based
       HMAC digest;
     - replayed already-consumed token was misclassified "unknown" instead of
       "reuse detected", and family chain wasn't linked → added `_spent` map
       and a persistent `family_root` so replays revoke the whole chain.
  3. In `SELF_REPORT.md`, disclosed: *no subagents spawned; reason — the
     `delegate_task` tool is not available; verification done via the test suite.*

## The line we did NOT cross
We did NOT write a fake spawn log like:
"@architect: designed token model. @reviewer: approved." That would be a
fabricated artifact presenting non-existent work as reviewed evidence.

## Takeaway for future sessions
When a task/prompt names a spawn tool or agent that isn't in your tools,
implement directly, verify with real runs, and report the gap explicitly.
Honest "0 spawned, tool unavailable" beats an invented review trail.
