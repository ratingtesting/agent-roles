---
name: long-horizon-context
description: >
  Design a long-running loop or agent that carries a GROWING context across many
  iterations without letting the carried context blow up. Use when a task says
  "long-horizon loop", "growing context", "append a line each iteration",
  "manage context growth", "compaction / trimming", or anytime you build a loop
  that accumulates state over many steps. Covers the sliding-window +
  bounded-compaction + checkpoint strategy, the #1 mistake (an accumulating
  summary string), and deterministic resume.
---

# long-horizon-context

Build a loop/agent that processes a **growing** context over many iterations while
keeping the carried context **bounded**. Use this whenever a task mentions a
"long-horizon loop", "growing context", "append a line each iteration",
"manage context growth (compaction or trimming or sub-agents)", or any
multi-step process that accumulates memory.

## The invariant (non-negotiable)

The carried context — what you keep in memory / pass forward each iteration —
MUST stay **bounded: O(1) in the number of iterations**. A loop that appends
forever, or keeps an ever-growing "summary", is *wrong* even if it "works" for
30 steps. Enforce it with an assertion on carried size.

## Three-layer strategy (use all three)

1. **Sliding window** — keep only the most recent `WINDOW` (e.g. 8) raw items
   verbatim. Older items are folded out, not retained.
2. **Bounded compaction** — when the window exceeds a soft budget
   (`COMPACT_EVERY`), fold the oldest items into summary structures that are
   *themselves capped*:
   - a **capped digest list** (keep only the last `SUMMARY_KEEP` digests, drop rest), and
   - a **trimmed cumulative term/frequency table** (keep only the top `TERM_KEEP` keys).
   The folded raw items are then dropped.
3. **Checkpointing** — periodically serialize the bounded state to disk so a
   crash/resume doesn't require re-deriving everything.

> **CRITICAL — the #1 mistake:** the summary must be a **bounded data structure**
> (capped lists/dicts), NOT a string that prepends the previous summary. A
> recursive `summary = f"prev summary: {summary}\n{digest}"` grows *linearly* with
> iterations and defeats the entire point. If you catch yourself building a
> "rolling summary" string, stop and use a capped digest list instead.

## Pitfalls (encode into every implementation)

- **Unbounded summary nesting** — see above. Cap it, or it grows forever.
- **Recursive reference nesting** — if each item references the previous item,
  read only the previous item's *canonical stem* (strip any prior
  ` (building on ...)` suffix) before embedding it, or you get infinite `))))`
  growth.
- **Term-counter noise** — when building a cumulative term/frequency table from
  items that carry reference scaffolding, strip the scaffold before tokenizing,
  or you'll count the scaffold token and double-count via suffixes.
- **Resume correctness** — a resume must continue from `total_appended` (not
  replay from 0) and, if the loop uses a seeded RNG, **re-prime the RNG** by
  consuming the same number of draws so the stream reproduces deterministically
  without double-counting already-folded work.

## Verification (prove the bound holds)

- Assert `carried_size() < BUDGET` at the end — the run must FAIL loudly if the
  context grew without bound.
- Log per-iteration `carried_size` (plus window/digest/term counts) so you can
  SEE it flatten. It should plateau after warm-up and stay flat, not creep up.
- Test `resume` separately: after a full run, resume and confirm `total_appended`
  does not increase and carried size is unchanged.

### Ship a `--no-compaction` baseline arm (the only real proof)

"Compaction works" cannot be supported by the compacted run alone — a bounded number
might just mean the workload was small. Put compaction behind a flag and run **both arms
on the same fixture**, then compare peaks:

```python
ap.add_argument("--no-compaction", action="store_true")   # baseline arm
ctx = WorkingContext(compaction=not args.no_compaction)
# metrics → context-metrics.csv  vs  context-metrics-baseline.csv
```

Measured example (30 iterations, same fixture, 8000-token window):

| Arm | Peak | % of window | Outcome |
|---|---|---|---|
| compaction ON | 1387 tok | 17% | completed 30 iterations |
| `--no-compaction` | 8393 tok | **105%** | window overflowed |

This makes the acceptance criterion **discriminating**: assert both that the compacted
peak is under budget AND that the baseline peak exceeds the window. An AC that checks
only the compacted arm still passes if you delete the compaction and shrink the fixture.

Assert the **shape** too, not just the peak — count per-iteration decreases
(`sum(1 for a, b in zip(t, t[1:]) if b < a) >= 3`). A sawtooth proves folds actually
fired; a flat line under budget can mean nothing ever needed folding.

### Make each lever separately visible

When several levers run together (tool-output trimming, structured summary + history
reset, sub-agent delegation), log which fired and how much it reclaimed (`compactions`,
`dropped_tokens`). Otherwise one working lever masks two broken ones. Trimming verbose
tool output is usually the largest single win — it is the biggest token consumer and can
be applied *before* the text ever enters the carried context (head N + tail M lines with
an explicit `... [trimmed K lines] ...` marker so the elision is visible, not silent).

### Sub-agent delegation is a compaction lever, not just orchestration

Route any oversized item (file above a `DELEGATE_MIN_CHARS` threshold) through a
sub-reader that returns only a verdict — `size, score, failing checks` — instead of the
full text. The parent never sees the subtask's working memory. Even when the "sub-agent"
is just a local function, keeping that contract is what bounds the parent's growth.

## Support files
- `templates/bounded_context.py` — copy-and-modify skeleton of the bounded
  `Context` class + a 30-iteration loop driver.
- `references/pitfalls.md` — concrete before/after of each failure mode above.

## When this is NOT the right skill
- One-off scripts that don't accumulate state: no context-growth problem exists.
- Orchestration/agent-swarm plumbing (phases, backpressure, delegation): see
  `keelwright` / `dispatching-parallel-agents`. This skill is about the
  single-loop *context-bounding* pattern, which composes with those.
