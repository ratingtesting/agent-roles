---
name: graphify-setup
description: Wire graphify to a custom backend and auto-run it.
---

# graphify-setup

Wire `graphify` (AST + semantic code knowledge graph) into a Hermes agent environment on a custom OpenAI-compatible backend, and make agents use it by default.

## When to use
- First-time graphify install (`uv tool install graphifyy`).
- Pointing graphify at a self-hosted/proxied OpenAI-compatible endpoint (9router, llama.cpp, vLLM, LM Studio).
- Agents are silently using the wrong model because graphify auto-detected a different API key.
- Enabling graphify auto-run via AGENTS.md / Hermes rules.
- Adding a periodic reminder to run deep clustering.

## Steps (idempotent — see scripts/graphify-setup.sh)
1. `uv tool install graphifyy` (no-op if already installed).
2. Verify the backend + model with a curl chat-completions call (see script). Fail fast if `API_*` key missing.
3. Write `~/.bash_profile.d/graphify.sh` with a `graphify-nemo` wrapper function that exports `OPENAI_BASE_URL`, `OPENAI_API_KEY`, `OPENAI_MODEL` and calls `graphify extract "$@" --backend openai --model "$OPENAI_MODEL"`.
4. **CRITICAL — set global `OPENAI_*` in `~/.bash_profile`** (BASE_URL, API_KEY, MODEL) BEFORE the loader loop. This makes even a *direct* `graphify extract` (called by an agent without the wrapper) hit the intended backend. Without this, auto-detect hijacks (see Pitfall 1).
5. `graphify hermes install` — writes the graphify section into `~/AGENTS.md` (always-on rule mechanism for Hermes; there is no PreToolUse hook equivalent).
6. Append an explicit rule to `~/AGENTS.md`: ALWAYS use `graphify-nemo` for any LLM extraction/clustering; do NOT call `graphify extract` directly (freellmapi auto-detect hijack). `query`/`path`/`explain`/`update` (no LLM) may call `graphify` directly. Guard with `grep -qF` so re-runs don't duplicate.
7. Optional: add a daily cron that reminds to run `--cluster` once a project crosses ~80 code files (see scripts/graphify-cluster-check.sh + the cronjob pattern in references/cron-cluster-reminder.md).

## Pitfall 1 — backend auto-detect hijack (FIRST CLASS)
graphify auto-detects its backend from env API keys. If Hermes's primary provider is `freellmapi` and `API_FREELLMAPI_KEY` is present in the shell env, a *direct* `graphify extract` routes LLM calls to `http://127.0.0.1:31415/v1` (llama-3.3-70b) — NOT your intended 9router/nemotron. Symptoms: `Context Warnings: @url:http://127.0.0.1:31415/v1: no content extracted`.
FIX (do both):
- Global `OPENAI_*` exports in `~/.bash_profile` so the default backend is forced even without the wrapper.
- AGENTS.md rule forbidding direct `graphify extract`.
The wrapper function alone is NOT enough — agents invoke `graphify` directly, bypassing the function.

### Third hijack vector — `~/.graphify/providers.json`
Even with correct `~/.bash_profile` exports and a working wrapper, this file can still declare ONLY `freellmapi` (`base_url http://127.0.0.1:31415/v1`, `default_model llama-3.3-70b`). graphify reads it for provider selection, so semantic extraction keeps aiming at the wrong (often dead — the port answers 401) endpoint while the AST graph builds fine. ALWAYS `cat ~/.graphify/providers.json` FIRST when diagnosing "semantics won't build"; never announce a missing-key story (GEMINI_API_KEY etc.) before reading it. Rewriting that file changes the user's environment — propose the edit and wait for approval.

## Pitfall 2b — do NOT brute-force the model list; ASK (FIRST CLASS)
When the intended model looks broken, the temptation is to loop over every model id found in the profile `config.yaml` (`SuperCombo_*`, `kr/*`, `qd/*`, `openrouter/*`, `freellmapi/*`) hunting for one that answers. This is WRONG and the user will hard-stop you: those ids belong to unrelated proxies/aggregators layered on top of the provider, not to the provider tier actually in use. Only a small named subset is ever in scope — here the `oc/` (OpenCode) models plus two Nous-portal ones. Also note 9router is the PROVIDER; the `9router-proxy/proxy.js` shims exist for other tools (OpenHands) and are irrelevant to graphify. If you do not have an explicit list, ASK before probing. One clarify call beats ten 100-second wasted requests.

