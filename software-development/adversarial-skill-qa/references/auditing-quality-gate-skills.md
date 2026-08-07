# Auditing a quality-gate skill (thresholds, tool commands, versions)

When the skill under test *itself* invokes quality tools (jscpd, lizard, scc,
gitleaks, semgrep), a whole class of latent defects lives in the gap between what
the skill's prose CLAIMS and what the tool command actually DOES. Grep for every
threshold/version and cross-check them. These are silent: the gate looks present
but fires at the wrong point or not at all.

## Threshold desync (the #1 finding)

The skill states a ceiling in prose but the example command uses a different number,
so the gate fires somewhere other than advertised.

- **lizard**: its DEFAULT warning threshold is **CCN > 15**. If the skill's ceiling
  is "CCN > 25" but the command is bare `lizard ./src` (or `-C 15`), the gate trips
  at 15, not 25. Fix: pass the threshold EXPLICITLY — `lizard -C 25` (and
  `-T cyclomatic_complexity=25`) so tool output and stated ceiling agree.
- **jscpd**: `--threshold N` is the fail line. If prose says "dup > 10%" but the
  command is `--threshold 5`, they disagree. Sync them: `--threshold 10`.
- Check EVERY copy: the same command is often duplicated across `writing-code.md`
  and each `bindings/<stack>.md` (python, flutter, …). Fixing one leaves the others
  desynced. Grep the whole skill dir, not just the main file.

## Verify the tools actually work before trusting an INFRA_FAIL

A run may report "jscpd/lizard returned 0 on obvious duplication → INFRA_FAIL". Do
not take it on faith — reproduce it yourself: write a file with 3 identical
functions and run the tools directly. In this session jscpd reported 62.86%
duplication and lizard computed CCN correctly, proving the tools were fine and the
INFRA_FAIL was a broken TEST SCAFFOLD (missing dir, wrong flags), not a dead tool.
Never patch the skill to work around a tool the skill's own environment can run —
fix the scaffold instead.

## Stale version notes

Skills sometimes hardcode "vX.Y.Z verified" in a tool table. When a run confirms a
newer working version, update the note so it doesn't read as an upper bound
(e.g. lizard `v1.22.2 verified` → `v1.23.0 verified`).

## What NOT to change

If a reported "gap" (e.g. "no prompt-injection defense", "verify gate ignores file
existence") contradicts text already in the skill, do not add a duplicate section.
Grep, confirm it's present, and instead test whether the existing mechanism FIRES.
