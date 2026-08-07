# OpenClaw → Hermes Migration Audit

Generated 2026-07-12. Full audit of all referenced repositories, their purpose, and Hermes adaptation status.

| # | Repository | Purpose | Hermes Adaptation | Status |
|---|---|---|---|---|
| 1 | `github.com/obra/superpowers` (252k ⭐) | 14 process skills (brainstorming, writing-plans, TDD, debugging, review, subagent-driven-dev...) | 14/14 installed. 8 via URL, 3 manually (DANGEROUS-blocked bypass), 3 bundled. All `superpowers:X → skill_view(name='X')` patched | ✅ |
| 2 | `github.com/nousresearch/hermes-agent` | Agent framework | Base platform. SOUL.md, AGENTS.md, TOOLS.md, SETUP_GUIDE.md, profiles, memory. 67 bundled skills | ✅ |
| 3 | `clawhub.ai/lanyasheng/execution-loop` | Ralph + Doubt + Drift + Task Completion + Triage | Custom execution-loop skill v2.1.0 — 5 layers unified system | ✅ |
| 4 | `clawhub.ai/rocketship4545-a11y/match-loop` | Generator ↔ Visual Analyst vibe-coding loop | Layer 5 in execution-loop | ✅ |
| 5 | `clawhub.ai/leostehlik/autoresearch-loop` | Bounded modify-verify-decide + escalation + lessons | Layer 3b in execution-loop | ✅ |
| 6 | `clawhub.ai/zhaobod1/huo15-autoresearch-loop` | Karpathy Modify→Verify→Keep/Discard→Repeat | Layer 3b (merged with leostehlik) | ✅ |
| 7 | 7 PowerShell loop scripts (ralph-init, ralph-cancel, ralph-stop-hook, doubt-gate, task-completion, drift-reanchor, auto-loop) | OpenClaw Windows adaptation of Ralph hooks | Not portable (Hermes = bash). Concepts → `/goal`, `todo`, `cronjob`, `notify_on_complete`. Ralph Mode skill replaces them | ❌ (replaced) |
| 8 | `github.com/Graphify-Labs/graphify` (82k ⭐) | Knowledge graph from codebase (tree-sitter AST, communities, query/path/explain) | `uv tool install graphifyy`. `graphify install --platform hermes`. providers.json → `freellmapi/llama-3.3-70b` (Groq). `/graphify .` in agent | ✅ |
| 9 | `github.com/msitarzewski/agency-agents` | Markdown persona agents (PM, Growth, Architect, DB Optimizer...) | Cloned to `C:\Projects\lazy-unicorn\agency-agents\`. Used as `context` for `delegate_task` | ✅ |
| 10 | `github.com/garrytan/gbrain` | Semantic memory (RAG, embeddings, FlashRank) | Described in TOOLS.md. Install deferred — user will set up separately | 📋 Pending |
| 11 | `github.com/decolua/9router` | Free model router (localhost:20128) | `custom:9router` provider in config.yaml. Models: supercombo (main), kr/glm-5, nvidia/deepseek-v4-flash | ✅ |
| 12 | `github.com/tashfeenahmed/freellmapi` | Local embedding router (port 31415) | `custom:freellmapi` provider. Also Graphify backend via providers.json | ✅ |
| 13 | `github.com/PrithivirajDamodaran/FlashRank` | Local CPU reranker (port 8000) | Python service, autostart via registry. For gbrain reranking | ✅ |
| 14 | `agentrouter.org` | Paid models (Claude Opus 4.8, GPT-5.5, GLM-5.2) | 2 providers: `custom:agentrouter-openai` + `custom:agentrouter-claude` | ✅ |
| 15 | `github.com/vercel-labs/agent-browser` | CLI browser on Rust (npm global) | Not used — Hermes browser toolset native. npm global preserved | n/a |
| 16 | `kilo.ai` / `@kilocode/cli` | Kilo Code CLI — vibe coding agent | `npm -g @kilocode/cli`. Invoke via `terminal(background=true, pty=true)` | ✅ |
| 17 | `npm:@guava-parity/guard-scanner` | Security MCP server (35 categories) | Deferred (Security Layer = last) | 🔄 Deferred |
| 18 | `clawhub.ai/yoder-bawt/yoder-skill-auditor` | Skill audit with trust score (0-100) | Deferred (Security Layer) | 🔄 Deferred |
| 19 | `clawhub.ai/seojoonkim/prompt-guard` | DLP + runtime protection (650+ patterns) | Deferred (Security Layer) | 🔄 Deferred |
| 20 | `clawhub.ai/nerua1/nerua1-vibe-safe` | CVE dependency scan (5 phases) | Deferred (Security Layer) | 🔄 Deferred |
| 21 | `clawhub.ai/halthelobster/proactive-agent` | WAL, Memory Protocol | Deferred — discuss later | 🧠 Later |
| 22 | `clawhub.ai/pskoett/self-improving-agent` | `.learnings/` capture, error patterns | Deferred — discuss later | 🧠 Later |
| 23 | `clawhub.ai/arminnaimi/agent-team-orchestration` | Multi-agent teams, roles, handoffs | Deferred — delegate_task already covers multi-agent | 🧠 Later |
| 24 | `clawhub.ai/paudyyin/coding-framework` | Ponytail + 7 review agents | Deferred (Security Layer) | 🔄 Deferred |
| 25 | `clawhub.ai/nathansebhastian/kilocli-coding-agent` | Kilo CLI usage instructions for agent | Not needed — Hermes has `terminal(background=true, pty=true)` + `process` | ❌ (covered) |
| 26 | `clawhub.ai/adboio/agentmail` | Email agent | Deferred — user said "later" | 🧠 Later |
| 27 | `supabase.com` | Backend (PostgreSQL, Auth, Storage) | MCP: `supabase-app` + `supabase-marketplace` via header auth (service_role_key from .env). `hermes config set mcp_servers.supabase-{app,marketplace}` | ✅ |
| 28 | `flutter.dev` | Flutter SDK | Installed (`C:\dev\tools\flutter`). Clean Architecture + feature-first in AGENTS.md | ✅ |
| 29 | `obsidian.md` | Notes (PARA vaults) | Hermes bundled `obsidian` skill. Vaults isolated per profile | 📋 Pending setup |
