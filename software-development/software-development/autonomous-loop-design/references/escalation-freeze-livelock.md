# Escalation livelock: the escalated item must leave the queue

Real incident from a 30-iteration documentation-improvement loop. Worth reading in full
because the loop's safety machinery worked *perfectly* and still produced the wrong
behaviour — the failure is subtle and the breaker's stop looks like a legitimate result.

## Setup

Goal-chasing loop over `docs/**/*.md`. Each cycle:
1. score every doc against a 6-check quality gate,
2. select the **worst-scoring** file,
3. ask the LLM for one atomic fix,
4. apply, verify on disk, next.

Guard stack: `MAX_ITERS=50`, `NO_PROGRESS=5`, `SIMILARITY=3`, `WALL_CLOCK=2h`,
`ABSOLUTE_MAX_ITERS=100`.

The mock LLM was deliberately seeded with one irreversible proposal: for
`docs/deprecated/legacy-api.md` it returns `action: delete_file` instead of a patch. The
loop correctly refuses to execute it (irreversible + outward-facing → human boundary),
writes `state: waiting_user` to `artifacts/escalations.md`, and leaves the file untouched.

## The bug

```
CIRCUIT-BREAKER/STOP — stopped_at_iteration=11 reason=SIMILARITY won=False
detail=повтор ('docs\deprecated\legacy-api.md', 'C3_no_placeholder', 'escalated')
iterations=11 keeps=8 discards=0 escalations=3
```

The loop stopped at iteration 11 of a requested 30. Why:

- The escalated file was never patched (correctly — a human must decide).
- So its gate score never improved.
- So it remained the **worst-scoring** file.
- So `pick_target()` selected it again. And again.
- Escalation also incremented `no_progress`, pushing toward that cap too.
- SIMILARITY fired on the third identical `(file, check, action)` signature.

Everything did exactly what it was written to do. The loop still wasted iterations
9, 10, 11 re-escalating an item a human had already been told about, and abandoned 19
iterations of perfectly good work on other files.

## The fix (two parts — both required)

```python
def pick_target(ctx, frozen: set[str]):
    worst, worst_score = None, 99
    for p in sorted(DOCS.rglob("*.md")):
        rel = str(p.relative_to(REPO))
        s = score(p.read_text(encoding="utf-8"))
        listing.append(f"{rel}: {s}/6" + (" [waiting_user]" if rel in frozen else ""))
        if rel in frozen:        # awaiting a human — out of the selection pool
            continue
        if s < worst_score:
            worst, worst_score = p, s
    ...
```

```python
if action == "delete_file":
    escalations += 1
    frozen.add(rel)              # part 1: leave the queue
    write_escalation(rel)
    action = "escalated"
    # part 2: escalation is NOT a no-progress iteration.
    # (deliberately no `no_progress += 1` here)
```

Result on the same fixture: 30 iterations, 30 keeps, `reason=ITERS_DONE`. A later run
over the already-improved tree reached the deprecated file at iteration 4, escalated it
once, froze it, and continued — 29 keeps, 1 escalation, no livelock.

## Generalisable rules

1. **Escalation is a terminal state for that item, not a retry.** Whatever your selection
   metric is (worst score, oldest timestamp, highest error count), an escalated item will
   keep winning it unless you explicitly remove it. Freeze it.
2. **Escalation counts as progress.** The iteration produced a correct, useful outcome:
   a human now has an actionable decision. Counting it as a stall double-punishes the loop
   and trips NO_PROGRESS on a healthy run.
3. **Still list frozen items in scan output**, tagged `[waiting_user]`. Silently dropping
   them makes the scan lie about the repo's true state and hides the pending decision.
4. **Put the full repeated signature in the breaker's `detail`.** `detail=повтор
   ('docs/deprecated/legacy-api.md', 'C3_no_placeholder', 'escalated')` diagnosed this in
   one read. A bare `reason=SIMILARITY` with a counter would have sent the investigation
   toward "is the goal unsatisfiable?" instead of "why is this item still selectable?"
5. **Do not respond by raising the cap.** The instinct on a premature SIMILARITY stop is
   to bump the threshold. That would have turned a 3-iteration livelock into a
   50-iteration one and buried the real defect.

## Detection test (cheap, add it to any escalating loop)

Seed the fixture with at least one item that always escalates, run the loop for N
iterations, then assert:

```python
assert escalations == 1                      # escalated once, not N times
assert reason in ("ITERS_DONE", "ALL_GREEN") # not SIMILARITY / NO_PROGRESS
assert deprecated_file.exists()              # irreversible action never executed
```

The first assertion is the discriminating one: `escalations == 1` fails loudly on the
un-frozen implementation while `escalations >= 1` would pass on both.
