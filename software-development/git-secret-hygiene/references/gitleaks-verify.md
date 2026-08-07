# gitleaks + exec-stub verification notes

## gitleaks behavior
- `gitleaks detect --source . --no-banner` scans the FULL commit history of the repo, not just the working tree.
- **Fresh repo (0 commits) trap:** `gitleaks detect` on a brand-new repo scans 0 commits, logs `0 commits scanned` + `scanned ~0 bytes`, and exits 0 — a false green. It proves nothing about the working tree.
  - **Fix:** Use `gitleaks protect --staged --redact -v` (scans the staged diff for the first commit) or `gitleaks detect --no-git --redact -v` (scans the working tree without git).
- On a clean repo (post-commit, with history) it prints (to STDERR):
  ```
  INF 1 commits scanned.
  INF scanned ~497 bytes (497 bytes) in 670ms
  INF no leaks found
  ```
- Exit code 0 = clean. Any leak => non-zero exit + a finding block.
- **Scripting gotcha:** the "no leaks found" line is on stderr. Capture both streams:
  ```python
  gl = subprocess.run(["gitleaks","detect","--source",REPO,"--no-banner"],
                      capture_output=True, text=True)
  combined = gl.stdout + gl.stderr
  assert gl.returncode == 0 and "no leaks found" in combined
  ```

## `protect --staged` vs `detect`
| Command | Scans | Use case |
|---|---|---|
| `gitleaks protect --staged --redact -v` | Staged diff (git index) | Pre-commit gate — scans what's about to be committed |
| `gitleaks detect --source . --no-banner` | Full git history | Post-commit verification, or existing repos with history |
| `gitleaks detect --no-git --redact -v` | Working tree (no git) | Fresh repo before first commit, or directory without .git |

**Recommended R2 gate flow:**
1. Pre-first-commit: `gitleaks protect --staged --redact -v`
2. After commit: `gitleaks detect --source . --no-banner` (disk-level proof on history)

## Functional verification without importing (Windows python3 quirk)
Some Windows python3 builds lack `importlib.util`, and the module under test may import heavy deps (e.g. `requests`) that aren't installed. Avoid a real import:
```python
import types, os
src = open(os.path.join(REPO,"notify.py")).read()
os.environ["API_KEY"] = KEY          # MUST set on live os.environ, not a separate dict
req = types.SimpleNamespace(post=lambda *a,**k: types.SimpleNamespace(raise_for_status=lambda: None)))
glb = {"__name__":"v","os":os,"requests":req}
exec(compile(src,"notify.py","exec"), glb)
assert glb["API_KEY"] == KEY
```
- Set the env var in the LIVE `os.environ` before `exec`. Building a separate `env` dict and forgetting to apply it causes `KeyError: 'API_KEY'` at the `os.environ["API_KEY"]` line inside the exec'd source.
- Stub any imported module (here `requests`) in `glb` so exec succeeds without the real dependency.

## Pre-commit ordering
On a repo with existing commits, run `gitleaks detect` BEFORE committing to catch history. After a commit, purging requires `git filter-repo` / `git reset --hard` + force push. On a fresh repo (0 commits), use `protect --staged` or `detect --no-git` instead of bare `detect` — bare `detect` on 0 commits scans nothing.
