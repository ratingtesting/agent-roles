## Breaking a two-file import cycle minimally

**Signal:** `a.py` does `import b`, `b.py` does `import a`; changing one side to a lazy import is not enough if the cycle still executes on the runtime path.

**Observed failure:** After moving `import a` inside `b.helper()`, `py_compile` passed, but runtime still recursed because `a.py` still called `b.helper()` at the top level of `run()`.

**Minimal fixes, pick one:**

1. Remove mutual runtime call edge. In `a.py`, replace `return b.helper() + 1` with a constant/value that does not require `b`.
2. Use forwarding indirection. Extract the shared behavior into a third module; both `a.py` and `b.py` import the third module, neither imports the other.
3. Late binding only works when the actual call edge is one-directional. A lazy import on side B does not cure a cycle if side A still calls into B during module execution.

**Verification must cover both:**

- `python -m py_compile a.py b.py` — import-time check.
- Execution of both entry points — runtime recursion check.

**Anti-pattern:** Treating "no ImportError" as "no cycle." Python happily accepts circular imports unless the cycle triggers an incomplete partially-initialized module execution. Always runtime-exercise both call directions.
