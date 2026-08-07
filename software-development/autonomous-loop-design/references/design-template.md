# Autonomous Loop — Design Doc Template

**Workspace:** <dir>
**Mode chosen:** <cron / webhook / goal-chasing> (+ rationale)
**Run model:** <one-shot-per-tick | long-lived daemon | event-driven>

## 1. Trigger
How each cycle starts. Primary + secondary models; how webhook/event forces a cycle.

## 2. What it checks each cycle
Ordered, cheapest first:
1. Stop sentinel / signal.
2. Resource readable (else unrecoverable → escalate + stop).
3. Inventory.
4. New-work detection vs persistent ledger (absent or pending/retryable = new).
5. Stability check (size read twice; unchanged = safe to process).
6. Legitimacy (allowlist / schema); drop or quarantine on fail.

## 3. The action
For each stable, new, legitimate item:
- Mark `processing` in ledger (prevent double-processing).
- Run pluggable processor.
- Success → commit (move/delete to done/, record checksum+ts).
- Transient fail → increment attempts, bounded backoff, retry.
- Permanent fail / illegitimate → quarantine to failed/, record failed.
Persist ledger atomically after every mutation.

## 4. When it stops
| Condition | Behaviour |
|---|---|
| Stop sentinel / signal | exit 0 after current cycle; consume sentinel |
| Goal met (idle-stop) | N consecutive idle cycles → exit 0 |
| Max runtime | hard cap → finish cycle, exit 0 |
| SIGINT/SIGTERM | graceful: finish item, flush ledger, exit 0 |
| Unrecoverable | escalate, exit non-zero |

## 5. When it escalates
Additive + non-fatal except infra failure. Log to alerts + optional hook:
- per-file retries exhausted
- error-rate threshold over window
- quarantine of illegitimate input
- stuck backlog (>= threshold for K cycles)
- critical infra failure (also stops)

## 6. Layout produced
```
watch/  out/  done/  failed/  state.json  alerts.log  STOP  loop.py
```

## 7. Configuration (env vars, all optional)
watch dir, interval, max attempts, stability wait, ext allowlist, idle-stop,
max-runtime, error-rate, backlog thresholds, custom processor, escalation hook,
delete-vs-archive.
