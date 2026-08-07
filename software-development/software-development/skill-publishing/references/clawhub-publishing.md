# ClawHub Publishing Procedure

## Prerequisites
- `clawhub` CLI installed and authenticated (`clawhub whoami` returns your handle)
- Clean git tree matching the tag you want to publish

## Step 1 — Create clean staging directory

ClawHub publishes EVERY file in the directory. If you point it at the skill dir,
internal files (drafts, verify scripts, .bak, __pycache__) leak into the public registry.

**Always publish from a clean staging copy made via `git archive`:**

```bash
STAGE="/c/Users/Unicorn/AppData/Local/Temp/clawhub-publish"
rm -rf "$STAGE" && mkdir -p "$STAGE"
git archive --format=tar <tag> | tar -x -C "$STAGE"
# Verify: count files, check no internal artifacts
find "$STAGE" -type f | wc -l
find "$STAGE" -name "*.bak" -o -name "__pycache__" -o -name "hermes-verify-*"
```

## Step 2 — Publish with explicit --name

**`--name` is MANDATORY.** Without it, ClawHub uses the DIRECTORY NAME as the display name.
Since staging dirs have random temp names, the published name becomes garbage.

```bash
clawhub publish "$STAGE" \
  --name "keelwright" \
  --slug keelwright \
  --version 1.5.1 \
  --tags "security,guardrails,vibe-coding,loop-coding"
```

## Step 3 — Version visibility

The published version is NOT immediately visible in the registry API until the user
runs a security scan on ClawHub. The `clawhub publish` command returns `OK` but
`clawhub search` still shows the old version. This is normal — ClawHub queues the
version for scanning before listing it.

## Step 4 — Verify

After publishing, verify with: `clawhub search <slug>`

## Gotchas

1. Without `--name` = garbage displayName. Always pass explicitly.
2. Publishing from skill dir directly = internal files leak. Always use `git archive`.
3. Version not visible after publish = normal (scan queue). Don't re-publish.
4. `.bak` files, `__pycache__/`, `hermes-verify-*` in staging = will publish. Clean first.
5. MSYS paths — `clawhub publish` needs Windows-style paths (`C:\...`), not POSIX.
