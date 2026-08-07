# Naive UTC datetimes with SQLAlchemy + SQLite

## Problem

SQLite (via SQLAlchemy) stores `DateTime` columns as **naive** datetimes (no
timezone info). When you compare a stored value against
`datetime.now(timezone.utc)` (which is **offset-aware**), Python raises:

```
TypeError: can't compare offset-naive and offset-aware datetimes
```

This bites in two places:
1. **Column defaults** — `default=lambda: datetime.now(timezone.utc)` stores an
   aware datetime, but SQLAlchemy/SQLite strips the tzinfo on round-trip.
2. **Runtime comparisons** — `if datetime.now(timezone.utc) > token.expires_at`
   fails because `token.expires_at` comes back naive from the DB.

## Fix: `utcnow()` helper returning naive UTC

```python
from datetime import datetime, timezone

def utcnow() -> datetime:
    """Naive UTC datetime — compatible with SQLite/SQLAlchemy storage."""
    return datetime.now(timezone.utc).replace(tzinfo=None)
```

Use `utcnow()` everywhere instead of `datetime.now(timezone.utc)`:

- Column defaults: `default=utcnow` (pass the callable, not a lambda)
- `onupdate=utcnow`
- Runtime comparisons: `if utcnow() > token.expires_at`
- Test assertions: `assertGreater(token.expires_at, utcnow())`

## Why not just use `datetime.utcnow()`?

`datetime.utcnow()` is **deprecated in Python 3.12+** (emits `DeprecationWarning`).
The `utcnow()` helper above avoids the deprecation while producing the same naive
UTC result that SQLite expects.

## When this matters

- SQLite backend (default for Flask dev / many small apps)
- Any SQLAlchemy backend that strips tzinfo on storage
- Token expiry checks, session timeouts, audit timestamps

## PostgreSQL note

PostgreSQL stores tz-aware datetimes natively. If you switch from SQLite to
Postgres, the `utcnow()` helper still works (naive UTC is interpreted as the
session timezone, which defaults to UTC). No code change needed.