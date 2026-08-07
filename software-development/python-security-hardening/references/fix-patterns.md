# Python Security Hardening — Fix Patterns

Companion to `python-security-hardening/SKILL.md`. Concrete recipes,
the `literal_eval` gotcha in detail, and the ad-hoc verification
template for security fixes.

## Complete hardened controller

All four fixes in one file (the controller fixed in the session that
produced this skill):

```python
"""Hardened user controller — parameterized SQL, safe arithmetic (no eval), safe path reads."""
import ast
import os
import re
import sqlite3

_DATA_ROOT = os.path.realpath("/app/data")
_SCORE_RE = re.compile(r"^[\d\s+\-*/().eE]+$")

_BIN_OPS = {
    ast.Add: lambda a, b: a + b,
    ast.Sub: lambda a, b: a - b,
    ast.Mult: lambda a, b: a * b,
    ast.Div: lambda a, b: a / b,
    ast.Mod: lambda a, b: a % b,
    ast.Pow: lambda a, b: a ** b,
}
_UNARY_OPS = {ast.UAdd: lambda a: +a, ast.USub: lambda a: -a}


def _safe_eval(node):
    """Recursively evaluate an AST node of a numeric/arithmetic expression."""
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body)
    if isinstance(node, ast.Constant):  # py3.8+
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("non-numeric constant")
    if isinstance(node, ast.Num):  # py<3.8 fallback
        return node.n
    if isinstance(node, ast.BinOp) and type(node.op) in _BIN_OPS:
        return _BIN_OPS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPS:
        return _UNARY_OPS[type(node.op)](_safe_eval(node.operand))
    raise ValueError(f"disallowed node: {type(node).__name__}")


def get_user(user_id):
    """Get user by ID — parameterized query."""
    conn = sqlite3.connect("users.db")
    cur = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cur.fetchone()


def calculate_score(expression):
    """Calculate score from arithmetic expression — AST whitelist, no eval."""
    if not isinstance(expression, str) or not _SCORE_RE.match(expression):
        raise ValueError("invalid score expression")
    return _safe_eval(ast.parse(expression, mode="eval"))


def read_file(filename):
    """Read a file under /app/data — reject traversal outside the root."""
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

## The `literal_eval` gotcha in detail

`ast.literal_eval` evaluates Python literal expressions only — strings,
numbers, tuples, lists, dicts, booleans, `None`. It **rejects any
operation**:

```python
>>> from ast import literal_eval
>>> literal_eval("5")
5
>>> literal_eval("[1, 2, 3]")
[1, 2, 3]
>>> literal_eval("1+2")
ValueError: malformed node or string on line 1: <ast.BinOp object at 0x...>
```

The error message (`malformed node or string`) is misleading — the node
is well-formed, it's just not a literal.

**When `literal_eval` IS the right tool:**
- Parsing config values that should be literals (`"True"` → `True`,
  `"[1,2,3]"` → `[1,2,3]`)
- Deserializing trusted-ish data where you want to reject code but
  accept nested structures

**When it is NOT the right tool:**
- Arithmetic from user input (use the AST whitelist in SKILL.md)
- Anything that needs function calls, attribute access, or operators
- Untrusted input where you need to allow expressions (same — AST walk)

The distinction matters because a common first attempt at removing
`eval` is `return literal_eval(expr)` — which breaks every caller using
arithmetic, as it did in the session that produced this skill.

## Multi-layer containment reasoning (path traversal)

Three checks, each catching a different attack class:

| Layer | Check | Catches |
|---|---|---|
| 1 | `filename != os.path.basename(filename)` | `../etc/passwd`, `subdir/x`, `a/b`, absolute paths |
| 2 | `os.path.realpath(...)` | Symlinks under `/app/data` pointing outside |
| 3 | `os.path.commonpath([root, path]) == root` | Anything that resolved above root despite 1-2 |

Why all three:
- Layer 1 alone is bypassable if `/app/data/legit` is a symlink to `/etc`.
- Layer 2 alone (realpath without basename check) is fine but lets users
  specify `subdir/file` which may not be intended — basename-only is a
  stricter policy choice, not just a security measure.
- Layer 3 alone (commonpath without realpath on root) fails if
  `_DATA_ROOT` itself contains `..` or symlinks — resolve root ONCE at
  module load, then compare.

`os.path.commonpath` (not `os.path.commonprefix`) — `commonprefix` is a
string comparison and `'/app/data2'` would match `/app/data` as a prefix.
`commonpath` compares path components.

On Windows: `os.path.basename` handles both `/` and `\` separators.
`os.path.isabs` catches `C:\...` and `\...`. Same three-layer shape works.

## Ad-hoc verification template for security fixes

Throwaway script shape (see `ad-hoc-verification` skill for the general
pattern — this is the security-specific payload):

```python
import importlib.util, os, sqlite3, tempfile, sys

