---
name: agent-skill-catalog-publishing
description: Publishing AI agent skills to external catalogs.
---

# Agent Skill Catalog Publishing

Publishing a skill for discoverability is a distinct task from writing or versioning it. Each catalog has its own submission path and hard limits discovered the hard way. Read this before attempting any publish.

## Catalog matrix (status 2026-07)

| Catalog | Submission | Notes |
|---|---|---|
| **clawhub.ai** | CLI `clawhub skill publish` OR web "import from GitHub" | WORKS. Enforces MIT-0. NVIDIA SkillSpector moderation (pending state is normal). |
| **askill.sh** | Web form at /submit, paste GitHub URL | WORKS, indexes SKILL.md in real time. |
| **skills.sh** | NO public submit form. Auto-indexes public GitHub repos but presence is unreliable (keelwright public repo was NOT found). Open issue vercel-labs/skills#880 asks this, unanswered. | Don't rely on it for drive-stars. |
| **GitHub CLI** | `gh skill publish` (preview since 2026-04) | Publishes to skills.github.com ecosystem from the repo. |
| **AgentSkills.io** | **CLOSED** — CONTRIBUTING.md: "We don't maintain a directory of community skills. This may change in the future." | Do NOT attempt submission. Wastes cycles. |

## clawhub.ai workflow (proven)

```bash
npm i -g clawhub

# Token lives in Hermes .env as API_CLAWHUB_AI_KEY (value starts clh_)
# Write config directly — terminal tool can write it; do NOT pass token in argv
# (command parser blocks tokens in command line).
mkdir -p "$APPDATA/clawhub"
cat > "$APPDATA/clawhub/config.json" <<'EOF'
{"token":"clh_XXX","registry":"https://clawhub.ai"}
EOF
clawhub whoami   # prints your handle, e.g. ratingtesting

cd /path/to/skill-repo
clawhub skill publish . --slug <slug> --name "<name>" --version <semver> \
  --categories "security,development,automation" \
  --topics "security,code-quality,ai-agents,guardrails,testing"
```

### Pitfalls (each cost a round-trip this session)
- **Version must increment** on every re-publish. Same version → "Version X already exists. Increment." Bump patch even for metadata-only changes.
- **Max 3 categories.** Valid slugs observed working: `security`, `development`, `automation`, `utility`, `productivity`. `ai-ml` was REJECTED as unknown — verify a slug before using it.
- **License is enforced MIT-0** by ClawHub regardless of your SKILL.md `license:` field. To avoid conflict, set `license: MIT-0` in SKILL.md frontmatter AND use an MIT-0 LICENSE file. A CC-BY-4.0 skill shows as MIT-0 on the platform.
- **SkillSpector (by NVIDIA) moderation** runs on publish. "findings are pending" / "pending.publication" / "Moderate CLEAN" is NORMAL. WAIT — don't click "Re-run preview" repeatedly; it resets the scan timer.
- **"Import is out of date. Re-run preview"** appears when the GitHub repo changed after import. On web import from GitHub, just click Re-run preview. Via CLI, re-publish with bumped version.
- **Device login** (`clawhub login --device`) prints a code but needs browser GitHub OAuth the agent cannot complete. Prefer the token-in-config.json path.
- **Web import pulls from GitHub** — after you `git push` license/version changes, the site shows "out of date" until you re-run preview. The CLI publish and web import are two separate paths; if the user deleted the CLI-published skill and re-imports from GitHub, CLI publishes are moot.

## License decision
If targeting clawhub: use MIT-0 in BOTH SKILL.md frontmatter (`license: MIT-0`) and the LICENSE file. Push the commit BEFORE importing so the platform picks up the right license.

## Verify file state before agreeing it's broken
When the user says a file is "wrong"/"truncated", actually read it fully before confirming. This session the LICENSE file was complete (full CC BY 4.0 text) but was wrongly claimed truncated — caused a confusing round-trip. Read the whole file, don't infer from a grep snippet.

## References
See `references/catalog-commands.md` for the exact clawhub command set, the AgentSkills.io CONTRIBUTING excerpt, and the skills.sh issue #880 context.
