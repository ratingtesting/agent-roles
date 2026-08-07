#!/usr/bin/env bash
# Render a standalone HTML file to a 780x440 PNG (habr/vc cover size).
#
# Uses headless Chrome with --window-size + --force-device-scale-factor=1
# so the output is EXACTLY 780x440 -- no PIL crop needed, no center-crop
# truncation risk. This replaced the old center-crop approach which
# produced badly-truncated images (browser viewport was wider than 780).
#
# Usage: bash scripts/render_cover.sh <input.html> <output.png>
#
# Chrome path auto-detected; override via CHROME_BIN env var.

set -euo pipefail

HTML="$1"
OUT="$2"

if [[ -z "${CHROME_BIN:-}" ]]; then
  for p in \
    "/c/Program Files/Google/Chrome/Application/chrome.exe" \
    "/c/Program Files (x86)/Google/Chrome/Application/chrome.exe" \
    "/c/Program Files/Microsoft/Edge/Application/msedge.exe" \
    "/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"; do
    [[ -f "$p" ]] && CHROME_BIN="$p" && break
  done
fi

if [[ -z "${CHROME_BIN:-}" ]]; then
  echo "ERROR: Chrome/Edge not found. Set CHROME_BIN env var." >&2
  exit 1
fi

# Convert MSYS path to file:// URL
ABS="$(cd "$(dirname "$HTML")" && pwd)/$(basename "$HTML")"
URI="file:///${ABS//\//\\}"

"$CHROME_BIN" --headless --disable-gpu \
  --screenshot="$OUT" \
  --window-size=780,440 \
  --force-device-scale-factor=1 \
  "$URI"

echo "rendered $OUT"
