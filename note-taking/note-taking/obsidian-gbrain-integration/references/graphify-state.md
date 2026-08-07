# Graphify state (this environment) — knowledge-graph build NOT yet working

## What Graphify is here
`graphify` v0.9.12, a compiled Windows EXE at `C:\Users\Unicorn\.local\bin\graphify.exe`.
Integrates with Hermes (`graphify install --platform hermes`) and can `export obsidian`.

## Provider config
- `~/.graphify/providers.json`: single provider `freellmapi`
  (`base_url: http://127.0.0.1:31415/v1`, `default_model: llama-3.3-70b`).
  Direct `graphify extract .` used this and got **429** ("All models exhausted").
- `~/.bash_profile.d/graphify.sh` defines `graphify-nemo()`:
  sets `OPENAI_BASE_URL=http://localhost:20128/v1` (the 9router endpoint),
  `OPENAI_MODEL=oc/nemotron-3-ultra-free`, then `graphify extract "$@" --backend openai --model ...`.

## Verified facts (no guessing)
- `graphify extract .` on a vault DID read the `.md` files: "found 0 code, 4 docs" — so the
  Obsidian→Graphify read pipeline works.
- With `graphify-nemo` it failed: `LLM returned empty or filtered response` (1/1 semantic chunk).
- Direct curl to 9router with `oc/nemotron-3-ultra-free` returned **valid clean JSON** in
  `message.content`, with `reasoning` in a SEPARATE field (`message.reasoning`), finish_reason
  `stop`. So the model does NOT corrupt JSON — the earlier "thinking model breaks extraction"
  hypothesis was WRONG and was retracted.
- Response ended with a trailing `data: [DONE]` SSE tail even without `stream:true` — possible
  cause of "empty or filtered" if Graphify's parser doesn't handle the trailing token. ROOT CAUSE
  NOT CONFIRMED.

## Open issue
Graphify `graph.json` has never been built from these vaults. Need to: (a) confirm which LLM
backend Graphify actually invokes, (b) check whether the SSE tail / response shape breaks its
parser, (c) try a non-thinking model or disable streaming. Do NOT claim the graph works.
