# PYTHONPATH Contamination on Hermes/Windows

## Problem

All terminal commands inherit `PYTHONPATH=C:\Users\<user>\AppData\Local\hermes\hermes-agent\venv\Lib\site-packages` from the Hermes desktop app. This means:

```bash
python -m venv .venv
.venv/Scripts/pip install torch ...
# -> torch goes to hermes-agent venv, NOT .venv !!
```

Evidence: `sys.path[0]` shows hermes-agent site-packages before `.venv`.

## Detection

```bash
python -c "import sys; print(sys.path[0])"
# C:\Users\Unicorn\AppData\Local\hermes\hermes-agent\venv\Lib\site-packages
```

## Fix Path A: `unset PYTHONPATH`

```bash
unset PYTHONPATH
.venv/Scripts/pip install torch  # now goes to .venv
```

Works for ad-hoc commands. Easy to forget.

## Fix Path B: `uv` (recommended)

`uv` does **not** inherit `PYTHONPATH` from the parent process. Create and install through uv:

```bash
uv venv .venv --python 3.11
uv pip install --python .venv/Scripts/python.exe <packages>
```

This guarantees isolation. The environment's `python` and `pip` then work correctly with `unset PYTHONPATH`.

## Fix Path C: `run_server.bat` guard

At the top of any `.bat`/`.sh` launcher:

```batch
@echo off
set PYTHONPATH=
```

Or for bash scripts:

```bash
export PYTHONPATH=""
```

## Why Hermes does this

The desktop app runs its commands through bash (git-bash/MSYS). The bash inherits the app's environment, which includes `PYTHONPATH` pointing to the Hermes agent's own venv (because the agent itself runs Python). This is intentional for the agent, but leaks into project venvs.
