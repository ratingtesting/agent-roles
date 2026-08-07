# Re-verify after any history rewrite

A verification result is only evidence for the **tree state it ran against**. Any git
operation that rewrites the working tree invalidates every check you ran before it — and
the most dangerous ones do so silently.

## The failure that motivated this

Sequence, condensed from a real session:

1. Edited `.gitignore` to add `__pycache__/`, ran an ad-hoc check — **PASS**.
2. Push rejected: branch had diverged from `origin/master`.
3. Resolved with `git reset --hard origin/master`.
4. Staged, committed, pushed. Reported the change as shipped.
5. A later verification run said **FAIL**: git still wasn't ignoring `__pycache__`.

Step 3 discarded the step-1 edit. `git add .gitignore` in step 4 then staged the *remote's*
version — a no-op — so the commit landed and the push succeeded while containing none of
the intended change. Nothing in the output of steps 3–4 mentioned the loss.

The claim in step 4 was false, and only re-running the check caught it.

## Rule

> After any operation that rewrites the working tree, re-run verification **and** re-assert
> that your change is still on disk — before claiming anything shipped.

Operations that invalidate prior verification:

| Operation | What it can silently drop |
|---|---|
| `git reset --hard <ref>` | every uncommitted edit in the tree |
| `git checkout -- <path>` | that file's uncommitted edits |
| `git stash` (without `pop`) | all stashed work |
| `git rebase` / `git pull --rebase` | edits lost to conflict resolution taking "theirs" |
| `git merge -X theirs` | your side of every conflicting hunk |
| `git clean -fd` | untracked new files |

## Cheap guard: grep for the change, not just the file

Staging a file proves nothing about its contents. Assert on the actual substring:

```bash
# after any tree-rewriting operation, before committing
grep -q '__pycache__' .gitignore || { echo 'FIX LOST — re-apply before committing'; exit 1; }
```

Generalized: check the fix survived, then verify behavior, then commit.

```bash
git reset --hard origin/master        # or rebase/stash/merge
grep -q "<sentinel from your fix>" <file> || echo "RE-APPLY THE FIX"
python "$TEMP/hermes-verify-<topic>.py"   # behavior, not just presence
git add <explicit paths> && git commit -m "..."
```

## Prefer inspecting the divergence over flattening it

`reset --hard` is the bluntest resolution and the easiest way to lose work. Before reaching
for it, look at what each side actually holds:

```bash
git fetch origin
git log --oneline HEAD..origin/master     # what remote has that you don't
git log --oneline origin/master..HEAD     # what you have that remote doesn't
git diff HEAD origin/master -- <file>     # per-file divergence
```

In the motivating session this diff revealed something worse than the lost edit: the remote
branch had **reverted a security fix** that was present locally. Flattening onto either side
without reading the diff would have silently dropped real work in one direction or the other.

When both sides hold changes you need, re-apply deliberately (cherry-pick the fix, or edit
after resetting) rather than hoping a merge strategy picks correctly.

## Confirm the push contained what you think

Sync state before pushing, and read back what landed:

```bash
git fetch origin -q
test -z "$(git log --oneline HEAD..origin/master)" && echo "in sync, safe to push"
git show --stat HEAD | grep <expected-file> || echo "WARNING: file not in the commit"
```

`git show --stat HEAD` is the honest answer to "did my change actually get committed?" — a
successful `git push` only proves *some* commit transferred, never that it carried your edit.
