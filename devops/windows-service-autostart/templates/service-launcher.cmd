@echo off
REM ======================================================================
REM Service Launcher Template — saved as %LOCALAPPDATA%\hermes\<service>_start.cmd
REM Run via Startup shortcut: TargetPath="...<service>_start.cmd", WindowStyle=7
REM ======================================================================

cd /d "%LOCALAPPDATA%\hermes"

REM --- SERVICE CONFIG (edit per service) ---
SET SERVICE_NAME=9router
SET EXECUTABLE=9router
SET ARGS=-p 20128 --no-browser --skip-update
SET HEALTH_URL=http://localhost:20128/v1/models
REM ------------------------------------------

echo Starting %SERVICE_NAME%...
%EXECUTABLE% %ARGS%

REM Health check (optional, runs after startup if needed)
REM timeout /t 3 >nul
REM curl -s %HEALTH_URL% >nul && echo %SERVICE_NAME% healthy || echo %SERVICE_NAME% FAILED