Verified `oc/` results (2026-08, 9router at localhost:20128 — strict-JSON + Cyrillic probe):
`oc/nemotron-3-ultra-free` OK ~13s · `oc/deepseek-v4-flash-free` OK ~2s · `oc/laguna-s-2.1-free` OK ~4s · `oc/mimo-v2.5-free` empty `content` (all output in reasoning field) · `oc/ling-3.0-flash-free` upstream 404.

### Probing an OpenAI-compatible endpoint reliably
- `/v1/models` may hang or time out on a proxy while `/v1/chat/completions` works fine. A models-endpoint timeout is NOT evidence the backend is down — confirm with a real chat call before declaring anything dead.
- Responses come in three shapes: one JSON object, SSE (`data: {...}` lines), or SEVERAL concatenated JSON objects on one line. Handle all three (raw_decode loop + SSE branch) and accumulate `choices[0].message.content` or `.delta.content`.
- Empty `content` on a reasoning model = "no usable output", not a pass.

## Pitfall 2 — "update the setup file" means UPDATE, not CREATE
When the user says "update the setup file" / "обнови файл сетапа", they mean an EXISTING artifact whose path is already documented somewhere (skill, AGENTS.md, a prior script). Do NOT create a new file. First search existing files/skills for the documented setup-file path, then patch that file. Creating a new one (e.g. a second `graphify-setup.sh`) is the wrong move and the user will be annoyed.

## Pitfall 3 — probing a backend with Cyrillic via curl = false "Input garbled" (FIRST CLASS)
When you suspect a model "doesn't support Russian/Cyrillic", the model is almost never the problem — **curl in git-bash mangles UTF-8**, so the model receives `������` and replies "Input garbled / garbled text / resend clear text". This looks exactly like a model-language limitation and wastes time switching providers. Diagnose Cyrillic (and any non-ASCII) ONLY through Python with `ensure_ascii=False`:
```bash
python -c "import json,urllib.request; body=json.dumps({'model':'oc/nemotron-3-ultra-free','messages':[{'role':'user','content':'Извлеки JSON: платформа Telegram Mini App'}]},ensure_ascii=False).encode('utf-8'); req=urllib.request.Request('http://localhost:20128/v1/chat/completions',data=body,headers={'Authorization':'Bearer $API_9ROUTER_KEY','Content-Type':'application/json'}); print(urllib.request.urlopen(req,timeout=60).read().decode()[:300])"
```
If the Python probe gets a real answer, the backend/model works with Cyrillic — the earlier failure was curl's encoding, not the model. Only if the Python probe ALSO returns "Input garbled" is it genuinely the model/provider. Related: 9router may return CONCATENATED JSON objects (`Extra data: line N` errors) — parse sequentially via `json.JSONDecoder().raw_decode` in a loop, not `json.loads` on the whole body.

## Pitfall 4 — "reference" sections inside a setup doc can be stale
A setup guide may carry both a current backend section (headed by a "Дата обновления / updated" stamp) and an older example (e.g. a Cloudflare+llama block). When wiring providers.json / a config, always read the STAMPED-current section first; copying a visually-adjacent-but-older block reintroduces the wrong model. For 9router + nemotron the current reference is backend `oc/nemotron-3-ultra-free` (unlimited) — not the older Cloudflare llama block. Quick truth-check: query `providerConnections` and `usageHistory (model,status)` in `~/AppData/Roaming/9router/db/data.sqlite`.

