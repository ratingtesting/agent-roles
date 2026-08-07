---
name: multi-agent-orchestration-frameworks
description: Select and set up multi-agent orchestration frameworks (CrewAI, Langflow, AutoGen/AG2, Flowise, LangGraph) to build agent teams / "AI companies" on local OpenAI-compatible providers. Covers framework/license selection, CrewAI setup recipe, and engine-agnostic adapter architecture for productized agent systems.
---

# Multi-Agent Orchestration Frameworks

Choosing and standing up a framework to run **teams of agents** (roles, departments, handoffs) — distinct from Hermes's own `delegate_task` (see `dispatching-parallel-agents`) and from delegating to CLI coding agents (see `claude-code`, `codex`, `opencode`). Use this when the user wants a persistent, structured agent org — an "AI company", a role-based crew, a sellable agent-team product — rather than a one-shot fan-out.

## Two distinct product categories — do not conflate them

There are TWO different things people mean by "agent orchestration", and the wrong one wastes days:

- **A) Framework-libraries** (CrewAI, Langflow, AutoGen, LangGraph, Flowise): you *build* an agent org in code/mouse. A motor with no working product until you assemble it. Covered by the table below.
- **B) Coding-agent swarm orchestrators** (Vibe Kanban, OpenHands, MetaGPT, ChatDev, agent-kanban): a working *swarm that writes code for you right now*, GUI out of the box. You use these to vibe-code, not to build a product on top of. See `references/coding-swarm-orchestrators.md`.

Note on OpenHands: it belongs to category B BUT also has internal multi-agent orchestration — `delegate_tool` for dynamic sub-agent spawning, `micro-agents` for specialized skill agents, `task_set_tool` for cross-agent task management. It is NOT just a "single coding agent" — it can orchestrate a swarm internally. This makes it the most versatile: category-B swarm AND internal orchestration AND Python SDK for custom engines.

"I want a swarm that can write things for me, with an interface, out of the box, free" = category B, NOT CrewAI. CrewAI is a library with no GUI. Match the category to the user's actual sentence before recommending.

## Decision flow

1. **Is it a one-shot parallel fan-out inside Hermes?** → use `delegate_task` / `dispatching-parallel-agents`, not a framework.
2. **Does it need to outlive the chat session (durable)?** → `delegate_task` is NOT durable (dies when parent session closes). Use `cronjob` workers OR a standalone framework.
3. **Want a working code-writing swarm NOW, with a GUI, to build things with?** → category B. Vibe Kanban (dirigates external CLI agents) or OpenHands (self-contained, has motor+runtime+UI, only one that spans build-with → engine → product). See references file.
4. **Fixed org chart, built by mouse?** → Langflow (visual, MIT).
5. **Role-based crew / dynamic hiring / code-first?** → CrewAI (MIT).
6. **Selling templates / white-label / universal layer?** → keep the template format engine-agnostic (see Adapter architecture below); never adopt a framework's native format as your product format.

## Framework landscape (2026) + licenses

Verify licenses from the GitHub LICENSE file before committing — they change. As checked 2026:

| Framework | License | No-Docker install | Mouse/no-code UI | Sell/white-label |
|---|---|---|---|---|
| **CrewAI** | MIT | `pip install crewai` | ❌ (Studio is paid) | ✅ clean |
| **Langflow** | MIT | `pip install langflow` → `langflow run` | ✅ node editor | ✅ clean |
| **Flowise** | Apache-2.0 core + **Commercial** `/enterprise` (RBAC, SSO, multi-tenant) | `npm -g flowise` | ✅ AgentFlow | ⚠️ multi-tenant/RBAC are paid — trap for "universal layer" products |
| **LangGraph** | MIT | pip (steep) | Studio + LangSmith (paid observ.) | ✅ core clean |
| **AutoGen / AG2** | MIT | `pip install autogenstudio` | ✅ Studio | ⚠️ AutoGen in maintenance mode, merged into MS Agent Framework |

For **category B** (working code-writing swarms with GUI — OpenHands, Vibe Kanban, MetaGPT, ChatDev), including OpenHands's no-Docker runtime options, see `references/coding-swarm-orchestrators.md`. For the outcome of a bare-Windows (no-WSL no-Docker) install attempt of OpenHands v1.16.0, see `references/openhands-windows-install-2026.md`.

Key traps:
- **Flowise open-core**: the exact features a "universal agent-company layer" needs (multi-tenant, RBAC) are the paid ones. Avoid as product foundation.
- **CrewAI "company" mapping is 1:1**: `role` + `goal` + `backstory` = an employee. Fastest idea→running crew.
- **Langflow graph is static**: you draw the org chart by hand; no dynamic "hire an agent on the fly". Hierarchy is built via the *agent-as-tool* pattern (wrap sub-agents as Tools given to a manager agent). CrewAI supports dynamic delegation natively.

## CrewAI on a local OpenAI-compatible provider (working recipe)

Verified against a local router (9router, localhost:20128) serving OpenAI-compatible models.

