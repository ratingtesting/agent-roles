# Case study — orchestrator-loss and file-corruption loop (Digital Unlock Platform)

Observed in a real session; written so a future agent recognizes the pattern fast.

## Setup
- A project corpus (`MASTER_PRODUCT_SPEC.md` ≈33.5 KB, `FOUNDER_DECISIONS.md` ≈32.5 KB, plus REVIEW/, 08_MVP/, CONFLICT_REGISTER, ADRs) lived inside a monorepo parent where the project dir was **untracked** (`?? NULL` in `git status`). It had its own review artifacts, but **no git ref of its own**.

## What went wrong (3 cascading failures)

1. **Role confusion — orchestrator self-executed.**
   The task text said you're the orchestrator and to consolidate the corpus. Instead of dispatching specialist agents into isolated output, the agent personally re-wrote `FOUNDER_DECISIONS.md` and `MASTER_PRODUCT_SPEC.md` (each as a full `write_file`/`patch` pass). Result: the agent became its own master model, contradicted findings it had just produced, and mutated the source-of-truth docs without approval.

2. **No git baseline → edits irreversible.**
   Because the dir was untracked, there was no `git checkout` point. Every "undo" was a new hand-write. Sizes fell: `FOUNDER_DECISIONS.md` 32 KB → 11 KB → 8 KB; `MASTER_PRODUCT_SPEC.md` drifted and re-acquired typos/duplicate section numbers each rewrite.

3. **Hand-reconstruction from memory worsened the corruption.**
   Recovery attempts re-typed the docs from model recall instead of from the pristine first `read_file`. Each pass produced a *different, smaller, garbage-adjacent* file (e.g. "#15 (Final) — Юрий-шлюз", duplicate "## 4", dropped `⚠️CONFLICT-NN` blocks). A `git checkout <baseline>` run failed because the baseline commit had been created **after** the first corruption — it restored the corrupted snapshot, not the original.

## The fix that DID work
- `git init -b main` inside the project dir + set local `user.email`/`user.name` + `git add -A && git commit -m "baseline..."` → after that, EVERY operation was revertible and sanity-checkable.
- Restoring a large doc: use `git checkout <last-clean-commit> -- <file>` from a baseline created while the tree was still clean, NOT a hand re-type.
- Corruption canaries: `wc -c` and `grep -c "CONFLICT-"` (or any unique marker count) against the known-good size — a drop flags regression immediately, before you keep editing a damaged file.

## Correct flow (encoded in SKILL.md)
1. Read role: orchestrator ⇒ delegate, never self-write docs.
2. Before ANY write: ensure git baseline exists in the project dir.
3. If a doc must be restored, restore from a CLEAN commit, never from memory.
4. After 3 identical worsening retries, stop and escalate.

## Concrete commands that recovered
```bash
cd "<project-dir>"
git init -b main                          # own repo for the project
git config user.email "agent@local"
git config user.name "Agent"
git add -A && git commit -m "baseline: pre-work snapshot"
git log --oneline                          # safety net
git checkout <clean-commit> -- <file>      # restore, not hand-type
wc -c <file> ; grep -c "CONFLICT-" <file>  # canaries
```