## Pitfall 5 — a setup doc may describe the SAME tool twice
Large SETUP_GUIDE-style files accumulate duplicate sections (seen: `## 9. Graphify` AND
`## 20. Graphify`, both with their own exports, helper functions and AGENTS.md rules block).
Patching only the first leaves a contradictory second copy that future agents will read as
truth. Before calling a doc update done: `grep -n "<tool-or-helper-name>" SETUP_GUIDE.md`
and reconcile EVERY hit — including helper names inside fenced code blocks and the
"проверка"/checklist snippets far from the main section. Then mark ONE section as the single
source of truth and point the duplicate at it instead of maintaining two.

## Choosing the extraction model — benchmark, never trust one ping
A single short prompt ranks models wrong: reasoning models answer a trivial ping in ~2s and
the real task in ~40s. Benchmark on the ACTUAL job (extract a code graph as strict JSON,
`temperature=0`, >=5 runs) and rank by DELIVERY RATE first, graph richness second — a batch
run over a repo is ruined by intermittent failures, not by a slightly thinner graph.
Measured 2026-08 (5 runs each): `oc/deepseek-v4-flash-free` 5/5 delivery, ~9.5s, coverage
5/5 → CHOSEN as default. `oc/nemotron-3-ultra-free` only 2/5 (3 runs died at ~0.8s) though
richer when it answered → demoted to fallback `graphify-nemo`. `tencent/hy3:free` 4/5 but
~49.5s. Harness + method: references/model-benchmark-for-extraction.md.
Set `max_tokens` >= 8000 when benchmarking reasoning models: at 1200 the budget is consumed
by the reasoning phase, `content` comes back empty/None with `finish_reason=length`, and you
will wrongly score a good model as broken.

## Pitfall 6 — `--cluster` alone does NOT produce GRAPH_REPORT.md
`graphify-ds . --cluster --max-concurrency 1 --api-timeout 600` computes communities but
leaves them NUMBERED and writes no report. It ends with a hint that is easy to miss:
`next: run graphify cluster-only <path> to generate GRAPH_REPORT.md and name communities`.
Clustering is therefore TWO commands, not one:
```bash
graphify-ds . --cluster --max-concurrency 1 --api-timeout 600   # 1) communities
graphify cluster-only . --backend=openai \
         --model=oc/deepseek-v4-flash-free --max-concurrency=1  # 2) names + report
```
Only after step 2 do `GRAPH_REPORT.md` and `graph.html` appear. Verify with
`grep -E '^### Community' graphify-out/GRAPH_REPORT.md` — you want
`### Community 0 - "Auth Remote Data Source"`, not a bare number. Note the naming lives in
`.graphify_labels.json` (and the report); inside `graph.json` the `community` field stays an
INTEGER, so counting distinct `community` values in graph.json tells you nothing about
whether labeling ran.
Healthy result on ~100 Dart files: 732 nodes / 1049 edges / 82 communities, report ~19 KB,
`graph.html` ~630 KB, plus useful sections `God Nodes`, `Import Cycles`, `Surprising Connections`.

## Pitfall 7 — graphify does NOT write to Obsidian (user-facing confusion)
When the user asks "why don't I see the graphs in Obsidian?", the answer is that these are two
unrelated graphs and graphify never touches the vault:
- graphify → `<project>/graphify-out/graph.html` — graph of CODE, viewed in a browser.
- gbrain → `Documents/Obsidian-Profiles/<profile>/` — graph of NOTES, this is what Obsidian shows.
Do not promise Obsidian integration as an automatic side effect of a graphify run. Deliver the
code graph by pointing at `graph.html` (in the desktop app: `MEDIA:<abs path>`).

## Changing the default model — the FULL set of places to update
Switching graphify's model touches five files; miss one and the environment contradicts itself.
Checklist (verified 2026-08 on the deepseek switch):
1. `~/.graphify/providers.json` — `default_model` (back it up first).
2. `~/.bash_profile` — global `OPENAI_MODEL`.
3. `~/.bash_profile.d/graphify.sh` — add the new helper (`graphify-ds`); KEEP the old one as
   a named fallback rather than deleting it.
4. The setup guide — EVERY duplicate section (see Pitfall 5), including checklist snippets.
5. `AGENTS.md` at the repo root — the `ALWAYS use the <helper>` rule is injected into every
   agent's system prompt, so a stale helper name there silently overrides the whole switch.
