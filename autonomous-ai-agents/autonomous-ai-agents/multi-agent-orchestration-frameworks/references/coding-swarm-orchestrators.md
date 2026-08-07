# Coding-Agent Swarm Orchestrators (category B)

Tools that give you a **working swarm that writes code**, GUI out of the box — as opposed to
framework-libraries (CrewAI/Langflow/etc.) that you assemble into a product. Use these when the
user wants to *vibe-code with a swarm now*, not build an orchestration product from parts.

Licenses verified from GitHub LICENSE files, 2026. All permissive — license is NOT the deciding
factor here; **architectural ability to grow into a reusable engine is.**

| Tool | ⭐ approx | License | GUI | Category | Grows into engine/product? |
|---|---|---|---|---|---|
| **OpenHands** (ex-OpenDevin) | ~82k | **MIT** | Web UI (Agent Canvas) | Self-contained agent platform with internal multi-agent orchestration | ✅ **Only one that spans all: build-with → motor → product.** Has multi-agent orchestration built-in: `delegate_tool` (spawns sub-agents), `micro-agents` (specialized sub-agents for different skills), `task_set_tool` (manage task sets across agents). Tiny core (Agent emits Actions, Conversation runs loop + append-only EventLog, Workspace executes, LLM via LiteLLM); Python SDK IS the reusable motor, GUI is a separable layer. |
| **Vibe Kanban** (BloopAI) | ~38k | **Apache-2.0** | Kanban dashboard | Dirigent over *external* CLI agents (Claude Code, Codex, Gemini CLI, OpenCode) | ❌ Thin conductor, no own engine. Great for step-0 UX, cannot become a reusable motor. Now **community-maintained** (BloopAI stepped back) |
| **MetaGPT** | ~65k | **MIT** | CLI + web (MGX) | "AI software company" (PM/architect/engineer roles + SOPs) | Concept = the step-2 product (roles pre-built), but weak day-to-day vibe-coding (one-shot generation, code often not runnable) |
| **ChatDev** (OpenBMB) | ~33k | **Apache-2.0** (whole stack, no paid tier) | Web Visualizer | "Virtual software company" (CEO/CTO/programmer/tester) | Research/demo flavor; weak as a working tool |

## Picking between the top two

- **Swarm should drive external agents you already have (Claude Code / OpenCode / Codex)** → Vibe Kanban. You conduct by mouse on a board. Recognize it is a consumable, not a foundation.
- **Want ONE tool that carries you build-with → engine → product** → OpenHands. Its Python SDK is the motor; UI is a separate layer over the same core.

## OpenHands without Docker (verified from docs.openhands.dev, 2026)

Docker is the DEFAULT sandbox, not a hard requirement. Runtime is pluggable. Non-Docker options:

- **Agent Canvas (new Web UI)** — install via `npm install -g @openhands/agent-canvas` (NOT `agent-canvas` — that's a different product). Requires **Bun** runtime. On old CPUs (pre-AVX2, e.g. Xeon E5 v3), use the **baseline** Bun build: `bun-windows-x64-baseline.zip` from GitHub releases. Run `agent-canvas` to start the full stack (frontend+backend) on localhost. Split mode: `--frontend-only` / `--backend-only` on separate ports.
- **Process / Local Runtime** — agent server runs directly on host as a normal process.
  `export RUNTIME=process` (legacy alias `RUNTIME=local`). **Zero isolation**: the agent can
  read/write any file the user account can, and run any host command. Acceptable only in a
  controlled solo environment; state it as a conscious risk (a swarm can touch anything).
- **Remote Runtime** — containers run on remote infra, not the local machine (needs a server).
- **Python SDK** — thin core; docker pulled in only if you ask. Best fit for step 1–2 (motor).

Install (isolated, no Docker):
- Requires **Python 3.12+** (uv will fetch it: `--python 3.12`). PyPI package name: `openhands`.
- `uv tool install openhands --python 3.12`  (isolated uv-tool env), OR explicit venv:
  `uv venv .venv --python 3.12 && uv pip install --python .venv/Scripts/python.exe openhands`.
- **Windows caveat**: official docs say run inside WSL (Ubuntu). Bare-Windows-no-WSL-no-Docker
  is possible via Local runtime + a maintainer gist (neubig), but it's an unofficial path;
  expect Windows-path / shell friction in the local runtime. Smoke-test small before full rollout.

## Verification approach for a swarm tool

Before a full install: run a minimal CLI/headless smoke test — does it launch, see the local
provider (LiteLLM, `openai/` prefix for OpenAI-compatible endpoints), and complete one trivial
task with `RUNTIME=process` (no Docker). If Windows path/shell specifics break the local runtime,
you see it on the small test, not after full setup.
