---
name: python-security-hardening
description: "Use when fixing Python security vulnerabilities — SQL injection, eval/code execution, path traversal, IDOR/broken access control — or hardening a controller/handler that takes user input. Triggers: fix SQL injection, remove eval, parameterize query, path traversal, IDOR, broken access control, harden controller, OWASP A01/A03/A07, safe file read, calculate from user expression. Covers four common fix patterns and the literal_eval-does-not-do-arithmetic gotcha."
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [security, python, sql-injection, eval, path-traversal, idor, broken-access-control, hardening, owasp]
    related_skills: [requesting-code-review, clean-code-review, ad-hoc-verification]
---

# Python Security Hardening

## When to use

Fixing or reviewing Python code that handles untrusted input and exhibits any of:

- **SQL injection** — query built by string concat / f-string / `.format()` with user data
- **eval / code execution** — `eval()`, `exec()`, `compile()` on user-supplied strings
- **Path traversal** — `open(os.path.join(root, user_filename))` without containment
- **IDOR / Broken Access Control** — fetching an object by user-supplied ID without
  verifying the authenticated user owns or is authorized to access that object
  (OWASP A01:2021). E.g. `ProfileDraft.query.get(draft_id)` without a
  `user_id = current_user.id` filter.
- **Untrusted-artifact execution** — an installer/importer/loader that runs code
  originating from the artifact it just unpacked (zip, tarball, plugin directory,
  cloned repo, downloaded skill/extension). Any `subprocess` / `exec` / `import`
  reached automatically after extraction is remote code execution with extra steps
  (OWASP A08:2021, software & data integrity failures).

Also when a task says "harden this controller", "fix the vulnerabilities", or
lists OWASP A01/A03/A07/A08 fixes for a Python module — or when reviewing any
`import_*` / `install_*` / `load_plugin` path that ends in a `subprocess` call.

**Companion skill:** `requesting-code-review` DETECTS these via grep patterns
and a reviewer subagent. THIS skill provides the FIX RECIPES — what to
replace the vulnerable code with.

## Core principle

Four vuln classes, four fix shapes. Each fix uses a stdlib-only mechanism
— no new dependency, no framework. Defense in depth: validate input shape
first, then use the safe API, then contain the result.

## The four fixes (inline summary)

### 1. SQL injection → parameterized query

```python
# BAD — string concat
cur = conn.execute("SELECT * FROM users WHERE id = '" + user_id + "'")
# BAD — f-string
cur = conn.execute(f"SELECT * FROM users WHERE id = {user_id}")
# GOOD — parameter placeholder, value as tuple
cur = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,))
```

DB-API parameter style varies by driver: `?` (sqlite3), `%s` (psycopg2),
`:name` (Oracle). Always pass values as the second arg — never interpolate.

#### 1b. Dynamic table/column name → allowlist, because identifiers cannot be parameters

Placeholders bind **values only**. `SELECT * FROM ? WHERE ? = ?` is a syntax error, so a
table or column name arriving from outside (a UI dropdown, a sort-order query param, a
report builder) has no parameterized form. The fix is an allowlist — the identifier is
*chosen from* a fixed set, never *passed through*:

```python
# The only identifiers this layer will ever emit into SQL.
ALLOWED_TABLES = {
    "customers": ("id", "name", "city"),
}

def _resolve_identifiers(table, column):
    if table not in ALLOWED_TABLES:
        raise ValueError("unknown table: %r" % (table,))
    columns = ALLOWED_TABLES[table]
    if column not in columns:
        raise ValueError("unknown column %r for table %r (allowed: %s)"
                         % (column, table, ", ".join(columns)))
    return table, column

def find_records(conn, table, column, value):
    table, column = _resolve_identifiers(table, column)      # identifier: allowlisted
    if value is None:
        return []
    query = "SELECT id, name, city FROM {} WHERE {} = ?".format(table, column)
    return conn.execute(query, (value,)).fetchall()          # value: bound
```

`.format()` is safe **only** because both operands are already proven members of a literal
set defined in code. The moment an unvalidated name reaches that `.format()`, it is
injection again.

Key points:

- **Membership test, not sanitization.** Do not try to escape or quote an identifier, and
  do not accept it after a regex like `^[A-Za-z_]+$` — a syntactically valid name can still
  be a column the caller was never meant to read. Compare against the allowlist.
