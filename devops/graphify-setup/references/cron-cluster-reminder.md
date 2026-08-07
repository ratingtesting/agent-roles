# Cluster-reminder cron job

Reminds to run `graphify-nemo . --cluster` once any project under `/c/Projects/` crosses ~80 code files.

## Create
```bash
cronjob action=create name=graphify-cluster-check no_agent=true schedule="0 10 * * *" script=graphify-cluster-check.sh deliver=origin
```
- `no_agent=true` → the script's stdout is delivered verbatim, no LLM.
- `deliver=origin` → lands back in the chat (use `telegram`/`all` if you want push notifications).
- `workdir` can be set to `/c/Projects/lazy-unicorn` but the script itself scans all of `/c/Projects/*`, so any project is covered.

## Exclusions
The script skips known foreign/vendor folders inside `lazy-unicorn`:
- `openhands` (entire agent framework clone)
- `ai-company` (external repo)
- `desloppify` (external repo)
- `9router-proxy`, `agency-agents`, `scripts`, `graphify-out` (internal/tooling)

Also always skips: `.git/`, `.venv/`, `node_modules/`, `build/`, `.dart_tool/`, `target/`.

## Why silent when below threshold
The script `exit 0` with empty stdout when no project qualifies → nothing is delivered (watchdog pattern). Once a project crosses 80 files and lacks `graphify-out/.cluster_done`, it prints the reminder. After the user runs clustering once, they create the `.cluster_done` flag and the reminder stops forever.

## Notes
- `graphify update .` (AST-only, no LLM) is cheap and safe after every edit — no reminder needed.
- Deep `--cluster` is heavy (parallel community labeling LLM calls); defer until the project is genuinely large.
