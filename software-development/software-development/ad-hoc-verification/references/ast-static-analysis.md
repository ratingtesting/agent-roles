# AST-Based Static Analysis Verification

## When to use instead of importlib

Importing a target module via `importlib` is the default ad-hoc approach, but fails when:

- The module has **missing dependencies** (e.g. `requests`, `flask`, framework code not installed in the env).
- The module has **dangerous side effects** at import time (network calls, file writes, daemon threads, `atexit` hooks).
- The module's import triggers **circular imports** or requires a complex `sys.path` setup.
- The verification question is about **source structure** (e.g. "is there a hardcoded API key?", "do all functions have type annotations?", "is `eval()` present?").

In all these cases, AST-based static analysis is the right technique.

## How it works

Parse the target with `ast.parse`, walk the tree with `ast.walk` or a custom `ast.NodeVisitor`, and assert on structural properties — without ever importing the module.

## Common patterns

### 1. Syntax validity + no hardcoded secrets

```python
import ast

with open("config.py") as f:
    tree = ast.parse(f.read())

# Check no string literals match known secret prefixes
SECRET_PREFIXES = ["sk-", "SG.", "ghp_", "gho_", "AKIA"]
for node in ast.walk(tree):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        val = node.value.strip()
        if any(val.startswith(p) for p in SECRET_PREFIXES) and len(val) > 12:
            raise AssertionError(f"Hardcoded secret-like value at line {node.lineno}")
```

### 2. Verify a specific function uses `os.getenv`

```python
for node in ast.walk(tree):
    if isinstance(node, ast.Assign):
        targets = [t.id for t in node.targets if isinstance(t, ast.Name)]
        if "API_KEY" in targets:
            assert isinstance(node.value, ast.Call) and \
                   getattr(node.value.func, 'attr', None) == 'getenv', \
                   "API_KEY not assigned via os.getenv"
```

### 3. Check for absence of dangerous functions

```python
dangerous = {"eval", "exec", "compile"}
for node in ast.walk(tree):
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        assert node.func.id not in dangerous, \
               f"{node.func.id}() call at line {node.lineno}"
```

### 4. Verify import style (stdlib-first, no wildcard)

```python
for node in ast.walk(tree):
    if isinstance(node, ast.ImportFrom) and node.names[0].name == "*":
        raise AssertionError(f"Wildcard import at line {node.lineno}")
```

## Limitations

- Cannot verify **runtime behavior** (return values, side effects, exception paths).
- Cannot detect **dynamically constructed strings** (e.g. `API_KEY = os.getenv("API_" + "KEY")` would pass AST check but the pattern is unusual).
- Does **not** execute the code — dead code, type errors, and NameErrors at runtime are invisible.
- When you need runtime behavior verification AND import is blocked, combine AST for structure + `exec(compile(...))` for targeted execution (see `ad-hoc-verification` main SKILL.md `Capture print from ad-hoc exec targets`).

## Combined approach for config modules

For a `config.py` with multiple secrets and missing dependencies:

```python
import ast, os, sys

with open("config.py") as f:
    src = f.read()

# Phase 1: AST analysis — verify structure
tree = ast.parse(src)
for node in ast.walk(tree):
    if isinstance(node, ast.Assign) and [t.id for t in node.targets if isinstance(t, ast.Name)]:
        names = [t.id for t in node.targets if isinstance(t, ast.Name)]
        if "API_KEY" in names or "SENDGRID_KEY" in names:
            assert isinstance(node.value, ast.Call) and \
                   getattr(node.value.func, 'attr', None) == 'getenv', \
                   f"{names[0]} not loaded from env"

# Phase 2: exec-stub — verify runtime guard fires correctly
os.environ.pop("API_KEY", None)
try:
    ns = {}
    exec(compile(src, "config.py", "exec"), ns)
    print("FAIL: should have raised RuntimeError")
except RuntimeError as e:
    assert "API_KEY" in str(e)
    print("PASS: runtime guard fires with descriptive message on missing key")
```
