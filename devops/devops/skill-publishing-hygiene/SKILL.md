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

## 6. License change propagation checklist

When switching licenses (e.g. CC BY 4.0 → MIT-0), ALL of these must be updated —
missing any one causes a confusing mismatch visible on GitHub or registries:

- [ ] `SKILL.md` frontmatter (`license:` field)
- [ ] `SKILL.md` body (Provenance & licensing section — full paragraph, not just frontmatter)
- [ ] `LICENSE` file (full canonical text, matches https://opensource.org/license/mit-0)
- [ ] `README.md` License section (link text + description: "free for use without attribution")
- [ ] `references/provenance.md` (both the attribution paragraph and the license table)
- [ ] `assets/architecture.html` footer div (`CC BY 4.0` → `MIT-0`)
- [ ] `assets/architecture.png` (re-generate or replace — footer text is rasterised)
- [ ] GitHub: push commit, verify via `gh api repos/owner/repo/license` (may return NOASSERTION
      for MIT-0 — that's GitHub's detector, not your file; the actual LICENSE is correct)
- [ ] GitHub: **check README.md rendered on the repo page** — the License section at the bottom
      is what visitors see. This was the actual source of the user complaint: SKILL.md was
      MIT-0 but README.md still showed CC BY 4.0.
- [ ] clawhub.ai: if already published, re-publish with bumped version (CLI enforces MIT-0
      anyway, but the displayed license text in SKILL.md preview must match)
- [ ] askill.sh: re-submit URL to re-index
- [ ] HF Space index.html: update via `api.upload_file` (has both JSON-LD `"license"` and
      visible footer text)
- [ ] HF Discussion post: manual Edit (agent cannot — needs browser login)

**Pitfall (this session):** after changing SKILL.md, LICENSE, and architecture.html, the
user still saw CC BY 4.0 on the repo page because README.md's License section had not been
updated. The README is what GitHub renders at the bottom of the page.

**Verification trap — check the rendered page, not just git files:**
```
git show origin/master:README.md | grep "license\|LICENSE"
# This shows the FILE. The PAGE may show something different.
# Instead: open the actual repo page and read what's displayed.
```

**askill.sh re-indexing:** submitting the URL again via https://askill.sh/submit
re-indexes the repo. The site says "Found and indexed 1 skill" — but this does NOT
guarantee the page immediately shows the latest version. Always verify by opening
the actual skill page after re-indexing.

## 7. Verification of current state — check before claiming

When the user asks about the current state of a publication (version, license, status),
**always query the remote directly** (API, CLI inspect, browser, curl) before answering.
Multiple agents may have modified state since your last action. Claiming "it's on old version"
without checking drew a justified correction this session (\`говорю же ты не единственный агент\`).
A `git log --oneline` on a stale clone is NOT evidence — pull first, or use the platform API.

## 8. Vercel skills.sh (separate from askill.sh)

`skills.sh` is a **different registry** by Vercel — not to be confused with `askill.sh`.
Skills appear on its leaderboard automatically via anonymous telemetry when users run:
```
npx skills add <owner>/<repo>
```
There is NO manual submission form. To get a skill listed:
1. Add the `npx skills add` command to README
2. Users who run it get counted in the leaderboard

This was verified this session: the command works with any GitHub repo containing a
recognizable skill file. Telemetry for `npx skills add ratingtesting/keelwright` was
registered successfully.
