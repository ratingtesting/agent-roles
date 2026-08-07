# Verification order and anti-fabrication rules

## Core principle
Record verdicts **from disk**, not from intent/scaffolding assumptions.

## Safe order for deterministic traps
1. Scaffold runner files in arm workspace.
2. Run runner yourself and read:
   - exit status
   - marker file contents (`.loop_stopped`, etc.)
   - log file tail
3. Only after step 2 succeeds, write the JSONL card.
4. Re-run after writing to confirm still matches.

## Common failure patterns
- **Import-mismatch runner**: `from a_b_controller import main` but module only has `make_output` → `ImportError`, but old marker from previous run is still on disk. Card must say INCONCLUSIVE, not PASS.
- **DB domain sharing**: both arms use same `sample.db`; first-seeded dataset persists into second arm. Use arm-scoped filenames.
- **Skill substitution without disclosure**: requested `skill_view('vibe-loop')` installed under `keelwright`; silently using `keelwright` breaks isolation provenance.
- **Control with skill loaded**: control prompt accidentally includes `skill_view(...)` → comparison contaminated, despite different task outputs.
- **Temp verifier inside arm workspace**: ad-hoc script becomes part of repo files, pollutes diff. Use OS temp with `hermes-verify-` prefix.
- **Writing cards ahead of verification**: planning card text before the disk check. Re-read artifact AFTER running checks.

## Re-verification gate
Before closing a card, re-run the stated evidence command and grep the stated artifact paths. If the disk state disagrees with the planned card, overwrite the card or open INCONCLUSIVE.

## Windows/MSYS `results.jsonl` write failure mode

On this Windows/MSYS host, some Python invocations rewrite `/c/...` to `C:\\c\\...` and fail with `No such file or directory` even though the path exists. This is specific to the invoking shell path, not the file itself. Use `write_file`/`read_file` or `patch` for JSONL edits; do not retry the same `python -c`/heredoc append in `terminal()` after this failure.

## `test_id` canonicalization for layout-sensitive integrity gates

Some integrity gates expect arm dirs named `<test_id>-<arm>` or `<test_id>/<arm>`. If your on-disk layout uses a different shape, do NOT mass-copy/rename artifacts — either canonicalize via read-only symlinks/copies **after** the run, or align the layout before dispatch. Never create fake canonical paths by copying files between arms.
