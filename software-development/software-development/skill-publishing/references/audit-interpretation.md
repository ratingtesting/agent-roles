# Interpreting Third-Party Security Audit Results

When a tool like SkillSpector, Semgrep, or Snyk flags findings, not all findings are bugs.
The key skill is separating **code-level defects** (fixable) from **design-choice flags**
(intentional product decisions).

## Pattern: real bug vs design choice

| Signal | Likely real bug | Likely design choice |
|---|---|---|
| Finding about specific code (`shell=True`, `env={}`) | ✅ Code-level defect | |
| Finding about broad behavior (auto-bootstrap, cron, rollback) | | ⚠️ Intentional feature |
| Finding contradicts own documentation (`X is enforced` but code says `X is NOT enforced`) | ✅ False assurance | |
| Finding says "too broad" for core product functionality | | ⚠️ That's the product |
| Finding about output handling, injection, path traversal | ✅ Code-level defect | |

## Real example (keelwright, 4 audit rounds)

Rounds 1-2 fixed real code bugs:
- `shell=True` in subprocess → injection vector (fixed to `shell=False`)
- `env=dict(PYTHONPATH=...)` replaced entire environment on Windows (fixed to `{**os.environ, ...}`)
- Export leaked local paths via `~/kw-qa/` (fixed with `--include-runs` flag)
- Post-install executed code from untrusted zip without consent (fixed with `--run-checks`)

Round 3 found:
- R9 claimed as "machine-enforced" but skill says it can't enforce it (false assurance — fixed)
- Auto-bootstrap, weekly cron, auto-rollback flagged as "excessive agency" (intentional design — not fixed)

## Rule of thumb

If the auditor says "the skill does X" and X is described in the skill's own description
as a feature, it's a design choice. If the auditor says "the skill does X" and X
contradicts what the skill claims about itself, it's a real bug.

Don't fix design choices to satisfy an auditor — that kills the product.
Do fix code defects and false assurances — those are real vulnerabilities.
