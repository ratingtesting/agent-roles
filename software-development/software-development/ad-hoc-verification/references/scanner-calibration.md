# A clean security scan is not evidence — calibrate the scanner first

## What happened

A `store.py` contained a textbook SQL injection:

```python
query = "SELECT id, name, city FROM %s WHERE %s = '%s'" % (table, column, value)
return conn.execute(query).fetchall()
```

Semgrep with two registry rulesets — 151 rules, targeted at exactly this class —
reported **`Findings: 0`**:

```bash
PYTHONPATH= semgrep scan --config=p/python --config=p/sql-injection --error --metrics=off store.py
# ✅ Scan completed successfully.
#  • Findings: 0 (0 blocking)
#  • Rules run: 151
```

The same command against the *fixed* file also reported `Findings: 0`. Identical output
for vulnerable and safe code, so the green result carried **zero** information.

Likely cause: the taint flowed through a local variable into
`sqlite3.Connection.execute` rather than `Cursor.execute`, which the registry rules
model. Whatever the mechanism, the lesson does not depend on it.

## The rule

**Before reporting a scanner as a passed gate, prove it can fail on this codebase.**
Run it against the known-bad version. If vulnerable and fixed produce the same output,
the scan is not a gate — it is decoration, and saying "Semgrep clean" overstates the
evidence to someone who cannot read the diff.

This is the scanner-level form of the two-implementation discipline in
`references/two-impl-discrimination.md`. Exactly the same question — *can this check
fail?* — applied to a third-party tool instead of your own assertions.

## How to report it honestly

Do not silently drop the scan; report it with its demonstrated blind spot, and name what
actually carried the proof:

> R1 Semgrep (151 rules) → 0 findings. **But the same scan also returns 0 findings on the
> known-vulnerable version**, so this green proves nothing here. The real evidence is the
> two-impl run: 6 failures pre-fix, 0 post-fix.

Wrong framings to avoid:

- ❌ "Semgrep clean, no SQL injection." — unsupported; the tool was never shown to detect it.
- ❌ Omitting the scan because it was uninformative — the blind spot is itself a finding a
  future session needs.

## Generalizes beyond Semgrep

Same calibration applies to any pass/fail tool used as a gate:

| Tool | Silent no-op that looks green |
|---|---|
| Semgrep / SAST | rule doesn't model the sink → `Findings: 0` on vulnerable code |
| `gitleaks detect` | fresh repo, 0 commits → scans ~0 bytes, "no leaks found" (use `protect --staged`) |
| jscpd / cpd | every file under `--min-tokens` → `Files analyzed: 0`, "No duplicates" |
| coverage | 0 tests collected → no failures reported |
| type checkers | file excluded by config → no errors because nothing was read |

The shared shape: **"found nothing" and "looked at nothing" print the same thing.** Always
confirm the tool *saw* the target (non-zero files/rules/commits scanned) and, when the
stakes justify it, that it *reacts* to a known-bad input.

## Complement it with a targeted grep

Cheap, and it does not depend on the scanner's sink model:

```bash
grep -nE 'execute\(f"|execute\(.*%|\.format\(|SELECT.*\+' *.py
```

A hit is a lead, not a verdict — `.format()` on an allowlisted identifier is fine, while
`%` on a user value is not. Read the line before judging.
