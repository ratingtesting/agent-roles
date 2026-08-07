---
name: autonomous-loop-design
description: >-
  Design and implement autonomous loops — cron/webhook/goal-chasing processes that
  monitor a folder (or resource), detect new work, act, decide when to stop, and
  escalate. Use when a task asks for a "loop", "watcher", "daemon", "cron job",
  "autonomous agent", or "monitor that processes new files". Covers the five
  mandatory design dimensions and a known-good stdlib-only implementation.
version: 1.1.0
metadata:
  hermes:
    tags: [loop, cron, daemon, watcher, automation, monitoring, escalation]
    related_skills: [windows-msys-shell, test-driven-development, verification-before-completion]
---

# Designing an autonomous loop

A robust autonomous loop must make five dimensions explicit. Call them out in the
design doc before writing code — missing any one is the usual cause of runaway,
silent, or data-destroying loops.

## 1. Trigger (how it starts each cycle)
Pick one primary model; the code can support several behind flags.
- **Cron / scheduled one-shot** (recommended default): the scheduler invokes the
  loop once per tick; it runs ONE cycle and exits. A crash is self-healing — the
  next tick retries. No durable process to babysit. Best for production.
- **Daemon / interval**: a long-lived process sleeps `interval_s` between cycles.
  Needs graceful SIGINT/SIGTERM handling and a goal-stop to avoid running forever.
- **Webhook / event**: an external event forces an immediate cycle. Treat as an
  *optional forcing mechanism* on top of one of the above — never the only path,
  or the loop dies when the webhook source is down.

## 2. Per-cycle checks (what it inspects each pass)
In order, cheap-to-expensive:
1. **Stop sentinel** — a `STOP` file or signal; exit cleanly if present.
2. **Resource readable** — can it list the folder / reach the API? If not →
   unrecoverable → escalate AND stop.
3. **Inventory** — list current items.
4. **New-work detection** — compare against a **persistent state ledger** (e.g.
   `state.json`). "New" = absent, or previously `pending`/`failed-retryable`.
5. **Stability check** — for files, read size twice with a short gap; if it
   changed the file is still being written → skip, revisit next cycle. Prevents
   processing partial uploads.
6. **Legitimacy** — extension allowlist / schema validation; drop or quarantine
   anything that fails.

## 3. Action (what it does to each item)
- Mark the item `processing` in the ledger FIRST so a concurrent/next cycle can't
  double-process it.
- Run a **pluggable processor** (dependency-injected command or callback), not
  hardcoded logic — keeps the loop reusable.
- On success: commit (move to `done/` or delete), record checksum + timestamp.
- On transient failure: increment `attempts`, back off (exponential, capped),
  retry next cycle.
- On permanent failure (attempts exceeded) or illegitimate input: quarantine to
  `failed/`, record `failed` in ledger (feeds escalation).

**State durability rule:** persist the ledger (atomically — write temp then
`rename`) after EVERY mutation. A mid-cycle crash must be recoverable: partially
processed item is retried, never lost and never double-committed.

## 4. Stop conditions (when it halts)
| Condition | Behaviour |
|---|---|
| Explicit stop sentinel / signal | exit 0 after finishing current cycle; consume the sentinel |
| Goal met (goal-chasing) | daemon: N consecutive idle cycles with zero new work → exit 0 |
| Max runtime | hard `max_runtime_s` cap → finish cycle, exit 0 (cron re-invokes) |
| SIGINT/SIGTERM | graceful: finish current item, flush ledger, exit 0 |
| Unrecoverable infra failure | escalate, then exit non-zero |

## Escalation (when it raises the alarm)
Escalation is *additive and non-fatal* except for infra failure. Triggers:
- Per-file retries exhausted → permanent-failure alert.
- Error-rate threshold: `failed/processed` ratio over a window exceeds limit.
- Quarantine of illegitimate/unprocessable input.
- Stuck backlog: pending items above threshold for K consecutive cycles.
- Critical infra failure (unreadable source / unwritable state) → alert AND stop.

Implement escalation as: append a structured event to `alerts.log` + optionally
run an `ESCALATION_HOOK` command. Keep the loop making progress on healthy items
while flagging the sick ones.

### Circuit breaker for fix loops (contradiction detection)
When the loop's action is "modify source to satisfy tests" (a fix loop), a
special escalation case arises: the test requirements may be **logically
contradictory** — e.g., `assert f(2, 3) == 5` and `assert f(2, 3) == 6` cannot
both pass. No amount of source modification will resolve this; the loop will
thrash forever between impossible states.

**Prevention:** Before entering the fix loop, perform a **static pre-analysis**
of test assertions. Group assertions by function-call signature; if any group
has more than one distinct expected value, a contradiction exists. Break the
circuit immediately — zero wasted iterations.

**Safety net:** Re-check for contradictions dynamically each iteration in case
the test file is modified mid-loop.

See `references/circuit-breaker-pattern.md` for the full pattern, implementation
sketch, and a real-world example.

## Configuration
Expose behaviour through env vars (all optional) rather than constants: watched
dir, interval, max attempts, stability wait, extension allowlist, idle-stop
threshold, max-runtime, error-rate, backlog thresholds, custom processor command,
escalation hook, delete-vs-archive on success.

## Implementation notes
- **Stdlib only** (Python) keeps it portable across Windows/Posix with zero
  install. Use `pathlib`, `json`, `hashlib`, `signal`, `subprocess`, `argparse`.
- Atomic state write: `tmp = state.with_suffix('.tmp'); tmp.write_text(...); tmp.replace(state)`.
- Backoff: `min(2 ** attempts, 30)` seconds between retries of the same item.
- A tested reference implementation lives at `templates/loop.py` (folder-watch
  loop: cron `--once` / `--daemon` / webhook-ready). Copy and adapt.
- A design-doc skeleton lives at `references/design-template.md`.
- A circuit breaker pattern for fix loops (contradiction detection) lives at
  `references/circuit-breaker-pattern.md`.
- Read any via `skill_view(name='autonomous-loop-design', file_path='...')`.

## Verification before claiming done
Write a functional self-test that exercises: empty source, a new valid file
(lands in `done/`), idle-stop in daemon mode, stop-sentinel consumption, and
quarantine of a disallowed file. Run it, then DELETE all test artifacts so the
deliverable directory holds only the real outputs.

## Pitfalls
- Don't design only the happy path. The four failure axes (crash, partial file,
  poison input, stuck backlog) are what separate a toy loop from a reliable one.
- Don't skip the stability check on file watchers — processing a half-written
  upload produces silent corrupt output.
- Don't make escalation fatal for transient per-file errors; that halts the whole
  loop over one bad file.
- On Windows/MSYS, the persistent shell cwd can drift between calls — always
  qualify paths with an absolute target dir before destructive/cleanup work
  (see `windows-msys-shell`).
