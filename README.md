# 🎭 Agent Roles

A library of production-ready role definitions for AI agents — reusable personas, skill templates, and agent configurations you can drop into your own agent systems.

![License: MIT-0](https://img.shields.io/badge/License-MIT-0-blue.svg)
![Agents](https://img.shields.io/badge/agents-282-green.svg)
![Format](https://img.shields.io/badge/format-Hermmes%20Skills-orange.svg)

## What's inside

- **282 role definitions** — specialists for engineering, design, marketing, sales, security, data, strategy, and regional markets.
- **Agent configurations** — ready-to-run configs for multi-agent orchestration, swarm runners, and independent agency-style agents.
- **Skill authoring template** — a 6-slot structure for defining your own agent roles with consistent semantics.

## Why this exists

When you build with AI agents, you spend a lot of time reinventing the same kind of persona: "you are an SEO specialist", "you are a code reviewer", "you are a UX researcher". This repo collects those roles in one place so you can copy, adapt, and compose them instead of writing them from scratch.

## License

MIT-0 — free to use, modify, and redistribute, including commercially, with **no attribution required**. Clean-room rewrite of [agency-agents](https://github.com/AgentLand/agency-agents) (MIT, AgentLand Contributors) into the Hermes skill format.

## Web safety requirements

Every agent that browses the web (`web_search` / `web_extract` / `browser` / `fetch_url` / `vision_analyze`) must use two protection layers:

1. **injection-guard** — Hermes plugin (hook `transform_tool_result`), DeBERTa classifier on web tool input. Author: gweber, MIT.
2. **agent-defense** — Hermes skill (scastile, MIT), layered defense (memory, egress, anti-cloaking).

Both are listed in `related_skills` of every agent and in the `agentic-skill-authoring` template.

### ⚠️ Critical: injection-guard plugin requires dependencies

Without dependencies the plugin is a **silent no-op** — web content is NOT scanned, and you think you're protected when you're not. This is a real problem on a clean machine.

Install in the Hermes venv (where `hermes-agent` runs):

```bash
<venv>/Scripts/python -m pip install "transformers>=4.40" torch sentencepiece
```

Then **restart the gateway**:

```bash
hermes gateway restart
```

Verify the classifier loads: in the gateway log on the first web request, there should be NO message `injection-guard: 'transformers' not installed — the hook is a no-op`.

## Usage

Each role lives in its own directory and is a self-contained Hermes skill. Copy any role folder into your own skills directory and adapt it to your agent.

Each role also has a generated avatar in `avatars/<role>.svg`.

## Author

[ratingtesting](https://github.com/ratingtesting)

---

*Last updated: 2026-08-31*
