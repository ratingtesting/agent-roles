# DDGS Install for Hermes Venv on Windows (git-bash)

## Problem

The `hermes` CLI binary embeds its own Python. Installing `ddgs` via `pip install ddgs` often installs to a **different Python** (e.g., system Python 3.14) than the Hermes venv (Python 3.11). The Hermes venv has `pip` stripped for size, so `pip install` inside the venv fails with "No module named pip".

## Solution: Copy Dependencies from Another Venv

### Step 1 — Install ddgs into Any Python Venv via uv

```bash
# Pick an existing project with a venv, or create one
cd /c/Projects/some-project
uv pip install ddgs
```

This installs ddgs + deps to `some-project/.venv/Lib/site-packages/`.

### Step 2 — Copy the Package Tree to the Hermes Venv

```bash
DST="/c/Users/<user>/AppData/Local/hermes/hermes-agent/venv/Lib/site-packages"
SRC="/c/Projects/some-project/.venv/Lib/site-packages"

# Core ddgs package
cp -r "$SRC/ddgs"* "$DST/"

# Dependencies (list may vary by ddgs version)
for pkg in primp lxml h2 hpack brotli socksio idna fake_useragent; do
  cp -r "$SRC/$pkg"* "$DST/" 2>/dev/null
done
```

### Step 3 — Verify

```bash
/c/Users/<user>/AppData/Local/hermes/hermes-agent/venv/Scripts/python \
  -c "import ddgs; from ddgs import DDGS; print('ddgs OK')"
```

Then test with `hermes chat`:

```bash
hermes chat -q "search the web for: test" --toolsets web
```

Expected: search returns DuckDuckGo results via DDGS, no "missing module" errors.

## Why Not `uv pip install --target`?

`uv pip install ddgs --target <venv>/Lib/site-packages` may appear to succeed but not actually place the files (uv resolves deps but writes to a different layer). The copy approach is more reliable on Windows with git-bash.

## Dependency Tree (ddgs 9.x)

- `ddgs` (main)
- `primp` (HTTP client with HTTP/2 support)
  - `h2` + `hpack` (HTTP/2 framing)
  - `brotli` (compression)
  - `idna` (domain name encoding)
  - `socksio` (SOCKS proxy support)
- `lxml` (HTML parsing)
- `fake_useragent` (User-Agent rotation)
- `httpx` (HTTP client, may already be in Hermes venv)
- `click` (CLI, may already be in Hermes venv)
- `typing_extensions` (may already be in Hermes venv)
