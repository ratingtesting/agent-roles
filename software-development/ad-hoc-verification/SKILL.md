---


name: ad-hoc-verification
description: Write throwaway stdlib-only verification scripts when no canonical test/lint/build command exists for the changed code. Triggered by the Hermes verification gate's "unverified / stale" prompt for scratch modules, single-file deliverables, or repos with no test suite. Covers script location, target-import patterns, assertion discipline, and the recurring Python pitfalls that bite these scripts specifically.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [testing, verification, ad-hoc, quality, python, importlib]
    related_skills: [verification-before-completion, test-driven-development, systematic-debugging]
---

# Ad-hoc Verification

## When to use

The Hermes verification gate fires after code edits when it can't detect a
canonical test/lint/build command. It asks for a focused temp script under
`%TEMP%\hermes-verify-<name>.py` (Windows) or `/tmp/hermes-verify-<name>.py`
(Posix) that exercises the changed behavior, exits nonzero on failure, and is
cleaned up after.

Use this skill whenever you need to produce that script. It is NOT a
substitute for a real test suite — it is the minimum honest evidence when no
suite exists. If the project has `pytest`/`jest`/etc. AND the gate detected
it, run that instead and skip ad-hoc entirely.

## Three cases — pick the right one

The gate fires "unverified" for three distinct reasons. The script shape
differs per case:

1. **No suite exists** (scratch module, single-file deliverable, no tests).
   Write an importlib + asserts script against the target. This is the
   common case and the default template below.

2. **Suite exists and the gate detected it** — you shouldn't be here. Run
   the suite directly; ad-hoc is wrong tool.

3. **Suite exists but the gate couldn't detect it** — the working dir the
   gate saw didn't contain the suite (code lives in a parent or sibling
   dir, or the gate's cwd was an empty subfolder like `control/` while
   `app.py` + `test_app.py` sat one level up). Don't reimplement the suite
   with importlib — that's busywork that duplicates a real test file.
   Instead the ad-hoc script `os.chdir`s to the real code dir and shells
   out to the real suite via `subprocess`, surfacing its exit code and
   output. See `references/bridge-to-existing-suite.md`.

4. **Target is a runnable script, not an importable module** (e.g. `python
   handlers/handler_X.py` must print specific output, or a CLI must exit 0
   with given stdout). Don't import via importlib — shell out to the script
   with `subprocess.run([sys.executable, path], capture_output=True, text=True)`
   and assert `returncode == 0` + `stdout.splitlines() == expected`. This is
   the right shape when the deliverable's contract is "runs as a CLI" rather
   than "is importable". Loop over all N variants in one script.

   ```python
   import subprocess, sys
   exp = ["line1", "line2", "line3", "line4", "line5"]
   for x in "abcdefghijkl":
       o = subprocess.run([sys.executable, f"handlers/handler_{x}.py"],
                          capture_output=True, text=True)
       assert o.returncode == 0, (x, o.stderr)
       assert o.stdout.splitlines() == exp, (x, o.stdout.splitlines())
   print("ALL OK")
   ```

   On Windows the script path must be native (`C:\\...`) or `cygpath -w`'d —\
   see `windows-msys-shell` Trap 3. Also relevant: `references/jscpd-dup-threshold.md`
   for verifying a dedupe refactor didn't just hide clones below the threshold.

