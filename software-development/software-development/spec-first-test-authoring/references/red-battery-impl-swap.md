# RED-BATTERY by impl-swap — worked example (Decimal money rule, unittest)

Session context: a sales-reporting module where the disputed business rule was *how returns are
priced*. The spec said returns are subtracted at the **discounted** price; the plausible-wrong
reading subtracts them at the **full** `unit_price`. Both readings produce believable numbers,
so only a discriminating test separates them — and only an impl-swap proves the test discriminates.

## 1. Spec first — hand-computed acceptance table

Written into `specs/sales-report.md` BEFORE any code or test existed:

```
effective_price = unit_price * (1 - discount_pct / 100)
net_revenue     = units * effective_price - returned * effective_price
```

| product | region | units | price | disc% | ret | net_revenue |
|---|---|---|---|---|---|---|
| Widget | South | 5 | 9.99 | 10 | 1 | 35.964 |

Plus the explicit discriminating line — this is what the buggy variant must reproduce:

> Under the wrong reading ("return at full price"), Widget/South would be
> `44.955 - 9.99 = 34.965` instead of `35.964`.

## 2. The discriminating test quotes the spec, both ways

```python
def test_discount_applies_to_returns_too(self):
    record = SaleRecord("Widget", "South", 5, Decimal("9.99"), Decimal("10"), 1, "2026-01-07")
    self.assertEqual(net_revenue(record), Decimal("35.964"))
    self.assertNotEqual(net_revenue(record), Decimal("34.965"))   # names the wrong reading
```

The `assertNotEqual` against the *specific* wrong value is cheap and documents the trap for the
next reader. It is not a substitute for the battery, but it makes the intent auditable.

## 3. Run the battery — automated swap, automated restore

```bash
cp sales_report/domain.py /tmp/domain_ok.py
python - <<'EOF'
import pathlib
p = pathlib.Path("sales_report/domain.py")
s = p.read_text(encoding="utf-8")
buggy = s.replace("    returns = record.returned * effective_price",
                  "    returns = record.returned * record.unit_price  # BUGGY")
assert buggy != s, "замена не сработала"     # fail loudly if the anchor moved
p.write_text(buggy, encoding="utf-8")
EOF

python -m unittest discover -s tests -t . 2>&1 | tail -5     # expect FAILED
cp /tmp/domain_ok.py sales_report/domain.py
python -m unittest discover -s tests -t . 2>&1 | tail -4     # expect OK
grep -n "returns = record" sales_report/domain.py            # prove restore landed
```

Actual result recorded: `FAILED (failures=3)` on the buggy impl, `OK` (8 tests) after restore,
and the grep showed `returns = record.returned * effective_price` back on line 57.

**The `assert buggy != s` line is the part people skip.** Without it, a drifted anchor string
makes `str.replace` a silent no-op, the suite stays GREEN, and you conclude "the tests are
tautological" when in fact nothing was ever swapped. Any no-op swap must abort the battery.

## 4. Reading the result

- 3 failures, not 1: the rule flowed into a per-record test *and* two aggregate totals. Multiple
  independent failures are stronger evidence than one.
- After restore, re-running is mandatory. A battery that ends on the buggy file is a landmine —
  the repo now holds the wrong business rule with a green report attached.

## Trap: swap the module the tests actually IMPORT, not a sibling copy

The battery only measures anything if the swapped bytes are the bytes the test run imports.
A runner invoked as `red_battery.py <tests.py> <correct_impl.py> <buggy_impl.py>` invites the
natural-but-wrong move of staging two copies in a scratch dir:

```bash
mkdir -p .rb
git show HEAD:pricing.py > .rb/pricing_buggy.py     # ← nothing imports these
cp pricing.py            .rb/pricing_correct.py
python red_battery.py test_pricing.py .rb/pricing_correct.py .rb/pricing_buggy.py
```

Because `test_pricing.py` does `from pricing import apply_tier_discount`, Python resolves
`pricing` from the project dir on `sys.path` — the `.rb/` copies are never loaded. Both phases
import the SAME (correct) module, so both go GREEN and the runner concludes:

```
Phase 2 (.rb/pricing_buggy.py): GREEN on buggy — trap weak
RED-BATTERY RESULT: FAIL — tests green on both, likely tautological
```

**That verdict is a harness artifact, not a finding.** The tests in that session were genuinely
discriminating — proven immediately after by swapping the real import target. Accepting the
false FAIL would have sent a future agent off rewriting perfectly good spec-derived tests.

**Fix — swap the real file in place, keep a scratch copy only for restore:**

```bash
cp pricing.py /tmp/kw_correct.py            # save the good one
git show HEAD:pricing.py > pricing.py       # buggy version AT THE IMPORT PATH
rm -rf __pycache__                          # stale .pyc would mask the swap
python -m pytest test_pricing.py -q | tail -3      # expect RED  -> 6 failed, 10 passed
cp /tmp/kw_correct.py pricing.py && rm -f /tmp/kw_correct.py
rm -rf __pycache__
python -m pytest test_pricing.py -q | tail -3      # expect GREEN -> 16 passed
```

Two guards worth keeping:

- **Clear `__pycache__` between phases.** A cached `.pyc` for the swapped module can serve the
  previous version and produce the same false-GREEN as the wrong-target mistake.
- **Prove the restore landed with behavior, not just a file copy** — e.g. re-import and print the
  disputed value (`gold/2000 = 1500.0`). A `cp` that silently failed leaves the buggy rule on disk
  under a green report, which is the exact landmine §4 warns about.

**Diagnostic rule of thumb:** if Phase 2 is GREEN *and every single test passed identically to
Phase 1*, suspect the swap target before suspecting the tests. A truly tautological suite usually
still shows some churn; an unswapped file shows byte-identical results.

## Portability notes

- Works with any runner (`unittest`, `pytest`, a bare script) because it only swaps the file
  under test — nothing about the harness changes between the two runs.
- With `git` available, `git stash` / `git checkout -- <file>` is a cleaner restore than a
  scratch copy; the scratch copy is the fallback when the workspace is not a repo (this session's
  case).
- On Windows/MSYS a `/tmp/...` path is fine for the shell `cp`, but **not** for a path handed to
  a native Python interpreter as an argument — see the `windows-msys-shell` skill, Trap 3. Keep
  the scratch copy inside the project tree if any native exe must read it.
