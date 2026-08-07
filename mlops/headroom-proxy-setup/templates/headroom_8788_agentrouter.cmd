@echo off
REM ============================================================
REM Headroom Proxy Launcher - 8788 (agentrouter with compression)
REM ============================================================
REM Copy this file, adjust env vars, place in your autostart folder
REM or run manually. Uses Python 3.14 with user site-packages.

set PYTHONPATH=C:\Users\Unicorn\AppData\Roaming\Python\Python314\site-packages
set OPENAI_TARGET_API_URL=https://agentrouter.org/v1
set ANTHROPIC_TARGET_API_URL=https://agentrouter.org
set HEADROOM_OUTPUT_SHAPER=1
set HEADROOM_VERBOSITY_AUTOTUNE=1
set HEADROOM_BACKEND=anyllm-openai
set HEADROOM_ANYLLM_PROVIDER=openai
set OPENAI_API_KEY=%API_AGENTROUTER_KEY%
REM set ANTHROPIC_API_KEY=%API_AGENTROUTER_KEY%  REM optional if using Anthropic format

C:\Python314\python.exe -c "from headroom.cli import main; import sys; sys.argv=['headroom','proxy','--port','8788']; main()"