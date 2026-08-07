--- 
name: local-embedding-server
description: Deploy and harden a local OpenAI-compatible embeddings server (lh0x00/lightweight-embeddings with bge-m3) on Windows using a venv, pinned dependencies, and login autostart. Use when the user wants a self-hosted /v1/embeddings endpoint for RAG/vector search, or asks to run lightweight-embeddings / bge-m3 locally.
---

# Local Embedding Server (lightweight-embeddings)

## When to use
- User wants a local, OpenAI-compatible `POST /v1/embeddings` endpoint.
- Self-hosted RAG, vector search, or agent needing embeddings without API keys.
- Model: **bge-m3** (Xenova/bge-m3, ONNX INT8, 1024d, 8192 tokens).

## Quick start

```bash
cd /c/Projects
git clone https://github.com/lh0x00/lightweight-embeddings.git
cd lightweight-embeddings
python -m venv .venv
# Use uv to avoid PYTHONPATH contamination from Hermes venv:
uv venv
uv pip install --python .venv/Scripts/python -U pip setuptools wheel
uv pip install --python .venv/Scripts/python numpy torch transformers sentence-transformers
uv pip install --python .venv/Scripts/python onnxruntime>=1.18 fastapi uvicorn pydantic pydantic-settings
uv pip install --python .venv/Scripts/python orjson httpx cachetools psutil prometheus-client Pillow sentencepiece
uv pip install --python .venv/Scripts/python huggingface-hub>=0.30.0 optimum[onnxruntime]
uv pip install --python .venv/Scripts/python h2 gradio pytest pytest-asyncio
```

## Version lock (tested working)

| Package | Version | Reason |
|---------|---------|--------|
| torch | 2.13.0 | shipped with sentence-transformers 5.x |
| optimum | 2.0.0 | only version compatible with torch 2.13 + sentence-transformers 5.x |
| optimum-onnx | 0.0.3 | adds ONNX support to optimum 2.0.0 |
| transformers | 4.55.4 | pulled by optimum 2.0.0 |
| tokenizers | 0.21.4 | compatibility with transformers 4.55 |
| huggingface-hub | 0.36.2 | works with transformers 4.55 |
| sentence-transformers | 5.6.0 | latest compatible |

### Known version pitfalls

- **optimum 2.x (≥2.1)** breaks with torch 2.13 — missing `_attention_scale`, `_causal_attention_mask`, `_onnx_symbolic` symbols.
- **optimum 1.x** also breaks with torch 2.13 (same symbol deletions).
- **optimum 2.0.0** is the only version that works, but lacks onnxruntime support → must add `optimum-onnx==0.0.3`.
- **tokenizers≥0.22** breaks transformers 4.55. Pin to 0.21.4.
- **transformers≥4.56** breaks optimum 2.0.0. Pin to 4.55.x.

Install the locked set explicitly:

```bash
uv pip install --python .venv/Scripts/python \
  torch==2.13.0 \
  optimum==2.0.0 \
  optimum-onnx==0.0.3 \
  transformers==4.55.4 \
  tokenizers==0.21.4 \
  huggingface-hub==0.36.2 \
  sentence-transformers==5.6.0
```

## PYTHONPATH Contamination

**Root problem:** Hermes sets `PYTHONPATH=$HERMES_VENV/site-packages`. This leaks into the project and `pip install` installs into the Hermes venv instead of the project's `.venv`.

**Solutions (pick one):**
1. **`uv` (preferred):** `uv venv` + `uv pip install` — uv never inherits `PYTHONPATH`.
2. **`unset PYTHONPATH`** before every pip command in this terminal session.
3. **`.venv/Scripts/pip install`** — fails silently on Windows (pip follows `PYTHONPATH` anyway).

```bash
# After cloning and cd, use uv:
uv venv .venv
uv pip install --python .venv/Scripts/python -r requirements.txt
```

## Config changes

### Change default model from multilingual-e5-small to bge-m3

In `lightweight_embeddings/api/schemas.py`:

```python
_DEFAULT_TEXT = "bge-m3"  # was "multilingual-e5-small"
```

### Fix race condition at model load

In `lightweight_embeddings/main.py`, **before** FastAPI imports:

```python
from optimum.onnxruntime import ONNX_WEIGHTS_NAME, ORTModelForFeatureExtraction  # noqa: F401
```

This pre-imports symbols that sentence-transformers otherwise imports inside threads during parallel model loading, preventing `ImportError` races.

### .env

```env
LWE_MODELS_PRELOAD=bge-m3
LWE_DEVICE=cpu
LWE_LOG_LEVEL=INFO
LWE_ENABLE_UI=true
LWE_LOG_JSON=false
LWE_SERVE_UI_AT=/
LWE_DEFAULT_TEXT_MODEL=bge-m3
LWE_ACCESS_TOKEN=sk-...  # optional
```

## Proxy Compatibility (9router & co.)

Some proxy/router services (notably **9router**) strip the `/v1` prefix from upstream base URLs. They compose requests like `{baseUrl}/embeddings` even when the API expects `/v1/embeddings`.

**Fix: add mirror routes without `/v1` on the server, NOT in the proxy config.** In `main.py`:

