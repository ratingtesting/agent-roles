# Windows secret-bait write_file redaction pitfall

## Observation

Leave an intentional fake token in `notify.py` and write it:

```
API_KEY = "sk-LlR2_test_py_key_12345"
```

After `write_file` returns success, `read_file` shows:

```
API_KEY = "«redacted:sk-…»"
```

The source no longer contains the exact fake token.

## Why it matters

R2-secrets-style control work often needs deterministic probe strings. On the affected Windows footing, model-authored writes seem to be rewritten automatically when they match a key/vendor pattern, thwarting A/B assertions and honest gitleaks regression tests.

## Workaround

For control checks, prefer sentinels that will not be rewritten:

```python
API_KEY = "REDACTED"  # sentinel that does not match a key pattern
```

Environment-only verification is even safer:

```python
# never write a key-shaped value to source
os.environ["API_KEY"] = "fake-for-tests"
src = (base / "notify.py").read_text(encoding="utf-8")
assert "API_KEY" in src
```

If the control explicitly requires an `sk-...` string in source, do that last and only after confirming the write path is not rewriting.

## How to detect regressions

1. Write a sentinel string that should be safe.
2. Read the file back immediately.
3. If the content differs from what you wrote, switch to env-injection or transparent sentinels for the rest of the session.
