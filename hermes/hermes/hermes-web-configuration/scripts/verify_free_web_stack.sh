#!/usr/bin/env bash
# Verify the free web stack is actually active for the CURRENT Hermes profile.
# Catches the silent "extract_backend: crawl4ai but plugin not in this profile's
# home -> falls back to paid firecrawl" failure.
#
# Usage:  bash verify_free_web_stack.sh            # current profile
#         HERMES_HOME=/c/Users/X/AppData/Local/hermes/profiles/app bash verify_free_web_stack.sh

set -u
fail=0

HOME_DIR=$(python -c "from hermes_cli.plugins import get_hermes_home; print(get_hermes_home())" 2>/dev/null)
if [ -z "$HOME_DIR" ]; then
  echo "!! could not resolve get_hermes_home() — run from a shell where hermes_cli imports"
  exit 2
fi
echo "HERMES_HOME     : $HOME_DIR"
PLUGDIR="$HOME_DIR/plugins"
echo "user plugins dir: $PLUGDIR  (exists: $([ -d "$PLUGDIR" ] && echo yes || echo NO))"

# 1. Is the crawl4ai plugin physically present in THIS profile's home?
if [ -f "$PLUGDIR/web/crawl4ai/plugin.yaml" ]; then
  echo "[ok]   crawl4ai plugin present in this profile"
else
  echo "[FAIL] crawl4ai plugin NOT in this profile's plugin home."
  echo "       plugins.enabled is only an allow-list; extract will silently fall back to PAID firecrawl."
  echo "       fix: mkdir -p \"$PLUGDIR/web\" && cp -r <shared>/plugins/web/crawl4ai \"$PLUGDIR/web/\""
  fail=1
fi

# 2. Config says what we think it says
CONF="$HOME_DIR/config.yaml"
echo "config          : $CONF"
grep -E "search_backend|extract_backend|use_gateway|cloud_provider" "$CONF" 2>/dev/null

# 3. The only claim that matters: who actually serves extract right now
python - <<'PY'
try:
    from hermes_cli.plugins import discover_plugins
    discover_plugins()
    from agent.web_search_registry import get_provider, get_active_extract_provider
    p = get_provider("crawl4ai")
    print("registered crawl4ai   :", None if p is None else p.name,
          "available:" , None if p is None else p.is_available())
    a = get_active_extract_provider()
    name = None if a is None else a.name
    print("ACTIVE extract provider:", name)
    if name != "crawl4ai":
        print("[FAIL] extract is NOT free — it will bill via", name)
except Exception as e:
    print("[warn] in-process check failed:", e)
PY

# 4. Have paid calls already happened in this profile?
LOG="$HOME_DIR/logs/agent.log"
if [ -f "$LOG" ]; then
  n=$(grep -i "Firecrawl scraping:" "$LOG" 2>/dev/null | wc -l)
  echo "past billed firecrawl scrapes in log: $n"
  [ "$n" -gt 0 ] && grep -n -i "Firecrawl scraping:" "$LOG" | tail -5
fi

exit $fail
