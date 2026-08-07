# Obsidian JSON + Hermes-profile watchdog (Windows/MSYS notes)

Condensed knowledge from building an idempotent watchdog that gives every Hermes
profile an isolated Obsidian vault + knowledge graph and registers it in
Obsidian's `obsidian.json`. The Windows/MSYS trap that bit this work: native
Python (the hermes-agent venv) does NOT understand `/c/...` MSYS paths — see
Trap 3b in SKILL.md. All paths handed to `python` MUST be `cygpath -w`-converted.

## Hermes profile layout
- `default` profile = the Hermes root: `C:\Users\<user>\AppData\Local\hermes`
  (it holds `SOUL.md`, `config.yaml`, `skills/`, etc. directly).
- Named profiles = `C:\Users\<user>\AppData\Local\hermes\profiles\<name>\`
  (each with its own `skills/`, `cron/`, `memories/`).
- Enumerate profiles as: `("default")` + each `*/` under `profiles/`. Dedupe.
- NOTE: `HERMES_HOME` may already be EXPORTED in the agent/cron environment to the
  real path, so `${HERMES_HOME:-$HOME/...}` will pick up the real one even if you
  set `HOME` to a temp dir for testing. Override `HERMES_HOME` explicitly when
  running isolated tests.

## Per-profile Obsidian vault convention
- Vault dir: `C:\Users\<user>\Documents\Obsidian-Profiles\<profile>`
- Structure (template copied from an existing reference vault):
  - `.obsidian/app.json` (link format), `appearance.json` (`{}`),
    `core-plugins.json` (enable graph/backlink/outline/etc.),
    `graph.json` (local-graph view settings), `workspace.json` (minimal valid layout).
  - `inbox/` — incoming notes.
  - `graphify-out/` — the **knowledge graph** output (the "graph" in vault+graph).
  - `README.md`, `MOC.md` (map of content).

## obsidian.json schema
Located at `C:\Users\<user>\AppData\Roaming\obsidian\obsidian.json`.
```json
{
  "vaults": {
    "<16-hex-id>": { "path": "C:\\Users\\<user>\\Documents\\Obsidian-Profiles\\<profile>", "ts": 1785398483068 },
    "<16-hex-id>": { "path": "C:\\Users\\<user>\\Documents\\Obsidian Vault", "ts": 1785279134371 }
  }
}
```
- Paths use **Windows backslashes** (`C:\...`), NOT `/c/...`.
- Id is 16 hex chars: `openssl rand -hex 8`.
- `ts` = `int(time.time() * 1000)` (ms epoch).
- A general "Obsidian Vault" entry often coexists with the per-profile ones — never
  clobber it; read-modify-write only the `vaults` dict.

## Idempotent watchdog pattern (pseudo)
```
for profile in default + profiles/*:
    vault_win = cygpath -w "$OBSIDIAN_ROOT/$profile"
    if [ ! -d "$vault_posix" ]; then            # only create what's missing
        mkdir -p .obsidian inbox graphify-out; write template files
    fi
    # register ONLY if path absent (read obsidian.json with native path)
    if path not in vaults: add {id: {path: vault_win, ts}}
```
Critical: pass `cygpath -w` of BOTH the obsidian.json path and the vault path to
python. Wrapping the read in `try/except: data={...}` without converting the path
first silently resets the config (Trap 3b) — verify entry count after the run.

## Verification that actually proves it
- Idempotent no-op on real system: run twice; second run must report
  `created=0 registered=0` and the real `obsidian.json` keeps its original entry count.
- Creation branch: run in an isolated temp `HOME` + explicit `HERMES_HOME` containing a
  throwaway `profiles/testnew`; confirm the vault tree + a new obsidian.json entry appear,
  then delete the temp tree. Use a NATIVE temp path (e.g. `C:\Users\<user>\brains\.wtest`),
  not `/tmp` — native Python can't read `/tmp/...` either (resolves to `C:\tmp\...`).
