# jscpd dup-threshold pitfall (Case 4 of ad-hoc-verification)

When refactoring away duplication, a copy-paste detector like `jscpd` is often
the acceptance gate. A real dedupe can still FAIL the gate — or a fake one can
PASS it while hiding clones. Know both.

## The gate can under-count (threshold hides real clones)

`jscpd -t 10 -l 3 -k 50 handlers/` counts ONLY files with >=3 lines AND >=50
tokens of analyzable content. A 3-line thin wrapper (e.g.
`from common import handle` + `if __name__ == "__main__": handle()`) has ~13
tokens — under the 50-token floor. jscpd silently excludes such files from
"Files analyzed", so 12 identical wrappers read as "1 file analyzed, 0% dup"
even though the wrappers are byte-identical.

**Verify with a stricter probe before trusting the required command:**

```bash
jscpd -t 10 -l 1 -k 5 handlers/   # min 1 line, 5 tokens — surfaces the wrappers
```

If that reports, say, 52% dup while the required `-l3 -k50` reports 0%, the
dedupe was cosmetic. The fix is a genuine unique token per file — e.g.
`from common import handle as _run_X` where X differs per file. After that the
strict probe drops to ~1-2% and the required command stays at 0%.

## The command can pass on a clean tree

```
jscpd -t 10 -l 3 -k 50 handlers/
# -> Files analyzed: 1, Duplicated lines: 0 (0.00%), exit 0
```

That is the desired state for a real dedupe: shared logic lives in one module,
and the few line-per-file wrappers sit under the token floor. Report it as
"jscpd dup 0.00%, exit 0" but ALSO confirm via the strict probe (above) that
no clone is merely hiding below the threshold.

## Pitfalls

- Don't trust the required/loose command alone when wrappers are tiny — always
  cross-check with `-l1 -k5`.
- Exit code 0 = under threshold. Nonzero = over threshold. Both are meaningful.
- jscpd excludes files below `min-lines`/`min-tokens` from the analyzed count
  entirely, not just from the clone math. "1 file analyzed" on a 12-file dir is
  the tell-tale of threshold-hiding, not a clean tree.
