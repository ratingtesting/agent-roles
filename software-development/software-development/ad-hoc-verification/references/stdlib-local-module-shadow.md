# Local module shadowing a stdlib package

## Symptom

```
ImportError while importing test module '.../test_math.py'.
E   ImportError: cannot import name 'divide' from 'math' (unknown location)
```

The test file says `from math import divide`, but pytest imports Python's real stdlib `math`, not the local `math.py`.

## Why

A qualified import like `from math import divide` only puts the import's
directory on `sys.path`, and `pytest` injection uses the test file's parent.
When the local `math.py` is not the package `math` active during collection,
`math` resolves to stdlib.

## Fix order

1. Run pytest from the parent directory that contains the control/treatment
   folder.
2. Add `pythonpath = [".."]` in `pytest.ini` / `pyproject.toml`.
3. Add `conftest.py` with:

```python
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
```

## Layout rule

Avoid naming source modules the same as stdlib packages in repos where tests
use standard `from <module> import <name>`.
