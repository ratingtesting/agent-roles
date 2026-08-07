# Windows-path gotcha for gbrain (Bun on Windows)

`gbrain` is a Bun/Node binary on Windows. It does **NOT** expand `~` and does **NOT**
understand MSYS-style paths (`/c/Users/...`). In git-bash this bites you silently:

```bash
gbrain export --dir /c/Users/Unicorn/Documents/...   # prints "Exported N pages" but writes NOTHING
gbrain export --dir ~/brains/out                     # same silent no-op
```

**Fix:** always convert to a native Windows path with `cygpath -w`:

```bash
export GBRAIN_HOME="$(cygpath -w "$HOME/brains/personal")"
gbrain export --dir "$(cygpath -w "$HOME/Documents/Obsidian-Profiles/default")"
```

Verify by actually listing the target dir afterward:
```bash
find "$dst" -name '*.md'    # if empty but gbrain said "Exported", it's the path bug
```

Same caution applies to any Bun/Node CLI invoked from git-bash on Windows: pass Windows
paths, not `/c/...` or `~`.
