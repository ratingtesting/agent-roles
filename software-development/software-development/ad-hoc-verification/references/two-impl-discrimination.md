# Two-impl discrimination: prove the check can fail (RED-BATTERY)

## The problem this solves

An ad-hoc verify script that only ever runs against the **fixed** code proves nothing
about itself. If the assertions are too loose, mis-scoped, or accidentally tautological,
they print all-green on code that is still broken. "14/14 green" is only evidence if the
same 14 checks are known to go RED on the pre-fix behavior.

This is the ad-hoc analogue of the red-green discipline in `test-driven-development`:
a check that never failed proves nothing.

## The shape

One script, two implementations, identical assertions, run back to back.

```python
"""argv: <fixed_impl.py> <prefix_impl.py>"""
def run(path):
    mod = load(path)                 # importlib by absolute path
    ...
    failed = results.count(False)
    print("  => %d/%d green, %d failing" % (results.count(True), len(results), failed))
    return failed

fixed_failed  = run(sys.argv[1])
prefix_failed = run(sys.argv[2])

print("VERDICT fixed-impl-green : %s (%d failing)"
      % ("PASS" if fixed_failed == 0 else "FAIL", fixed_failed))
print("VERDICT discriminating   : %s (%d failing on pre-fix)"
      % ("PASS" if prefix_failed else "FAIL (tautological!)", prefix_failed))
sys.exit(0 if (fixed_failed == 0 and prefix_failed > 0) else 1)
```

Exit 0 requires **both**: fixed is clean AND pre-fix fails. `prefix_failed == 0` is a
loud failure, not a pass — it means the assertions cannot detect the bug they were
written for.

## Getting the pre-fix implementation

Commit a baseline of the broken code first, then extract it from history:

```bash
git show HEAD~1:store.py > "$(mktemp ... )"   # or HEAD: before you commit the fix
```

If the working dir is not a repo, `git init` + commit the original content as the
baseline *before* applying the fix (see the security-gate note about never
`git stash`-ing on empty history — the edit is silently dropped).

**Windows path trap:** `git show HEAD~1:store.py > /tmp/x.py` writes somewhere MSYS
understands, but Windows Python then reads `/tmp/x.py` as `C:\tmp/x.py` and raises
`FileNotFoundError`. Use `tempfile.mkstemp()` / `tempfile.gettempdir()` for the path, or
convert with `cygpath -w` at the call boundary. See `windows-msys-shell` Trap 3.

## Never abort the run on the first crash

The pre-fix pass is *expected* to raise. Wrap every expectation so a crash is recorded
as one failure and the remaining checks still execute — otherwise the first exception
hides the other N-1 results:

```python
def check(label, probe):
    try:
        ok, detail = probe()
    except Exception as exc:
        print("    FAIL %-44s CRASH %s: %s" % (label, type(exc).__name__, exc))
        return False
    print("    %s %-44s %s" % ("OK  " if ok else "FAIL", label, detail))
    return ok
```

This also produces the most useful evidence in the report: the pre-fix column names the
exact exception (`OperationalError: near "Reilly": syntax error`) next to the fixed
column's correct result.

## Cover both directions

Group the assertions so the output shows what was proven:

- **fix path** — the thing the user asked for now works (each problem input returns the
  right row).
- **former-bug path** — the specific old failure is gone AND cannot be reached another
  way (injection payloads return `[]`, the table still exists afterwards, an arbitrary
  identifier is rejected).
- **boundary** — `None`, empty string, and any value the caller can realistically pass.

## Worked example (customer-directory search fix)

14 assertions over 4 problem names, a second search column, 4 injection payloads, a
table-intact probe, 3 rejected identifiers, and a `None` boundary:

```
### FIXED impl   ###  => 14/14 green, 0 failing
### PRE-FIX impl ###  =>  8/14 green, 6 failing
VERDICT fixed-impl-green : PASS (0 failing)
VERDICT discriminating   : PASS (6 failing on pre-fix)
```

The 6 pre-fix failures were the proof: a crash on the apostrophe name, a tautology
payload returning every row, a multi-statement crash, and an identifier splice that
returned the whole table. Without the second column, the first column alone would have
been indistinguishable from a script that asserts nothing.