```python
import os
from crewai import Agent, Task, Crew, Process, LLM

# CrewAI uses LiteLLM. For any OpenAI-compatible endpoint the model name
# MUST carry the openai/ prefix, or LiteLLM won't route it.
llm = LLM(
    model="openai/<MODEL_ID>",          # e.g. openai/SuperCombo_256k_100
    base_url="http://localhost:20128/v1",
    api_key=os.getenv("PROVIDER_KEY", "sk-noauth"),  # local routers often ignore the key
)

analyst = Agent(role="Product Analyst", goal="...", backstory="...", llm=llm, verbose=False)
writer  = Agent(role="Tech Writer",     goal="...", backstory="...", llm=llm, verbose=False)

t1 = Task(description="...", expected_output="...", agent=analyst)
t2 = Task(description="...", expected_output="...", agent=writer, context=[t1])  # handoff

crew = Crew(agents=[analyst, writer], tasks=[t1, t2], process=Process.sequential, verbose=False)
result = crew.kickoff()
```

Install isolated (avoids contaminating the Hermes venv):
```bash
uv venv .venv --python 3.11
uv pip install --python .venv/Scripts/python.exe crewai   # Windows path shown
```

## Engine-agnostic adapter architecture (for sellable agent systems)

When the goal is a **product** — selling company templates / trained companies / a layer that plugs into any agent system — do NOT let the orchestration engine's native format become the product format. That is vendor lock-in wearing a different hat.

```
Company Schema (YAML/JSON) = the IP, portable, engine-independent
    company → departments → roles(agents) → tools → tasks → handoffs
        │
        ▼
   ADAPTER  (thin layer: load(schema) → run() → observe())
        │
        ▼
   Swappable engine:  Adapter→CrewAI | Adapter→Langflow | Adapter→Hermes | Adapter→any
```

Sequence for a product build: **Schema first → Adapter → real crew**. Starting with the schema keeps every later line of code behind the adapter boundary. Start on CrewAI (MIT, dynamic, clean license); add Langflow later as a *visual adapter* (it imports/exports flow JSON) so the org chart can be edited by mouse without becoming the canonical format.

Durable state for a running "company": use the user's existing DB (e.g. Supabase Postgres) as the checkpoint store, and its realtime channel to drive a live dashboard. This fixes CrewAI's main weakness (persistence needs bolt-on infra) with infrastructure the user already runs.

## Pitfalls

