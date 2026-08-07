# Windows Graphify gotchas (verified on graphify 0.9.12, MSYS/git-bash)

## Command surface differs from the bundled SKILL.md
The shipped `graphify` SKILL.md documents a Python CLI (`/graphify <path>`). The installed
binary on this machine is a **compiled Windows EXE** (`C:\Users\Unicorn\.local\bin\graphify.exe`,
`graphify 0.9.12`) with a different surface. Real subcommands observed:

- `graphify extract <path>`        — headless full extraction (AST + semantic LLM)
- `graphify export obsidian ...`   — write the graph back into a vault
- `graphify query "Q"` / `path "A" "B"` / `explain "X"` — graph Q&A
- `graphify install --platform hermes` — integrates with Hermes
- `graphify global ...`            — merge multiple project graphs into `~/.graphify/global-graph.json`
- `graphify update <path>` / `cluster-only <path>` / `label <path>` / `watch <path>`

## THE TWO-PLACE CONFIG TRAP (caused a real misrun)
`graphify extract` reads `~/.graphify/providers.json`. On this machine it contains a single
broken default:
{ "freellmapi": { "base_url": "http://127.0.0.1:31415/v1", "default_model": "llama-3.3-70b", ... } }
That endpoint returns HTTP 429 "All models exhausted". A bare `graphify extract .` therefore
fails semantic extraction — even though the user's *actual* working config is elsewhere.

The real working config is a shell function in `~/.bash_profile.d/graphify.sh`:
  graphify-nemo() {
    export OPENAI_BASE_URL="http://localhost:20128/v1"   # 9router
    export OPENAI_API_KEY="${API_9ROUTER_KEY}"
    export OPENAI_MODEL="oc/nemotron-3-ultra-free"
    graphify extract "$@" --backend openai --model "$OPENAI_MODEL"
  }
ALWAYS `source ~/.bash_profile.d/graphify.sh` and use `graphify-nemo`, not bare
`graphify extract`. Never trust `providers.json` alone — check both places.

## Thinking models break Graphify's JSON parsing
`oc/nemotron-3-ultra-free` is a THINKING model: it returns a `reasoning`/`refusal`
structure and `finish_reason: length` at low `max_tokens`, instead of clean JSON. Graphify
reports `LLM returned empty or filtered response`. For semantic extraction use a
non-thinking model. General rule: reasoning models + tools that expect strict JSON = parse
failures.

## No API key needed to run, but semantic needs an LLM
`graphify` needs no key to build a code-only (AST) graph. Markdown/paper/image corpora need
semantic extraction (an LLM). Here it is driven via the `openai` backend to 9router.
