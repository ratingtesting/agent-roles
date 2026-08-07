# Catalog publishing — quick reference

## AgentSkills.io
- Status: closed to skill submissions.
- Evidence: `CONTRIBUTING.md` → `Skill submissions — We don't maintain a directory of community skills.`
- Action: do not open PRs/Issues there for catalog listing.

## skills.sh
- Status: unclear / no manual submit form documented.
- Evidence: docs only describe `npx skills add owner/repo`; the API requires Vercel OIDC (`Authorization: Bearer <VERCEL_OIDC_TOKEN>`). No public `POST /skills` submit endpoint.
- Fallback: open vercel-labs/skills issue for clarification; meanwhile try askill.sh.

## askill.sh
- Status: open submit form.
- URL: https://askill.sh/submit
- Input: GitHub repo URL, directory URL, or direct SKILL.md URL.
- Auth: optional GitHub login for canonical `@author/slug`.
- Use when: repo has a valid top-level `SKILL.md` with frontmatter `name`/`description`.

## clawhub.ai
- Status: open publish via CLI.
- Prereq: `npm i -g clawhub`, GitHub account old enough to pass upload gate.
- Auth flows:
  - interactive: `clawhub login`
  - device/headless: `clawhub login --device` → code at `https://clawhub.ai/cli/device`
  - token: `clawhub login --token clh_...` or env `API_CLAWHUB_AI_KEY` in Hermes `.env`
- Publish skill: `clawhub skill publish <path> --name "..." --slug ... --version 1.0.0`
- Config: `%APPDATA%\clawhub\config.json`
- Network caveat on Windows DESKTOP: passing secret values inline may be blocked; export to temp env or run interactively.
