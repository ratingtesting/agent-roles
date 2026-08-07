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

Also when a task says "harden this controller", "fix the vulnerabilities", or
lists OWASP A01/A03/A07 fixes for a Python module.

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

## Common mistakes

| Mistake | Why it fails | Fix |
|---|---|---|
| `literal_eval("1+2")` | Raises `ValueError` — only literals, no ops | Use AST whitelist above |
| Only `os.path.basename` check | Symlink under `/app/data` could still escape | Add realpath + commonpath |
| `commonpath` without `realpath` on root | Root with `..` in it compares wrong | `realpath` the root once at module load |
| Manual `startswith(base + os.sep)` for containment | Reinvents `commonpath` less robustly; misses `base == filepath` edge (root file itself) | Use `os.path.commonpath([root, filepath]) == root` |
| Parameterized query but f-string for table name | Table/column names can't be parameterized | Whitelist allowed identifiers; never user-supplied |
| Regex-only eval filter | ReDoS / unicode bypass | AST walk authoritative; regex is pre-filter only |
| Fetch-then-check ownership (TOCTOU) | Race window between fetch and check; easy to forget on one code path | Filter by `user_id` in the same query; never fetch-then-check |
| Returning 403 on IDOR | Tells attacker the resource exists, enabling enumeration | Return 404 so the resource is indistinguishable from non-existent |
| Sequential integer IDs for user-owned objects | Trivially guessable; enumeration is instant | Use UUIDs for objects referenced by users |
| New SQLite connection per query (`:memory:`) | Each `connect(":memory:")` creates a separate empty DB; `CREATE TABLE` then `SELECT` fails with "no such table"; writes silently lost | Use a single shared connection with `check_same_thread=False` |

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
