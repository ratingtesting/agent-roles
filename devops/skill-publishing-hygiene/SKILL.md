---
name: skill-publishing-hygiene
description: >
  Publishing a public skill repo cleanly and release-ready.
version: 1.0.0
license: CC-BY-4.0
author: ratingtesting (https://github.com/ratingtesting)
---

# Skill Publishing Hygiene

Rules for keeping a public skill/OSS repo clean and release-ready. Learned the hard way
(angry user, authority complaints, broken automation, skipped setup steps).

## 1. Internal vs publishable file split (NON-NEGOTIABLE)

A publishable skill repo must NOT contain the author's kitchen. Separate them:

- **NEVER push (internal):** publishing registries (links, tokens, internal commands),
  article drafts, cover/debug PNGs, scraped site HTML (habr/vc settings pages),
  session transcripts, environment-specific notes, cookies exports.
- **ALWAYS push (publishable):** `SKILL.md`, `references/`, `templates/`, `scripts/`,
  `assets/`, `LICENSE`, `README.md`, `qa-results/` (sanitized — no tokens/paths).

Enforce with `.gitignore`. Pattern that works:
```
# Internal working artifacts — never published
PUBLISHING_REGISTRY.md
habr-article-*.md
medium-article-draft.md
devto-article-draft.md
huggingface-card.md
reddit-*-draft.md
cover.html
cover.png
cover_debug_*.png
habr_*.html
vcru_*.html
vcru_editor.js
```
Verify after editing: `git status --porcelain --ignored | grep "^!!"` should list the
internal files; `git ls-files | grep -i PUBLISHING_REGISTRY` should return nothing.

**Pitfall (real anger):** pushing an internal registry to a public repo drew "Нафига в
гитхабе реестр ссылок?" — the registry is for the author's local workflow only. If you
temporarily commit it (e.g. user says "запушил"), immediately `git revert` the commit
and re-push; keep the file locally only.

## 2. GitHub Release after every version push (NON-NEGOTIABLE)

After `git tag vX.Y.Z` + `git push --tags`, ALWAYS create a Release:
```bash
gh release create vX.Y.Z --repo <owner>/<repo> --title "vX.Y.Z — <what>" --notes "<body>"
```
gh marks the newest as Latest automatically. Do NOT leave only a tag — a user checking
"Releases" will think the repo is stale.

**Pitfall (real complaint):** a tag without a Release made the user think the version
wasn't published. Rule: tag + Release, every time a version bumps.

## 3. Skills for vibe-coders must SELF-EXECUTE

If the user is a non-programmer who will not read the skill file, any setup step the
agent "should remember" WILL be skipped. Make steps concrete runnable commands:

- BAD: "On first load, the agent MUST copy the templates into the project root."
- GOOD: a shell `cp` loop the agent runs at load time (see keelwright ⚡ Auto-bootstrap).

Evidence: an agent loaded keelwright v1.4.0 (which said "agent MUST create files") and
never created them — because it was prose, not a command. v1.4.1 fixed it by shipping a
runnable `cp` loop. Prefer `cp` in bash over a Python script (gotcha #4).

## 4. Windows Python / MSYS path gotchas

Under Hermes on Windows the terminal is git-bash/MSYS. Python quirks:

- `python` may resolve to the **Microsoft Store alias** (pops a Store page, non-zero exit).
  Use the venv Python explicitly:
  `C:\Users\<user>\AppData\Local\hermes\hermes-agent\venv\Scripts\python`
  — or just avoid Python; use bash `cp` (the agent's `write_file` tool also needs no Python).
- MSYS paths (`/c/Users/...`) are NOT understood by Windows Python's `os.path.isdir`.
  Normalize before use: `/c/foo` → `C:/foo` (see `references/windows-python-gotchas.md`).
- For shell file ops prefer bash: `cp src dst` works reliably.

## 5. External platform publishing (habr / vc / etc.)

Strict-auth APIs (e.g. vc.ru `auth:"strict"`) reject session cookies — they require
`access_token` from `localStorage`, which cookie exports don't include. So:

- Automating posting via API often FAILS with 401 even with all cookies present.
- The human posts manually in the browser; you prepare text + cover image locally.
- Keep the canonical backlink (GitHub repo) in every external post.
- habr.ru: a fresh/non-full-rights account is `readonly` and API publishing 404s; submit
  to the Sandbox manually. Read-only is NOT caused by negative karma for a +1-karma account —
  do not advise "reset karma" blindly.

## When NOT to encode
Environment-only failures (missing binary, unconfigured creds) are fixable by the user —
not durable rules. Don't harden "X tool is broken" into a skill; capture the FIX under a
setup/troubleshooting reference instead.