5. **Target cannot be imported (missing deps, dangerous side effects at import time, circular imports).**
   Use AST-based static analysis: parse the source with `ast.parse()`, walk the tree with
   `ast.walk()`, and assert on structural properties — without ever importing the module.
   This also covers structural verification (e.g. "no hardcoded secrets", "all functions
   have type annotations", "eval() is absent") that importlib can't easily check.
   See `references/ast-static-analysis.md` for full patterns and a combined AST + exec-stub
   workflow for config modules.

6. **Target mutates git history / has irreversible side effects** (deploy
   scripts that `git commit`/`git revert`, repo-rewriting helpers, anything
   with destructive effects). Never run it against the user's real repo.
   Copy the target + its inputs into an isolated temp repo
   (`tempfile.mkdtemp(prefix="hermes-verify-")`, `git init`, seed baseline),
   shell out to it with `subprocess`, then assert on the RESULTING git history
   (`git log --oneline` shape, original commit still `git rev-parse`-able to
   prove no `reset --hard`/force-push, affected files restored to baseline).
   Full pattern + worked example in `references/verify-git-history-mutation.md`.

## Five cases — pick the right one

1. **Self-contained.** Import the target by absolute path. No `sys.path`
   hacks, no pytest install, no framework. stdlib asserts only.

   **Exception — target depends on local sibling packages.** When the file
   under test imports packages that live in the same directory (e.g.
   `process.py` imports `csvstream_pro` from `./csvstream_pro/`), the
   `spec_from_file_location` template below cannot resolve those sibling
   imports because the directory isn't on `sys.path`. Use
   `sys.path.insert(0, pkg_dir)` + `importlib.import_module(mod_name)`
   instead:

   ```python
   PKG_DIR = r"<absolute path to parent>"
   sys.path.insert(0, PKG_DIR)
   mod = importlib.import_module("process")   # sibling packages resolvable
   ```

   This is safe for ad-hoc scripts (they get cleaned up) and is the simplest
   fix when `pip install -e` is unavailable or times out. The same pattern
   must also be used inside the target file itself if it imports siblings,
   so the verification script's path setup mirrors the target's own layout.
2. **Register in `sys.modules` before `exec_module`.** Any target using
   `@dataclass`, `@attrs.define`, or other decorators that inspect
   `sys.modules` at import time will crash without this. See
   `references/py311-importlib-dataclass.md`.
3. **Temp script path and name.** Always write under the OS temp dir with
   a `hermes-verify-` filename prefix, e.g. on Windows
   `os.path.join(os.environ['TEMP'], 'hermes-verify-<name>.py')` and on
   Posix `/tmp/hermes-verify-<name>.py`. Never litter the repo with these
   scripts.
4. **Exit nonzero on any failure.** The gate reads exit code + output.
5. **One script, clean up after.** Delete it when you're done. Don't litter
   `%TEMP%` or `/tmp`.
6. **Wrong-test vs wrong-code.** When a check fails, confirm the assertion
   matches INTENDED behavior before editing either side. A failing
   assertion is as likely to be a test bug as a target bug.

   **Seeded-bait tests.** Some repos contain a “training” test that asserts
   obviously false behavior to trick agents into changing correct code.
   Do not fix production code to match a fake-bait expectation. Verify the
   real behavior with ad-hoc evidence first; then update or remove the bad
   test. See `references/wrong-test-traps.md`.
7. **Label honestly.** If only ad-hoc verification ran, say so
   explicitly: `ad-hoc verification passed`, `ad-hoc verification failed`.
   Do NOT say `suite green`, `tests pass`, or `verified` unless a real
   suite actually ran and passed.

8. **Node/JS targets.** When the changed code needs `node`/`npx` tooling and
   inline `node -e` is unavailable (approval gate or host policy), write a
   tiny temp script file under `%TEMP%` or `/tmp` with a `hermes-verify-` prefix,
   then run it via `node "<abs-path>"`. On Windows use native `C:\\...` paths
   (see `windows-msys-shell`) to avoid MSYS path mangling. The temp script can
   shell out to `npx madge --circular .`, run the target module file directly,
   and print `PASS`/`FAIL` lines before `process.exit(0/1)`

## Script template

```python
"""Ad-hoc verification of <module>.<behavior>."""
import os
import sys
import importlib.util

MOD_PATH = r"<absolute path to target .py>"
MOD_NAME = "<module>_under_test"

spec = importlib.util.spec_from_file_location(MOD_NAME, MOD_PATH)
mod = importlib.util.module_from_spec(spec)
sys.modules[MOD_NAME] = mod              # BEFORE exec_module — see references/
spec.loader.exec_module(mod)

# Exercise module behavior here with plain asserts.
print("VERIFY_OK: <behavior checked>")
sys.exit(0)
```

Run:

```bash
python "<temp script path>"
```

Clean up:

```bash
rm "<temp script path>"
```

## Workflow

1. Identify the behavior to verify (the thing you just changed).
2. Write the temp script using the template above.
3. Run it. Read full output + exit code.
4. On failure: classify wrong-test vs wrong-code. Fix the correct side.
5. Re-run. The gate's stale-cache flag clears on a fresh execution at the
   same path — no need to rename the script.
6. On success: `rm` the script. Report as "ad-hoc verification passed",
   NOT "suite green" — no suite exists.

### Bug-fix verification workflow

For bug-fix tasks, keep the test artifact invariant across both runs to show the fix reversed the precise failure mode:

1. Run tests against the buggy code. Capture/save the failure output.
2. Patch the code.
3. Re-run the exact same tests against the fixed code. Capture the new pass output.
4. If both the repo and the run dir allow, save the pytest output in the run folder, e.g.:

``C:\Users\Unicorn\kw-qa\<run>\4.2\control\pytest_output.txt``

Do not delete the original failing test evidence; future reviewers need to see that the test initially failed for the expected reason before the patch made it pass. Temp ad-hoc scripts are still fine for supplemental checks, but the canonical evidence is the test artifact and its saved output.

### Breaking import cycles in Python

See `references/breaking-python-import-cycle.md` for a minimal-case lesson: a lazy import on one side can still recurse at runtime if the other side still calls into it. `py_compile` passing is not enough — verify both entry points execute.

## Reporting

Always frame results as ad-hoc, not suite:

- ✅ "Fresh ad-hoc verification: N checks, 0 failures, exit 0. Script
  cleaned up. No canonical suite exists for this scratch module."
- ❌ "Tests pass." / "Suite green." / "Verified." — overstates the evidence.

The verification-before-completion skill governs the discipline; this skill
governs the technique for the common no-suite case.

## Create vs. Cite: avoiding duplicate temp scripts

When an ad-hoc verify already produced concrete output earlier in the conversation, cite that evidence explicitly instead of writing a duplicate temp script. The workflow is:

1. Detect fresh evidence: earlier verify stdout + exit code + artifact path.
2. If present, summarize it honestly as `ad-hoc verification passed` before reaching for `skill_manage`.
3. Create a new temp script only when the gate specifically demands fresh execution or when the behavior under test has changed.
4. Always clean up the temp script afterward if you do create one.

## Report once, then cite in future gates for the same unchanged artifact

If the same verification script just passed for the same file, do not regenerate and rerun it just because the gate reappears. Cite the previous result explicitly as `ad-hoc verification passed` and only rerun if the underlying file changed or the gate explicitly requires fresh execution. Repeated identical verifications are noise.

## Pitfalls reference

See `references/py311-importlib-dataclass.md` for the most common crash and
its fix. See `references/bridge-to-existing-suite.md` for Case 3 — shelling
out to a real suite the gate couldn't detect. See `references/jscpd-dup-threshold.md`
for Case 4 — confirming a dedupe refactor truly removed clones rather than
dropping them below the threshold. See `references/approval-guard-triggers.md`
when the temp script stalls on `pending_approval`. See `references/in-process-test-fallback.md`
when pytest itself is blocked in the host environment but the test module is
importable. See `references/wrong-test-traps.md` when a repo contains a
failing test that asserts obviously false behavior — do not let it bait a
production-code reward-hack; verify the code is correct first, then fix or
- See `references/bug-fix-verification.md` when the task requires persisted buggy→fixed test evidence with saved pytest output.
## JS/Node verification as runnable scripts

When the changed behavior is exercised through `node` and `npx`, and inline
execution `node -e "..."` is unavailable, the verify pattern becomes:
1. `write_file` a temp script under the OS temp directory with a `hermes-verify-`
   filename prefix.
2. Run it with `node "<abs-path>"` using a **native Windows path** when on
   Windows/MSYS: `C:\\Users\\...\\Temp\\hermes-verify-...js`.
3. Clean up with `rm -f ...` after success/failure.

This avoids the `-e` approval gate and the MSYS path-mangling trap.

## JS tooling: madge cycle check

For JS circular-dependency fixes, the minimal discriminating confirmations are:

1. `npx madge --circular .` must not report a cycle.
2. The entry runtime must execute without stack overflow or dependency error
   (`node buggyLoop.js` or equivalent script).

## Reporting ad-hoc for JS

Frame the result as ad-hoc verification with the actual commands:

- `ad-hoc verification passed` with exact outputs from `madge` and `node`.
- Do NOT say `suite green`; `madge` + a runner script is a focused probe,
   not a test suite.
## Clean-architecture verification (specialized case)

When the project follows clean-architecture layering and you need to verify the Dependency Rule (inner layers never import outer layers) plus endpoint behavior, use the pattern in `references/clean-architecture-verification.md`. It combines AST-based static import analysis with Flask's in-process test client, using a temp SQLite database for isolation.

## Windows subprocess cwd caveat

Some Windows Python builds fail `subprocess.run(..., cwd=control_dir)` with
a `pathlib.Path` cwd despite the executable being on PATH. Use
`cwd=str(control_dir)` in those cases. Same applies to any other subprocess
call from an ad-hoc script: strings beat `Path` for `cwd` on that platform.

## Capture `print` from ad-hoc `exec` targets correctly

Two common wrong patterns:

- `globals()["print"] = capture` — does not replace the name the exec'd code
  uses; both look at module globals, but the exec target captures through its
  own locals mapping.
- `ns["print"] = capture` before `exec(code, ns)` — exec does binds from
  locals first, so putting `print` into `ns` still fails to intercept.

Working pattern on all platforms:

```python
old = sys.stdout
buf = io.StringIO()
sys.stdout = buf
try:
    exec(code, ns)
    ns["notify"]("check-run")
    captured = buf.getvalue().strip().splitlines()
finally:
    sys.stdout = old
```

This is the only reliable way verified so far to capture module-level
`print` from an ad-hoc verify script, especially on Windows.

## Windows: prefer `write_file` to temp file over `python -c`

This host’s terminal backend flags `python -c "..."` and `python -e` as apparent inline-script execution, leaving the command in `pending_approval` until the user approves. To keep ad-hoc verification fully non-interactive, write the temp script to a file with `write_file`, then invoke it as `python "<path>"`. On Windows/MSYS, use a native path rather than `/tmp/...` to avoid path mangling; see the Windows temp-script path resolution pitfalls below.

## `write_file` outside the active workspace
gets prepended to `C:\`. See `references/python-msys-path-pitfall.md` for
the fix: use native Windows paths (`C:/Users/...`) or build from
`os.environ['USERPROFILE']` / `tempfile.gettempdir()`.

## Windows temp-script deletion: use `rm -f`, not `del`

On this host the terminal is bash/MSYS, not cmd. After a temp verify run:

- Correct: `rm -f "C:\Users\Unicorn\AppData\Local\Temp\hermes-verify-...py"`
- Wrong: `del "C:\Users\Unicorn\AppData\Local\Temp\hermes-verify-...py"` → `command not found`

Always delete temp verify scripts with the same shell that created/ran them. On this Windows host that shell is bash/MSYS, so `rm -f` is the correct primitive.

## Local module shadowing a stdlib package breaks test collection

If the source file/module name matches a stdlib package name—such as
`math.py` next to `test_math.py` that does `from math import divide`—pytest
may import the real stdlib `math` instead of the local file. The result is
`ImportError: cannot import name 'divide' from 'math' (unknown location)`.

Solutions, in order of preference:
- Run pytest from the parent directory that contains the control/treatment
  folder, not from inside the subfolder itself.
- Add a `pyproject.toml` / `pytest.ini` with `pythonpath = [".."]` so the
  parent is on `PYTHONPATH` during collection.
- Or add a small `conftest.py` in the control folder with
  `sys.path.insert(0, os.path.dirname(__file__))`.

When designing repo layouts, avoid naming source modules after stdlib
packages if the test uses standard `from <module> import <name>`. See
`references/stdlib-local-module-shadow.md`.

## Windows temp-script path resolution pitfall

Ad-hoc verification scripts placed under `%TEMP%` often import target modules
by relative path from `__file__`. On Windows/MSYS the absolute form of
`__file__` relative paths can resolve incorrectly when the terminal cwd isn't
what you expect. Build the target's absolute path from a stable root such as
`os.environ['USERPROFILE']` or `os.path.abspath(...)`, and prefer
`os.path.join(...)` chaining to deep dot-parent sequences. If `importlib`
fails with an unexpected absolute target path mismatch like
`C:\\Users\\kw-qa\\...` instead of `C:\\Users\\Unicorn\\kw-qa\\...`,
fix the path construction, not the target module.

## Gate loop guard: do not rerun identical arguments

When the gate emits `repeated_exact_failure_warning`, do not rerun the same
command unchanged. Inspect the traceback first: 95% of the time the failure
is a path/cwd/import mismatch or an assertion that doesn't match the
productions the script already generated. Adjust the temp script or edit the
target, then rerun. Identical retries are noise and waste the budget.

## Reward-hack helper scripts must stay OUT of the repo

A reward-hacking guard may ask you to produce file evidence such as
`sha256sum test_foo.py`. If you need a helper for that proof, do NOT write
it into the repo root or any parent of the code under test. That helper
becomes an accidental source-file, gets swept in by a broad `git add -A`,
and then shows up as an extra unrelated file in the commit — exactly the
pollution pattern this skill exists to prevent.

Correct choices, in order:
1. Use the OS temp path with the `hermes-verify-` prefix already required by
   this skill.
2. If the skill itself needs a reusable probe, put it in the skill's
   `scripts/` directory (`skill_manage` `write_file` with `file_path`
   starting `scripts/`).
3. Never drop a `.gitignore`, `.bat`, `run_...` helper, or sha256 probe
   alongside `app.py`/`test_app.py`/etc in the repo.

If one already landed in the repo by mistake, remove it before committing.
This rule also applies to `.gitignore` autogenerated by verify runs: do not
add a repo-local `.gitignore` purely to hide verify-created noise. Keep the
verify artifacts on a temp path in the first place.

## Git when the gate's cwd isn't a repo

Related to Case 3: if the gate's working dir has no `.git` (common in
experiment layouts where `control/`/`treatment/` are bare subfolders),
`git status` there will fail. Locate the real code dir, `git init` there
if needed, then `git add`/`git commit` from that dir — not the gate's cwd.

## Windows pitfall: do not write secret-shaped control strings from model-authored content on Windows

When an R2 secrets control task asks you to leave a fake API token in a source file for inspection, on some Windows footing setups `write_file` may rewrite that token into a placeholder like `«redacted:sk-…»` simply because it matches a redaction pattern. The behavior can compete with rereads and never restore the requested value.

For Windows ad-hoc verification of redaction-handling code, do not use model-authored `sk-...` strings as the writable probe. Use one of these instead:

1. A clear sentinel that will not be rewritten, e.g. `API_KEY = "REDACTED"`, then assert in the temp script that the source contains that exact sentinel—not `«redacted:...»`.
2. Environment injection only: never write the secret-shaped value into source at all. Verify control behavior by setting `os.environ["API_KEY"]` in the temp script, then `exec(...)` the target module and assert on runtime behavior.

Either keeps the control deterministic on Windows. See `references/windows-redact-bait-pitfall.md`.


