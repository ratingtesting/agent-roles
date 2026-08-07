# Catalog commands & context

## clawhub CLI command set (v0.23.1)
```bash
npm i -g clawhub
clawhub login --token clh_XXX        # OR write config.json (preferred, see SKILL.md)
clawhub whoami                       # verify token
clawhub skill publish . --slug <s> --name "<n>" --version <semver> \
  --categories "a,b,c" --topics "x,y,z"
clawhub inspect @owner/slug           # check visibility + moderation state
clawhub sync --source-repo owner/repo --bump patch   # re-sync from GitHub
```
Moderation states: `pending.publication` (hidden, scanning), `Moderate CLEAN` (visible), `hidden by moderation`.

## AgentSkills.io — why closed (CONTRIBUTING.md excerpt)
> "Skill submissions — We don't maintain a directory of community skills. This may change in the future."
> Also: reference library `skills-ref/` not accepting code contributions.
Only logo/ecosystem listings accepted. Do NOT submit a skill there.

## skills.sh — no submit path
- Issue vercel-labs/skills#880 "How to submit/publish a new skill?" — opened 2026-04-08, no resolution in thread.
- Docs say it auto-indexes public GitHub repos, but in practice keelwright (public, SKILL.md in root) was NOT found via search or direct URL `skills.sh/ratingtesting/keelwright` (404).
- Conclusion: don't count on skills.sh for launch drive-stars.

## askill.sh
- Form: https://askill.sh/submit — paste GitHub repo / tree / SKILL.md URL.
- Indexes SKILL.md in real time; slug from frontmatter `slug` → publishes to `@author/slug`.
- No CLI, no auth required to submit.

## GitHub CLI (gh skill)
- `gh skill publish` (preview since 2026-04-16, GitHub Changelog).
- Publishes from a repo following Agent Skills spec → skills.github.com ecosystem.
- Check `gh skill --help` for exact flags in your gh version.
