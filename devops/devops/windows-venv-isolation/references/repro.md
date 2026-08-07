# Reproduction: lightweight-embeddings venv isolation failure

Context: deployed lh0x00/lightweight-embeddings (bge-m3) on Windows via the
Hermes desktop app. Server would not start; `pip install` reported success but
transitive imports failed.

## Root cause
1. `python -m venv .venv` used the Hermes agent's temp venv as base →
   `.venv/pyvenv.cfg` pointed `executable` at `.../hermes-agent/venv/...`.
2. Hermes process exported `PYTHONPATH=.../hermes-agent;.../hermes-agent/venv/Lib/site-packages`
   → project `python`/`pip` resolved packages from the agent venv.

## Symptom chain (each step surfaced the next missing/wrong module)
- Server start → `ImportError: tokenizers>=0.22.0,<=0.23.0 required, found 0.23.1`
  (agent venv had 0.23.1; project wanted 0.22.2).
- After pinning huggingface-hub==0.36.2, tokenizers: `pip` said
  "Not uninstalling tokenizers at .../hermes-agent/venv ... outside environment"
  and left 0.23.1 in place.
- Fix A: recreated venv with uv cpython 3.11.15 explicitly:
  `"C:\Users\Unicorn\AppData\Roaming\uv\python\cpython-3.11.15-windows-x86_64-none\python.exe" -m venv .venv`
- Fix B: every pip/python command prefixed `env -u PYTHONPATH`.
- Then transitive deps were missing from the isolated venv (they had been
  "satisfied" from the agent venv): installed one by one with
  `env -u PYTHONPATH .venv/Scripts/pip install`:
  requests, tqdm, filelock, pyyaml, packaging, regex, typing_extensions,
  onnxruntime, safetensors, joblib, scikit-learn, networkx, fsspec, protobuf,
  httptools, httpx, orjson, cachetools, prometheus-client, psutil,
  pydantic-settings, uvicorn[standard], h2, jinja2, pytest, pytest-asyncio.
- Manual package dir wipe needed once: `rm -rf .venv/Lib/site-packages/tokenizers*`
  then `env -u PYTHONPATH .venv/Scripts/pip install --no-deps tokenizers==0.22.2`.

## Verification that proved it worked
- `env -u PYTHONPATH .venv/Scripts/python -c "import sys; print(sys.prefix)"`
  → `C:\Projects\lightweight-embeddings\.venv`
- `env -u PYTHONPATH .venv/Scripts/python -c "import transformers, tokenizers; ..."`
  → transformers 4.57.6, tokenizers 0.22.2, no ImportError.
- Server start with `env -u PYTHONPATH .venv/Scripts/python -m uvicorn ...`:
  `Application startup complete`.
- `curl /healthz` → ok; `curl /v1/models` → bge-m3 loaded=True dim=1024;
  `curl -X POST /v1/embeddings -d '{"input":"test"}'` → dim 1024 (default model,
  no API key, no `model` field).
- `env -u PYTHONPATH .venv/Scripts/python -m pytest tests/unit` → 44 passed.

## Note on handoff prompt accuracy
The handoff prompt claimed: server running, `/embeddings` mirrored without /v1,
`LWE_ACCESS_TOKEN` in .env, `set PYTHONPATH=` in run_server.bat, specific pinned
versions. ALL of these were false on inspection. Always live-verify, never trust.
