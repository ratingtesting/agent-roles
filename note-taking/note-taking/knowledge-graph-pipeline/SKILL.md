---
name: knowledge-graph-pipeline
description: GBrain to Obsidian graphs, visualized by Graphify.
platforms: [windows, linux, macos]
---

# Knowledge Graph Pipeline (GBrain -> Obsidian -> Graphify)

Turn GBrain "brains" (one per Hermes profile) into navigable Obsidian vaults with Graph
view, and into Graphify knowledge graphs. Three layers, one pipeline.

## Mental model
- **Hermes profiles** -> **GBrain brains** via `~/brains/brains.json`:
  - `default` -> `personal`, `app` -> `app`, `marketplace` -> `marketplace`
  - Each brain lives at `C:\Users\Unicorn\brains\<brain>`; `GBRAIN_HOME` points there.
- **GBrain export** -> markdown files in an **Obsidian vault** (one vault per profile).
- **Obsidian** shows the graph (Ctrl+G) from `[[wikilinks]]`.
- **Graphify** reads the vault's `.md` files and builds a semantic knowledge graph
  (HTML + `graph.json` + `GRAPH_REPORT.md`), and can write it back via `export obsidian`.

## Step 1 - Export a brain to its vault
Use `scripts/brain2vault.sh [profile...]` (default: all three). It maps profile->brain,
runs `gbrain export --dir <WINPATH>`, and writes a `MOC.md` with `[[wikilinks]]` so the
Obsidian graph is connected.

**CRITICAL pitfall:** `gbrain export --dir` only writes to **Windows paths** (`C:\...`).
MSYS paths (`/c/...`) and `~/` are silently ignored (export reports success but writes
nothing). Always `cygpath -w` the target. The script already does this.

## Step 2 - Open the vault in Obsidian
Obsidian -> `File > Open folder as vault` -> `Documents/Obsidian-Profiles/<profile>`.
Then `Ctrl+G` for Graph view. Reload (`Ctrl+R`) after re-exporting.

## Step 3 - Build the Graphify graph
See `references/windows-graphify-gotchas.md` for the real 0.9.12 command surface and the
**two-place config** trap. TL;DR:
- Do NOT run bare `graphify extract` - it uses the broken default provider.
- Use the shell function `graphify-nemo` (defined in `~/.bash_profile.d/graphify.sh`),
  which points Graphify at 9router.
- `oc/nemotron-3-ultra-free` is a **thinking model** and breaks Graphify's JSON parsing
  -> use a non-thinking model for semantic extraction.
- Graphify integrates with Hermes (`graphify install --platform hermes`) and can write a
  vault back via `graphify export obsidian`.

## Honesty note
GBrain stores semantic links in its vector DB, **not** in note text. `gbrain export` emits
flat `.md` without cross-`[[links]]`; the graph is structural/folder-based unless you
generate wikilinks (the script's MOC does this minimally). True semantic linking in
Obsidian would require an extra pass (`gbrain search` per note -> inject `[[wikilinks]]`).

## Pitfalls
- `gbrain export` Windows-path-only (above).
- Graphify config in TWO places: `~/.graphify/providers.json` (default `freellmapi`/
  `llama-3.3-70b`, 429s) vs `~/.bash_profile.d/graphify.sh` `graphify-nemo` (9router).
  Always check both; prefer the function.
- Thinking models -> Graphify "empty or filtered response".
