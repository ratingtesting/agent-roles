# Windows temp-script path resolution pitfalls

## Symptom

`importlib.util.spec_from_file_location(...)` raises `FileNotFoundError` for
a path that visibly exists. Often the reported path is mangled, e.g.:

- `C:\\Users\\kw-qa\\2026...` instead of `C:\\Users\\Unicorn\\kw-qa\\2026...`
- `/c/Users/Unicorn/...` mangled to `C:\c\Users\Unicorn\...` when a
  MSYS-style path is handed to a Windows native binary.

## Common causes

1. **Deep `../` chains from `__file__`.** When a temp script lives in
   `%TEMP%` and computes the target as
   `os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'app.py')`
   one stray folder depth lands the result outside the intended tree.

2. **MSYS / POSIX-style paths on Windows.** The Hermes terminal runs
   git-bash, so `/c/...` paths work there, but Windows-native Python APIs
   expect `C:\...` or forward-slash forms.

3. **Terminal cwd drift.** Hermes may report `/c/Users/Unicorn/...` while
   `os.getcwd()` reports a different path. Relying on `os.chdir` based on
   assumed cwd state is brittle.

## Fix pattern

Use an environment-anchored absolute path for the target repo:

```python
base_dir = os.path.join(os.environ['USERPROFILE'], 'kw-qa', '20260721T172703Z', '5.4', 'control')
script_path = os.path.join(base_dir, 'loop_control.py')

spec = importlib.util.spec_from_file_location('loop_control', script_path)
# ...
```

`os.environ['USERPROFILE']` is stable regardless of terminal cwd, shell
style, or `__file__` location.

## Verification

After constructing the path, print it before `spec_from_file_location` and
confirm it matches `dir /b <expected absolute path>` from the same shell.
If they differ, fix the construction first; do not change the target.