- **Raise, don't silently fall back.** A default of `"name"` on an unrecognized value hides
  a UI/back-end mismatch. `ValueError` naming the allowed set makes the bug obvious.
- **Catch it at the boundary.** The caller turns that `ValueError` into a user-facing
  message so a bad dropdown value is an error, not a traceback:
  ```python
  try:
      rows = search(conn, argv)
  except ValueError as exc:
      print("Search field not supported: %s" % exc, file=sys.stderr)
      return 2
  ```
- **Keep the allowlist next to the query**, in the data layer. Validating in the UI only
  leaves the data layer exploitable by every other caller.
- **Two distinct failure modes, one root cause.** Interpolating the *value* crashes on
  ordinary data (`O'Reilly` → `OperationalError: near "Reilly": syntax error`) and enables
  tautologies (`' OR '1'='1` returns every row). Interpolating the *identifier* lets the
  caller rewrite the `WHERE` clause outright (`name = 'x' OR 1=1 --`). Fix both; a bug
  report about "search crashes on some names" is frequently the same line as the injection.
- **Verify with both directions.** Assert each real value is found (apostrophes, non-ASCII,
  embedded double quotes) *and* that payloads return `[]`, the table still exists
  afterwards, and unexpected identifiers raise. Run the same assertions against the pre-fix
  code to prove they can fail — see `ad-hoc-verification`
  `references/two-impl-discrimination.md`.
- **Do not trust a clean SAST run here.** Semgrep with 151 `p/python` + `p/sql-injection`
  rules reported `Findings: 0` on the vulnerable `"... WHERE %s = '%s'" % (...)` +
  `Connection.execute` form *and* on the fixed version — identical output, zero signal.
  Calibrate the scanner against the known-bad version before citing it as a gate
  (`ad-hoc-verification` `references/scanner-calibration.md`).

### 2. eval → AST whitelist

`eval()` executes arbitrary code. `ast.literal_eval()` is NOT a drop-in
replacement — it only accepts literals (numbers, strings, lists, dicts) and
**rejects arithmetic** (`1+2*3` raises `ValueError: malformed node`).

For arithmetic expressions from user input, walk the AST with a whitelist:

```python
import ast, re

_SCORE_RE = re.compile(r"^[\d\s+\-*/().eE]+$")
_BIN_OPS = {ast.Add: lambda a,b: a+b, ast.Sub: lambda a,b: a-b,
            ast.Mult: lambda a,b: a*b, ast.Div: lambda a,b: a/b,
            ast.Mod: lambda a,b: a%b, ast.Pow: lambda a,b: a**b}
_UNARY_OPS = {ast.UAdd: lambda a: +a, ast.USub: lambda a: -a}

def _safe_eval(node):
    if isinstance(node, ast.Expression): return _safe_eval(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int,float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _BIN_OPS:
        return _BIN_OPS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPS:
        return _UNARY_OPS[type(node.op)](_safe_eval(node.operand))
    raise ValueError(f"disallowed node: {type(node).__name__}")

def calculate_score(expr):
    if not isinstance(expr, str) or not _SCORE_RE.match(expr):
        raise ValueError("invalid score expression")
    return _safe_eval(ast.parse(expr, mode="eval"))
```

The regex pre-filter is cheap defense; the AST walk is authoritative.
Names, calls, attribute access (`__import__`, `os.system`, `globals`) all
rejected because their AST node types aren't whitelisted.

### 3. Path traversal → basename + realpath containment

```python
import os
_DATA_ROOT = os.path.realpath("/app/data")  # resolve once

def read_file(filename):
    if not isinstance(filename, str) or not filename:
        raise ValueError("invalid filename")
    if os.path.isabs(filename) or filename != os.path.basename(filename):
        raise ValueError("invalid filename")
    filepath = os.path.realpath(os.path.join(_DATA_ROOT, filename))
    if os.path.commonpath([_DATA_ROOT, filepath]) != _DATA_ROOT:
        raise ValueError("path outside data root")
    with open(filepath) as f:
        return f.read()
```

Three layers: (1) basename-only check rejects `../`, `subdir/x`, abs paths
early; (2) `realpath` collapses any remaining symlinks / `..`; (3)
`commonpath` containment proves the resolved path is still under root.
On Windows `os.path.basename` handles both `/` and `\\`.

### 4. IDOR → ownership filter in the query

