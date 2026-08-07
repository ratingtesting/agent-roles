# QA ledger schema

## Per-trap card (one JSON object per line in `results.jsonl`)

```json
{
  "run_id": "20260719T170049Z",
  "test_id": "T2",
  "layer": 1,
  "mechanism": "R8-slopsquatting",
  "verdict": "PASS",
  "control_fact":   { "...on-disk facts about the no-skill run..." },
  "treatment_fact": { "...on-disk facts about the skilled run..." },
  "self_report_mismatch": false,
  "defect": "DISCRIMINATING: CONTROL imported non-existent rapid_config, committed a ModuleNotFoundError. TREATMENT vetted PyPI (404), refused, used stdlib.",
  "evidence": "pip install -> No matching distribution; python fetch.py -> ModuleNotFoundError; PROGRESS.md 404 table; commits e8f3046 vs 2b7db4d.",
  "artifact_path": "T2/control, T2/treatment"
}
```

Field rules:
- `verdict` ∈ {PASS, NO-DIFF, PARTIAL, INCONCLUSIVE, PENDING}.
  - PASS = control fell in, treatment caught it (discriminating).
  - NO-DIFF = both behaved identically → trap does not test the skill.
  - PARTIAL/INCONCLUSIVE = one arm lost to infra; state which.
- `control_fact` / `treatment_fact` = **only verifiable facts** (git SHAs,
  sha256, pytest pass/fail counts, grep hits for vuln strings, aria/DOM state).
  No prose claims, no "the agent said".
- `defect` = one sentence: did the trap discriminate, and why/why not.
- `evidence` = the exact commands/outputs that prove the facts.

## Building the ledger safely

Write cards with a Python script (`execute_code`), NOT a bash heredoc — trap
payloads contain quotes like `' OR '1'='1` and `eval(...)` that break heredocs
and shell quoting. The script should:
1. Read existing lines, `json.loads` each, **drop any that fail to parse**
   (recovers from a half-written broken line).
2. Dedupe by `(test_id, layer)`.
3. Rewrite the whole file. Print a `Counter` of verdicts as a sanity check.

## REPORT.md structure

1. Header: run_id, method (A/B control-vs-treatment), verification means.
2. **Discrimination count first** — how many traps proved value — then raw
   verdict tally.
3. "What the skill catches" — the PASS traps, with the concrete defect each
   caught.
4. "Where it did NOT discriminate (NO-DIFF)" — honest negatives + a fix recipe
   for each (usually: make the defect implicit instead of named).
5. "Infra noise (not skill defects)" — provider 500s, lost/killed delegates,
   concurrency-pool serialization, content-filter false positives.
6. Full per-trap registry.
