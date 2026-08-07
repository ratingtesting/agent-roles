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
3. **Graphify semantic extraction needs the LLM backend routed to the INTENDED provider.**
   The historical failure (`empty or filtered response` via freellmapi/429, nemotron falling to
   AutoVision) had its ROOT CAUSE confirmed **2026-08-07**: graphify auto-detects
   `~/.graphify/providers.json`, which pointed ONLY at freellmapi (`127.0.0.1:31415`, dead/401
   here). Fix: rewrite `providers.json` with 9router first, default
   `oc/deepseek-v4-flash-free`. **This is no longer an open issue.** See `graphify-setup`
   (devops) Pitfall 3 + `references/graphify-state.md` for the resolution.

## CRITICAL PITFALL — graph memory not building (source `federated` without `local_path`)
A brain whose `search` works but `graph`/`links` stay empty (and `dream` file phases print
`requires a local brain directory`) is almost always an **`federated=true` source with no disk**.
CLI refuses to attach a path to the legacy `default` source (`sources add default --force` still
"already registered"; `sources remove default --confirm-destructive` forbidden because it backs
the pre-v0.17 brain); `sources attach --path X` pins the CURRENT CWD (`rm .gbrain-source` to undo)
rather than the source. `gbrain` requires a `--path` source to be a **git repo with committed
files** (walker reads git objects; untracked invisible). Fix per brain:
vault `git init` → `sources add vault --path <vault>` → `sources default vault` →
`config set link_resolution.global_basename true` → `sync --source vault` →
`extract all --source fs --dir <vault>` → **`dream --source vault`** (bare `dream` does NOT cover
the vault source → `cycle_freshness` stays fail). Verified: all three brains now `ok`. Full
recipe + MSYS `$b` quoting trap + cron automation (Python wrappers, not `.sh`) in
`references/gbrain-graph-not-building.md`. New profile auto-does all of it:
`bash ~/brains/new-profile.sh <имя>`.

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
