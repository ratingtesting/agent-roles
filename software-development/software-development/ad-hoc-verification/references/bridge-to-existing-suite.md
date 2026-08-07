# Bridge-to-existing-suite pattern (Case 3)

Use when a real test suite exists but the verification gate fired "unverified"
because its working dir didn't contain the suite. Don't reimplement checks
with importlib — shell out to the real suite and surface its verdict.

## When this fires

- Gate's working dir is an empty subdir (`control/`, `treatment/`, a dated
  run folder) while `app.py` + `test_app.py` live in a parent or sibling.
- The gate couldn't detect a canonical command because from its cwd there
  is nothing to detect — the code isn't there.
- You already located the real files via `search_files` (don't guess).

## Script shape

```python
"""Ad-hoc verification: bridge to existing pytest suite in parent dir."""
import subprocess, sys, os

# Absolute path to the dir that actually contains the suite + code under test.
CODE_DIR = r"C:\path\to\real\code\dir"

os.chdir(CODE_DIR)
r = subprocess.run(
    [sys.executable, "-m", "pytest", "test_app.py", "-q"],
    capture_output=True, text=True,
)
print("EXIT:", r.returncode)
print(r.stdout)
print(r.stderr)
sys.exit(r.returncode)
```

## Why not importlib + asserts here

- A real `test_app.py` already encodes intended behavior, including
  contradictory-test traps (e.g. `test_add_5` vs `test_add_6` asserting
  `f(2,3)==5` AND `==6`). Reimplementing asserts in the ad-hoc script
  would either duplicate the suite or silently drop a check.
- The suite's exit code IS the verification signal. Re-surfacing it is
  honest; re-authoring it risks drifting from intent.
- The gate wants fresh execution evidence. Shelling out to the real
  suite gives exactly that, against the real assertions.

## Committing in the bridged dir

Same gotcha applies to git: the gate's cwd may not be a repo. Check
`git status` from the CODE_DIR, not the gate's cwd. If no repo exists,
`git init` in CODE_DIR before `git add` / `git commit`. (Session
20260719T170049Z/P4 hit this: `control/` had no `.git`, parent `P4/`
had the files and no repo either — init at P4, commit there.)

## Reporting

Frame as ad-hoc even though a suite ran, because the gate couldn't
detect the suite on its own:

- ✅ "Ad-hoc verification (bridged to existing pytest at <CODE_DIR>):
  N passed, 0 failed, exit 0. Script cleaned up."
- ❌ "Suite green." — the gate didn't see a suite; claiming suite-green
  overstates what the gate observed.

## Cleanup

`rm` the temp script regardless of pass/fail. The bridge script itself
is throwaway; the real suite it invoked persists in the repo.
