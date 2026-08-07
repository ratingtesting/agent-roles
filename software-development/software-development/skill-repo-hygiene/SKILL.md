---
name: skill-repo-hygiene
description: Before push to a user public repo, keep internal files out.
---

# skill-repo-hygiene

Discipline for publishing a skill/code project to a PUBLIC GitHub repo the user maintains.
Established after the user was furious that an internal publishing registry
(`PUBLISHING_REGISTRY.md`) was pushed to the public `keelwright` repo. The user is a
non-programmer founder — he says "commit and push X" meaning the deliverable, not the
whole working directory.

## When to load
- Before any `git add` / `commit` / `push` to a public repo the user owns.
- When the user says "push X" — verify X is publishable FIRST.
- When editing `.gitignore` for a skill repo.

## The split: published vs internal

**PUBLISH (shipped skill/content):**
- `SKILL.md`, `AGENTS.md`, `CLAUDE.md`, `llms.txt`
- `README.md`, `LICENSE`
- `references/` (patterns, bindings, provenance)
- `scripts/` (validated tooling)
- `templates/` (reusable prompts)
- `qa-results/` (machine-verified run data — NOT session notes)
- `assets/` (real diagrams referenced by README, e.g. `architecture.png`)
- `.gitignore` (the guard itself)

**NEVER PUBLISH (internal kitchen — local only):**
- Publishing registries / link trackers (`PUBLISHING_REGISTRY.md`)
- Article drafts (`*-article-*.md`, `*-draft*`, `huggingface-card.md`, `reddit-*-draft.md`)
- Generated cover/debug assets (`cover*.png`, `cover*.html`)
- Scraped site HTML for debugging (`habr_*.html`, `vcru_*.html`, `vcru_16.js`, `vcru_editor.js`)
- `internal/`, `backups/`, `*.log`, session notes, private test prompts

## Behaviors
1. User says "push X" and X is an internal artifact → STOP and confirm. Do not treat
   "push" as literal for internal files. Ask: "X is internal — push only, or keep local?"
2. Enforce via `.gitignore`: explicit `NEVER PUBLISH` section listing internal patterns,
   so `git add` physically cannot leak them.
3. Verify before claiming clean: `git status --porcelain --ignored` and
   `git check-ignore <internal files>` → all must report ignored.
4. Never `git add -A` — stage explicit paths (also per AGENTS.md). This is the secondary
   guard; `.gitignore` is the primary.

## Anti-patterns (real, from this user)
- Pushing `PUBLISHING_REGISTRY.md` (personal links + internal commands) → user:
  "нафига в гитхабе реестр ссылок? О чем ты думал?"
- Pushing article drafts / covers / scraped HTML as if they were skill content.
- Reading "commit and push" as "push everything in the working directory".

## keelwright example (exact file map)
Publishable: `SKILL.md`, `AGENTS.md`, `CLAUDE.md`, `README.md`, `LICENSE`, `llms.txt`,
`references/*`, `scripts/*`, `templates/*`, `qa-results/*`, `assets/architecture.png`,
`assets/architecture.html`, `assets/architecture.md`, `.gitignore`.

Internal (gitignored): `PUBLISHING_REGISTRY.md`, `habr-article-draft.md`,
`habr-article-human.md`, `medium-article-draft.md`, `devto-article-draft.md`,
`huggingface-card.md`, `reddit-chatgptcoding-draft.md`, `cover.html`, `cover.png`,
`cover_debug_*.png`, `habr_*.html`, `vcru_*.html`, `vcru_editor.js`, `internal/`.

## Stray file detection (before every commit)

Before `git add`, scan for files that don't belong in a public repo:

```bash
# Verify scripts, temp files, backups
git status --short | grep -iE "hermes-verify|\.bak$|__pycache__|\.pyc$"

# Local paths leaked into tracked files
git ls-files | while read f; do
  grep -l "/c/Users/Unicorn\|C:\\\\Users\\\\Unicorn" "$f" 2>/dev/null
done
```

Common offenders:
- `hermes-verify-*.py` — throwaway verification scripts that got committed accidentally
- `*_bak` / `*.bak` — backup files from sed/patch operations
- `__pycache__/` — Python bytecode (add to .gitignore)
- Local paths in `.py` / `.jsonl` files — hardcoded `C:\Users\<name>\...` in test data

Real case: `hermes-verify-sqlfix.py` was markdown saved as `.py`, shipped in 7 releases,
never compiled. A pre-commit `.py_compile` check would catch this class.

## Verification (ad-hoc, no suite)
After editing `.gitignore`, run (PowerShell on Windows, or `git status`|check-ignore in bash):
```
git check-ignore PUBLISHING_REGISTRY.md cover.png vcru_editor.js   # must all print
git check-ignore SKILL.md README.md architecture.png              # must all be silent
```
If any internal file is NOT ignored, the guard is broken — fix `.gitignore` before push.
