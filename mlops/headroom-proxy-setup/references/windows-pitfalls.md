# Windows Pitfalls — Headroom Proxy

## 1. Stale SQLite WAL Files

**Symptom:** Headroom prints the full startup banner then hangs indefinitely.
`netstat -ano | grep PORT` shows nothing listening.

**Cause:** A forced kill (`taskkill /F`, Ctrl+C in terminal, or process crash)
leaves `ccr_store.db-shm` and `ccr_store.db-wal` in an inconsistent state.
Headroom hangs during `uvicorn.run()` trying to open the SQLite database.

**Fix:**
```bash
rm -f ~/.headroom/ccr_store.db-shm ~/.headroom/ccr_store.db-wal
```

The main `ccr_store.db` is fine — only the shared-memory and WAL files need
to be removed. Headroom will recover the database on next startup.

## 2. Curl Unreliability

**Symptom:** `curl -s http://127.0.0.1:PORT/health` returns empty output or
"Connection refused" even though the server IS running and listening.

**Root cause:** MSYS curl on Windows has timing issues with localhost
connections, especially when the server takes time to start. The server may
not be accepting connections within curl's default connect timeout, or there
are edge cases with MSYS socket translation.

**Workaround:** Use Python sockets for reliable health checks:

```python
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(5)
s.connect(('127.0.0.1', PORT))
s.sendall(b'GET /health HTTP/1.0\r\nHost: 127.0.0.1\r\n\r\n')
data = b''
while True:
    chunk = s.recv(4096)
    if not chunk: break
    data += chunk
s.close()
```

Or use httpx from within Python:
```python
import httpx
r = httpx.get(f'http://127.0.0.1:{PORT}/health', timeout=5)
print(r.json())
```

## 3. Very Slow Startup (60-100 seconds)

**Symptom:** Banner prints immediately but the server takes 60-100 seconds to
start accepting connections. `netstat -ano | grep PORT` shows nothing for a
long time. This is NORMAL on this Windows machine, not a hang.

**Root cause:** Headroom's `uvicorn.run()` on Windows with `loop=SelectorEventLoop`
has a very slow initialization phase. The banner is printed by headroom's own
code and flushes immediately, but uvicorn does not bind the port for 60-100
seconds (Kompress ML model loading takes time). The process looks stuck but
is actually working.

**Mitigation:** After starting headroom in the background, ALWAYS wait at
least 60 seconds before attempting health checks. Use a retry loop:

```bash
# Wait and retry approach
sleep 60 && python -c "
import socket, json
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(10)
s.connect(('127.0.0.1', 8787))
s.sendall(b'GET /health HTTP/1.0\r\nHost: 127.0.0.1\r\n\r\n')
data = b''; [data := data + c for c in iter(lambda: s.recv(4096), b'')]
s.close()
print(json.loads(data.split(b'\r\n\r\n',1)[1]))
"
```

**Do NOT kill the process thinking it's hung.** The startup delay is
normal. If you kill and restart, you reset the clock.

**Observed:** After first startup takes 60-100s, subsequent starts may be faster (~30-35s) because the Kompress model is already cached. But always budget for the worst case.

## 4. No `&` Shell Backgrounding

**Symptom:** Hermes terminal rejects commands with `&`:
```
Foreground command uses '&' backgrounding. Use terminal(background=true)
```

**Fix:** Always use `terminal(background=true)` for long-lived processes.
Never use shell-level backgrounding (`&`, `nohup`, `disown`).

## 5. `taskkill /F` Kills All Instances

**Symptom:** After killing one headroom, the other stops too.

**Cause:** `taskkill /F /IM headroom.exe` matches ALL `headroom.exe` processes
by image name, not just the one you want.

**Fix:** Kill by PID:
```bash
taskkill /F /PID 1234
```
Or find the right PID first:
```bash
netstat -ano | grep 8787 | grep LISTENING
```

## 6. Background Processes Terminated by SIGTERM (UPDATED 2026-07-17)

**Symptom:** Headroom started via Hermes `terminal(background=true)` gets killed by SIGTERM (-15) when the Hermes session ends, resets (`/new`), or hits a network error / stream timeout. The `cmd /c` wrapper process receives SIGTERM.

**Cause:** Hermes background processes are lifecycle-bound to the session that spawned them. When that session dies, all its `terminal(background=true)` children get SIGTERM. This is **not** a headroom bug.

