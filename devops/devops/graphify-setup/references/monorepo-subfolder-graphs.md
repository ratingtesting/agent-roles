# Building Graphs for Subfolders in a Monorepo

## Problem
`lazy-unicorn` is a monorepo containing:
- **Your actual projects**: `app/` (Flutter Mini App), `marketplace/` (Ai Company OS)
- **Foreign/vendor clones**: `openhands/`, `ai-company/`, `desloppify/`, `9router-proxy/`, `agency-agents/`, etc.

Running graphify on the monorepo root includes all foreign code → massive graphs, timeouts, wrong context.

## Solution: Build per-subfolder graphs

Each real project gets its own isolated `graphify-out/`:

```bash
# Your actual projects (run from monorepo root)
cd /c/Projects/lazy-unicorn/app && graphify-nemo . --no-cluster
cd /c/Projects/lazy-unicorn/marketplace && graphify-nemo . --no-cluster
```

**Do NOT run** `graphify-nemo /c/Projects/lazy-unicorn --no-cluster` — that drags in 1400+ foreign files.

## Why this works

- Graphify looks for the nearest `graphify-out/` UP the tree from CWD.
- Running from `app/` creates `app/graphify-out/` — isolated from `marketplace/graphify-out/`.
- Foreign folders stay ignored (they have no `graphify-out/` and aren't scanned from your project roots).

## AGENTS.md Integration

The rule in `~/AGENTS.md` (written by `graphify hermes install`) tells agents:
> "For codebase questions, first run `graphify query \"<question>\"` when `graphify-out/graph.json` exists."

Since each project has its own `graphify-out/`, agents automatically query the right graph when working inside `app/` or `marketplace/`.

## When to build the root graph (rare)

Only if you genuinely need cross-project relationships. Then run:
```bash
cd /c/Projects/lazy-unicorn && graphify-nemo app marketplace --no-cluster
```
(Pass explicit subfolders, not the whole root.)

## Update workflow

After editing code in `app/`:
```bash
cd /c/Projects/lazy-unicorn/app && graphify update .
```
AST-only, instant, updates only `app/graphify-out/`.

## Cron job compatibility

The existing `graphify-cluster-check.sh` already excludes foreign folders from the count. It will correctly trigger clustering reminders for `app/` and `marketplace/` when THEY cross 80 files, ignoring the monorepo's total.