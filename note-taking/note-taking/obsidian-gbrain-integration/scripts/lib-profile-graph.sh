#!/bin/bash
# lib-profile-graph.sh — общие функции для связки профиль Hermes -> изолированный vault+граф в Obsidian.
# Идемпотентно: повторный вызов не дублирует и не ломает.
# Все пути в Windows-виде для gbrain; остальное в MSYS-виде.
# КОПИЯ рабочего файла с диска ~/brains/lib-profile-graph.sh (поддерживай в синхроне).

# Где живут vault'ы под профили
OBS_PROFILES="/c/Users/Unicorn/Documents/Obsidian-Profiles"
OBS_REGISTRY="/c/Users/Unicorn/AppData/Roaming/Obsidian/obsidian.json"

# ensure_registered <windows_vault_path>
#   регистрирует путь в obsidian.json, если его там ещё нет (идемпотентно)
ensure_registered() {
  local vdir_w="$1"
  [ -z "$vdir_w" ] && { echo "ensure_registered: нужен Windows-путь" >&2; return 1; }
  python - "$vdir_w" <<'PY'
import json, sys, secrets
vdir_w = sys.argv[1]
reg = r"C:\Users\Unicorn\AppData\Roaming\Obsidian\obsidian.json"
try:
    d = json.load(open(reg, encoding="utf-8"))
except Exception:
    d = {"vaults": {}}
vaults = d.setdefault("vaults", {})
already = any(v.get("path","").replace("/","\\").lower() == vdir_w.lower() for v in vaults.values())
if not already:
    vid = secrets.token_hex(8)
    vaults[vid] = {"path": vdir_w, "ts": 1785177334234, "open": False}
    json.dump(d, open(reg,"w",encoding="utf-8"), indent=2, ensure_ascii=False)
    print("  registered in obsidian.json:", vid)
else:
    print("  already registered in obsidian.json")
PY
}

# ensure_vault_for_profile <profile_name> <brain_name>
#   - создаёт папку Obsidian-Profiles/<profile_name> + .obsidian (граф включён)
#   - регистрирует vault в obsidian.json (если ещё нет)
#   - экспортирует мозг <brain_name> туда через gbrain export (Windows-путь!)
ensure_vault_for_profile() {
  local prof="$1" brain="$2"
  [ -z "$prof" ] && { echo "ensure_vault_for_profile: нужен профиль" >&2; return 1; }
  [ -z "$brain" ] && brain="$prof"

  local vdir="$OBS_PROFILES/$prof"
  local vdir_w
  vdir_w=$(cygpath -w "$vdir")

  # 1. Папка + .obsidian (копируем ВАЛИДНЫЙ конфиг из рабочего vault'а,
  #    не сочиняем сами — самопальный workspace.json ломает открытие в Obsidian)
  mkdir -p "$vdir/.obsidian"
  [ -f "$vdir/README.md" ] || echo "# Vault профиля: $prof (мозг: $brain)" > "$vdir/README.md"
  local REF="$HOME/Documents/Obsidian Vault/.obsidian"
  for f in app.json workspace.json core-plugins.json appearance.json graph.json; do
    if [ -f "$REF/$f" ] && [ ! -f "$vdir/.obsidian/$f" ]; then
      cp "$REF/$f" "$vdir/.obsidian/$f"
    fi
  done

  # 2. Регистрация в obsidian.json (если этого пути ещё нет)
  ensure_registered "$vdir_w"

  # 3. Экспорт мозга GBrain -> vault (только если мозг инициализирован)
  local brain_fs="$HOME/brains/$brain/.gbrain/brain.pglite"
  if [ -e "$brain_fs" ]; then
    export PATH="$HOME/.bun/bin:$PATH"
    export GBRAIN_NO_ONBOARD_NUDGE=1
    local K
    K=$(powershell.exe -NoProfile -Command '[Environment]::GetEnvironmentVariable("API_9ROUTER_KEY","User")' | tr -d '\r')
    export OPENAI_API_KEY="$K" OPENAI_BASE_URL="http://localhost:20128/v1"
    export GBRAIN_HOME="$(cygpath -w "$HOME/brains/$brain")"
    mkdir -p "$vdir"
    echo "  экспорт мозга '$brain' -> vault '$prof'..."
    gbrain export --dir "$vdir_w" 2>&1 | grep -vi "tier.subagent\|prompt caching\|hot (cost" | tail -1
    # MOC со связями
    {
      echo "# MOC — $prof (мозг: $brain)"
      echo
      echo "> Авто-сгенерировано brain2vault.sh/lib-profile-graph.sh. Не редактируй вручную."
      echo
      echo "## Заметки"
      echo
      find "$vdir" -name '*.md' -print | while read -r f; do
        b=$(basename "$f" .md)
        case "$b" in README|MOC) continue ;; esac
        echo "- [[$b]]"
      done
    } > "$vdir/MOC.md"
    echo "  готово: $vdir ($(find "$vdir" -name '*.md' ! -name 'README.md' ! -name 'MOC.md' | wc -l) заметок)"
  else
    echo "  мозг '$brain' не инициализирован — vault создан пустым (граф появится после capture)"
  fi
}

# list_profiles — имена профилей Hermes (папки в profiles/ + default)
list_profiles() {
  echo "default"
  for d in "$HOME/AppData/Local/hermes/profiles"/*/; do
    [ -d "$d" ] && basename "$d"
  done
}
