---
name: graphify-setup
description: Wire graphify to a custom backend and auto-run it.
---

# graphify-setup

Wire `graphify` (AST + semantic code knowledge graph) into a Hermes agent environment on a custom OpenAI-compatible backend, and make agents use it by default.

## When to use
- First-time graphify install (`uv tool install graphifyy`).
- Pointing graphify at a self-hosted/proxied OpenAI-compatible endpoint (9router, llama.cpp, vLLM, LM Studio).
- Agents are silently using the wrong model because graphify auto-detected a different API key.
- Enabling graphify auto-run via AGENTS.md / Hermes rules.
- Adding a periodic reminder to run deep clustering.

## Steps (idempotent — see scripts/graphify-setup.sh)
1. `uv tool install graphifyy` (no-op if already installed).
2. Verify the backend + model with a curl chat-completions call (see script). Fail fast if `API_*` key missing.
3. Write `~/.bash_profile.d/graphify.sh` with a `graphify-nemo` wrapper function that exports `OPENAI_BASE_URL`, `OPENAI_API_KEY`, `OPENAI_MODEL` and calls `graphify extract "$@" --backend openai --model "$OPENAI_MODEL"`.
4. **CRITICAL — set global `OPENAI_*` in `~/.bash_profile`** (BASE_URL, API_KEY, MODEL) BEFORE the loader loop. This makes even a *direct* `graphify extract` (called by an agent without the wrapper) hit the intended backend. Without this, auto-detect hijacks (see Pitfall 1).
5. `graphify hermes install` — writes the graphify section into `~/AGENTS.md` (always-on rule mechanism for Hermes; there is no PreToolUse hook equivalent).
6. Append an explicit rule to `~/AGENTS.md`: ALWAYS use `graphify-nemo` for any LLM extraction/clustering; do NOT call `graphify extract` directly (freellmapi auto-detect hijack). `query`/`path`/`explain`/`update` (no LLM) may call `graphify` directly. Guard with `grep -qF` so re-runs don't duplicate.
7. Optional: add a daily cron that reminds to run `--cluster` once a project crosses ~80 code files (see scripts/graphify-cluster-check.sh + the cronjob pattern in references/cron-cluster-reminder.md).

## Pitfall 1 — backend auto-detect hijack (FIRST CLASS)
graphify auto-detects its backend from env API keys. If Hermes's primary provider is `freellmapi` and `API_FREELLMAPI_KEY` is present in the shell env, a *direct* `graphify extract` routes LLM calls to `http://127.0.0.1:31415/v1` (llama-3.3-70b) — NOT your intended 9router/nemotron. Symptoms: `Context Warnings: @url:http://127.0.0.1:31415/v1: no content extracted`.
FIX (do both):
- Global `OPENAI_*` exports in `~/.bash_profile` so the default backend is forced even without the wrapper.
- AGENTS.md rule forbidding direct `graphify extract`.
The wrapper function alone is NOT enough — agents invoke `graphify` directly, bypassing the function.

## Pitfall 2 — "update the setup file" means UPDATE, not CREATE
When the user says "update the setup file" / "обнови файл сетапа", they mean an EXISTING artifact whose path is already documented somewhere (skill, AGENTS.md, a prior script). Do NOT create a new file. First search existing files/skills for the documented setup-file path, then patch that file. Creating a new one (e.g. a second `graphify-setup.sh`) is the wrong move and the user will be annoyed.

