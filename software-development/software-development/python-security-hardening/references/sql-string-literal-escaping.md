# SQL String-Literal Escaping (Fallback When Parameterization Is Impossible)

## When this applies

Parameterization (`?` / `%s` / `:name`) is the **always-preferred** fix for SQL
injection. But there are rare cases where you must interpolate a value into a
SQL string literal directly — e.g. a demo that intentionally shows the
vulnerable pattern, a table-name whitelist that must be spliced in, or a
legacy code path that cannot be refactored to use placeholders.

In those cases, you MUST at minimum escape single quotes by doubling them:
`'` → `''`. This is the SQL standard escape for a literal single-quote inside
a string literal.

## The pattern

```python
# BAD — breaks on O'Reilly, enables injection
query = f"SELECT * FROM users WHERE name = '{name}'"

# MINIMUM ESCAPING — handles apostrophes, but NOT injection-proof
safe_name = name.replace("'", "''")
query = f"SELECT * FROM users WHERE name = '{safe_name}'"

# PREFERRED — parameterized, no escaping needed
query = "SELECT * FROM users WHERE name = ?"
cur.execute(query, (name,))
```

## Why escaping alone is NOT enough

Doubling single quotes prevents syntax errors from apostrophes in data, but
it does **not** prevent SQL injection. A value like `'; DROP TABLE users; --`
becomes `'; DROP TABLE users; --` after escaping (no change, since there are
no single quotes to double) and still executes as multiple statements.

Escaping is a **correctness** fix (so `O'Reilly` doesn't crash), not a
**security** fix. Parameterization is the security fix.

## Unicode support

SQLite handles UTF-8 natively. Names like `José`, `Мария`, `中文用户` work
correctly in both parameterized queries and escaped string literals — no
special handling needed beyond ensuring the connection uses UTF-8 (the
default in Python 3).

## Test cases to verify

Always test with:
- Names containing apostrophes: `O'Reilly`
- Unicode names: `José`, `Мария`, `中文用户`
- SQL injection attempts: `' OR '1'='1`, `'; DROP TABLE users; --`
- Non-existent names (should return `None`, not error)

## See also

- `python-security-hardening` → Section 1: SQL injection → parameterized query
- `references/sqlite-memory-pitfall.md` for the `:memory:` connection pitfall