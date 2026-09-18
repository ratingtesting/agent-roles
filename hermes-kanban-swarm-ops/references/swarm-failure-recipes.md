# Swarm Failure Recipes — real crash transcript + recovery

From a real `hermes kanban swarm` run (corpus cleaning, 3 workers) that crashed on
launch. Three distinct failure modes, in order they were hit.

## Symptom
All 3 workers went `blocked` within ~75s. `hermes kanban diag` showed:
```
t_1027dd6c  blocked   @swarm   wordstat-corpus-cleaner
  !! [error] repeated_failures: Agent crash x2: pid 12504 not alive
     data: consecutive_failures=2 | most_recent_outcome=crashed | last_error=pid 12504 not alive
```
`hermes kanban log t_1027dd6c`:
```
Query: work kanban task t_1027dd6c
Initializing agent...
Error: Unknown skill(s): wordstat-corpus-cleaner
```

## Fix 1 — install roles into default skills dir
Roles lived in `C:\Projects\swarm-kanban\third_party\agent-roles\` but were not Hermes
skills. Copy to the REAL local path (no `Roaming`):
```bash
SRC=/c/Projects/swarm-kanban/third_party/agent-roles
DST="C:/Users/Unicorn/AppData/Local/hermes/skills"
for r in wordstat-corpus-cleaner real-estate-buyer-seller search-query-analyst reality-checker content-creator; do
  rm -rf "$DST/$r"; mkdir -p "$DST/$r"; cp -r "$SRC/$r/." "$DST/$r/"
done
```
Verify (must answer WITHOUT the error):
```bash
hermes chat --profile swarm -Q -q "Одна фраза: твоя роль?" --skills wordstat-corpus-cleaner
# OK response → "Я — Емеля (Hermes Agent): ..."  (no Error line)
```
After this, workers stop crashing on launch. NOTE: copying into
`profiles/swarm/skills/` did NOT help the kanban dispatcher (only the direct chat test
passed) — install into `~/.hermes/skills/`.

## Fix 2 — absolute data paths in the goal
Worker log after Fix 1 still complained:
```
Workspace is empty but the comment claims data should be here. Prior attempts crashed
repeatedly. Let me hunt for it across the filesystem...
```
Root cause: worker workspace is
`C:\Users\Unicorn\AppData\Local\hermes\kanban\boards\<board>\workspaces\<task_id>\`,
isolated from `C:\Projects\...`. Hand-copying into that workspace failed because the path
changes after reclaim/reset.
Fix: state absolute paths in the swarm GOAL:
```
Очистить корпус Wordstat от мусора ВРУЧНУЮ. ДАННЫЕ по абсолютному пути:
читай батчи C:\Projects\_master-1000-articles\wordstat-collector\clean_batches\batch_001.csv
... batch_061.csv (61 файл), критерии C:\Projects\_master-1000-articles\wordstat-collector\
CORPUS_FILTER_CRITERIA.md. Пиши результат в C:\Projects\_master-1000-articles\
wordstat-collector\cleaned\batch_XXX_cleaned.csv (колонки phrase;count;category, utf-8-sig).
```
Workers then read/write via filesystem directly.

## Fix 3 — triage-loop recovery
Thrashing `reclaim`+`block`+`unblock` on a stuck card triggered:
```
t_1027dd6c → triage (unblock loop detected — needs a human decision)
```
Fix: archive ALL cards, create a FRESH swarm.
```bash
hermes kanban archive t_c3410de1   # root
for wid in t_1027dd6c t_63f7a02b t_699404cc t_9f4adfd8 t_47bb96c7; do
  hermes kanban archive "$wid"
done
# board empty → create fresh swarm with absolute-path goal (Fix 2)
hermes kanban swarm "..." --worker swarm:wordstat-corpus-cleaner:wordstat-corpus-cleaner \
  --worker swarm:real-estate-buyer-seller:real-estate-buyer-seller \
  --worker swarm:search-query-analyst:search-query-analyst \
  --verifier swarm:reality-checker:reality-checker \
  --synthesizer swarm:content-creator:content-creator
```

## Watchdog script (monitor_swarm.sh)
```bash
#!/usr/bin/env bash
set -u
BOARD="${SWARM_BOARD:-wordstat-cleanup}"
STATE_DIR="$HOME/AppData/Local/hermes/swarm_monitor"; mkdir -p "$STATE_DIR"
STATE="$STATE_DIR/${BOARD}.state"; LIST="$STATE_DIR/${BOARD}.list"
hermes kanban list --board "$BOARD" > "$LIST" 2>&1
[ ! -s "$LIST" ] && { echo "ALERT[$BOARD]: kanban list empty/err"; exit 0; }
FAIL=$(grep -iE 'failed|blocked' "$LIST" | grep -v 'done' || true)
if [ -n "$FAIL" ]; then
  echo "ALERT[$BOARD]: РОЙ УПАЛ — failed/blocked:"; echo "$FAIL"
  echo "--- Оркестратор: открой hermes kanban list --board $BOARD, найди карточку, прочитай лог, перезапусти ---"
  exit 0
fi
ACTIVE=$(grep -E '^▶' "$LIST" || true)
if [ -n "$ACTIVE" ]; then
  H=$(md5sum "$LIST" | cut -d' ' -f1); P=$(cat "$STATE" 2>/dev/null || echo "")
  if [ "$H" = "$P" ]; then
    echo "ALERT[$BOARD]: РОЙ ЗАВИС — active не менялись 3+ проверки:"; echo "$ACTIVE"
  else echo "$H" > "$STATE"; fi
  exit 0
fi
rm -f "$STATE"; exit 0
```
Cron (wakes orchestrator on ALERT):
```bash
cronjob create --name "Swarm Wordstat watchdog" --schedule "every 15m" \
  --script monitor_swarm.sh   # prompt instructs agent to wake + report on ALERT
```
Use an AGENT prompt + `deliver='all'` (NOT `no_agent`) so the orchestrator actually
wakes. `no_agent=true`+`deliver=local` only logs silently — it will NOT notify you.

## Final state (working)
```
● t_6c3cb028  running   swarm   wordstat-corpus-cleaner
● t_4ea49cd1  running   swarm   real-estate-buyer-seller
● t_80e33402  running   swarm   search-query-analyst
◻ t_ffc65716  todo     swarm:reality-checker:reality-checker   Verify swarm outputs
◻ t_e88c32dc  todo     swarm:content-creator:content-creator   Synthesize swarm outputs
```
Worker log: "I'll start by understanding the task state — checking the batch files,
what's already cleaned, and the filter criteria." → running, reading absolute paths.
