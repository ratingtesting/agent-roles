#!/usr/bin/env python3
"""
BOUNDED-CONTEXT LONG-HORIZON LOOP — copy and modify.

Strategy:
  1. Sliding window  : keep only the most recent WINDOW raw items verbatim.
  2. Bounded compaction: when window > COMPACT_EVERY, fold the oldest items into
       (a) a CAPPED digest list (last SUMMARY_KEEP), and
       (b) a TRIMMED cumulative term table (top TERM_KEEP).
  3. Checkpointing   : serialize bounded state every CHECKPOINT_EVERY iters.

Invariant: carried context is O(1) in iterations. Assert it at the end.
"""

import json
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
CHECKPOINT_PATH = os.path.join(HERE, "context_checkpoint.json")
REPORT_PATH = os.path.join(HERE, "loop_log.jsonl")

N_ITERATIONS = 30
WINDOW = 8                 # raw items kept verbatim
COMPACT_EVERY = 4          # compact when window exceeds this
CHECKPOINT_EVERY = 10      # checkpoint cadence
SUMMARY_KEEP = 3           # max recent digests retained
TERM_KEEP = 10             # max cumulative terms retained
SEED = 20260722


from dataclasses import dataclass, field


@dataclass
class Context:
    window: list[str] = field(default_factory=list)
    digests: list[str] = field(default_factory=list)
    cumulative_terms: dict[str, int] = field(default_factory=dict)
    total_appended: int = 0
    compactions: int = 0

    def append(self, line: str) -> None:
        self.window.append(line)
        self.total_appended += 1
        if len(self.window) > COMPACT_EVERY:
            self.compact()

    def compact(self) -> None:
        keep = self.window[-WINDOW:]
        folded = self.window[:-WINDOW]
        if folded:
            digest = _summarize(folded)
            self.digests.append(digest)
            if len(self.digests) > SUMMARY_KEEP:
                self.digests = self.digests[-SUMMARY_KEEP:]
            for w, c in _term_counts(folded).items():
                self.cumulative_terms[w] = self.cumulative_terms.get(w, 0) + c
            if len(self.cumulative_terms) > TERM_KEEP:
                self.cumulative_terms = dict(
                    sorted(self.cumulative_terms.items(),
                           key=lambda kv: kv[1], reverse=True)[:TERM_KEEP]
                )
            self.compactions += 1
        self.window = keep

    def carried_size(self) -> int:
        return (sum(len(w) for w in self.window)
                + sum(len(d) for d in self.digests)
                + sum(len(k) + len(str(v)) for k, v in self.cumulative_terms.items()))

    def snapshot(self) -> dict:
        return {"digests": self.digests,
                "cumulative_terms": self.cumulative_terms,
                "window": self.window,
                "total_appended": self.total_appended,
                "compactions": self.compactions,
                "carried_size": self.carried_size()}

    def restore(self, snap: dict) -> None:
        self.digests = list(snap.get("digests", []))
        self.cumulative_terms = dict(snap.get("cumulative_terms", {}))
        self.window = list(snap.get("window", []))
        self.total_appended = snap.get("total_appended", 0)
        self.compactions = snap.get("compactions", 0)


def _term_counts(lines):
    words = {}
    for ln in lines:
        ln = ln.split(" (building on")[0]   # strip scaffold before counting
        for w in ln.lower().split():
            w = w.strip(".,:;-)")
            if len(w) > 3:
                words[w] = words.get(w, 0) + 1
    return words


def _summarize(lines):
    words = _term_counts(lines)
    top = sorted(words.items(), key=lambda kv: kv[1], reverse=True)[:3]
    return f"{len(lines)} lines; key terms: " + (
        ", ".join(f"{w}({c})" for w, c in top) or "n/a")


def make_line(i, rng, ctx):
    topic = rng.choice(["alpha", "beta", "gamma", "delta", "epsilon", "zeta"])
    value = rng.randint(0, 99)
    stem = f"iter={i:02d} topic={topic} value={value}"
    if ctx.window:
        prev = ctx.window[-1].split(" (building on")[0]   # canonical stem only
        ref = f" (building on: {prev})"
    elif ctx.digests:
        ref = " (building on compacted history)"
    else:
        ref = ""
    return f"{stem}{ref}"


def run(start=0, resume=False):
    rng = random.Random(SEED)
    ctx = Context()
    if resume and os.path.exists(CHECKPOINT_PATH):
        with open(CHECKPOINT_PATH, "r", encoding="utf-8") as fh:
            ctx.restore(json.load(fh))
        start = ctx.total_appended
        _topics = ["alpha", "beta", "gamma", "delta", "epsilon", "zeta"]
        for _ in range(start):           # re-prime RNG for deterministic stream
            rng.choice(_topics)
            rng.randint(0, 99)
    with open(REPORT_PATH, "a", encoding="utf-8") as log:
        for i in range(start, N_ITERATIONS):
            line = make_line(i, rng, ctx)
            ctx.append(line)
            log.write(json.dumps({"iter": i, "produced": line,
                                  "carried": ctx.carried_size()}) + "\n")
            if (i + 1) % CHECKPOINT_EVERY == 0:
                with open(CHECKPOINT_PATH, "w", encoding="utf-8") as fh:
                    json.dump(ctx.snapshot(), fh, indent=2)
    ctx.compact()
    with open(CHECKPOINT_PATH, "w", encoding="utf-8") as fh:
        json.dump(ctx.snapshot(), fh, indent=2)
    return ctx


if __name__ == "__main__":
    ctx = run()
    assert ctx.carried_size() < 2000, "carried context grew without bound!"
    print("carried context bounded at", ctx.carried_size(), "chars")
