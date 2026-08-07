# jscpd intra-file detection gap: Rust port vs node CLI

## Problem

The Rust port `cpd 5.x` (the default `jscpd` binary on many systems) only
detects duplicates **across different files**. When all duplication lives
within a single file, it reports `Files analyzed: 1, Clones found: 0` —
a false green that can pass the anti-erosion gate while identical code
remains.

## Verified reproduction (2026-07-22)

A single `handlers.py` with 6 near-identical handler functions (same
log→validate→transform→persist→log body, differing only in handler name
and a constant):

```
# Rust port (global jscpd)
$ jscpd --version
cpd 5.0.12
$ jscpd --min-tokens 10 --min-lines 3 --threshold 10 --format python --reporters console-full .
Files analyzed: 1 │ Clones found: 0 │ 0.00% dup │ exit 0   ← FALSE GREEN

# Node jscpd (npx pinned)
$ npx --yes jscpd@4.0.0 --min-tokens 10 --min-lines 3 --threshold 10 --format python --reporters console-full .
Clone found (python): handlers.py [55:29 - 58:35] ← handlers.py [35:32 - 38:38]
Clone found (python): handlers.py [75:33 - 78:39] ← handlers.py [35:32 - 38:38]
Clone found (python): handlers.py [95:31 - 98:37] ← handlers.py [35:32 - 38:38]
Clone found (python): handlers.py [115:36 - 118:42] ← handlers.py [35:32 - 38:38]
Clone found (python): handlers.py [135:32 - 138:38] ← handlers.py [35:32 - 38:38]
5 clones, 10.2% dup │ exit 1   ← CORRECT
```

## Root cause

The Rust port's clone detection is scoped to cross-file comparison only.
Intra-file duplicates (two functions in the same file sharing a code block)
are never evaluated. The node jscpd (v3/v4) performs intra-file detection
and correctly flags them.

## Fix

When scanning a single file or when intra-file duplication is suspected,
use the node jscpd explicitly:

```bash
npx --yes jscpd@4.0.0 --min-tokens 10 --min-lines 3 --threshold 10 --format python --reporters console-full .
```

The global `jscpd` binary (Rust port) is fine for multi-file cross-file
scanning, but **never trust a `Files analyzed: 1` result from the Rust
port** — it means the file was seen but intra-file clones were not
evaluated.

## Diagnostic checklist

1. Check which binary you have: `jscpd --version` → `cpd 5.x` = Rust port.
2. If Rust port and scanning a single file (or suspecting intra-file dup):
   re-run with `npx --yes jscpd@4.0.0`.
3. Always confirm `Files analyzed > 0` in the console-full output before
   trusting a "0.00%" result.
4. If `Files analyzed: 1` and `Clones found: 0` on the Rust port, treat
   it as "unscanned for intra-file dup" — not "clean".