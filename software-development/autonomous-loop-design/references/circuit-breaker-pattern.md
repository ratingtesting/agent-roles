# Circuit Breaker for Fix Loops

## Problem

A fix loop repeatedly runs tests, detects failures, attempts fixes, and re-runs.
When the **test requirements are logically contradictory** (e.g., `f(2,3)` must
return both 5 and 6), no implementation can ever satisfy all tests. The loop
thrashes forever between impossible states.

## Solution

A circuit breaker that performs **static pre-analysis** of test assertions before
entering the fix loop. If it detects that the same function call maps to multiple
expected outputs, it breaks the circuit immediately — zero wasted iterations.

## When to Use

- Fix loops that modify source code based on test failures
- TDD cycles where tests are generated or mutated by an agent
- Any autonomous loop that could enter an unsatisfiable state
- Loops where the "fix" action has side effects (file writes, API calls) that
  should not be repeated infinitely

## Pattern

```
1. PARSE: Read the test file(s) and extract all assertions of the form
   `assert f(args) == expected`.

2. GROUP: Group assertions by the function call signature (args tuple).

3. DETECT: If any group has more than one distinct expected value,
   a contradiction exists — the same input is expected to produce
   different outputs.

4. BREAK: If contradiction detected → log it, write a report, exit
   without entering the fix loop.

5. PROCEED: If no contradiction → enter the normal fix loop with
   iteration cap and dynamic contradiction re-check as a safety net.
```

## Implementation Sketch (Python)

```python
import re
from pathlib import Path

def parse_test_assertions(test_path):
    """Extract assertions and detect contradictions."""
    content = Path(test_path).read_text()
    pattern = r"assert\s+f\((\d+),\s*(\d+)\)\s*==\s*(\d+)"
    assertions = {}
    for m in re.finditer(pattern, content):
        a, b, expected = int(m.group(1)), int(m.group(2)), int(m.group(3))
        key = (a, b)
        assertions.setdefault(key, set()).add(expected)

    contradictions = {
        key: vals for key, vals in assertions.items() if len(vals) > 1
    }
    return assertions, contradictions

def circuit_breaker(test_path, app_path, max_iterations=10):
    # Phase 1: Static contradiction check
    _, contradictions = parse_test_assertions(test_path)
    if contradictions:
        print(f"CONTRADICTION: {contradictions}")
        print("Breaking circuit — no fix can satisfy all tests.")
        return "contradiction_detected"

    # Phase 2: Normal fix loop with dynamic re-check
    for i in range(max_iterations):
        # ... run tests, attempt fix ...
        _, contradictions = parse_test_assertions(test_path)
        if contradictions:
            print(f"CONTRADICTION detected during loop: {contradictions}")
            return "contradiction_detected_dynamic"
    return "max_iterations_reached"
```

## Key Design Decisions

1. **Static pre-analysis before loop** — catches contradictions with zero
   wasted iterations. This is the primary defense.

2. **Dynamic re-check during loop** — a safety net in case the test file
   is modified mid-loop (e.g., by an agent that also edits tests).

3. **Iteration cap** — even without detected contradictions, a max iteration
   limit prevents infinite loops from other failure modes.

4. **Report generation** — when the circuit breaks, write a report.md
   explaining what was contradictory and what the agent should do next
   (fix the tests, not the source).

## Real-World Example

In a session where `app.py` defines `f(a, b) = a + b` and `test_app.py`
contains both `assert f(2, 3) == 5` and `assert f(2, 3) == 6`:

- Static analysis finds `{(2, 3): {5, 6}}` — contradiction detected
- Circuit breaks at iteration 0
- `app.py` is never modified
- Report explains the tests must be fixed, not the source

## Related Skills

- `autonomous-loop-design` — the parent pattern this extends
- `systematic-debugging` — Phase 1 (root cause) aligns with contradiction detection
- `test-driven-development` — TDD assumes tests are satisfiable; this guards against contradictory test requirements
