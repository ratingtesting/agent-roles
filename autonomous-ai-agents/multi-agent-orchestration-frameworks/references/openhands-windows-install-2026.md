# OpenHands Windows Bare-Metal Install Attempt (2026-07)

OpenHands v1.16.0 (MIT), installed in isolated venv on Windows 11 without WSL or Docker.
Goal: no-Docker `RUNTIME=process` + local 9router (localhost:20128) provider.

## What worked
- `uv venv .venv --python 3.12` + `uv pip install` — clean, exit 0, ~1 GB deps including pywin32.
- CLI binaries: `.venv/Scripts/openhands.exe`, `.venv/Scripts/openhands-acp.exe`.
- SDK imports: `from openhands.sdk import LLM, Agent, Conversation, LocalRuntime` resolves.
- Architecture confirmed: tiny core (Agent→Actions, Conversation→EventLog, Workspace, LLM/LiteLLM).
- `PYTHONPATH=` neutralises hermetic venv drift (hermes-agent venv exporting incompatible pydantic).

## CORRECTED — what I had wrong the first pass

A later session of this skill burned several rounds guessing the settings file. Reading the **command-reference** page end-to-end (NOT truncating it on first read) revealed the truth. Three mistakes that cost real time:

1. **Wrong filename.** Headless looks for `~/.openhands/agent_settings.json` — NOT `settings.json`. A hand-written `settings.json` is silently ignored and the CLI keeps printing "Headless mode requires existing settings". The Configuration Files table in command-reference gives the canonical name verbatim.
2. **There is an env-override path that needs NO file at all.** `--override-with-envs` + env vars `LLM_MODEL`, `LLM_API_KEY`, `LLM_BASE_URL` runs headless with zero config files. Quicker for smoke tests than authoring JSON; pair with `RUNTIME=process`.
3. **`serve` is the ONLY mode that hard-requires Docker.** `web` (browser TUI, `--host`/`--port`), `--headless`, and the Python SDK all run WITHOUT Docker via `RUNTIME=process` (legacy alias `local`). The earlier "GUI needs Docker" claim was wrong — only `openhands serve` does.

Confirmed env-var smoke-test invocation (no settings file, no Docker):
```bash
export LLM_MODEL="openai/SuperCombo_256k_100"
export LLM_API_KEY="<key-or-sk-noauth>"
export LLM_BASE_URL="http://localhost:20128/v1"
export RUNTIME=process          # local process, no container isolation
PYTHONPATH= .venv/Scripts/openhands.exe --headless --override-with-envs -t "<task>"
```

CLI `--version`/interactive modes still TUI-hang in a non-TTY shell (Rich detects no terminal), but `--headless` (no TUI chrome) bypasses that. To touch interactive modes use a real terminal (`pty=true`, the Hermes desktop Terminal pane, or outside Hermes). To generate a persistent `agent_settings.json` for future headless runs, the interactive first-run wizard inside a real TTY is the blessed path.

## Docker availability on Windows — the "no nested virtualization" wall

A separate user question "replace Docker with something?" surfaced an important trap: web_search returns `wslc` (WSL Containers, Microsoft), Podman, Rancher Desktop, OrbStack as Docker alternatives. Inspection of their docs showed ALL of them ultimately need Hyper-V / WSL2 / paravirtualization underneath. They do NOT work around missing host virtualization — they repackage the same requirement. **Do not present Docker alternatives as a fix for "no virtualization"; verify the underlying requirement first, then either enable paravirtualization in BIOS/host, or pivot to a no-Docker tool entirely.** Real no-Docker pivots from this skill: openhands `LocalRuntime`/`--override-with-envs` (above), or category-B GUI orchestrators that need no container at all (Vibe Kanban + external CLI agents such as OpenCode/Claude Code). With paravirtualization enabled on the host, full `openhands serve` (Docker) also becomes available.

## Conclusion (as of July 2026, revised)
OpenHands installs and imports on Windows without WSL/Docker. Three usable entry points: `--headless --override-with-envs` (no file needed), `openhands web` (browser TUI), and the Python SDK. `openhands serve` requires Docker and is the only mode that does; with paravirtualization enabled it becomes available too. Headless on 9router via the env-var path is the recommended smoke test; the interactive wizard in a real terminal is the blessed way to generate `agent_settings.json` for persistent runs.
