#!/bin/bash
# profile-graph-watchdog.sh — автоматически создавать изолированный vault+граф в Obsidian
# для любого НОВОГО профиля Hermes, у которого ещё нет vault'а.
# Запускать по cron (каждые 15 мин) — тогда граф появляется САМ при создании профиля любым способом.
# КОПИЯ рабочего файла с диска ~/brains/profile-graph-watchdog.sh (поддерживай в синхроне).
set -u
source "$HOME/brains/lib-profile-graph.sh"

PROFILES_DIR="$HOME/AppData/Local/hermes/profiles"
changed=0

# default-профиль -> мозг personal
ensure_one() {
  local prof="$1" brain="$2"
  local vdir="$OBS_PROFILES/$prof"
  if [ -d "$vdir/.obsidian" ]; then
    return  # уже есть граф
  fi
  echo "NEW PROFILE DETECTED: $prof -> мозг $brain"
  ensure_vault_for_profile "$prof" "$brain"
  changed=1
}

ensure_one default personal
for d in "$PROFILES_DIR"/*/; do
  [ -d "$d" ] || continue
  prof=$(basename "$d")
  ensure_one "$prof" "$prof"
done

[ "$changed" -eq 0 ] && echo "watchdog: все профили уже имеют vault'ы, ничего не делал." || echo "watchdog: создал граф(ы)."
