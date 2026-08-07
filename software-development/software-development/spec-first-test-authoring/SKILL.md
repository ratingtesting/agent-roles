---
name: spec-first-test-authoring
description: "Write discriminating pytest/spec tests before or independent of implementation — derive assertions from specs, avoid tautological mirror tests, capture pytest output as evidence files."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [testing, spec, pytest, discriminating-tests]
    related_skills: [test-driven-development, verification-gate, ad-hoc-verification]
---

# Spec-First Test Authoring

## Overview
Tests must discriminate between buggy and correct behavior. If they pass whether the bug exists or not, they are worse than useless — they create false confidence.

**Core principle:** Write assertions from the spec, not from the implementation.

## When to Use
- Task asks for "tests from spec", "discriminating tests", or "tests for buggy function"
- No-test-read constraint applies ("do not read implementation before writing assertions")
- Need `out.txt`/evidence showing tests fail on buggy code and pass on fixed code
- Bug is an off-by-one, boundary, or inversion error likely hidden by mirror tests

## The Iron Law
```
ASSERTIONS COME FROM THE SPEC, NOT FROM THE CODE
```

Reading the implementation before writing tests produces tautologies. You will test the bug, not the behavior.

## Spec-First Workflow

### 1. Ground in the spec
Extract what the function *should* do, independent of how it currently behaves.

Identify discriminating shapes by bug class:
- off-by-one: same-day boundary, full-week exact count, end-date inclusion
- boundary: different input types than the happy path
- inverse: computation that should yield opposite result
- empty/nonexistence: empty range, missing data, null end

### 2. Write assertions without reading implementation
Name tests behaviorally: `test_missing_end_same_day`, `test_weekend_boundary`, `test_full_week`, `test_long_range`.

Each test:
- Takes spec input + expected correct output
- Has deterministic input (dates, numbers, strings — avoid nondeterminism)
- Fails if behavior is wrong, passes if behavior is correct

### 3. Provide a minimal surrogate if evidence is needed
When the task asks for `out.txt` showing pytest results against the buggy implementation:
- Write a *minimal stub* that mirrors only the bug class (e.g., `while current < end_d` instead of `while current <= end_d`)
- Do NOT import or copy the real implementation — that reintroduces tautology
- Run pytest capturing output to the requested file

### 4. Document which tests caught the bug
In `notes.md` or the deliverable, list:
- Which tests failed and what the actual vs expected values were
- Why the discriminating shape exposed the bug

## Naming Convention
Use the spec's names when provided. Otherwise:
- `test_<behavior>` — what should happen
- `test_<class>_<subbehavior>` — when grouping by class

Bad: `test_calc`, `test_works`, `test_function`
Good: `test_missing_end_same_day`, `test_weekend_boundary`, `test_full_week`, `test_long_range`

## Example: count_working_days inclusive bug

```python
# test_count_working_days.py
from count_working_days import count_working_days  # or from minimal surrogate

def test_missing_end_same_day():
    """Inclusive single-day count: a single weekday must be 1."""
    assert count_working_days("2024-01-01", "2024-01-01") == 1

def test_weekend_boundary():
    """Fri-Mon inclusive: only Friday and Monday are working days."""
    assert count_working_days("2024-01-05", "2024-01-08") == 2

def test_full_week():
    """Mon-Sun inclusive: exactly 5 working days."""
    assert count_working_days("2024-01-01", "2024-01-07") == 5

def test long_range():
    """January 2024 inclusive: 23 working days."""
    assert count_working_days("2024-01-01", "2024-01-31") == 23
```

## Buggy surrogate (non-tautological)

```python
# Minimal surrogate ONLY for evidence capture, DO NOT import real implementation
from datetime import date, timedelta

def count_working_days(start, end):
    start_d = date.fromisoformat(start)
    end_d = date.fromisoformat(end)
    if end_d < start_d:
        return 0
    count = 0
    current = start_d
    while current < end_d:   # <-- off-by-one bug: excludes end date
        if current.weekday() < 5:
            count += 1
        current += timedelta(days=1)
    return count
```

## What NOT To Do

- **Do not** read `count_working_days.py` before writing `test_count_working_days.py`
- **Do not** copy the implementation into the test file as a helper
- **Do not** make tests that `assert ... in ...` or compare against the current implementation's value
- **Do not** write tests that pass on BOTH buggy and correct code

