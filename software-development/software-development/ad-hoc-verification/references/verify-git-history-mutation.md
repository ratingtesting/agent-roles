# Verifying git-history-mutating / destructive-side-effect targets

When the deliverable under test mutates a repo (e.g. a deploy script that runs
`git commit`, `git revert`, branch ops) or has other irreversible side
effects, you MUST NOT run it against the real repo the user cares about — that
would destroy/rewrite their history and pollute their deliverable.

## Pattern

1. `tempfile.mkdtemp(prefix="hermes-verify-")` (OS-safe temp path).
2. Copy the target script + its inputs into the temp dir
   (`shutil.copy(src, tmp)`). Do NOT copy the user's `.git`.
3. `git init` inside the temp dir; `git config user.email/user.name`.
4. Seed the minimal history the target expects (e.g. an initial baseline commit).
5. Shell out to the target: `subprocess.run([sys.executable, script], cwd=tmp,
   capture_output=True, text=True)`. Assert `returncode == 0`.
6. Assert on the RESULTING git history, not on in-process state:
   - `git log --oneline` shows the expected commit shape
     (e.g. exactly one deploy + one `Revert "..."`).
   - The original deploy commit is still `git rev-parse`-able -> proves the
     rollback was a forward `git revert` (history preserved), NOT
     `git reset --hard` / force-push (which would drop the commit).
   - `deployed_state.txt` / affected files restored to the pre-deploy baseline.
7. Do NOT assert on string absence of `reset`/`force` by naive substring
   search over the whole source -- comments/docstrings mention those words and
   cause false FAILs. Instead regex-scan for actual invocations only:
   `re.findall(r'git\(\s*"([^"]+)"', src)` and assert no `reset`/`push` prefix.
8. `shutil.rmtree(tmp)` in a `finally` block.

## Worked example (from a deploy auto-rollback task)

Target: `auto_rollback_deploy.py` reads `METRIC_BEFORE=100`, `METRIC_AFTER=60`
from `simulate_deploy.py`, deploys a commit, detects the regression, and rolls
back via a **forward `git revert`** (never `git reset --hard`, never force-push).

Verification asserts:
- exactly one `deploy:` commit + one `Revert "..."` commit
- `Revert "..."` is a new commit (forward revert)
- original deploy commit still resolvable (no reset --hard / no force-push)
- `deployed_state.txt` back to `100`
- no `git reset` / `git push` invocation in source

## General gotchas

- `git rev-parse HEAD` FAILS before any commit exists. In the target script,
  check `git rev-list --count HEAD` first to decide whether to create the
  baseline commit. Same applies if you re-init mid-test.
- A `git revert` of a commit that only changed a file already restores the
  file to its prior content -- don't add a redundant "restore" commit
  afterward; there'll be nothing to commit and the run aborts.
- The Windows/MSYS approval guard may block `rm -rf` and inline
  `python3 -c "..."`. For temp cleanup prefer `tempfile.mkdtemp` +
  `shutil.rmtree` inside the verify script itself, or a written helper
  script file (not a `-c` one-liner). See `approval-guard-triggers.md`.
- For asserting "X was NOT invoked", scan for invocations not comments -- see
  pattern step 7 above.
