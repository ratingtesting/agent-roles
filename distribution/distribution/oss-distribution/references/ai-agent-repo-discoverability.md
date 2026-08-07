# AI-Agent Repo Discoverability Checklist

Making a GitHub repo findable and usable by AI coding agents (Claude Code, Copilot, Cursor, Gemini CLI, Codex, Jules). Validated 2026-07-30 on ratingtesting/flutter-clean-arch-unicorn (v1.3.1).

## Checklist (order matters — cheap wins first)

1. **GitHub topics** — agents and search rank on these. Add ~15-20 via one command:
   ```bash
   gh repo edit --add-topic flutter --add-topic clean-architecture --add-topic ai-agents --add-topic agents-md --add-topic llms-txt ...
   ```
   Include: tech stack, category (template/boilerplate/starter-kit), audience (startup/mvp), AND agent-standard markers (`ai-agents`, `agents-md`, `llms-txt`).
2. **Description** — `gh repo edit --description "..."` mentioning "AI-agent ready (AGENTS.md, llms.txt)" — agents grep descriptions.
3. **Template flag** — `gh repo edit --template` enables the "Use this template" button; template repos rank in template search.
4. **Agent config files** (each tool looks for its own entry point; keep AGENTS.md as single source of truth, others are thin pointers):
   - `AGENTS.md` — full guide (agents.md standard, cross-tool)
   - `llms.txt` — machine-readable summary (llmstxt.org standard)
   - `CLAUDE.md`, `GEMINI.md` — root, ~10 lines: "read AGENTS.md" + quick facts
   - `.github/copilot-instructions.md` — Copilot
   - `.cursor/rules/project.mdc` — Cursor; MUST have YAML frontmatter: `description`, `globs`, `alwaysApply: true`. Verify frontmatter parses (`yaml.safe_load`).
5. **README "AI-Agent Ready" section** — table listing all agent files with links + one-line "point any agent at this repo" pitch. Humans forking for agent workflows scan for this.
6. **Release** — tag + `gh release create vX.Y.Z --latest` (per house rule: tag alone is not enough).

## Verification
- `gh repo view --json isTemplate,repositoryTopics` — confirm flags landed. NOTE: `repositoryTopics` is `null` (not `[]`) when empty — `-q` iteration over it errors.
- Browser-check the live repo page (Пётр требует визуальную верификацию, не только API).
- Run the project's test suite after any repo changes, even doc-only, before claiming done.

## Content principles for agent files
- Thin pointers, single source of truth (AGENTS.md). Duplicate only 5-7 "quick facts": architecture rule, test command, secrets policy.
- llms.txt: stack table, features, links, "use this when" section — written for retrieval, not marketing.