## Pitfall 3 — the REAL hijack is in `~/.graphify/providers.json`, not only bash_profile (FIRST CLASS)
Pitfall 1 (bash_profile OPENAI_* + AGENTS rule) is necessary but NOT sufficient. graphify ALSO reads `~/.graphify/providers.json` and auto-detects the FIRST provider listed there. If that file contains ONLY `freellmapi` pointing at `http://127.0.0.1:31415/v1` (llama-3.3-70b), EVERY semantic extraction silently routes there — and that port returns **401** in this environment, so `graphify extract` "completes" but produces a near-empty semantic layer (0 communities / 0 extracted nodes; `graphify query` returns "No matching nodes found").
Symptom triad: graph built OK via AST but `semantic extraction` step is missing from logs; `query` finds nothing; `providers.json` has exactly one entry named `freellmapi`.
FIX (do this too): write `~/.graphify/providers.json` with 9router as the FIRST/only provider:
```json
{
  "9router": {
    "base_url": "http://127.0.0.1:20128/v1",
    "default_model": "oc/deepseek-v4-flash-free",
    "env_key": "API_9ROUTER_KEY",
    "vision": false,
    "max_tokens": 8192
  }
}
```
Backup first: `cp ~/.graphify/providers.json ~/.graphify/providers.json.bak.$(date +%Y%m%d-%H%M%S)`.
Verify after: `python -c "import json,os;d=json.load(open(os.path.expanduser('~/.graphify/providers.json')));print(list(d), d['9router']['default_model'])"`.

## Pitfall 4 — MSYS shell var expansion inside single quotes
On git-bash/MSYS, `bash -c '... $VAR ...'` with `$VAR` inside SINGLE quotes does NOT expand (it stays literal `$b`). The session burned a `config set sync.repo_path` with a literal `$b` path. Always use double quotes for the command string, or export the var first and reference it outside quotes:
```bash
V="C:\\Users\\Unicorn\\Documents\\Obsidian-Profiles\\marketplace"
bash ~/brains/gb.sh marketplace config set sync.repo_path "$V"   # double quotes, expands
```

## Model selection — benchmark the REAL task, not ping latency
Latency from a 1-call `/v1/chat/completions` ping is misleading: a model at 2.1s on ping took 40s on a real graphify extraction. Benchmark by running the actual extraction prompt (strict-JSON entity/edge extraction) at `temperature=0`, 3 repeats, and score: (a) JSON parses, (b) entity completeness vs a known ground-truth set, (c) stability across repeats. Some models return content inside a `reasoning` field or as SSE chunks that need a robust `content()` parser (see references/model-benchmark.md). In this env the winner was `oc/deepseek-v4-flash-free` (5/5 completeness, stable) over `oc/nemotron-3-ultra-free` (2/5) and `oc/laguna-s-2.1-free` (stable but drops infrastructure entities).

## Notes (updated)
- Graphs are isolated per project (`<project>/graphify-out/`). Each project "knows" only itself unless you run `graphify global add`.
- `graphify update .` is AST-only (no API cost) — safe to run after every code edit.
- Deep clustering is a TWO-STEP process: `graphify extract . --cluster` builds the graph, then `graphify cluster-only . --backend=openai --model=<model>` generates `GRAPH_REPORT.md`, names communities, and writes `graph.html`. Defer until ~80+ code files.
- Wrapper naming convention (this env): `graphify-ds` = 9router + `oc/deepseek-v4-flash-free` (primary); `graphify-nemo` = 9router + `oc/nemotron-3-ultra-free` (fallback, richer but only 2/5 delivery reliability). Keep `OPENAI_*` in `~/.bash_profile` pointing at 9router+deepseek so direct `graphify extract` is forced correct.
- `which graphify-nemo` reports "not found" for shell functions — use `type graphify-nemo` to verify.

## Notes
- Graphs are isolated per project (`<project>/graphify-out/`). Each project "knows" only itself unless you run `graphify global add`.
- `graphify update .` is AST-only (no API cost) — safe to run after every code edit.
- Deep clustering (`--cluster`) is heavy/expensive; defer until a project has ~80+ code files. The cron reminder handles this.
- `which graphify-nemo` reports "not found" for shell functions — use `type graphify-nemo` to verify.

## Support files
- scripts/graphify-setup.sh — full idempotent setup (steps 1–6).
- scripts/graphify-cluster-check.sh — watchdog counting code files across /c/Projects/*, alerts when ≥80 and not yet clustered.
- references/cron-cluster-reminder.md — cronjob create/update incantation.
- references/monorepo-subfolder-graphs.md — how to build isolated graphs per subfolder in a monorepo (app/, marketplace/) while excluding foreign clones.