**Fix — Detach from Hermes entirely with `start /B` (verified working):**
```bash
cmd /c "start /B C:\Users\Unicorn\AppData\Local\hermes\headroom_start_8787.cmd"
cmd /c "start /B C:\Users\Unicorn\AppData\Local\hermes\headroom_start_8788.cmd"
```
`start /B` launches a detached process that is NOT a child of the Hermes terminal. Hermes cannot SIGTERM it. Processes survive after the Hermes session that started them is gone.

**Fix — Registry Run (survives reboot, most durable):**
```bash
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "Headroom-8787" /t REG_SZ /d "wscript.exe //B \"C:\Users\Unicorn\AppData\Local\hermes\headroom_8787.vbs\"" /f
```
Where `headroom_8787.vbs` runs the `.cmd` with `WindowStyle=7` (minimized). `wscript //B` = silent, no console.

**Recommendation:** Use BOTH `start /B` (immediate, survives session end) AND Registry Run (post-reboot). Startup `.lnk` is a third redundant layer.

**Verifying detachment:** After starting with `start /B`, reset the Hermes session (`/new`) and check:
```bash
netstat -ano | grep -E ":8787|:8788" | grep LISTENING   # should still show PIDs
curl -s http://127.0.0.1:8787/health                     # should return ready:true
```

**Old mitigation (less reliable):** Autostart via `.lnk` in Startup folder only triggers at login, not during a session. Task Scheduler with `/RL HIGHEST` and restart-on-failure is also viable but requires admin privileges.

## 7. `.py` Launcher Env Vars Not Propagating via `cmd /c` (NEW)

**Symptom:** A `.py` launcher that sets `os.environ['HEADROOM_OUTPUT_SHAPER'] = '1'` before `from headroom.cli import main` works when run directly (`python.exe launcher.py`), but when launched via `cmd /c` (as Hermes terminal does), the env vars set inside the Python process **do not propagate** to the uvicorn child process reliably.

**Fix:** Prefer the `.cmd` approach which sets env vars in the shell before Python starts. If you must use a `.py` launcher, ensure it's run directly (not via `cmd /c`).

## 8. System Site-packages is EMPTY (NEW)

**Symptom:** `headroom.exe --version` works but `python -c "from headroom.cli import main"` fails with `ModuleNotFoundError` even when PYTHONPATH points to what looks like the right location.

**Cause:** The system site-packages (`C:\Python314\Lib\site-packages`) only contains pip. Headroom and all dependencies (fastapi, uvicorn, etc.) are in **user** site-packages: `C:\Users\Unicorn\AppData\Roaming\Python\Python314\site-packages`.

**Fix:** ALWAYS point PYTHONPATH at user site-packages:
```batch
set PYTHONPATH=C:\Users\Unicorn\AppData\Roaming\Python\Python314\site-packages
```

Never use `C:\Python314\Lib\site-packages` — it's empty and will cause import failures.

## 9. anyllm-openai Backend — Only for Single-Protocol OpenAI-Only Upstreams (UPDATED 2026-07-17)

**Current recommendation:** Use the **default** `anthropic` backend for both 8787 and 8788. Do NOT set `HEADROOM_BACKEND` — the default backend routes `/v1/messages` and `/v1/chat/completions` natively to their respective upstream URLs without format conversion.

**When you still need `anyllm-openai` (rare):** Only for a single-protocol OpenAI-only upstream where the default backend's litellm credential check rejects your custom model name. In earlier sessions this appeared necessary, but the real root cause was a model-name mismatch (`SuperCombo_256k` vs `SuperCombo_256k_100`), not the backend.

**Pitfall — `anyllm-openai` breaks dual-protocol proxies:** It converts `/v1/messages` (Anthropic) to OpenAI format and sends it to `OPENAI_TARGET_API_URL/v1/chat/completions`. This breaks `agentrouter-claude` which expects native Anthropic Messages API. User caught this: *"опенаи!!! шлет на антропик."*

**If you do need `anyllm-openai`, install the dependency:**
```bash
C:\Python314\python.exe -m pip install "any-llm-sdk[openai]"
```
Verify visibility:
```bash
PYTHONPATH="C:\Users\Unicorn\AppData\Roaming\Python\Python314\site-packages" \
  /c/Python314/python.exe -c "import any_llm; print('ok')"
```
Must be in the same Python 3.14 user environment that headroom uses — installing in Hermes's 3.11 venv does NOT help.