# Windows Python / MSYS gotchas (Hermes on Windows)

Terminal is git-bash/MSYS, NOT PowerShell. Python behaves oddly:

## 1. `python` → Microsoft Store alias
Typing `python` or `python3` at the terminal can open the Windows Store "install Python"
page (non-zero exit, does nothing). This is the `App execution aliases` hijack.

Fix / use instead:
- Explicit venv Python: `C:\Users\<user>\AppData\Local\hermes\hermes-agent\venv\Scripts\python`
- Or avoid Python entirely — use bash `cp` / the agent's `write_file` tool.

## 2. MSYS paths break Windows Python's os.path
A script receiving `/c/Users/foo` as argv sees `os.path.isdir("/c/Users/foo")` == False
under Windows Python, even though bash `ls /c/Users/foo` works. Windows Python expects
`C:\Users\foo` or `C:/Users/foo`.

Fix — normalize in the script BEFORE any `os.path` call:
```python
import re, os
def norm(p):
    if os.name == "nt" and re.match(r"^/[a-zA-Z]/(?:\S+)?$", p):
        return p[1].upper() + ":" + p[2:]   # /c/foo -> C:/foo
    return p
```
Real case: `bootstrap_l4.py` failed with "project root not found" when the agent passed
the MSYS project root from a bash command. After adding norm(), MSYS paths worked.

## 3. Prefer bash for file ops
`cp src dst`, `mkdir -p`, `ls` — reliable under MSYS. Avoid invoking Python just to copy
a file. If a skill needs a bootstrap step, ship a `cp` loop, not a Python script.
