#!/bin/bash
# brain2vault.sh [profile...]  — export GBrain brain(s) into per-profile Obsidian vaults.
# profile default->brain personal, app->app, marketplace->marketplace (see ~/brains/brains.json)
# Writes .md notes + MOC.md ([[wikilinks]]) into Documents/Obsidian-Profiles/<profile>/.
#
# KEY: gbrain export --dir needs a WINDOWS path (C:\...). MSYS (/c/...) and ~/ silently
# write nothing. So every target path is passed through `cygpath -w`.
set -u
export PATH="$HOME/.bun/bin:$PATH"
export GBRAIN_NO_ONBOARD_NUDGE=1
K=$(powershell.exe -NoProfile -Command '[Environment]::GetEnvironmentVariable("API_9ROUTER_KEY","User")' | tr -d '\r')
export OPENAI_API_KEY="$K" OPENAI_BASE_URL="http://localhost:20128/v1"

BRAINS_HOME_W=$(cygpath -w "$HOME/brains")
VAULTS_HOME_W=$(cygpath -w "/c/Users/Unicorn/Documents/Obsidian-Profiles")

map_brain() {
  case "$1" in
    default)     echo personal ;;
    app)         echo app ;;
    marketplace) echo marketplace ;;
    *)           echo "$1" ;;
  esac
}

brains="${1:-default app marketplace}"

for prof in $brains; do
  brain=$(map_brain "$prof")
  src_w="$BRAINS_HOME_W\\$brain"
  dst_w="$VAULTS_HOME_W\\$prof"
  src_fs="$HOME/brains/$brain/.gbrain/brain.pglite"
  [ -e "$src_fs" ] || { echo "SKIP: мозг '$brain' не инициализирован (нет $src_fs)"; continue; }
  mkdir -p "$dst_w"
  echo "==> Экспорт '$brain' -> vault '$prof' =="
  GBRAIN_HOME="$src_w" gbrain export --dir "$dst_w" 2>&1 | grep -vi "tier.subagent\|prompt caching\|hot (cost" | tail -2

  moc_w="$dst_w\\MOC.md"
  {
    echo "# MOC — $prof (мозг: $brain)"
    echo
    echo "> Авто-сгенерировано brain2vault.sh. Не редактируй вручную."
    echo
    echo "## Заметки"
    echo
    find "$dst_w" -name '*.md' -print | while read -r f; do
      b=$(basename "$f" .md)
      case "$b" in README|MOC) continue ;; esac
      echo "- [[$b]]"
    done
  } > "$moc_w"
  cnt=$(find "$dst_w" -name '*.md' ! -name 'README.md' ! -name 'MOC.md' | wc -l)
  echo "    заметок: $cnt  -> $(cygpath -u "$moc_w")"
done
echo
echo "DONE. Obsidian:  File > Open folder as vault  ->  $(cygpath -u "$VAULTS_HOME_W")/<профиль>"
echo "Затем Ctrl+G — граф связей. Обновление:  bash ~/brains/brain2vault.sh [профиль]"