CTRL = r"<absolute path to hardened module>"
spec = importlib.util.spec_from_file_location("ctrl", CTRL)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

failures = []
tmpdir = tempfile.mkdtemp(prefix="hermes-verify-")
os.chdir(tmpdir)
conn = sqlite3.connect("users.db")
conn.execute("CREATE TABLE users (id INTEGER, name TEXT)")
conn.execute("INSERT INTO users VALUES (1, 'alice')")
conn.commit(); conn.close()

# SQL injection — parameterized; injection yields None, not a row
assert mod.get_user(1) == (1, "alice")
assert mod.get_user("1' OR '1'='1") is None
assert mod.get_user("0 UNION SELECT 1, 'admin'") is None

# eval removed — code execution rejected
for payload in ['__import__("os").system("x")', 'open("/etc/passwd").read()',
                'os.system("id")', 'globals()']:
    try:
        mod.calculate_score(payload); failures.append(f"ran: {payload!r}")
    except (ValueError, SyntaxError): pass

# arithmetic still works
assert mod.calculate_score("1+2*3") == 7
assert mod.calculate_score("(2+3)*4") == 20
assert mod.calculate_score("2**10") == 1024
assert mod.calculate_score("-5") == -5

# path traversal rejected
for p in ["../../etc/passwd", "/etc/passwd", r"..\..\windows\win.ini", "subdir/x"]:
    try:
        mod.read_file(p); failures.append(f"traversal: {p!r}")
    except (ValueError, OSError): pass

# legit read works
os.makedirs("/app/data", exist_ok=True)
with open("/app/data/legit.txt", "w") as f: f.write("hi")
assert mod.read_file("legit.txt") == "hi"

print("FAILURES:", failures) if failures else print("ALL CHECKS PASSED")
sys.exit(1 if failures else 0)
```

Key points specific to verifying security fixes:
- **SQL injection success = `None` return**, not an exception. A
  parameterized query with a non-matching ID returns `None`. Don't
  `try/except OperationalError` — that's the pre-fix behavior.
- **eval rejection = `ValueError` or `SyntaxError`**, not `Exception`
  broadly — the regex pre-filter raises `ValueError`, the AST walk
  raises `ValueError`, malformed expressions raise `SyntaxError`.
- **Trivial arithmetic must still pass.** A common regression: the fix
  rejects attacks but also rejects legit use (`1+2*3`). Always test
  both sides.
- **Windows path traversal uses both separators.** Test `..\..\` as
  well as `../../`.

## IDOR / Broken Access Control pattern

**Detection recipe:** when reviewing a controller/handler, look for any place
an object is fetched by a user-supplied ID without an ownership filter.

```python
# VULNERABLE — fetches by ID alone
draft = ProfileDraft.query.get(draft_id)

# VULNERABLE — fetches by ID, then checks ownership separately (TOCTOU)
draft = ProfileDraft.query.get(draft_id)
if draft.user_id != current_user.id:
    abort(403)
```

**Fix:** fold the ownership check into the query itself, and return 404
(not 403) so the resource is indistinguishable from non-existent:

```python
draft = ProfileDraft.query.filter_by(
    id=draft_id, user_id=current_user.id
).first()
if draft is None:
    return jsonify({'error': 'Not found'}), 404
```

**Defense in depth:** use UUIDs instead of sequential integers for any
object ID that users can reference, so enumeration is infeasible even if
the ownership check is accidentally removed.

See `SKILL.md` §4 for the full recipe and the 404-vs-403 reasoning.

## Pitfalls

- **`os.path.commonprefix` vs `os.path.commonpath`** — `commonprefix`
  is a string op; `/app/data2` matches `/app/data`. Use `commonpath`.
- **`realpath` at call time vs module load** — resolve `_DATA_ROOT`
  once at module load. Calling `realpath` every invocation is fine but
  wasteful; the risk is resolving it relative to a cwd that changes.
- **sqlite3 text factory** — if `user_id` is meant to be int, validate
  type before the query too; parameterization prevents injection but
  not type confusion.
- **Regex ReDoS on the eval pre-filter** — the `_SCORE_RE` above is
  linear-time (no backreferences, no nested quantifiers). Don't add
  complexity to it; the AST walk is the real gate.
