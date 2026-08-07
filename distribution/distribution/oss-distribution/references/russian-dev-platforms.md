# Russian Dev Platforms — Publishing Patterns
(From keelwright cross-posting launch, 2026-07. Reusable for any blog/forum publish.)

## habr.ru
- New accounts land in `readonly` group (NOT negative karma). No public POST API works
  (`/api/v1/...`, `/api/v2/...` → 404/401). Publish only via browser → Sandbox (`/ru/sandbox/new/`).
- MODERATION REJECTS: AI-generated text, self-promotion/ads, list-heavy posts (>50% bullets).
  Write human voice, max ONE GitHub link, no "my product" framing. Sandbox approval → full-rights.
- Karma reset button exists but is IRRELEVANT for new-account readonly (readonly ≠ negative karma).

## vc.ru (Osnova network: DTF, TJournal share the engine)
- Editor SPA at `/editor`. API `api.vc.ru/v2.4/editor` (POST, body `{entry: JSON.stringify(s)}`).
- AUTH is `strict`: needs `access_token` from **localStorage**, cookies alone → 401.
  Cookie export insufficient; need browser localStorage dump OR manual publish in `/editor`.
- Cover image: exactly 780×440. Render via headless Chrome (`chrome --headless --screenshot`
  or `--window-size`), NOT browser-screenshot-then-crop (crops the wrong region).

## Publishing discipline (apply to ANY skill repo)
- Internal artifacts NEVER in public repo: link registries, article drafts, cover PNGs,
  scraped site HTML. Keep local; list in `.gitignore`.
- Source of truth = local skill dir; push ONLY the skill (SKILL.md, references/, scripts/).
- Accidentally pushed internal file? `git revert <sha>` + push, then add to `.gitignore`.
- Verify visual assets yourself (render + inspect) before "done" — vibe-coder user won't.
- Human publishes manually when API is blocked ( habr sandbox, vc strict-auth): give them
  ready text + cover file, don't burn cycles on blind API calls that 404/401.
