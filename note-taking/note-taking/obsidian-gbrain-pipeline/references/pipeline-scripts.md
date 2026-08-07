# Pipeline scripts (deployed in ~/brains/)

Put these in `~/brains/`. They are the working implementation behind
`obsidian-gbrain-pipeline`. Copy/modify as needed.

## lib-profile-graph.sh
```bash
#!/bin/bash
# Идемпотентно: повторный вызов не дублирует и не ломает.
OBS_PROFILES="/c/Users/Unicorn/Documents/Obsidian-Profiles"
OBS_REGISTRY="/c/Users/Unicorn/AppData/Roaming/Obsidian/obsidian.json"

ensure_vault_for_profile() {
  local prof="$1" brain="$2"
  [ -z "$prof" ] && { echo "need profile" >&2; return 1; }
  [ -z "$brain" ] && brain="$prof"
  local vdir="$OBS_PROFILES/$prof"
  local vdir_w; vdir_w=$(cygpath -w "$vdir")

  mkdir -p "$vdir/.obsidian"
  [ -f "$vdir/README.md" ] || echo "# Vault профиля: $prof (мозг: $brain)" > "$vdir/README.md"
  [ -f "$vdir/.obsidian/app.json" ] || cat > "$vdir/.obsidian/app.json" <<'JSON'
{ "alwaysUpdateLinks": true, "newLinkFormat": "shortest", "useMarkdownLinks": false, "graph": { "showTags": true } }
JSON
  [ -f "$vdir/.obsidian/workspace.json" ] || cat > "$vdir/.obsidian/workspace.json" <<'JSON'
{ "main": { "type": "leaf", "state": { "type": "graph" } }, "left": { "type": "split", "state": { "type": "sidebar", "collapsed": false } }, "right": { "type": "split", "state": { "type": "sidebar", "collapsed": false } } }
JSON

  # 2. Регистрация в obsidian.json (если пути ещё нет)
  python - "$vdir_w" <<'PY'
import json, sys, secrets
vdir_w = sys.argv[1]
reg = r"C:\Users\Unicorn\AppData\Roaming\Obsidian\obsidian.json"
try: d = json.load(open(reg, encoding="utf-8"))
except Exception: d = {"vaults": {}}
vaults = d.setdefault("vaults", {})
if not any(v.get("path","").replace("/","\\").lower() == vdir_w.lower() for v in vaults.values()):
    vid = secrets.token_hex(8)
    vaults[vid] = {"path": vdir_w, "ts": 1785177334234, "open": False}
    json.dump(d, open(reg,"w",encoding="utf-8"), indent=2, ensure_ascii=False)
    print("  registered:", vid)
else:
    print("  already registered")
PY

  # 3. Экспорт мозга GBrain -> vault (только если инициализирован). WINDOWS PATH!
  local brain_fs="$HOME/brains/$brain/.gbrain/brain.pglite"
  if [ -e "$brain_fs" ]; then
    export PATH="$HOME/.bun/bin:$PATH" GBRAIN_NO_ONBOARD_NUDGE=1
    local K; K=$(powershell.exe -NoProfile -Command '[Environment]::GetEnvironmentVariable("API_9ROUTER_KEY","User")' | tr -d '\r')
    export OPENAI_API_KEY="$K" OPENAI_BASE_URL="http://localhost:20128/v1"
    export GBRAIN_HOME="$(cygpath -w "$HOME/brains/$brain")"
    mkdir -p "$vdir"
    gbrain export --dir "$vdir_w" 2>&1 | grep -vi "tier.subagent\|prompt caching\|hot (cost" | tail -1
    { echo "# MOC — $prof (мозг: $brain)"; echo; echo "> auto-generated, do not edit."; echo; echo "## Заметки"; echo
      find "$vdir" -name '*.md' -print | while read -r f; do b=$(basename "$f" .md); case "$b" in README|MOC) continue;; esac; echo "- [[$b]]"; done; } > "$vdir/MOC.md"
    echo "  готово: $vdir"
  else
    echo "  мозг '$brain' не инициализирован — vault пустой (граф после capture)"
  fi
}
```

## profile-graph-watchdog.sh (cron `*/15 * * * *`)
```bash
#!/bin/bash
source "$HOME/brains/lib-profile-graph.sh"
PROFILES_DIR="$HOME/AppData/Local/hermes/profiles"
changed=0
ensure_one() { local prof="$1" brain="$2"; local vdir="$OBS_PROFILES/$prof"
  [ -d "$vdir/.obsidian" ] && return; echo "NEW PROFILE: $prof -> $brain"; ensure_vault_for_profile "$prof" "$brain"; changed=1; }
ensure_one default personal
for d in "$PROFILES_DIR"/*/; do [ -d "$d" ] || continue; ensure_one "$(basename "$d")" "$(basename "$d")"; done
[ "$changed" -eq 0 ] && echo "watchdog: все профили уже имеют vault'ы" || echo "watchdog: создал граф(ы)."
```

## new-profile.sh <name> (one-shot full automation)
Creates `hermes profile create "$NAME"`, runs `ensure-brain.sh` in background, writes the
per-profile `hooks/<name>/ensure-brain/{handler.py,HOOK.yaml}` (BRAIN="$NAME", event
`session:start`), then calls `ensure_vault_for_profile "$NAME" "$NAME"`.

Note: `hermes profile create` can hang ~60s if something blocks; run it with a timeout or in
background. `ensure-brain.sh` is slow — run it backgrounded (`&`) so the vault+graph appear
immediately even before the brain finishes initializing.
