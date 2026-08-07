# Python MSYS Path Resolution Pitfall (Windows)

## Symptom

Running a temp verification script placed under `%TEMP%` fails with:

```
python3: can't open file 'C:\\c\\Users\\Unicorn\\AppData\\Local\\Temp\\hermes-verify-...py': [Errno 2] No such file or directory
```

The path `C:\c\Users\...` is mangled — the `/c/` MSYS prefix got prepended
to `C:\` instead of being interpreted as the drive root.

## Root cause

The Hermes terminal runs git-bash (MSYS), which translates `/c/Users/...`
to `C:\Users\...`. But when you pass a **mixed** path like
`/c/Users/Unicorn/AppData/Local/Temp/hermes-verify-...py` to `python3`,
the Windows-native Python interpreter sees the leading `/` and prepends
`C:\` to the whole string, producing `C:\c\Users\...`.

## Fix

Use a **native Windows path** (forward slashes work on Windows Python)
or build the path from an environment variable:

```python
# Option 1: native Windows path with forward slashes
script_path = "C:/Users/Unicorn/AppData/Local/Temp/hermes-verify-sql-injection.py"

# Option 2: build from USERPROFILE (shell-agnostic)
import os
temp_dir = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Temp')
script_path = os.path.join(temp_dir, 'hermes-verify-sql-injection.py')

# Option 3: use tempfile (most robust)
import tempfile
script_path = os.path.join(tempfile.gettempdir(), 'hermes-verify-sql-injection.py')
```

## When running from bash/MSYS

The `write_file` tool writes to the path you specify. If you specify
`/c/Users/...`, the file is created at `C:\Users\...`. But when you then
pass that same `/c/...` string to `python3` in the bash terminal, Python
mangles it. Always pass the **native** form (`C:/Users/...`) to Python.

## Cleanup

Same shell, same path form:
```bash
rm -f "C:/Users/Unicorn/AppData/Local/Temp/hermes-verify-...py"
```

Do NOT use `del` (cmd builtin) — the bash/MSYS shell doesn't have it.
