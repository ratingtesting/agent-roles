# Pitfall: `gbrain` export only accepts Windows-style paths

## Environment
`gbrain` is a Bun/Node binary on Windows (`~/.bun/bin/gbrain`, v0.42.66). It does NOT understand
MSYS paths (`/c/Users/...`) and does NOT expand `~`.

## Reproduction (failure)
```
gbrain export --dir "/c/Users/Unicorn/Documents/Obsidian-Profiles/default"
# prints "Exported 2 pages to /c/Users/Unicorn/..." but writes ZERO files
find ... -name '*.md'   # empty
```
Same with `~/brains/exp2` — 0 files written. No error, silent no-op.

## Working form
```
dst_w=$(cygpath -w "$dst")          # -> C:\Users\Unicorn\Documents\...
gbrain export --dir "$dst_w"        # files appear under <dst>/inbox/*.md
```
Proven: `C:\Users\Unicorn\Documents\Obsidian-Profiles\default\inbox\2026-07-27-*.md` created.

## Notes
- `gbrain list` / `gbrain export` operate on the brain pointed to by `$GBRAIN_HOME`
  (also must be a Windows path: `export GBRAIN_HOME="$(cygpath -w "$HOME/brains/$brain")"`).
- API key for embedding/LLM: `OPENAI_API_KEY=$API_9ROUTER_KEY`, `OPENAI_BASE_URL=http://localhost:20128/v1`
  (read from Windows User env via `powershell.exe -NoProfile -Command '[Environment]::GetEnvironmentVariable("API_9ROUTER_KEY","User")'`).
- `gbrain export` emits noisy `[models] tier.subagent ... does not support prompt caching` lines;
  pipe through `grep -vi "tier.subagent\|prompt caching\|hot (cost"`.
- Exported markdown has YAML frontmatter and body, but NO `[[wikilinks]]` between pages
  (GBrain stores semantic links in the vector DB, not in text). Add `MOC.md` with manual
  `[[wikilinks]]` to make the Obsidian graph non-empty.
