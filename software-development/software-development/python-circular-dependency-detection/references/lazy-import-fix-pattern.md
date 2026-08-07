# Lazy Import Fix Pattern (Session: user.py / profile.py)

## Scenario

Two modules with a direct mutual import cycle, where neither can be extracted into a shared module because both sides need the other's runtime functions/classes:

```python
# user.py
from profile import get_profile_name

class User:
    def get_display_name(self):
        return f"{self.name} ({get_profile_name(self.profile_id)})"
```

```python
# profile.py
from user import User

def create_user_with_profile(name, profile_id):
    return User(name=name, profile_id=profile_id)
```

## Problem

- `import user` → triggers `from profile import get_profile_name` → triggers `from user import User` → `User` not yet defined → `ImportError`
- `import profile` → triggers `from user import User` → triggers `from profile import get_profile_name` → `get_profile_name` not yet defined → `ImportError`
- Both import orders fail.

## Fix: Lazy Import (Deferred Import)

Move the import statement inside the function/method body so it executes at call time, not at module load time:

```python
# user.py — FIXED
class User:
    def __init__(self, name, profile_id):
        self.name = name
        self.profile_id = profile_id

    def get_display_name(self):
        from profile import get_profile_name  # lazy import
        return f"{self.name} ({get_profile_name(self.profile_id)})"
```

```python
# profile.py — FIXED
PROFILE_NAMES = {1: "Admin", 2: "Editor", 3: "Viewer"}

def get_profile_name(profile_id):
    return PROFILE_NAMES.get(profile_id, "Unknown")

def create_user_with_profile(name, profile_id):
    from user import User  # lazy import
    return User(name=name, profile_id=profile_id)
```

## Why This Works

- At module load time, neither module tries to import the other — the import statements are inside function bodies, not at module scope.
- When a function is actually called, the other module is already fully loaded, so the import succeeds.
- The module-level names (`User`, `get_profile_name`) are available when needed at runtime.

## Pitfall: Stdlib Name Conflicts

`user` and `profile` are both Python standard library module names. This can cause additional import errors:

```
ImportError: cannot import name 'User' from 'user'
  (consider renaming '...\\user.py' if it has the same name as a library
   you intended to import)
```

**Mitigation:** When working in a scratch folder, the local module shadows the stdlib module. This is usually fine for throwaway code, but in production, rename modules to avoid conflicts (e.g., `user_model.py`, `profile_service.py`).

## Verification

Create a `test_imports.py` that imports modules in all possible orders:

```python
import sys

def test_user_first():
    for mod in list(sys.modules.keys()):
        if mod in ("user", "profile"):
            del sys.modules[mod]
    import user
    u = user.User("Alice", 1)
    assert u.get_display_name() == "Alice (Admin)"

def test_profile_first():
    for mod in list(sys.modules.keys()):
        if mod in ("user", "profile"):
            del sys.modules[mod]
    import profile
    u = profile.create_user_with_profile("Bob", 2)
    assert u.get_display_name() == "Bob (Editor)"
```

## When to Use This vs. Other Strategies

| Strategy | Use When |
|----------|----------|
| Lazy import | Cycle is between 2-3 modules, no natural shared abstraction |
| Extract shared module | Both modules use common data/helpers that can live in a third module |
| `TYPE_CHECKING` | Only need the import for type hints, not runtime |
| Architecture refactor | Cycle indicates deeper design problem (e.g., services calling each other) |
