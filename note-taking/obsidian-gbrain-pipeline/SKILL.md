---
name: obsidian-gbrain-pipeline
description: Bridge Hermes/GBrain to per-profile Obsidian vaults.
platforms: [windows]
---

# Obsidian ↔ GBrain ↔ Graphify pipeline (Windows / Hermes)

Bridge a Hermes user's GBrain "brains" (per-profile knowledge stores) into isolated
Obsidian vaults, so each Hermes profile gets its own navigable Graph view, and Graphify
can build a knowledge graph on top. Includes automation so a new Hermes profile gets its
vault+graph automatically.

## When to use
- "отдельные графы Obsidian для профиля default/app/marketplace"
- "построить граф для профиля", "связать GBrain и Obsidian", "GBrain → Obsidian → Graphify"
- "чтобы при создании нового профиля граф появлялся сам"

## Architecture
```
Hermes profile  ──maps to──►  GBrain brain (~/brains/<brain>)   (brains.json: default→personal, app→app, ...)
        │                              │  gbrain export --dir <WinPath>
        │                              ▼
        │                  Obsidian vault (Документы/Obsidian-Profiles/<prof>/)
        │                      │  Graph view (Ctrl+G) — isolated per vault
        │                      ▼
        └──────────────►  Graphify extract .  → graph.json + HTML (semantic LLM needed for .md)
```
- **Isolation** lives at the Obsidian **vault** level: each profile = one folder = one vault =
  one Graph view. Vaults never see each other. This is Obsidian's native model — no extra config.
- Hermes profiles live in `AppData\Local\hermes\profiles/<name>/` (+ the implicit `default`
  profile at `AppData\Local\hermes/`). Brain mapping is enforced by per-profile hooks
  `hooks/<name>/ensure-brain/` (event `session:start`, hardcodes `BRAIN = "<name>"`, except
  default→`personal`).

## Key scripts (in ~/brains/) — see references/pipeline-scripts.md for full source
- `lib-profile-graph.sh` — `ensure_vault_for_profile <prof> <brain>`: creates vault folder +
  `.obsidian/{app.json,workspace.json}` (graph open by default), registers it in Obsidian's
  `obsidian.json`, exports the GBrain brain there, writes `MOC.md` (wikilink index). Idempotent.
- `brain2vault.sh [prof...]` — re-export brains → vaults (refresh graphs). Maps `default→personal`,
  everything else 1:1.
- `new-profile.sh <name>` — full automation: `hermes profile create` + `ensure-brain.sh` (bg) +
  writes the `ensure-brain` hook + `ensure_vault_for_profile`.
- `profile-graph-watchdog.sh` — scans `profiles/`; for any profile lacking a `.obsidian` vault,
  creates it. Run on cron `*/15 * * * *` so graphs appear for profiles created by ANY means.

## Steps (manual, if not using the scripts)
1. Create vault folder `Документы/Obsidian-Profiles/<prof>/` with a `.obsidian/` subfolder.
2. Put `app.json` (`{"graph":{"showTags":true}, ...}`) and a `workspace.json` whose `main` leaf
   is `{"type":"graph"}` so the graph shows on open.
3. **Register the vault** in `AppData\Roaming\Obsidian\obsidian.json`:
   `{"vaults": { "<16hexid>": {"path": "C:\\Users\\Unicorn\\Documents\\Obsidian-Profiles\\<prof>", "ts": 1785177334234, "open": false } }}`.
   Obsidian picks it up after a restart; it then appears in the vault switcher.
4. Export the GBrain brain (see PITFALL re: Windows paths) and write a `MOC.md` linking notes.
5. Open in Obsidian → `Ctrl+G` for the isolated graph.

## PITFALLS (read before claiming anything)
- **gbrain export needs WINDOWS paths.** `gbrain` (Bun on Windows) does NOT expand `~` and does
  NOT understand MSYS paths like `/c/Users/...`. Passing `--dir /c/Users/...` makes export
  **silently write nothing** (it prints "Exported N pages" but no files land). ALWAYS pass
  `cygpath -w "$path"` for both `--dir` and `GBRAIN_HOME`. See references/windows-path-gotcha.md.
- **VERIFY config claims from ALL locations before stating them.** The user keeps separate
  config files; one file can contradict another. Example this session: `graphify` had a default
  provider in `~/.graphify/providers.json` (`freellmapi`/`llama-3.3-70b`), but the real working
  path was the wrapper `graphify-nemo()` in `~/.bash_profile.d/graphify.sh` (9router /
  `oc/nemotron-3-ultra-free`). Stating "Graphify is configured for X" from a single file was wrong.
  Grep every candidate: `providers.json`, `~/.bash_profile.d/*.sh`, `~/.bashrc`, env, HOOK.yaml.
- **NEVER invent or assume a tool's failure cause.** The user explicitly warned: fabricating/
  guessing conclusions ("model X breaks because of Y") without real output will get you disabled.
  When a tool fails, show the ACTUAL error/output and, if you must hypothesize, label it clearly
  as unverified. This session I wrongly claimed `nemotron-3-ultra-free` "returns reasoning instead
  of JSON → breaks Graphify" — it does NOT; the raw response has clean JSON in `content` and
  reasoning in a separate `message.reasoning` field. Verify with a direct `curl` before concluding.
- **Graphify build can fail on semantic extraction for `.md`** with "empty or filtered response"
  or `429`. This is an LLM-endpoint issue, NOT a failure of the vault/pipeline architecture. The
  vault+graph in Obsidian still works regardless. Keep the two concerns separate when reporting.
- **Graphify 0.9.12 is a compiled EXE** at `~/.local/bin/graphify` (NOT the Python `graphifyy`
  package from the skill doc — different version, different CLI). `graphify extract <path>` builds
  the graph; `graphify install --platform hermes` wires it into Hermes; `export obsidian` writes a
  vault back. Markdown needs semantic LLM (no AST for docs).

## Honest reporting
- A vault + Obsidian Graph is REAL once `ensure_vault_for_profile` wrote files and `obsidian.json`
  lists the path. Graphify's `graph.json` is a SEPARATE artifact and was NOT produced this session
  (semantic extraction blocked by endpoint). Don't claim "the pipeline works end-to-end" until
  `graph.json` actually exists.
