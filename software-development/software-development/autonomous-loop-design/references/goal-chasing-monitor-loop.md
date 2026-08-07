# Goal-chasing monitor loop — worked design (CI-watchdog case)

Concrete, verified design for "watch an external resource, remediate what you can,
escalate what you can't, stop when healthy." Written from a CI-build watchdog, but the
shape applies to any health-driven loop (service healthy, queue drained, index rebuilt).

## Layering that keeps the loop testable

```
run_demo.py        CLI entry point (no interactive prompts — unattended by construction)
loop core          observation → ONE action → goal check → sleep
breaker.py         pure guard logic, no IO (caps, counters, per-iteration budget)
throttle.py        pure rate-limit + debounce
<resource>_mock.py adapter at the IO boundary, with call journals
```

The core must NOT import the mock. Type it against a `Protocol` with just the two or
three methods it needs (`list_builds()`, `rerun(id)`), so swapping the mock for the real
API needs zero core edits. This is also what makes the whole loop unit-testable without
network.

**Inject `clock` and `sleep`.** Every guard that measures time (wall-clock cap, rate
window, debounce) takes a `clock` callable. Tests pass a `FakeClock` whose `advance()` is
used as `sleep`, so a run with a 30 s poll interval completes in milliseconds and the
real timing code is still the code under test. Do not fake this by setting the interval
to 0 — that skips the sleep path entirely.

## The five design answers (fill these before coding)

| Dimension | CI-watchdog answer |
|---|---|
| Trigger | goal-chasing heartbeat: start once, poll every `poll_interval_s` |
| Per-cycle check | list builds on the watched branch for the latest commit |
| Action | exactly ONE per cycle: re-run a retryable failure, OR escalate a non-retryable one |
| Stop | machine-checkable: all builds `passed` for `stable_polls` consecutive polls |
| Escalate | non-retryable failure · any breaker fired · irreversible action needed |

## Guard stack that was actually needed

| Guard | Default | Catches |
|---|---|---|
| MAX_ITERS | 50 | ordinary runaway |
| ABSOLUTE_MAX_ITERS | 100 | a *misconfigured* MAX_ITERS (checked first, always wins) |
| NO_PROGRESS | 5 | work not advancing |
| SIMILARITY | 3 | identical failure signature repeating (fires before NO_PROGRESS — cheaper, more precise) |
| WALL_CLOCK | 2 h | unattended time budget |
| external calls / iteration | 3 | one confused iteration hammering the API |
| rate limit + debounce | 10 / 60 s, 5 s | poll storms; identical snapshot re-triggering an action |
| **per-item action cap** | 3 | **flapping resource — see below** |

### The flapping hole (real bug, found by logic review, not by tests)

Every stall breaker resets on progress. A green poll IS progress. So a job that alternates
`red → (rerun) → green → red → …` resets NO_PROGRESS and SIMILARITY on every green sample,
and the loop keeps "healing" it until the hard iteration ceiling — burning budget while
looking busy. Neither breaker can see it.

Fix: count remediation actions **per item id** and escalate when a single item exceeds the
cap, with `classification: "rerun_limit_exceeded"` distinct from `needs_human`.

Guard-check ordering inside a cycle that works out cleanly:
```
rate limit → external-call budget → fetch state → all-green? (stability window)
→ nothing failed? (wait) → debounce → non-retryable? (escalate)
→ per-item cap exceeded? (escalate) → remediate (one item)
```

## Progress-check ordering (subtle, cost 20 min)

Check the iteration ceiling **before** doing the cycle's work, and report the stop at
`iteration - 1` — otherwise the loop performs one cycle beyond its own cap and the
"absolute ceiling" test is off by one. Same for wall-clock.

## On-disk state (what makes it recoverable and observable)

- `.loop_state` — iteration counter as a file, rewritten **before** each cycle's work. A
  counter that lives only in process memory or model context is the mechanism by which
  runaway loops lose count.
- `.loop_stopped` — written on every exit path with `{iteration, reason, goal_reached}`.
  This is the machine-readable proof the loop terminated; a verifier asserts it exists.
- `loop-progress.md` — ONE overwritten machine-readable STATUS block at the top
  (`state: running|waiting_user`, `iter`, `goal`, `last_action`, counter/budget values),
  followed by appended per-iteration history. A dashboard polls the block, not the log.
- `incident-<id>.md` — escalation report in plain language: what happened, why it matters,
  what the loop did, and explicitly **what it did not do because a human must decide**.

## Autonomy boundary, made machine-checkable

Give the mock separate journals for reversible (`rerun_calls`) and irreversible
(`reverts`, `notifications`) actions. Then:
- tests assert `reverts == [] and notifications == []` on every scenario;
- the demo entry point exits non-zero if either journal is non-empty at the end.

That converts "the loop must not do irreversible things" from a promise into a gate. A
mutation that inserts a `revert_commit()` call into the escalation path must turn tests RED.

## Scenario set worth mocking

`all-green` (goal immediately) · `flaky` (heals after one remediation → goal reached
autonomously) · `non-retryable` (compile/test error → escalate, zero remediation attempts)
· `permanently-broken` (retryable-looking but never heals → SIMILARITY fires) ·
`flapping` (alternates green/red → per-item cap fires).

Drive them from a `script(call_number, state) -> state` callback on the mock, so a scenario
is a few lines rather than a subclass.
