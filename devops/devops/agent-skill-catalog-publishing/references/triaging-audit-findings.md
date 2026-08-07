# Triaging automated skill-audit findings (SkillSpector et al.)

An automated audit of an agent skill returns 25–30 findings. Roughly one in ten is a real
defect. The rest are the scanner objecting that an orchestrator orchestrates. Fixing
everything guts the product; fixing nothing ships real holes. This is the triage method,
derived from three consecutive rounds on the same skill.

## The loop

1. **Never fix from the report.** Verify each finding on disk first. The report quotes code
   that may already be fixed — round 3 flagged `subprocess.run(...)` at Medium on a call
   that had *already* been converted to `shell=False` in the previous round.
2. **Sort into three buckets** (below).
3. Fix bucket A. Consider bucket B. Write down bucket C and stop re-litigating it.
4. Prove each fix behaviourally, not by wording.
5. Ship one version per round, with release notes naming what was *not* changed and why.

## Bucket A — real defects (fix these)

Recognisable by: the skill's own documentation contradicts itself, or an argument/flag does
not do what its name says, or untrusted input reaches execution.

Concrete instances found across three rounds:

| Defect | Why it was real |
|---|---|
| Docs advised renaming a log parameter to dodge a Semgrep credential rule, while still printing `secret[:8]` | Detector evasion *and* a partial secret leak, in a security skill |
| `run_pytest(test, impl_file)` accepted `impl_file` and ignored it | Function lied about what it tested; verdict derived from scanning output for `"FAILED"` rather than exit code, so crashed runs reported green |
| Importer ran post-install shell commands from the just-unpacked archive, unconditionally | Unpacking an untrusted zip executed its code |
| Post-install commands built as shell strings with the install path interpolated | Install path is attacker-influenceable via env var → command injection |
| `restore` overwrote snapshot files but silently kept files added since | In a tamper-recovery tool, a planted file survived a "restore" and the tree only *looked* clean |
| Bootstrap script fell back to `os.getcwd()` when its documented required argument was missing | Created files in whatever unrelated tree the process happened to sit in |
| SKILL.md advertised a gate as "machine-checked" while the reference file stated it cannot be enforced | False assurance is worse than no claim |
| Export bundled external run directories by default | Local absolute paths, raw prompts and machine names travelled with any shared archive |

The pattern connecting them: **a stated contract that the code does not honour.** That is
the question to ask of every finding — not "is this dangerous in the abstract" but "does
this do what it says".

## Bucket B — defensible hardening (judgement call)

Capability that is legitimate but scoped wider than necessary. Usually resolved by making
it opt-in rather than removing it: keep the feature, add a flag, print a warning, document
the risk in `--help`. Export-includes-run-data and run-post-install-checks both landed here
and both became `--include-runs` / `--run-checks`.

Rule of thumb: if the safe default costs the user nothing and the risky path is still one
flag away, take the hardening.

## Bucket C — framing complaints (do not fix)

The scanner treats an autonomous coding engine as though it should be a passive linter.
Repeatedly flagged across all three rounds, deliberately unchanged:

- auto-bootstrap writing state files into the project root (6 findings in one round)
- a weekly self-improvement cron that can patch memory or the skill (2 findings, both High)
- auto-rollback after a bad deploy
- `delegate_task` subagent spawning
- broad load triggers ("load before any coding session")
- `subprocess` usage *per se*, after the injection vector is already closed

These are the product. Removing them does not make the skill safer, only useless. Say so
explicitly in the release notes — otherwise the same findings get re-fought every round,
and a future maintainer may "fix" them out of the product.

**Mitigate the legitimate concern underneath instead.** The auto-bootstrap complaint is
really about surprise, so the fix was a one-line announcement of what was created, why it
helps, and that deleting it is allowed — not removing the bootstrap.

## Proving a fix

Assert on behaviour with a real payload. For the archive-execution fix, that meant building
a genuinely hostile zip — valid recomputed SHA256 manifest, plus a post-install script that
writes a marker file — and confirming the marker does **not** appear on a default import,
then *does* appear with the opt-in flag. Checking log text would have passed both before and
after the fix.

Corollary worth internalising: **an integrity manifest shipped inside the artifact it
describes proves self-consistency, never provenance.** An attacker who edits a file
recomputes the hash and the gate passes.

## Reading the delta between rounds

The most useful signal is what *disappeared*. Round 2 carried High-severity
`shell=True` findings (Tool Parameter Abuse, Unvalidated Output Injection, Context
Leakage); round 3 had none of them — confirmation the argv fix landed, worth stating in the
release notes. Rising finding counts are not necessarily regressions either: 30 → 25 → 29
across three rounds while severity fell, because the scanner surfaces different subsets.
Compare composition and severity, never the raw count.