- **LiteLLM routing**: OpenAI-compatible endpoints need the `openai/` model prefix in CrewAI `LLM(model=...)`. Without it, routing fails.
- **CrewAI telemetry prompt hangs non-TTY runs**: first run shows an interactive "view execution traces? [y/N]" prompt that blocks scripted/CI runs until timeout. Set `CREWAI_TRACING_ENABLED=false` (env or `.env`) to disable, and for a product-on-sale disable it explicitly for privacy.
- **git-bash `$TEMP` resolves to a non-existent `C:\tmp`**: heredocs (`cat > "$TEMP/x.py"`) silently write nothing, then the run fails "No such file". For temp scripts on Windows git-bash, write to an explicit `%LOCALAPPDATA%\Temp\...` path (use the write_file tool), not `$TEMP`.
- **`delegate_task` is not durable and caps at 3 concurrent, depth 1**: for a true long-lived swarm (>3 workers, survives session close) use cronjob workers or a standalone framework — not `delegate_task`.
- **Verify license from the LICENSE file, not blog posts**: open-core projects (Flowise) advertise "open source" but gate the enterprise features. Read `github.com/<repo>/blob/main/LICENSE`.
- **Verify a new crew with an ad-hoc probe, not a suite**: a brand-new orchestration project has no canonical test/lint/build. Write a minimal 1-agent crew to a temp script, assert a non-empty non-error `kickoff()` result, report it explicitly as ad-hoc verification, then clean up. Don't re-run a passing LLM crew just to satisfy a stale unverified flag — that only burns tokens.
- **Do NOT install/act before the selection discussion is closed** (workflow correction, stated firmly by the user): when the user is comparing options or still adapting one item from a migration list, stay on THAT task. Finish the compare/decide loop and get an explicit "go" before running installs or scaffolding. Jumping ahead to "let me just set it up" — especially skipping to step 1/2 while the user is still on step 0 — reads as not listening and forces a rollback. Comparison/landscape questions warrant analysis + a decision prompt, not action.
- **Separate the user's "steps" and honor which one they're on**: users staging a big migration often think in phases (e.g. step 0 = get a working swarm to build with; step 1 = engine/motor behind an adapter; step 2 = sellable product). Different phases have different constraints (step 0: GUI + free, lock-in OK; step 2: permissive license mandatory). Confirm which step you're serving before optimizing for another step's constraints.
- **OpenHands CLI in a non-TTY shell (Hermes `terminal`, CI) hangs**: v1.16.0's `openhands.exe --version` / interactive TUI crashes deep in the Textual import stack; Rich detects a non-interactive terminal and blocks. Use `--headless` (no TUI chrome) or smoke-test via the **Python SDK directly** (`from openhands.sdk import LLM, Agent, Conversation, LocalRuntime` in `execute_code`) when you cannot give the process a real TTY.
- **OpenHands headless: use env-override, do NOT hand-write `settings.json`**: the settings file is `~/.openhands/agent_settings.json` (NOT `settings.json` — a wrong name is silently ignored and the CLI keeps saying "Headless mode requires existing settings"). For a smoke test, skip the file entirely: `--override-with-envs` + env vars `LLM_MODEL` / `LLM_API_KEY` / `LLM_BASE_URL` + `RUNTIME=process`. Only `openhands serve` requires Docker; `web`, `--headless`, and the SDK run without it. Full reproduction and the Docker-availability wall in `references/openhands-windows-install-2026.md`.
- **"Replace Docker with X" on Windows usually does not work**: `wslc`, Podman, Rancher Desktop, OrbStack all ultimately need Hyper-V / WSL2 / paravirtualization. They repackage the requirement, they do not bypass "no nested virtualization". Verify the underlying virtualization requirement first; then either enable paravirtualization in BIOS/host, or pivot to a genuinely no-Docker tool (OpenHands `RUNTIME=process`, Vibe Kanban + external CLI agents).
- **Agent Canvas (`@openhands/agent-canvas`): the correct OpenHands UI.** The npm package `agent-canvas` (v0.1.x) is an unrelated tool for Claude Code canvases — NOT the OpenHands web UI. Install `npm install -g @openhands/agent-canvas` to get the OpenHands browser interface. Start: `agent-canvas` opens full stack (frontend + backend) on localhost; `agent-canvas --frontend-only` / `--backend-only` for split mode.\n- **Agent Canvas requires Bun. On old CPUs (Xeon E5 v3, pre-Skylake), use the baseline build.** The regular Bun binary crashes with `Illegal instruction` on CPUs without AVX2 (Xeon E5-2696 v3 and similar). Download `bun-windows-x64-baseline.zip` from GitHub releases instead of the default. Install: extract to `~\.bun\bin\`, add to PATH. Verify with `bun --version`. The baseline build is slightly slower but works on any x86-64 CPU.
- **Hermes-agent venv contaminates isolated venvs via `PYTHONPATH`**: `openhands.exe` raised `ModuleNotFoundError: No module named 'pydantic_core._pydantic_core'` because it pulled an incompatible pydantic from the hermes-agent venv. Prefix any python call from an isolated tool venv with `PYTHONPATH=` (empty) — this stops the leak. Same trick works for CrewAI, OpenHands, SkillSpector, and any tool installed via `uv pip` while Hermes's own venv sits on the machine.

## OpenHands / LiteLLM provider-prefix mapping (9router / local routers)

**Symptom:** `litellm.BadRequestError: LLM Provider NOT provided. You passed model=/oc/...` or `model=openai/oc/...`.
**Cause:** OpenHands uses LiteLLM internally. LiteLLM **preserves** the `provider/` prefix when routing to a custom `api_base`. It does not rewrite `openai/oc/...` to `oc/...`. So the final outbound model name must be acceptable to the upstream router.
**9router behavior:** 9router expects the **real provider prefix**, e.g. `oc/deepseek-v4-flash-free`. It does not know a virtual `openai/` provider unless one is configured there.

### Verified solutions (pick one)

**A. Model Canonical Name (preferred, no extra process)**
- Field: **Custom Model** → `openai/oc/deepseek-v4-flash-free` (LiteLLM accepts this)
- Field: **Model Canonical Name** → `oc/deepseek-v4-flash-free` (OpenHands uses this internally)
- Field: **Base URL** → `http://localhost:20128/v1` (direct to 9router)

**B. Prefix-stripping proxy on a separate port**
- A ready-to-run example: `templates/9router-liteLLM-prefix-proxy.js`
- Run: `node <skill-templates-dir>/9router-liteLLM-prefix-proxy.js`
- Base URL → `http://localhost:20129/v1`
- Model → `openai/oc/deepseek-v4-flash-free` (or `openai/<anything>`)
- Proxy removes leading `openai/` before forwarding to 9router on `20128`

### Cross-check before claiming success
1. Check model discovery endpoint: `GET http://localhost:20128/v1/models`
2. Do a manual completion test with the literal model string you configured in UI.
3. If LiteLLM returns `LLM Provider NOT provided`, you have a prefix-mapping problem — not an auth problem.

## Windows-specific OpenHands runbook

- `NODE_OPTIONS` is **silently ignored** by Electron packaged apps. Do not rely on it inside Agent Canvas.
- Agent Canvas Desktop is an Electron window. `browser_navigate` to `http://localhost:8000` returns `ERR_CONNECTION_REFUSED` even when the process is running; the UI must be operated through its own window, not Hermes browser.
- Agent Canvas crash log: check `/tmp/agent-canvas.log` via `tail`. If the port-check phase completes but no ports open and the process disappears, capture full log before assuming it is "just slow".
