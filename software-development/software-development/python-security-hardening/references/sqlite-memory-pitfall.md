# SQLite `:memory:` Pitfall — Repository Pattern

## The Problem

When implementing a repository adapter for a Use Case that needs to work
with an in-memory SQLite database, a common mistake is to open a **new
connection per query**:

```python
# ❌ BROKEN — each call creates a SEPARATE empty database
class SqliteUserRepository(UserRepository):
    def get_by_id(self, user_id: int) -> User | None:
        conn = sqlite3.connect(":memory:")  # ← new DB every time!
        conn.execute("CREATE TABLE IF NOT EXISTS users ...")
        row = conn.execute("SELECT ... WHERE id = ?", (user_id,)).fetchone()
        conn.close()
        return User(...) if row else None
```

Even though `CREATE TABLE` ran successfully, the subsequent `SELECT`
fails with `sqlite3.OperationalError: no such table: users` because each
`sqlite3.connect(":memory:")` call creates a **brand-new, empty database**.

## The Fix

Use a **single shared connection** that lives for the lifetime of the
repository instance:

```python
# ✅ CORRECT — one connection, reused across all queries
class SqliteUserRepository(UserRepository):
    def __init__(self, db_path: str = ":memory:") -> None:
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_db()  # creates table + seeds data once

    def get_by_id(self, user_id: int) -> User | None:
        row = self._conn.execute(
            "SELECT id, name, email FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        return User(id=row["id"], name=row["name"], email=row["email"]) if row else None
```

### Key points

1. **`check_same_thread=False`** — SQLite connections are thread-local by
   default. In a Flask app (which may serve requests on different threads),
   you need this flag to share the connection across threads. For
   production with a file-based DB, prefer a connection pool instead.

2. **File-based databases don't have this issue** — `sqlite3.connect("app.db")`
   opens the same file each time, so the table persists. The problem is
   specific to `:memory:`.

3. **For testing** — if you need a fresh database per test, create a new
   `SqliteUserRepository(db_path=":memory:")` instance per test. The
   shared connection ensures the table exists within that instance's lifetime.

4. **Alternative for tests** — use a temporary file path instead of
   `:memory:` if you need per-query connection semantics:
   ```python
   import tempfile, os
   fd, path = tempfile.mkstemp(suffix=".db")
   os.close(fd)
   repo = SqliteUserRepository(db_path=path)
   # ... test ...
   os.unlink(path)
   ```

## Why This Matters for Security

A broken repository that opens new connections per query can lead to
**silent data loss** — writes that appear to succeed but are lost when
the connection closes. This can cause:

- User data not being persisted (false success on writes)
- Inconsistent state between read and write operations
- Race conditions in concurrent access patterns

The fix ensures the repository maintains a consistent, persistent
connection to the database, preserving data integrity across all
operations within a single repository instance.

## Clean Architecture Boundary

The repository adapter is the **outer circle** — it's the only layer that
should know about SQLite. When the `:memory:` bug bites, it's tempting to
move connection management into the Use Case or Controller, which would
violate the Dependency Rule (inner circles depending on outer details).

The fix keeps all connection management **inside the adapter**, preserving
the clean boundary: the Use Case still just calls `repository.get_by_id()`
and gets a `User` entity back, with no knowledge of SQLite internals.