Verify with `source ~/.bash_profile && echo $OPENAI_MODEL && type graphify-ds`. Env vars only
apply to NEW shells — already-open terminals keep the old value until re-sourced.

## Proving to the user that requests really happened (evidence, not narration)
This user verifies agent claims against independent sources and WILL ask "did you actually run
those tests? I don't see them in the 9router stats." Never answer by re-describing your own
actions — pull the router's own log:
```bash
python - <<'EOF'
import sqlite3,os
p=os.path.expanduser("~/AppData/Roaming/9router/db/data.sqlite")
con=sqlite3.connect("file:"+p+"?mode=ro",uri=True)   # read-only, never lock the live DB
for m,s,n in con.execute("""select model,status,count(*) from requestDetails
                            where timestamp >= '2026-08-06T19:30' group by model,status"""):
    print(m,s,n)
EOF
```
CRITICAL distinction, and the actual answer to "why is the dashboard empty":
- `requestDetails` — per-request log (timestamp, provider, model, status). Your calls land here.
- `usageHistory` — the aggregate that FEEDS THE DASHBOARD. Free `oc/*` OpenCode routes arrive
  with `connectionId=None` and `cost=0` and are NOT aggregated into it.
So an empty dashboard is NOT evidence the requests never happened — it is a blind spot in the
user's stats for the whole free-OpenCode route. Say that plainly; it is useful to them beyond
your own alibi. Confirm who owns the port before theorising: `netstat -ano | grep 20128`, then
`(Get-CimInstance Win32_Process -Filter 'ProcessId=<pid>').CommandLine` — on this machine 20128
is 9router's own `custom-server.js`, while `9router-proxy/proxy.js` serves OpenHands on 20129.

## Verifying the run actually used the LLM
`semantic extraction on N files via openai` in the run log is the proof that the semantic
layer built; its absence means you silently produced an AST-only graph. A healthy full run
on ~100 Dart files looks like: 737 nodes / 1068 edges, `graph.json` ~640 KB, est. cost ~$0.02.
A 4 KB `graph.json` is a stub, not a graph. Cross-check the provider actually received the
calls: `requestDetails` table in `~/AppData/Roaming/9router/db/data.sqlite`.

## Notes
- Graphs are isolated per project (`<project>/graphify-out/`). Each project "knows" only itself unless you run `graphify global add`.
- `graphify update .` is AST-only (no API cost) — safe to run after every code edit.
- Deep clustering (`--cluster`) is heavy/expensive; defer until a project has ~80+ code files. The cron reminder handles this.
- `which graphify-nemo` reports "not found" for shell functions — use `type graphify-nemo` to verify.

## Support files
- scripts/graphify-setup.sh — full idempotent setup (steps 1–6).
- scripts/graphify-cluster-check.sh — watchdog counting code files across /c/Projects/*, alerts when ≥80 and not yet clustered.
- references/cron-cluster-reminder.md — cronjob create/update incantation.
- references/monorepo-subfolder-graphs.md — how to build isolated graphs per subfolder in a monorepo (app/, marketplace/) while excluding foreign clones.
- references/model-benchmark-for-extraction.md — reusable harness + method for picking the extraction model on evidence (delivery rate first), plus endpoint quirks for 9router and the Nous portal.
- references/model-inventory-and-probing.md — WHICH models exist and where (9router `oc/*` vs Nous portal `stepfun/`,`tencent/`), how to read the Nous OAuth token, verified per-model results, the three-shape response parser, and the "ASK, don't enumerate" rule.
- references/verifying-provider-usage.md — prove a test actually hit the provider: 9router `requestDetails` (per-request log) vs `usageHistory` (dashboard feed; free `oc/*` routes have connectionId=NULL and are NOT aggregated), the empty-dashboard blind spot, `/v1/models` timeout quirk, Nous-portal model ids.
- scripts/probe-models.py — runnable benchmark harness: N runs per model on the real code-graph→strict-JSON job, ranks by delivery rate, handles all three response shapes and Cyrillic. Edit its MODELS list, run in the BACKGROUND (5×5 runs exceeds the 600s foreground cap).