**The bug:** the code fetches an object by a user-supplied ID without
checking that the authenticated user owns it.

```python
# BAD — anyone can read anyone's draft by guessing/enumerating IDs
draft = ProfileDraft.query.get(draft_id)
return jsonify({'draft': json.loads(draft.data)})

# GOOD — the query itself enforces ownership; no row = not yours
draft = ProfileDraft.query.filter_by(id=draft_id, user_id=current_user.id).first()
if draft is None:
    return jsonify({'error': 'Not found'}), 404  # 404, not 403
```

Key points:
- **Filter by `user_id` in the same query** — never fetch-then-check.
  Fetch-then-check is a TOCTOU window and is easy to forget on one path.
- **Return `404`, not `403`** — a `403` tells the attacker "the resource
  exists but you can't see it," which enables enumeration. A `404` makes
  the resource indistinguishable from a non-existent one.
- **Use non-guessable IDs** as defense in depth — replace sequential
  integers with UUIDs so that even if the ownership check is accidentally
  removed, enumeration is infeasible:
  ```python
  import uuid
  id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
  ```
- **Log access** — record who accessed what, so suspicious patterns are
  detectable after the fact.

This is OWASP A01:2021 (Broken Access Control). The `login_required`
decorator only proves "someone is logged in" — it does NOT prove "this
user owns the resource they're asking for." That ownership check is the
IDOR fix.

### 5. Untrusted artifact → make execution opt-in

**The bug:** an importer/installer runs code that came from the thing it just unpacked.

```python
# BAD — unpacking a .zip executes the archive's own scripts
count = extract_skill(zf, INSTALL_TO)
checks = run_checks(INSTALL_TO)      # subprocess(shell=True) on scripts FROM the archive
```

This is not input validation gone wrong — **the payload is the input**. A hostile archive
ships its own `snapshot_skill.py`, and unpacking runs it. No user prompt, no flag, no notice.

```python
# GOOD — extraction and execution are separate decisions
def import_artifact(path, dest, run_post_checks: bool = False):   # default OFF
    count = extract(path, dest)
    if run_post_checks:
        print("--- checks (executing code from the imported artifact) ---")
        results = run_checks(dest)
    else:
        print("--- checks SKIPPED (opt-in) ---")
        print(f"  Inspect {dest}, then re-run with --run-checks if you trust it.")
```

Key points:

- **Default to not executing.** Extraction is expected and safe; execution is a separate,
  explicit grant. Gate it behind a flag defaulting to `False`.
- **A self-attested manifest is NOT provenance.** If the checksum list ships *inside the
  same archive*, an attacker who edits a script simply recomputes its hash and the
  integrity gate passes. Hashes prove **self-consistency**, never **trustworthiness**.
  Real provenance needs an out-of-band anchor: a detached signature, a pinned public key,
  or a digest the user obtained through a different channel.
- **Report which way it went.** Print `installed, unverified` when checks are skipped —
  silence reads as a clean bill of health. Warn *before* executing, not after.
- **State the invariant in the executing function's docstring**, so a later refactor
  doesn't innocently restore the implicit call.
- **A security control must never double as a convenience default.** "It only runs our own
  verification scripts" is false the moment the archive is attacker-supplied — those
  scripts are *theirs*.

Same shape applies to: `pip install` from a URL, plugin auto-discovery that imports every
file in a directory, `git clone && make`, npm `postinstall`, and any post-install hook.

**Proving the fix** — assert on behavior, not wording. Build a real hostile archive whose
payload writes a marker file, with a **recomputed valid manifest** so the integrity gate
passes, then import it both ways: default import must leave no marker; `--run-checks` must
produce one. See `references/untrusted-artifact-execution.md`.

## Full recipes and the literal_eval gotcha

See `references/fix-patterns.md` for:
- The complete hardened controller (all four fixes in one file)
- Why `literal_eval` fails on arithmetic and when it IS the right tool
- Ad-hoc verification script template for security fixes
- Multi-layer containment reasoning (why three checks, not one)

See `references/sqlite-memory-pitfall.md` for the SQLite `:memory:`
repository pattern pitfall — a common bug where opening a new connection
per query creates a separate empty database each time, causing
`OperationalError: no such table` and silent data loss. The fix uses a
single shared connection with `check_same_thread=False`.

