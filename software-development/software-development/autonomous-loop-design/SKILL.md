---
name: autonomous-loop-design
description: >-
  Design and implement autonomous loops — cron/webhook/goal-chasing processes that
  monitor a folder, service, or CI/build state, detect work, act, decide when to stop,
  and escalate. Use when a task asks for a "loop", "watcher", "watchdog", "monitor",
  "daemon", "cron job", "autonomous agent", "self-healing", or "goal-chasing" process.
  Covers the five mandatory design dimensions, the guard stack (iteration ceiling, stall
  breakers, per-item action cap, call budget, rate limit), the human/irreversible-action
  boundary, and how to prove the guards are really tested.
version: 1.2.0
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

## Goal-chasing loops (watch an external resource until it is healthy)

A goal-chasing loop differs from a folder-watcher: the "work" is not new items but a
**resource state you are trying to drive to a target** (CI builds all green, service
healthy, queue drained). Four rules that are easy to miss:

1. **The goal needs a stability window, not a single observation.** `stable_polls >= 2`.
   One green poll is not the goal — a failing job may simply not have started yet.
   Declaring victory on the first good sample is the most common false-positive.
2. **Classify each problem into auto-fixable vs needs-human before acting.** Match the
   failure text against an explicit `RETRYABLE_MARKERS` list (network/timeout/disk
   full/flaky/503). **An unknown or empty reason must classify as needs-human**, never
   as retryable — silently retrying a cause you don't understand is how a loop spins
   forever.
3. **Per-item action cap, separate from the stall breakers.** SIMILARITY / NO_PROGRESS
   breakers are **blind to a flapping resource**: a job that alternates red → green →
   red resets the stall counters on every green poll, so the loop would "heal" it up to
   the hard iteration ceiling. Cap the number of remediation actions **per item**
   (`max_reruns_per_build`-style, default 3) and escalate on exceeding it. Found the
   hard way — see `references/goal-chasing-monitor-loop.md`.
4. **Gate irreversible/outward-facing actions on a human even in unattended mode.** The
   loop may freely do reversible, contained things (re-run a job, retry a fetch). Revert,
   deploy, delete, notify-a-channel go into a `suggested_actions_requiring_human` list in
   the escalation payload — never executed. Make this machine-checkable: give the mock an
   action log and assert it stays empty.
5. **An escalated item MUST be frozen out of the work queue.** Escalation without freezing
   is a livelock: the item still ranks worst by the selection metric, so the very next
   cycle re-selects it, re-escalates, and no healthy work gets done. Keep a
   `frozen: set[item_id]`, skip frozen items during target selection (still *list* them
   marked `[waiting_user]` so the scan output stays honest), and **do not count an
   escalation as a no-progress iteration** — handing an item to a human is a correct
   outcome, not a stall. Full incident → `references/escalation-freeze-livelock.md`.

## A breaker that fires can be pointing at YOUR bug, not an unsatisfiable goal

The reflex when SIMILARITY/NO_PROGRESS trips is "the task is impossible, escalate." Often
it is instead a **defect in target selection** — the loop keeps picking the same item
because nothing removed it from the queue. Triage before you accept the stop:

1. Read the breaker's `detail` payload. Always include the **full repeated signature**
   (`(item, sub_check, action)`), not just a counter — the signature names the culprit.
2. If the same item appears in every repeat, ask "why is this item still selectable?"
   before "why is this goal unsatisfiable?"
3. Fix the selection logic (freeze / mark done / advance a cursor). **Never raise the cap
   or loosen the breaker to get past it** — that converts a 3-iteration livelock into a
   50-iteration one.

Corollary: a breaker firing *correctly* and the loop behaving *correctly* are different
claims. Both need checking.

## Testing layered guards (each cap needs an isolating test)

Once a loop has several brakes (iteration ceiling, stall breaker, per-item cap, call
budget, rate limit), they **shadow each other**: whichever fires first hides the rest.
- A test that targets ONE cap must neutralise all the others (set them to `10**6`), or
  it silently asserts the wrong mechanism.
- Symptom that you got this wrong: adding a NEW guard breaks an existing, previously
  green test of an OLD guard. That failure is correct information — fix the test's
  isolation, do not weaken the new guard.
- Assert **both** the stop reason and the stop iteration (`reason == "SIMILARITY"` AND
  `stopped_at_iteration == 3`). A reason-only assertion that accepts two alternatives
  (`in ("SIMILARITY", "NO_PROGRESS")`) is non-discriminating — disabling one breaker
  entirely still passes it.

## Prove the loop's tests actually discriminate (mutation battery)

Loop-guard tests are unusually prone to being tautological: they pass because the loop
happens to stop, not because the specific brake worked. Machine proof: copy the tree to
an arena dir, apply ONE string mutation that disables a single guard (`if X >= cap:` →
`if False:`), rerun the SAME suite, and require RED. Green on a mutant = that guard is
untested. A copy-and-adapt runner lives at `templates/mutation_battery.py`.

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
- A worked goal-chasing monitor design (guard stack, flapping hole, on-disk state,
  machine-checkable autonomy boundary) lives at
  `references/goal-chasing-monitor-loop.md`.
- A copy-and-adapt mutation-battery runner (proves each guard is really tested) lives at
  `templates/mutation_battery.py`.
- The escalation-freeze livelock (escalated item keeps winning target selection, SIMILARITY
  fires early, and why raising the cap is the wrong fix) lives at
  `references/escalation-freeze-livelock.md`.
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
- **Stall breakers cannot see a flapping resource.** Any guard that resets on progress
  is blind to alternating good/bad states. Add a per-item action cap; do not assume
  NO_PROGRESS/SIMILARITY covers it.
- **Check the iteration ceiling BEFORE doing the cycle's work**, and report the stop at
  `iteration - 1`. Checking after means the loop runs one cycle past its own cap.
- **Adding a new guard will break existing guard tests** — the new brake fires before the
  one under test. That is correct signal: neutralise the new cap inside the old test
  (set it to `10**6`), never loosen the guard to make a test pass.
- **A refactor invalidates mutation-battery anchors.** After Extract Function / renames,
  re-run the battery; an "anchor not found" INCONCLUSIVE is a re-anchoring chore, not a
  green result. Never let INCONCLUSIVE be reported as a pass.
- **Deduplication scans must be re-run with the exact same command after refactoring**,
  and the "files analyzed" count checked — a scan that analysed 0–1 files is not a clean
  gate, it scanned nothing.
- Budget the wrap-up. Verification loops (tests → mutation battery → quality scans →
  re-verify after each fix) expand fast; write the README/design doc once the code first
  goes green, not after the last scan, or the deliverable doc is what gets dropped when
  time runs out.
- On Windows/MSYS, the persistent shell cwd can drift between calls — always
  qualify paths with an absolute target dir before destructive/cleanup work
  (see `windows-msys-shell`).
