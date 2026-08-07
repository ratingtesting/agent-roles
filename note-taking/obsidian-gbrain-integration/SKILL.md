---
name: obsidian-gbrain-integration
description: GBrain→Obsidian vault wiring and vault open-error fixes.
tags: [obsidian, gbrain, graphify, hermes, knowledge-graph, windows]
---

# Obsidian ↔ GBrain ↔ Graphify integration

## Environment shape (Windows 11, Hermes)
- Hermes profiles: `default` (main `AppData\Local\hermes`) + `app`, `marketplace` (`AppData\Local\hermes\profiles/<name>/`).
- Profile → GBrain brain mapping lives in `~/brains/brains.json`: `default→personal`, `app→app`, `marketplace→marketplace`. **New profiles: brain name = profile name.**
- Brains are PGlite DBs at `~/brains/<name>`; built by `~/brains/ensure-brain.sh` (idempotent). A hook `ensure-brain` on `session:start` keeps each brain alive (same mechanism as default/app/marketplace).
- Obsidian vaults are per-profile folders `Documents/Obsidian-Profiles/<profile>/`, each an isolated graph.

## Pipeline status (verified)
- GBrain `--export` → markdown in vault → Obsidian **Graph view**: ✅ works.
- Obsidian vault `.md` → `graphify extract` reads them: ✅ works (Graphify found the files).
- Graphify builds `graph.json` from these vaults: ❌ currently NOT built — semantic extraction failed (see Pitfall 3). Open issue, not a config bug.

## Create an isolated vault for a profile
Use `scripts/lib-profile-graph.sh::ensure_vault_for_profile <profile> <brain>` (idempotent):
creates `Documents/Obsidian-Profiles/<profile>/`, copies a **VALID** `.obsidian/*` config from a
working vault, registers the path in `AppData\Roaming\Obsidian\obsidian.json`, and runs
`gbrain export --dir <windows_path>`.

## Automation
- `scripts/new-profile.sh <name>` — full chain: `hermes profile create` + `ensure-brain.sh` (backgrounded, ~3 min) + writes `hooks/ensure-brain` + vault.
- `scripts/profile-graph-watchdog.sh` — cron every 15 min; auto-creates a vault for any new profile (so a vault appears even if the profile was made by hand with `hermes profile create`). Already registered as cron job `profile-graph-watchdog`.

## CRITICAL PITFALLS
1. **NEVER hand-craft Obsidian `.obsidian/workspace.json`.** A simplified form like
   `{"main":{"type":"leaf","state":{"type\":\"graph\"}},"left":{...},"right":{...}}` is REJECTED by
   Obsidian and throws an open error. ALWAYS copy the full valid config
   (`app.json`, `workspace.json`, `core-plugins.json`, `appearance.json`, `graph.json`) from an
   existing working vault (`Documents/Obsidian Vault/.obsidian/`). See `references/obsidian-config-pitfall.md`.
2. **`gbrain` (Bun on Windows) accepts ONLY Windows-style paths** (`C:\...` via `cygpath -w`).
   It SILENTLY exports 0 files with `/c/...` MSYS paths or `~`. Always
   `gbrain export --dir "$(cygpath -w "$dst")"`. See `references/gbrain-windows-paths.md`.
3. **Graphify semantic extraction on `.md` needs an LLM backend and FAILED here** with
   `empty or filtered response` via both `freellmapi` (429) and `graphify-nemo` (9router/nemotron).
   `nemotron-3-ultra-free` returns clean JSON in `content` + `reasoning` in a SEPARATE field — it
   does NOT corrupt JSON. Do NOT assume thinking models break extraction. Root cause of the
   Graphify failure is NOT confirmed. See `references/graphify-state.md`.

## HARD USER RULE: verify, never fabricate
This user disconnects agents that guess or invent. When reporting tool/library behavior, timings,
or errors, state ONLY what real tool output showed. If you don't know how long an op takes,
MEASURE it (run with a timer / `process` poll) — do not estimate. If you were wrong, say so
plainly and re-verify with real output. **Stay in Russian for the entire response**, including
technical explanations — a slip into English was explicitly flagged.

## References
- `references/obsidian-config-pitfall.md` — broken vs valid workspace.json + fix.
- `references/gbrain-windows-paths.md` — gbrain export path requirement + reproduction.
- `references/graphify-state.md` — Graphify run log, provider config, open issue.
- `scripts/lib-profile-graph.sh` — core `ensure_vault_for_profile` (Windows-path safe, idempotent).
- `scripts/profile-graph-watchdog.sh` — cron auto-vault creator.
- Other scripts on disk: `~/brains/brain2vault.sh`, `~/brains/new-profile.sh`.
- `templates/` — copy a known-good vault scaffold from `Documents/Obsidian Vault/.obsidian/`.
