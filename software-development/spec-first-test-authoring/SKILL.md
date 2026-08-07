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

## Verification Checklist

- [ ] All assertions derive from spec, not from reading implementation
- [ ] Test names match the spec
- [ ] Tests fail on the buggy behavior (discriminating)
- [ ] `out.txt` captured and summarized
- [ ] `notes.md` lists which tests failed and why
