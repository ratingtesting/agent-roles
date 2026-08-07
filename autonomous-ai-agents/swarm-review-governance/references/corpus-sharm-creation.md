# Corpus-swarm creation — worked example (SWARM REVIEW v2, Digital Unlock Platform, 2026-08-07)

Session where the principal (master model) corrected the orchestrator: "рой через канбан, НЕ delegate_task",
and required role-skills to be mapped/created BEFORE dispatching. Full sequence that worked.

## 0. Pre-flight (order matters)
1. `hermes --profile app gateway status` — dispatcher lives ONLY in the gateway.
   If down: `hermes --profile app gateway run` (terminal background=true). Port config:
   `hermes --profile app config get platforms.api_server.port` (project used 8643; default may clash at 8642).
2. `git rev-parse --is-inside-work-tree || git init -b main` in the PROJECT dir (project-isolation: own repo,
   even inside a monorepo parent whose dir is untracked `??`). Commit a baseline BEFORE any edit.
3. `hermes --profile app kanban boards create swarm-review-v2 --name "SWARM REVIEW v2" --icon 🧠 --switch`
   (switch makes it the active board; monitor/dashboard read BOARD by name).

## 1. Role-skill inventory BEFORE cards
Master directive named 11 roles. Mapped:
- product_strategy → `chief-product-architect`
- viral_growth → `growth-hacker`
- economy → `economy-designer`
- marketplace_supply → `china-ecommerce-operator`
- ux_behavior → `ux-heuristics`
- architecture → `engineering-software-architect`
- security → `security-architect`
- legal_platform → `risk-reviewer-legal`
- mvp_experiment → **CREATED** `mvp-experiment-designer`
- devil_advocate → `strategy-duel-agent`
- simplicity → `chief-simplicity-officer`
- synthesis → **CREATED** `swarm-synthesis`

Creation rule (per `agent-authoring`): description fits the ≤60-char budget, trigger first;
body = Role / Context (what to read first) / Task (output slots) / Hard Rules (no source edits, one file in SWARM/) /
Output Example / Dependencies. Pitfall hit: a stray Korean char (`설계`) sneaked into one description — patch it out,
then verify with `skill_view`.

## 2. Batch card creation (Python driver, not shell heredoc)
Shell heredoc with `declare -A` broke on the apostrophe in "DEVIL'S ADVOCATE" and on `done` parse.
Robust: write `.swarm/make_cards_v2.py` with `subprocess.run([...])` per role, JSON body from a list,
capture `--json`, regex `"id"\s*:\s*"([^"]+)"` → `t_<hex>` STRING, dump `SWARM/card_ids.json`.
Critical body line (because `--skill` is NOT resolved by kanban create — confirmed error):
```
## РОЛЬ
Первым делом вызови skill_view(name='<skill>') и работай строго в этой роли.
...
ЖЁСТКО: НЕ редактировать MASTER_PRODUCT_SPEC/FOUNDER_DECISIONS/арх-доки. Пиши ОДИН файл: SWARM/<slug>_review.md
```
Every card also got: `--workspace "dir:C:\Projects\...\Digital Unlock Platform"` (Windows abs path),
`--assignee app --max-retries 3 --created-by founder --json`.

## 3. Synthesis card (race-safe)
- Create with `--parent <first_worker_id>` inline → goes `todo` immediately, waits parents.
- Link the OTHER 10 parents: `kanban link <parent_id> <child_id>` (POSITIONAL — `link <child> --parent <p>` fails with usage error).
- Verify: `kanban show <synth_id>` lists `parents: ...` — all 11 present, status `todo`.
- Do NOT write synthesis_id.txt from the same timed-out subprocess; `printf 't_...' > SWARM/synthesis_id.txt` after confirming id via `list`.

## 4. Dashboard adaptation
`kanban-swarm-orchestration` provides `templates/swarm_monitor.py` + `dashboard.html`. Copy into `.swarm/`, then edit:
- `BOARD = "swarm-review-v2"` (was the previous wave's board).
- `FACES` keyed by the ROLE TITLE (card titles are `SWARM: <РОЛЬ>`; strip the prefix before lookup, truncate to 22 chars).
- Monitor's file block: point `rd` at `SWARM/` not `REVIEW/` so worker outputs appear.
Launch: `terminal(background=true) python monitor.py`, then `open_preview http://127.0.0.1:8777`.

## 5. Verification of one-off orchestration scripts (not a test-suite)
Orchestration helpers (make_cards, monitor) have no canonical test. Use an ad-hoc stdlib verifier under
`$LOCALAPPDATA/Temp/hermes-verify-*.py`: py_compile each script, assert card_ids.json has N roles with `t_*` ids,
regex FACES keys cover role titles, hit `http://127.0.0.1:8777/api` (≥N tasks), `kanban show` parents count.
Expectation gotchas: dashboard API returns 11 workers + 1 synthesis = 12 (check `>= N`, not `== N`);
`kanban show` parents regex must match to end-of-line (`[^\r\n]+`), there is no trailing `;`.

## 6. Orchestrator discipline (the actual correction)
- Do NOT offer `delegate_task` for a review swarm the user will watch — they asked for kanban + "мой дашборд".
- Do NOT edit MASTER/FOUNDER_DECISIONS/architecture yourself in either role (orchestrator or reviewer).
- Once cards run: observe via dashboard, unblock at gates, wait for `FINAL_*_SYNTHESIS.md`, then STOP.
