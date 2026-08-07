---
name: swarm-review-governance
description: Run a swarm review; never self-edit source docs.
---

# Swarm Review Governance

When the user/master hands you a **role** (orchestrator, founder-decision-gate, swarm of N specialist agents) and a corpus of documents to review and consolidate, this skill governs the class of work. It prevents two observed failures:

1. **Orchestrator self-executes the work** instead of delegating, then contradicts its own produced findings.
2. **Source-of-truth files get corrupted** because edits were made without versioning, and then "restored from memory" — which itself corrupts further.

## Resolve ROLE vs EXECUTE before doing anything

- If the task says **"you are the orchestrator"**, "дирижируешь", "канban / swarm review" — **you do NOT write the analysis or the documents yourself.** You:
  1. Map the question(s) to specialist roles/skills (product, growth, economy, architecture, legal, security, experiment-design, devil's advocate, simplicity, UX).
  2. **Verify a role SKILL exists for every dispatched role; create any missing one via the `agent-authoring` skill BEFORE dispatching** (description must fit the ≤60-char budget, trigger first). Do not dispatch a role whose agent-skill isn't on disk — the worker has no definition to follow and drifts.
  3. Dispatch each as an independent worker writing **only** into an isolated `SWARM/` (or `REVIEW/`) output dir.
  4. Run a synthesis pass that reads ALL worker outputs and produces ONE `FINAL_*_SYNTHESIS.md` (consensus / disagreements / confirmed+rejected reco / new risks / new opportunities / N-question conclusion / correct model / scope / gates / experiment / founder-decisions-left).
  5. **Stop at the decision gate.** Do not edit `MASTER_*` / `FOUNDER_DECISIONS` / architecture docs until the principal approves and downstream work is explicitly authorized.
- If you are the decision-maker doing a read-only review, produce a **new** file (e.g. `FOUNDER_DECISION_PACKET.md`); never overwrite the corpus you compose.

**: Neither handles the edit-in-place** of the supplied corpus.

## Dispatch MECHANISM: use Hermes native kanban, NOT `delegate_task` (verified correction)

The principal (master model / founder) explicitly directs: "ром через канбан, НЕ delegate_task". When a user says "запускай рой" / "ты оркестратор" for a N-agent review, the expected engine is **Hermes native kanban** (`hermes --profile <p> kanban`), not `delegate_task`. `delegate_task` is for ad-hoc parallel subtasks in the CURRENT session; a review swarm the user will MONITOR ("мой дашборд") runs on the kanban board + dashboard server.

Concrete orchestration recipe (see `references/corpus-sharm-creation.md` for the full worked example):
- Start the dispatcher FIRST: `hermes --profile <p> gateway run` (background); dispatcher lives only in the gateway. Check `gateway status`.
- Create / switch a dedicated board: `hermes --profile <p> kanban boards create <slug> --name "<name>" --icon <emoji> --switch`.
- Create one card per role, `--workspace "dir:<project-abs-path>" --assignee app --max-retries 3 --created-by founder`. **Do NOT pass `--skill`** (kanban does not resolve skills — confirmed; it errors `Unknown skill(s)`); instead put the skill call in the **card body**: line `## R-nnn\nно чтобы skill_view(name='<skill>') ...`. Guided by `kanban-swarm-orchestration` skill too.
- Parse the new card `id` from `--json` output (it is a `t_<hex>` STRING, not an int). Batch-create via a small Python driver (subprocess per card, JSON to `SWARM/card_ids.json`).
- Synthesis card: create with `--parent <first-parent>`, then `link <parent> <child>` for the remaining parents; it stays `todo`/`ready` until ALL parents complete (race-safe). Watch for the RACE pitfall in `kanban-swarm-orchestration` (a card with no parent goes `running` immediately).
- Live dashboard: adapt `kanban-swarm-orchestration`'s `templates/swarm_monitor.py` to the new `BOARD` + role FACES, run background on its port, `open_preview`. User watches THIS, so get it up as soon as cards exist.
- Orchestrate = observe + unblock, never re-write the worker's document yourself.

## ALWAYS establish local versioning BEFORE touching anything (root-cause fix)

Observed root cause of a real loss: target project dir was untracked (`??`) and **not** under git → edits were irreversible, and "undo" attempts worsened the files.
Before ANY edit / multi-write in a project:

```bash
cd <project-dir>
git rev-parse --is-inside-work-tree || git init -b main
git config user.email "agent@local" && git config user.name "Agent"   # if missing
git add -A && git commit -m "baseline: pre-work snapshot"
```

Now every operation has a revert point. Never run multiple writes on an uncommitted/untracked tree.

## NEVER hand-reconstruct a large file "from memory" — use git checkout / last-good commit

Fatal loop: a large corpus source doc was corrupted by edits, and recovery re-typed it from memory. Each rewrite produced a *different, smaller* corrupted version (e.g. 32 KB → 11 KB → 8 KB → garbage), and `git checkout <bad-baseline>` restored that already-corrupted snapshot, not the original.

- **Always** `read_file`(whole) the true file first; commit its pristine content as a baseline.
- **Do not recompose authoritative docs from recall.** If true content lives only in transcript context and the on-disk copy is degraded: **stop, say the file must be restored from a trusted source / git history, ask** — do not regenerate by hand.
- If a `write_file` regresses the doc (sanity `wc -c`/`grep -c` falls), that's corruption, not partial progress: revert to last clean commit and restart.

## Network/process outage recovery (swarm midway)
When a swarm is running and internet/processes drop:
1. Diagnose EVERYTHING first, don't assume full loss: `gateway status` (often `stale` = process died ungracefully), dashboard `/api`, and `git status`/board to see what already survived. Often most workers are `done` with full review files on disk — "start the whole task over" is wasted money not safety.
2. Restart the dispatcher: `hermes --profile app gateway run` (background). Restart the monitor: `python <proj>/.swarm/monitor.py` (background, its port) + reopen `open_preview`. Both die on the same drop; neither self-heals.
3. Workers that were `running` at the drop get STUCK on `running` with empty output; the dispatcher will NOT re-pick them by itself after restart.
4. **Peter's preference (clean restart, not reuse):** release each hung card with `hermes --profile app kanban --board <slug> reclaim <tid>` → it returns to `ready` → the gateway cleanly re-dispatches it fresh. Do NOT try to reuse/merge partial worker state, and do NOT rerun the whole task — reclaim only the hung tail. He explicitly asked for this "во избежание ошибок".
5. Verify the tail actually re-dispatched (`running` again), that `SWARM/` has non-empty files for `done` workers, and distinguish a real regression from a stale check (e.g. synthesis linked to 11 parents, dashboard showing 11 workers + 1 synthesis = 12 are all CORRECT).

## Loop guard: 3 strikes → stop & escalate

Repeated "same re-edit getting worse" = stable-degradation loop. After 3 attempts on ONE target with the same failing approach (especially hand-reconstruction), switch strategy (git revert) or escalate — never attempt a 4th recomposition.

## Deliverables inventory (all NEW files)
- `FOUNDER_DECISION_PACKET.md` — per-issue verdict: confirmed/partial/rejected with evidence + source refs.
- `FOUNDER_DECISIONS.md` — only the founder marks final; keep A/B/C options + rationale + source + "what's blocked".
- `SWARM/<role>_review.md` — worker outputs.
- `SWARM/FINAL_SWARM_SYNTHESIS.md` — cross-role consensus then gate.

## Pitfalls
- `git checkout` from a baseline **created AFTER the corruption** reproduces the corruption; only baseline a clean tree.
- In a monorepo parent with an untracked project dir, give each project its **own git repo** (project-isolation rule).
- Fast corruption canaries for markdown corpora: `grep -c "CONFLICT-"`, `wc -c` vs a known-good size.

See `references/orchestrator-loss-recovery.md` for the corruption case study, and
`references/corpus-sharm-creation.md` for the worked example of dispatching an N-agent corpus review on Hermes
native kanban (gateway-first, role-skill creation, batch visual cards, race-safe synthesis, dashboard adaptation).