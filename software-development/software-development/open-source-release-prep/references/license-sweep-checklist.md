# License-change sweep checklist

Run this when switching a project's license (e.g. CC BY 4.0 → MIT-0).
**DO NOT** stop after updating LICENSE file + SKILL.md frontmatter — the stale license
survives in at least 5 other places, and the user WILL catch each miss separately.

## Repo-internal files (grep the whole tree)

- [ ] `LICENSE` — full canonical text, not just SPDX
- [ ] `SKILL.md` frontmatter — `license:` field
- [ ] `SKILL.md` body — look for "Provenance & licensing", "This skill is licensed",
      "attribution", any prose mention of the old license name
- [ ] `README.md` — License section near the bottom (not just the badge/link)
- [ ] `references/provenance.md` — the full attribution/provenance file
- [ ] `AGENTS.md` / `CLAUDE.md` / `.cursorrules` — any project-rule file
- [ ] `internal/` setup guides — env-specific instructions that mention the license
- [ ] Architecture/visual files:
      - `assets/architecture.html` — footer line with license
      - `assets/architecture.png` — text overlay with license (regenerate from HTML)
      - Any generated SVGs, diagrams, or Excalidraw files with text
- [ ] Any other `.md`, `.html`, `.txt` files — grep for the stale license name

## External publications (update each manually or via API)

- [ ] **dev.to article** — check body_markdown for license mention, update via API
- [ ] **HF Space README** — edit the space card / README.md in the HF repo
- [ ] **HF Discussion** — edit the discussion post (bottom attribution line)
- [ ] **vc.ru article** — if published, edit the body
- [ ] **habr.ru article / sandbox** — if published/pending, edit the body
- [ ] **Medium article** — if published, edit via API
- [ ] **ClawHub listing** — re-publish; platform auto-detects license from SKILL.md
- [ ] **ClawHub re-preview** — press "Re-run preview" to re-import from GitHub
- [ ] **askill.sh / skills.sh** — re-submit or trigger re-index
- [ ] **Any other catalogs** (AgentSkills.io, etc.) — check listing

## Verification

- [ ] `grep -r "CC BY\|OLD_LICENSE_NAME" .` — zero hits
- [ ] Browser-navigate to the GitHub repo page, scroll to bottom — License text in
      README shows new license
- [ ] Browser-navigate to the repo's About sidebar — the License badge shows new
      license (if GitHub's Licensee detects it)
- [ ] Open the architecture.html in a browser — no stale footer
- [ ] Open the architecture.png — no stale text overlay (visually check)
- [ ] `gh api repos/<owner>/<repo>/license` — check SPDX detection

## Pitfalls from real session (2026-07)

- SKILL.md body says "Provenance & licensing: ... This skill is licensed CC BY 4.0"
  — easy to miss because you only look at frontmatter `license:` field
- references/provenance.md — the full attribution page, frequently has its own
  license statement
- README.md License section — written as `[CC BY 4.0](LICENSE) — free for commercial
  use with attribution.` — looks like a simple link but text says the old license
- architecture.html footer: `keelwright by ratingtesting · CC BY 4.0` — a div.foot
  that's easy to miss when you search only `.md` files
- architecture.png — PNG text overlay doesn't appear in grep; must regenerate from
  HTML source
- HF Discussion — attribution at bottom of the post: `keelwright by <user> — CC BY 4.0`
  — this is in a Discussion post, NOT in the repo files
- User frustration: every missed occurrence triggers a separate correction.
  The correct approach is to sweep ALL files before claiming "done".
