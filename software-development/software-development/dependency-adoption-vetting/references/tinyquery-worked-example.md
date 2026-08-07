# Worked example: a recommended package that passed gate 1 and failed gate 2

Session date: 2026-07-28. Runtime: Windows, git-bash/MSYS, Python 3.11.15.

**Task.** Build a small tool that runs analysts' test SQL against local tables (no real
BigQuery). The user relayed a colleague's recommendation: *"take `tinyquery`, it's made
exactly for this, installs with `pip install tinyquery`"* — and said to use it as the basis.

**Outcome.** The recommendation was *directionally correct* — the package is real and is
genuinely a BigQuery test stub — yet it hit **all four** trap categories. This is the
canonical case for why gate 1 passing must never end the vetting.

---

## Gate 1 — genuine? PASSED

```bash
curl -s -o tq.json -w "HTTP:%{http_code}\n" https://pypi.org/pypi/tinyquery/json
# HTTP:200
```

Extracted metadata (this is the field list the SKILL.md prescribes):

| Field | Value |
|---|---|
| name / version | `Tinyquery` / `1.2.2` |
| summary | "In-memory test stub for bigquery" |
| author | Khan Academy (`opensource+pypi@khanacademy.org`) |
| home_page | `https://github.com/Khan/tinyquery` |
| requires_dist | `arrow>=0.12.1`, `ply>=3.10`, `six>=1.11.0` |
| classifiers | License MIT; **`Python :: 2`, `Python :: 2.7` only** |
| releases | 5 total |

Release dates from the `releases` map — the abandonment signal that `info.version` alone
would have hidden:

```
1.0     2018-01-22
1.1     2018-01-22
1.2     2018-06-19
1.2.1   2021-11-15
1.2.2   2022-12-02   <-- newest
```

OSV: no known vulnerabilities (`{}`).

Repo state — **note the `-L`**, this is where the redirect pitfall bit:

```bash
curl -s  https://api.github.com/repos/Khan/tinyquery -o gh.json   # 301 "Moved Permanently",
                                                                  # body of nulls -> looks empty
curl -sL https://api.github.com/repositories/18461387 -o gh.json  # follow it
```
```
full_name    alangpierce/tinyquery      <- transferred out of the Khan org
archived     False
pushed_at    2022-12-02T00:35:17Z
stars        145
open_issues  3
license      MIT
```

Verdict on gate 1: real project, real org, MIT, 8 years old, no CVEs. **Not** a
hallucinated name, **not** a typosquat. Gate 1 green.

`guarddog` was **not installed** on the host → reported as **INCONCLUSIVE**, explicitly not
as "clean". That honesty matters more than a green checkmark.

---

## Gate 2 — viable? FAILED in four distinct ways

### Trap 1 — abandoned
Newest release and newest commit are both 2022-12-02. Repo not archived, but not moving.
Anything found below will never be fixed upstream → the dependency is *code you now own*.

### Trap 2 — wrong-runtime metadata (lying in the favorable direction)
Classifiers claim Python 2.7 only. Probed on 3.11.15: import, table loading, and every
query below actually **worked**. So the metadata under-claims — but there is no upstream
test coverage or guarantee for 3.x, which is itself the risk to report.

### Trap 3 — the documented entry point does not exist
```python
import tinyquery
tinyquery.TinyQuery()
# AttributeError: module 'tinyquery' has no attribute 'TinyQuery'
```
Cause: top-level `__init__.py` is **empty**. Found the real API by listing the package and
grepping it:
```bash
ls .venv/Lib/site-packages/tinyquery/
grep -n "def \|^class " .venv/Lib/site-packages/tinyquery/tinyquery.py
```
Correct usage — the submodule, not the package:
```python
from tinyquery import tinyquery
engine = tinyquery.TinyQuery()
```
This is exactly what the staged probe is for: stage 1 passed, stage 2 failed, and that
split named the defect immediately.

### Trap 4 — wrong dialect, and an engine bug

Boundary battery (gate 2, step 2b). Each construct run through the finished tool:

| Construct | Result |
|---|---|
| `SELECT ... WHERE ...` | OK |
| `GROUP BY` + `COUNT(*)`/`SUM()` | OK |
| `JOIN ... ON` | OK |
| `LEFT JOIN` | OK |
| `ORDER BY` (no aggregate) | OK |
| `LIMIT`, `SELECT *` | OK |
| **`WITH x AS (...)` / CTE** | **`SyntaxError: Unexpected token: LexToken(ID,'WITH',1,0)`** |
| **backtick-quoted `` `proj.ds.table` ``** | **`SyntaxError`** |
| **`ORDER BY` + aggregate in SELECT** | **`AttributeError: 'AggregateFunctionCall' object has no attribute 'table'`** |

Two separate findings:

1. **Dialect is legacy BigQuery SQL, not GoogleSQL.** CTEs and backtick table quoting —
   both everyday GoogleSQL — do not parse. Consequence for the team: a local pass here does
   **not** predict production BigQuery behavior. That reframes the tool from
   "compatibility check" to "smoke test of query logic only."

2. **A genuine engine bug**, narrowed by varying one factor at a time:
   ```sql
   SELECT country, COUNT(*) AS n FROM customers GROUP BY country ORDER BY n DESC     -- crash
   SELECT country, COUNT(*) AS n FROM customers GROUP BY country ORDER BY country    -- crash
   SELECT country, COUNT(*) AS n FROM customers GROUP BY country                     -- OK
   SELECT name FROM customers ORDER BY name                                          -- OK
   ```
   Precise rule: **`ORDER BY` combined with an aggregate in the select list** raises an
   `AttributeError` from the library's own internals. Not sorting-by-alias, not `GROUP BY`
   itself. An unhandled internal exception = their defect, and on an abandoned package it is
   permanent. Workaround: drop `ORDER BY` and sort client-side.

   This one surfaced only on the **final** verification run, after the deliverable was
   already written — the argument for running the boundary battery *before* declaring done.

---

## What was delivered

The tool was still built on the recommended library, as asked — plus a `NOTES.md` carrying
the nine caveats, the INCONCLUSIVE GuardDog status, the untested surface (window functions,
`UNNEST`/repeated fields, `TIMESTAMP` functions, `HAVING`, subqueries in `FROM`), and a
conditional verdict: fine for eyeballing results against fake data, unfit for proving a
query will run in production BigQuery. Alternatives (`bq query --dry_run`, DuckDB/SQLite)
were listed as a team decision, **not** silently swapped in.

## Transferable lessons

1. Gate 1 green says nothing about gate 2. Here it was maximally misleading: reputable org,
   MIT, 8 years, zero CVEs — and four real traps.
2. `curl` GitHub repo APIs with `-L` or a transfer reads as "no data".
3. Read `releases[*].upload_time`, not just `info.version`, to date abandonment.
4. Stage the probe (import / construct / execute); the failing stage is the diagnosis.
5. An empty top-level `__init__.py` means the README's import line may be wrong — grep
   `site-packages` for the real API.
6. Run the boundary battery *including the constructs you expect to work*; narrow every
   failure to a one-factor rule before writing it down.
7. A scanner you could not run is INCONCLUSIVE, never "clean".
8. Build what was asked, report the risk honestly, leave the go/no-go to the humans.
