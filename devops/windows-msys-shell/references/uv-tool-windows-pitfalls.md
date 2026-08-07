# uv-tool Installation Pitfalls on Windows + Hermes

## Problem: PYTHONPATH contamination

Hermes sets `PYTHONPATH` to include `hermes-agent/venv/Lib/site-packages`.
This leaks into every Python process spawned by Hermes, including `uv tool` executables.

**Symptom:** `ModuleNotFoundError: No module named 'pydantic_core._pydantic_core'`
(the .pyd binary was compiled for cp312 in the tool's own venv, but the imported module
comes from hermes-agent's venv which may use a different Python version).

**Fix:** Always launch uv-tool executables with `PYTHONPATH=` (empty):
```bash
PYTHONPATH= ~/AppData/Roaming/uv/tools/<tool>/Scripts/<tool>.exe --version
```

## Problem: MSYS paths rejected by Windows-native binaries

SkillSpector, Semgrep, Gitleaks, and most uv-tool binaries don't accept
MSYS paths (`/c/Users/...`, `/tmp/...`). They get mangled to `C:\c\Users\...`.

**Symptom:** `Error: Cannot determine input type` or `Invalid scanning root: \tmp\file`

**Fix:** Always wrap paths with `cygpath -w`:
```bash
PYTHONPATH= ~/AppData/Roaming/uv/tools/skillspector/Scripts/skillspector.exe \
  scan "$(cygpath -w ./skill-dir)" --no-llm
```

Note: `gitleaks protect --staged` does NOT need cygpath (it reads git staging, not paths).
But `gitleaks detect --source` DOES need it.

## Verified tool launch patterns (July 2026)

| Tool | Install command | Launch command |
|------|----------------|----------------|
| SkillSpector | `uv tool install git+https://github.com/NVIDIA/skillspector.git` | `PYTHONPATH= "$SS" scan "$(cygpath -w $DIR)" --no-llm` |
| Semgrep | `uv tool install semgrep` | `PYTHONPATH= "$SG" scan --config=auto "$(cygpath -w $FILE)"` |
| Gitleaks | Binary from GitHub release → `~/AppData/Local/hermes/bin/gitleaks.exe` | `gitleaks detect --source "$(cygpath -w $DIR)" --no-git --redact` |

## When PYTHONPATH= doesn't work

If `PYTHONPATH=` alone doesn't fix the import error, the tool may have been installed
under a different Python version than the one Hermes selects. Force the tool's own venv:
```bash
~/AppData/Roaming/uv/tools/<tool>/.venv/Scripts/python.exe -c "import <module>; print('ok')"
```
If this works, the issue is purely PYTHONPATH leaking.