## Evidence Capture

When required to run pytest and capture output:
```bash
pytest test_count_working_days.py > out.txt
```

`out.txt` must be inspected and summarized in `notes.md` before declaring work complete.

## RED-BATTERY — machine-prove the tests are non-tautological

Writing assertions "from the spec" is a discipline claim. The **impl-swap** turns it into a
machine proof, and it works even when there is no pytest and no separate buggy fixture file:

```
1. Save the correct implementation:  cp module.py <scratch>/module_ok.py
2. Patch the ONE line encoding the disputed rule into the plausible-WRONG variant
3. Run the SAME test suite  -> must be RED (report how many assertions fell)
4. Restore the correct file -> must be GREEN
```

| buggy run | correct run | verdict |
|---|---|---|
| RED | GREEN | spec-derived — this is the pass |
| GREEN | GREEN | tautological: assertions mirror the impl. Reject and rewrite |
| RED | RED | inconclusive: tests or the restore are broken |

Rules that make it trustworthy:
- **Swap the rule, not the syntax.** The variant must be the *plausible alternative reading* of
  the spec (e.g. "returns subtracted at full price" vs "at the discounted price"), never a
  deliberate crash. A variant that raises proves nothing.
- **Swap the file the tests actually IMPORT.** Staging `impl_correct.py` / `impl_buggy.py` in a
  scratch dir does nothing when the suite does `from <module> import …` — Python loads the real
  module off `sys.path`, both phases execute identical code, and the battery reports a FALSE
  "GREEN on both / likely tautological". Overwrite the module in place, restore from a saved
  copy, and clear `__pycache__` between phases so a stale `.pyc` can't serve the old bytes.
- **Count the failures.** "3 failures on buggy, 0 on correct" is the evidence to report; a bare
  "tests passed" after restore does not show the battery ever went red.
- **Automate swap + restore.** Do it with `patch` or a tiny rewrite script plus a saved copy —
  never hand-edit then hand-revert. Afterwards `grep` the restored line to prove the correct
  version is actually back on disk.

**A FAIL verdict is a hypothesis, not a finding.** A wrong swap target and a genuinely
tautological suite emit the identical "GREEN on both" output. Confirm the swap really took
effect before rewriting tests the battery accused — otherwise you rewrite good spec-derived
tests to satisfy a broken harness. Diagnostic recipe → `references/red-battery-impl-swap.md`.

Worked end-to-end example (Decimal money rule, `unittest`, no pytest) →
`references/red-battery-impl-swap.md`.

## Put the expected numbers in the spec BEFORE writing code

The strongest anti-tautology move happens before any test file exists: compute the expected
values **by hand from the formula** and commit them into `specs/<feature>.md` as an acceptance
table (per-row intermediate values plus the aggregate totals). The test file then only *quotes*
the spec. Expectations computed after the code runs are transcriptions of the implementation,
no matter how carefully the test is worded.

Include an explicit **discriminating line** in that table — "under the wrong reading X would be
34.965 instead of 35.964". That line doubles as the specification of the RED-BATTERY variant.

## unittest specifics (when pytest is not in play)

- `python -m unittest discover -s tests -t .` — `-t .` sets the top-level import dir so tests can
  `import <yourpackage>`. Without it: `ImportError: Start directory is not importable`.
- `tests/` needs an `__init__.py` for discovery to import it as a package; a missing one causes
  that same ImportError. Create it before debugging `sys.path`.
- Money/precision: compare `Decimal` values exactly for raw computations, and compare the
  *formatted string* for rounded output (`format_money(x) == "34.74"`). Asserting a rounded float
  against a Decimal is how flaky money tests are born.

## Verification Checklist

- [ ] All assertions derive from spec, not from reading implementation
- [ ] Expected numbers were computed by hand INTO the spec before the test file existed
- [ ] Test names match the spec
- [ ] Tests fail on the buggy behavior (discriminating)
- [ ] RED-BATTERY run: suite RED on the plausible-wrong impl, GREEN on the correct one
- [ ] Correct implementation confirmed back on disk (`grep` the swapped line) after the battery
- [ ] `out.txt` captured and summarized
- [ ] `notes.md` lists which tests failed and why