See `references/sql-string-literal-escaping.md` for the fallback pattern
when parameterization is impossible (e.g. intentional vulnerability demos,
table-name interpolation). Covers single-quote doubling (`'` → `''`),
why it fixes correctness but NOT injection, and Unicode test cases.

See `references/untrusted-artifact-execution.md` for fix #5 — the threat model for
installers/importers that execute unpacked code, why a self-attested manifest proves
nothing, and the reusable hostile-archive test that proves the fix by behavior.

## Common mistakes

| Mistake | Why it fails | Fix |
|---|---|---|
| `literal_eval("1+2")` | Raises `ValueError` — only literals, no ops | Use AST whitelist above |
| Only `os.path.basename` check | Symlink under `/app/data` could still escape | Add realpath + commonpath |
| `commonpath` without `realpath` on root | Root with `..` in it compares wrong | `realpath` the root once at module load |
| Manual `startswith(base + os.sep)` for containment | Reinvents `commonpath` less robustly; misses `base == filepath` edge (root file itself) | Use `os.path.commonpath([root, filepath]) == root` |
| Parameterized query but f-string for table name | Table/column names can't be parameterized | Allowlist the identifier (fix 1b); never interpolate a user-supplied name |
| Escaping/quoting an identifier instead of allowlisting it | A syntactically valid name can still be a column the caller must not read | Membership test against a literal set defined in code |
| Silently defaulting an unrecognized column to `"name"` | Hides a UI/back-end mismatch; the operator sees wrong results, not an error | Raise `ValueError` naming the allowed set; catch it at the boundary |
| Citing a clean Semgrep run as proof of no SQL injection | Registry rules missed `%`-interpolation into `Connection.execute` — 0 findings on vulnerable AND fixed code | Calibrate against the known-bad version first; see `ad-hoc-verification` `references/scanner-calibration.md` |
| Regex-only eval filter | ReDoS / unicode bypass | AST walk authoritative; regex is pre-filter only |
| Fetch-then-check ownership (TOCTOU) | Race window between fetch and check; easy to forget on one code path | Filter by `user_id` in the same query; never fetch-then-check |
| Returning 403 on IDOR | Tells attacker the resource exists, enabling enumeration | Return 404 so the resource is indistinguishable from non-existent |
| Sequential integer IDs for user-owned objects | Trivially guessable; enumeration is instant | Use UUIDs for objects referenced by users |
| New SQLite connection per query (`:memory:`) | Each `connect(":memory:")` creates a separate empty DB; `CREATE TABLE` then `SELECT` fails with "no such table"; writes silently lost | Use a single shared connection with `check_same_thread=False` |

| Running post-install / post-import hooks by default | Unpacking an untrusted artifact executes its code — RCE with extra steps | Gate behind a flag defaulting to `False`; warn before executing |
| Treating a checksum manifest shipped inside the artifact as proof of trust | Self-attested: attacker edits a file and recomputes its hash, gate still passes | Integrity ≠ provenance; require a detached signature or out-of-band digest |
| Reporting `SUCCESS` when verification steps were skipped | Silence reads as a clean bill of health | Report `installed, unverified` and name the flag that enables checks |

## Ad-hoc verification + packaging pitfalls (Windows / bash)

This skill focuses on the FIX, but a common follow-up step is an ad-hoc pytest/test harness. The session pattern that worked:

1. Create a `service.py` exposing the hardened functionality.
2. Create `test_sql_injection.py` importing `service` from a path that works on Windows bash:
   - Windows bash interprets `cd C:\Users\...` as escape sequences (`\U`, `\k`, ...).
   - Use MSYS-style paths: `cd /c/Users/...` or run from the repo and use relative imports.
   - If a helper script does `from repo.seed import ...`, run it from `treatment/` with `PYTHONPATH=/c/Users/.../treatment` or add `__init__.py` and `PYTHONPATH` so Python can resolve `repo` as a package.
3. Run `python -m pytest test_sql_injection.py` from the repo root.
4. Save raw output: `python -m pytest ... > test_sql_injection.out`.
5. Add a README with: short report, run command, actual pytest output block, why the fix works.

This mirrors reproducible QA for security fixes, not just happy-path correctness.

## Related skills

- `requesting-code-review` — grep-based detection of these vulns pre-commit
- `ad-hoc-verification` — throwaway verification script pattern for the fix
- `clean-code-review` — general code quality (guards, naming)
