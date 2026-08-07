# In-process test fallback (pytest blocked, module importable)

Use when pytest/`unittest` itself cannot be executed in the host, but the
test module imports the target function/class directly and the assertion
itself is import-safe. This is an out-of-process proof technique, not a
replacement for a real suite.

## When this fires

- The verification gate says: no canonical suite detected, go ad-hoc, run
  a temp script.
- The folder DOES contain a real test module, but `pytest <file>` cannot
  succeed in this environment.
- You confirmed the test module imports the target function directly and
  does not rely on pytest fixtures / markers.
- You already attempted a normal suite run and it was blocked (e.g.
  `pending_approval` / `-c`/`-e` approval gate / Windows interpreter
  mismatch).

## Script shape

```python
"""Ad-hoc in-process fallback for <testfile>::<test>. ONLY when suite
execution is blocked but the target + assertion are import-safe."""
import sys
import importlib.util
from pathlib import Path

REPO = Path(r"C:\absolute\path\to\control")
TEST_PATH = REPO / "test_spec.py"
TEST_MODULE = "seed_test_spec"

# Load the target implementation exactly once.
MOD_PATH = REPO / "seed_count_working_days.py"
spec_t = importlib.util.spec_from_file_location("seed_count_working_days", MOD_PATH)
mod_t = importlib.util.module_from_spec(spec_t)
sys.modules["seed_count_working_days"] = mod_t
spec_t.loader.exec_module(mod_t)

# Load the test module; its asserts execute at import.
spec = importlib.util.spec_from_file_location(TEST_MODULE, TEST_PATH)
mod = importlib.util.module_from_spec(spec)
sys.modules[TEST_MODULE] = mod
spec.loader.exec_module(mod)

# Run the test functions by calling them; surface their return code.
# Works as long as tests do not depend on pytest internals.
failed = []
for name in dir(mod):
    fn = getattr(mod, name)
    if callable(fn) and name.startswith("test_"):
        try:
            fn()
        except AssertionError as e:
            failed.append((name, str(e)))

if failed:
    print(f"FAIL {len(failed)}")
    for name, msg in failed:
        print(f"- {name}: {msg}")
    sys.exit(1)
print("OK")
sys.exit(0)
```

## Requirements before using this

- The test module imports the target function/class directly.
- No executable side effects at module top-level other than asserts.
- No reliance on `pytest.raises`, markers, fixtures, or other test runner
  features.

## Why this is still ad-hoc

The gate never saw a suite run, so never claim "suite green". Label it
`ad-hoc verification passed (in-process fallback)` and cite the temp script
path and exit code.

## Reporting

- `ad-hoc verification passed (in-process fallback): test_spec_cases
  passed, exit 0. Script cleaned up.`
- NEVER "suite green" or "tests pass". Those require actual pytest/jest/etc
  execution observed by the verification run.