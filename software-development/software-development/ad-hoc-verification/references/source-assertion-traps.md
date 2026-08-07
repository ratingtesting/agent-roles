# Source-assertion traps: when the verify script lies about the code

Some verifications can only inspect source text — "this dangerous call is gone", "this
instruction was removed", "no local paths shipped". Those assertions are unusually easy to
get wrong in a way that **passes when it should fail**, which is worse than no check at all.
Three traps, all hit in one session.

## Trap 1 — the comment explaining the fix matches the pattern you banned

After replacing `shell=True` with an argument vector, the code carried an explanatory
comment:

```python
# Building these as strings + shell=True was a command-injection vector: the
# install path is attacker-influenceable via HERMES_SKILLS.
```

The check `"shell=True" not in source` therefore **failed on correctly-fixed code**. The
tempting response — delete the comment, or weaken the check — is backwards: the comment is
valuable, the check is wrong. Assert against executable tokens only:

```python
import io, tokenize

def code_tokens(text):
    """Executable source: comments and string literals dropped, spacing normalised."""
    try:
        joined = " ".join(
            t.string for t in tokenize.generate_tokens(io.StringIO(text).readline)
            if t.type not in (tokenize.COMMENT, tokenize.STRING)
        )
    except tokenize.TokenError:
        joined = text
    return re.sub(r"\s*([=(),])\s*", r"\1", joined)
```

The same applies to docstrings — a `"""...shell=False..."""` docstring is a STRING token and
must not satisfy a check about real arguments.

## Trap 2 — token joining changes the spelling you are searching for

`" ".join(tok.string ...)` turns `shell=False` into `shell = False`. A follow-up check for
the literal `"shell=False"` then fails on code that is correct.

Worse, the *negative* check `"shell=True" not in tokens` silently became **vacuous** for the
same reason — it could never match, so it would have passed even on unfixed code. A negative
assertion that cannot fail is indistinguishable from a passing one, and this is exactly how a
verification script manufactures false confidence.

Fix: normalise spacing after joining (the `re.sub` above), and where practical pair every
negative assertion with a positive one — assert `shell=True` is absent **and** `shell=False`
is present. If only the negative exists, prove it can fail by running it against the pre-fix
source (`git show HEAD~1:<file>`), same discipline as
`references/two-impl-discrimination.md`.

## Trap 3 — `git archive HEAD` does not see staged deletions

A block asserting "these stray files are no longer shipped" ran against a tree built with:

```bash
git archive --format=tar HEAD -o t.tar
```

The files had been removed with `git rm --cached` and deleted from disk, and the working-tree
checks passed — but `git archive HEAD` reads the **last commit**, where they still existed. So
the shipped-tree block failed while the on-disk block passed, in the same run.

That contradiction is the useful signal:

- disk clean + archive dirty → **the change is uncommitted**, commit it and re-run
- disk dirty + archive clean → the fix regressed locally after the commit

Verify against the exact ref you intend to publish, and say which one:

```bash
git archive --format=tar <tag> -o t.tar    # the bytes that actually ship
```

When the artifact is published from a tag, verifying `HEAD` is not equivalent — a
`git tag -f` after the commit is easy to forget, and then the published bytes are not the
verified bytes.

## Rule of thumb

A source-text assertion is only trustworthy if you know **what makes it fail**. Before
trusting a green run, answer: which byte would I have to change to turn this red? If the
answer is "none" or "not sure", the check is decorative.
