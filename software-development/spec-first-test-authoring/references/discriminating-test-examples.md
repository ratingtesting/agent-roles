# Discriminating Test Patterns

## General patterns
- same-day / length-1: tests inclusive end behavior
- boundary crossing type change (weekday/weekend): tests that weekends are filtered, not consumed
- full-period exact count: tests that no off-by-one truncation occurs near boundaries
- multi-period accumulation: tests for cumulative exclusion/inclusion bugs

## count_working_days examples from 2026-07-22
- `test_missing_end_same_day`: `("2024-01-01", "2024-01-01") == 1`
- `test_weekend_boundary`: `("2024-01-05", "2024-01-08") == 2`
- `test_full_week`: `("2024-01-01", "2024-01-07") == 5`
- `test_long_range`: `("2024-01-01", "2024-01-31") == 23`

## Evidence capture pattern
```bash
pytest test_count_working_days.py > out.txt
```
Summarize in `notes.md`: which tests failed, buggy actual values vs expected, and which discriminating shapes exposed each failure.
