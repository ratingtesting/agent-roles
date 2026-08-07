# Weekend weekday bug: `2026-01-01` Thursday case

## Observed behavior
A function `is_weekend(d)` is expected to return `False` for Thursday dates.
For `date(2026, 1, 1)` the buggy implementation returned `True`.

## Root cause
Off-by-one / wrong axis in weekday mapping. Common variants:
- `d.day` instead of `d.weekday()`
- `isoweekday()` with threshold `>= 7` instead of `>= 5`
- Swapped weekend detection (`<= 1`) vs weekday range

## Fix shape
Use `d.weekday()` and check `>= 5` for Saturday/Sunday.
That matches real Python semantics and all weekday code in existing `count_working_days` files in this workspace.

## Quick reproduce
```python
from datetime import date
assert is_weekend(date(2026, 1, 1)) is False  # Thursday
assert is_weekend(date(2026, 1, 3)) is True   # Saturday
assert is_weekend(date(2026, 1, 4)) is True   # Sunday
```

## Verification pattern used here
Importlib load of absolute `check_date.py` path inside a temp `hermes-verify-...py` script. Five cases asserted, all passed, temp script removed.

## Windows cleanup note
After running, delete the temp verify script with `rm -f`, not `del`; this host uses bash/MSYS.
