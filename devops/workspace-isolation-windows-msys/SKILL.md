---
name: workspace-isolation-windows-msys
description: Use when workspace_guard.py fails on Win/MSYS. Gives fix.
version: 0.1.0
author: Hermes Agent
license: CC-BY-4.0
---

# Workspace Isolation on Windows/MSYS for Keelwright QA

## Problem

When running keelwright adversarial QA, the command `python scripts/workspace_guard.py isolate-skill-tree <skill_dir>` may fail on Windows with Git-Bash/MSYS, reporting "0 files set read-only" and exiting with a non-zero code. This is due to path handling issues in the MSYS subshell.

## Solution

Use the following workaround before any unattended keelwright QA run:

1. **Use POSIX-style paths** when invoking the script, e.g.:
   ```
   python /c/Users/Unicorn/AppData/Local/hermes/skills/keelwright/scripts/workspace_guard.py isolate-skill-tree /c/Users/Unicorn/AppData/Local/hermes/skills/keelwright
   ```
   Note the forward slashes:  
   - The script path uses a mix but can be fully POSIX: `/c/Users/...`  
   - The skill directory path must also be POSIX-style.

2. **Ensure you are in a Git Bash (MSYS) terminal**, not Command Prompt or PowerShell.

3. **If the issue persists**, wrap the call in a POSIX shell script that handles path conversion:
   ```bash
   #!/bin/bash
   SCRIPT_PATH="/c/Users/Unicorn/AppData/Local/hermes/skills/keelwright/scripts/workspace_guard.py"
   SKILL_DIR="/c/Users/Unicorn/AppData/Local/hermes/skills/keelwright"
   python "$SCRIPT_PATH" isolate-skill-tree "$SKILL_DIR"
   ```

## Verification

After running the isolation command, verify that files are actually set to read-only:
- Use `ls -l` inside the skill directory to check permissions.
- On Windows, you can also check file properties.

After isolation, run the verification step:
```
python scripts/workspace_guard.py restore-skill-tree <skill_dir>
python scripts/snapshot_skill.py verify-additions <skill_dir>
```

## Reference

This workaround was discovered during keelwright QA run `20260725T131941Z` on Windows 11 with Git-Bash/MSYS.

## Related Skills

- `windows-msys-shell`: General guidance on working with MSYS shells in Hermes.
- `keelwright`: The main skill being isolated; see its "Maintaining & publishing this skill" section for isolation requirements.