```python
app.include_router(embeddings_route.router, prefix="/v1")
app.include_router(rank_route.router, prefix="/v1")
app.include_router(stats_route.router, prefix="/v1")
app.include_router(models_route.router, prefix="/v1")
app.include_router(quota_route.router, prefix="/v1")
# Mirror routes without /v1 for proxies that strip the prefix
app.include_router(embeddings_route.router)
app.include_router(rank_route.router)
app.include_router(models_route.router)
app.include_router(health_route.router)  # already exists without /v1
```

This way both `/v1/embeddings` and `/embeddings` work; rank, models, and health are covered too. The proxy's `baseUrl` stays at `http://localhost:7860` (no `/v1`), and it sends requests to `/embeddings` which the server now handles.

**⚠️ HARD RULE: NEVER edit 9router's config to fix connectivity.** The user explicitly forbids touching 9router's SQLite DB (`%APPDATA%/9router/db/data.sqlite`) or any 9router settings. All fixes go on the server side (lightweight-embeddings). Reasons:
- Changes in proxy config may be lost on 9router update
- 9router is the user's central aggregator — they control it entirely
- The correct fix is always: make our server compatible with how 9router sends requests

### External proxy connectivity debug flow

When lightweight-embeddings and a proxy (9router) don't connect:

1. **Check the server logs** — see what path the proxy is actually requesting (e.g. `POST /embeddings` without `/v1`).
2. **DO NOT touch the proxy config or DB** — the user manages the proxy.
3. **Fix the server** — add the missing route or adjust the server so both the canonical path and the proxy-intended path work.
4. **Update SETUP_GUIDE.md** — the canonical reference doc (`C:\Projects\lazy-unicorn\SETUP_GUIDE.md`) must reflect the new server endpoints.

**Pitfall:** Do NOT edit 9router's SQLite DB (`%APPDATA%/9router/db/data.sqlite`) to fix connectivity. Changes may be lost on update, and the fix belongs on your server.

## API Key

lightweight-embeddings supports optional API key enforcement via `LWE_ACCESS_TOKEN` in `.env`. When set:

- Requests with `Authorization: Bearer <token>` → PRO tier (no rate limits).
- Requests without → anonymous tier (shedder limits, but raising them to 100 works).

Recommended to set a key if exposing the server to local network (not just localhost).

## Run

```bash
cd /c/Projects/lightweight-embeddings
unset PYTHONPATH
.venv/Scripts/python -m uvicorn lightweight_embeddings.main:create_app \
  --factory --host 0.0.0.0 --port 7860 --log-level info
```

### Autostart at Windows login

Create `run_server.bat` in project root:

```bat
@echo off
cd /d C:\Projects\lightweight-embeddings
set PYTHONPATH=
.venv\Scripts\python -m uvicorn lightweight_embeddings.main:create_app --factory --host 0.0.0.0 --port 7860 --log-level info
```

Then create a `.lnk` in `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\`:

```powershell
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\lightweight-embeddings.lnk")
$Shortcut.TargetPath = "C:\Projects\lightweight-embeddings\run_server.bat"
$Shortcut.WorkingDirectory = "C:\Projects\lightweight-embeddings"
$Shortcut.Save()
```

> **Pitfall:** Python servers that write to `sys.path` on import may fail when launched from a shortcut vs. terminal. The `set PYTHONPATH=` in `run_server.bat` prevents contamination from Hermes.

## Testing

```bash
# Health
curl http://localhost:7860/healthz
# Models
curl http://localhost:7860/v1/models
# Embedding (default model = bge-m3)
curl -X POST http://localhost:7860/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{"input": "hello world"}'
# Rank
curl -X POST http://localhost:7860/v1/rank \
  -H "Content-Type: application/json" \
  -d '{"model":"bge-m3","queries":"happy person","candidates":["sad dog","sunny day","That is a very happy person"]}'
# Unit tests
.venv/Scripts/python -m pytest tests/unit -v
```

## Shedder limits

The server has adaptive shedding (503 when overloaded). Limit models:

```env
# In .env — set high for local use
LWE_CONCURRENCY_GLOBAL=100
LWE_CONCURRENCY_PER_MODEL=100
```

## Frequently needed curl commands

```bash
# Embedding (explicit model)
curl -X POST http://localhost:7860/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{"model":"bge-m3","input":"text"}'

# Embedding (anonymous, no key)
curl -X POST http://localhost:7860/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{"input":"text"}'

# Embedding (with API key)
curl -X POST http://localhost:7860/v1/embeddings \
  -H "Authorization: Bearer sk-your-key" \
  -H "Content-Type: application/json" \
  -d '{"input":"test"}'

# Via 9router (model = provider/name format)
curl -X POST http://localhost:20128/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{"model":"lightweight-embeddings/bge-m3","input":"text"}'

# Python openai client
from openai import OpenAI
client = OpenAI(base_url="http://localhost:7860/v1", api_key="sk-noop")
resp = client.embeddings.create(model="bge-m3", input="text")
```

## Linked Files

- `references\9router-integration.md` — 9router's internal config schema and the baseUrl quirk that caused the 404.
- `references\gradio-transformers-conflict.md` — Gradio 5 vs transformers 4.55 incompatibility.
- `references\pythopath-contamination.md` — PYTHONPATH leakage from Hermes venv and how uv solves it.
- `references\rerank.md` — How rank endpoint works (cosine similarity via bge-m3 embeddings, no cross-encoder).
- `references\version-hell.md` — Full dependency version resolution history.
