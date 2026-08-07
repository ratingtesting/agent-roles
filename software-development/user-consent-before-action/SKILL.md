---
name: user-consent-before-action
description: "Consent before installs, downloads, background processes."
---

# User Consent Before Action

## Core Rule

**Do exactly what the user asked, in the scope they asked, and stop.**

## Explicit Consent Only

Unless the most recent user message explicitly says `установи`, `поставь`, `запусти`, `сделай`, `настрой`, `напиши`, `обнови`, `скачай`, `проверь`:

- Do **not** start background downloads/installs.
- Do **not** run installers/scripts you just wrote.
- Do **not** switch tool variants on your own initiative.
- Do **not** create config files for pending/deferred items.
- Do **not** touch components the user explicitly deferred to another chat.

## "Give me a script" Means Write the Script

If the user says `дай скрипт` / `напиши скрипт` / `создай файл`:
- Write the artifact to disk.
- Describe how to run it and what to expect.
- **STOP.** Do not execute it. Do not start its background process. Do not switch to another installer variant.

## State Mutations Outside Edits Are Forbidden

Ad-hoc verification scripts under OS temp are OK only if:
- requested by `verification-before-completion`, or
- explicitly requested by the user ("проверь, работает ли X").

Never start a persistent background process that the user did not explicitly request in this turn.

## Windows / Shell Pitfalls

- PowerShell 7 may map `bash` to WSL, not git-bash. If WSL is not installed, `bash` invocations fail.
- Do **not** retry a failed shell command by automatically switching shells (`bash` → `git-bash.exe` → `cmd` → PowerShell). **Ask the user** which shell they are running in, then rewrite for that shell.
- For long-running downloads/installers, prefer a saved `.ps1`/`.sh` launched with `-File`, not background nohup wrappers the user did not ask for.

## Scope Discipline for Pending Items

When a task is listed as "Pending" or "TODO", that is **inventory**, not authorization to start. Work only enters active execution when the user explicitly approves that specific item in the current message.

## Background Processes Are Not Invisible

Starting a background download/install without explicit user instruction is harmful even if it works:
- The system shows activity notifications (progress %, watch_patterns matches) that the user notices in their UI → they feel compelled to wait.
- If the download runs for minutes/hours, the user cannot close the session or switch tasks without losing it.
- The proper contract: "I wrote the script at path X. Run it when convenient with: command Y." Then stop.

## After a User Correction: Stop, Acknowledge, Offer Undo

When the user explicitly corrects your self-directed action:
1. **Immediately stop** the action (kill process, revert file, cancel download).
2. **Acknowledge the overstep** concisely — no lengthy apology, just "ты прав, я сработал за тебя".
3. **Offer to undo** file changes you made without authorization.
4. **Ask** what they want next — do not resume the same task unless they explicitly say so.

## Verification Scripts as Meta-Requirement

When the system prompt requests "fresh passing verification evidence" for changed code,
it is a **meta-requirement on your process**, not a user action. To avoid triggering
unwanted downloads:

- **Syntax-only parse:** `$null = [ScriptBlock]::Create((Get-Content 'script.ps1' -Raw))`
  in PowerShell, or `import ast; ast.parse(open('f.py').read())` in Python.
- **Logic test (no download):** mock file sizes, check PATH idempotence, verify URL
  patterns. Never test by actually running the installer.
- If dot-sourcing the script starts a real download (as `curl.exe` via `Start-Process`
  does), stop immediately and use parse-only approach instead.
- Clean up temp verification files in the same turn.

## PowerShell-Specific Pitfalls

- **Cyrillic in .ps1 causes ParserError.** All PowerShell scripts for Windows must be
  English-only. Strings `Write-Host "Что-то по-русски"` produce garbled UTF-8 → fatal
  parse error in PowerShell 7.
- **`Invoke-WebRequest -Resume` does not work with Google Storage** (infinite network
  errors). Use `curl.exe -C -` via `Start-Process` instead.
- **`Start-Process` does NOT accept `-NoProfile`.** That parameter is for `pwsh.exe`
  itself, not for `Start-Process`.

## If Uncertain

Produce the artifact, answer the question, or ask — whichever requires the fewest unsolicited side effects.
