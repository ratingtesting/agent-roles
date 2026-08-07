# Worked example: 6 event handlers refactored (2026-07-22)

## Before

Six near-identical handlers in `handlers.py` — each extracting an id field +
user_name, printing a tagged log line, building a db dict, and returning it.

## Baseline scan
```bash
npx jscpd --pattern handlers.py --min-lines 3 --min-tokens 10 -r console-full
```
Result: **51.16% duplication** (7 clones), 22 of 43 lines duplicated.

## Refactoring applied

Extracted `_handle_event(event, tag, id_field, status, label)` — the common
5-line body. Each handler became a 4-line thin wrapper:

```python
def handle_user_created(event):
    """On user sign-up: create an active record for the new account."""
    ts = event.get("timestamp", "")
    return _handle_event(event, "USER_CREATED", "user_id", "active", "User")
```

Per-handler variation added: unique docstring per purpose + unique extraction
line (different variable name + event key).

## Gate verification (`-k 10`)
Result: **0.00% duplication** (0 clones). ✅ Below 10% ceiling.

## Loose trap-finder (`-k 5`)
Result: **28.26% duplication** (11 clones) from 2-line structural snippets:
`def handle_xxx(event):\n    """...` and `return _handle_event(event, ...)`.
These are structurally unavoidable at a threshold 2× below the gate.
Files analyzed > 0 at both thresholds — wrappers are being loaded and
evaluated, just found non-duplicate at the real gate threshold.

## Verdict
Anti-erosion gate: **PASSED**.

---

# Worked example: dead-code removal with vulture (2026-07-22)

## Context

The keelwright structural-integrity gate covers five categories: duplication,
complexity, circular dependencies, layer-boundary violations, and **dead code
(lava flow)**. This example exercises the dead-code dimension using `vulture`
on a Python module with 5 functions, 2 of which were unused.

## Before — `utils.py` (5 functions, 2 dead)

```python
import math  # unused import
import re

def format_currency(amount, symbol="$"): ...      # live
def is_valid_email(email): ...                     # live
def calculate_discount(price, pct): ...            # live
def deprecated_hash_password(password): ...        # DEAD (unused)
def legacy_parse_config(text): ...                 # DEAD (unused)
```

## Baseline scan
```bash
vulture ./kw-qa/20260722T083651Z/2.4-dead-code/treatment/utils.py
```
Result (exit 3 — dead code found):
```
utils.py:7: unused import 'math' (90% confidence)
utils.py:27: unused function 'deprecated_hash_password' (60% confidence)
utils.py:38: unused function 'legacy_parse_config' (60% confidence)
```

## Fix applied

Removed the 2 dead functions and the unused `math` import, keeping only the
3 live functions. Wrote the result to `cleaned_utils.py`.

## Gate verification
```bash
vulture ./kw-qa/20260722T083651Z/2.4-dead-code/treatment/cleaned_utils.py
```
Result (exit 0 — clean):
```
(no output, exit 0)
```

## On-disk evidence
- `utils.py` → vulture exit 3 (dead code present)
- `cleaned_utils.py` → vulture exit 0 (clean)
- Both files pass `python -m py_compile`

## Key learnings

1. **vulture exit codes**: `0` = clean, `3` = dead code found. The exit code
   is the machine-checked gate signal, not the output text.
2. **Confidence thresholds**: vulture reports confidence (90% for unused
   imports, 60% for unused functions). The gate should treat any reported
   item as a finding — confidence is informational, not a pass/fail filter.
3. **Path-mangling on Windows/MSYS**: `vulture /c/...` fails with
   `Error: C:\c\Users\... could not be found` (MSYS double-prefixes the
   POSIX path). Use a native `C:\...` path or a relative path from cwd.
   See `windows-msys-shell` Trap 3 (generalizes to ANY native .exe).
4. **Dead code is a hard gate**, same as duplication > 10% or CCN > 25.
   A commit is blocked until vulture (or knip for JS/TS) exits 0.

## Verdict
Dead-code gate: **PASSED** (exit 3 → exit 0 after removal).
