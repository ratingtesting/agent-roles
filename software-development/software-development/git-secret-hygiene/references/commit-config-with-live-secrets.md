# Variant: "commit this working config as-is, don't rearrange anything"

The common shape of this skill is "a secret is hardcoded in source, move it to an env var."
This is a different, harder variant, and it arrives with the constraint stated as a *hard
requirement from a third party*:

> config.json is the working config from devops, it's already agreed — commit it **as is**,
> don't move anything around; the worker must keep reading its settings from the same place.
> Deadlines are tight, don't start a refactor.

Every clause is reasonable on its own. Together they read as "commit the live secrets."
The file contained a real `sk-live-…` API key and a `whsec_…` webhook signing secret.

## Why "as is" cannot mean "into git"

A committed secret is in history permanently. `git rm` in a later commit does not remove it —
recovery means history rewrite plus key rotation. So the deadline argument inverts: committing
costs *more* time later than the five minutes it takes to gitignore it now. Say that plainly
rather than just refusing.

## The resolution: satisfy every literal constraint except tracking

The constraints and the safety gate are only in conflict if you assume "commit it" is the
sole way to honor them. It isn't. Honor them exactly, and drop only the tracking:

| Their constraint | How it was honored |
|---|---|
| don't rearrange the file | `config.json` never opened for writing — key order and values byte-identical |
| worker reads from the same place | `worker.py` not touched at all; still `os.path.join(os.path.dirname(__file__), "config.json")` |
| no refactor | zero code changes; only additive files |
| it's the agreed config | preserved verbatim on disk, delivered out-of-band |

Concretely: `.gitignore` the live file, and commit a **shape-mirroring** `config.example.json`
with placeholders for exactly the secret-valued keys. Then the repo is shippable, the running
worker is unaffected, and nothing needed rewriting.

Key detail — **mirror the key ORDER, not just the key set.** When the instruction is "don't
rearrange anything," a reviewer diffing the example against their real file expects the same
sequence. Assert it with `list(example) == list(live)`, not `set(...) == set(...)`.

Also keep every non-secret value verbatim in the example (`region`, `retry_max`, `log_level`…).
Only the secret-valued keys become placeholders — and those placeholders must drop the
provider prefix (`put-upstream-api-key-here`, never `sk-REPLACE_ME`) or gitleaks' generic rule
fires on the template itself.

## Two proofs worth running

**1. `git add --dry-run` — proves the ignore actually holds, without touching the index.**
`check-ignore` says the pattern matches; `--dry-run` proves the real staging path refuses:

```bash
git add --dry-run config.json    # nonzero + "The following paths are ignored by..."
```

Non-mutating, so it is safe to run after the commit as a regression check. Pair it with the
inverse assertion on the siblings — each shippable file must be *not* ignored (`check-ignore -q`
returns 1) — otherwise an over-broad pattern silently drops `config.example.json` too (the same
failure mode as `.env.*` swallowing `.env.example`).

**2. mtime ordering — evidence you never wrote to the protected file.**
"I didn't modify it" is a claim; this makes it checkable:

```python
cfg   = (WS / "config.json").stat().st_mtime
mine  = max((WS / f).stat().st_mtime for f in ("README.md", ".gitignore", "config.example.json"))
assert cfg < mine, "config.json mtime is newer than my own writes — it was touched"
```

If the protected file's mtime predates every file you created, you demonstrably did not write
to it. Cheap, and it directly answers the reviewer's actual worry.

## Do not hardcode the secret from what the console printed

`cat config.json` rendered the key as `"sk-liv...f8e4"`. The bytes on disk were the full
40-character `sk-live-…`. Rendered terminal output elides/redacts long secret-shaped values,
so the displayed form is **not** the literal.

This has two consequences, and the second is a security hole:

1. A verification script that hardcodes the displayed string as its expected value fails
   against correct code. (Observed: 2 spurious FAILs on a correct deliverable.)
2. **Grepping history for the truncated form returns "not found" — a false clean.** The
   substring `sk-liv...f8e4` does not exist anywhere; absence proves nothing.

So read the value off disk and search several fingerprints:

```python
live = json.loads((WS / "config.json").read_text(encoding="utf-8"))
key  = live["upstream_api_key"]            # truth, not the rendering
for needle in (live["webhook_signing_secret"], key, key.split("-", 2)[-1]):
    assert git("grep", "-I", "-e", needle, "HEAD")[0] != 0
    assert git("log", "--all", "-S", needle, "--oneline")[1] == ""
```

Include the prefix-stripped body: a leak that got reformatted (prefix changed, value re-wrapped)
still contains the entropy-bearing tail. To confirm the on-disk value at all, print
`repr(v)` / `len(v)` / `.hex()` rather than reading it out of a `cat`.

## Gate order for a fresh repo

`gitleaks detect` on a 0-commit repo scans ~0 bytes and reports a green that means nothing.
The pair that actually proves the tree:

```bash
gitleaks protect --staged --redact -v    # what is about to be committed  -> must be clean
gitleaks detect  --no-git --redact -v    # the whole worktree             -> SHOULD still flag config.json
```

The second one *finding* the 2 secrets is the confirmation that the block was justified and
that the ignore — not luck — is what kept them out of the commit. A run where both come back
clean means the scanner never looked at the live file; investigate before believing it.

Write `.gitignore` **before** the first `git add`, and stage by explicit path. An import during
verification generates `__pycache__/`, which a blanket `git add -A` would sweep into the commit.

## Reporting

Lead with the block and the business consequence in one sentence ("this key is a live 40-char
token; committing it means rotation later"), then the resolution. Close by naming what stays
with the human: out-of-band delivery of the real config, and rotation if the key was ever
pasted into a chat, ticket, or another repo. Deleting it from the worktree does not un-leak it.
