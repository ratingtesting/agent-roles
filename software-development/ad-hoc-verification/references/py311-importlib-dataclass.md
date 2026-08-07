# py3.11 + `@dataclass` via importlib

The single most common crash in ad-hoc verification scripts.

## Symptom

Loading a target module by absolute path with
`importlib.util.spec_from_file_location` + `module_from_spec` + `exec_module`
blows up inside `@dataclass` decoration:

```
File ".../python3.11/dataclasses.py", line 712, in _is_type
    ns = sys.modules.get(cls.__module__]).__dict__
AttributeError: 'NoneType' object has no attribute '__dict__'. Did you mean: '__dir__'?
```

Same shape hits `@attrs.define` and any decorator that inspects
`sys.modules` during class body processing.

## Root cause

`dataclasses._is_type` resolves the class's module via
`sys.modules[cls.__module__].__dict__`. But the module isn't registered in
`sys.modules` until `exec_module` RETURNS — and `@dataclass` runs DURING
that exec, before registration completes. The lookup returns `None`, hence
the `AttributeError` on `.__dict__`.

## Fix

Register the module in `sys.modules` BEFORE `exec_module`:

```python
spec = importlib.util.spec_from_file_location("mod_under_test", MOD_PATH)
mod = importlib.util.module_from_spec(spec)
sys.modules["mod_under_test"] = mod  # BEFORE exec_module
spec.loader.exec_module(mod)
```

## When it matters

| Target uses... | Needs pre-registration? |
|---|---|
| `@dataclass` | yes |
| `@attrs.define` / `@attr.s` | yes |
| Plain functions/classes, no decorators inspecting `sys.modules` | no, but harmless |
| Pydantic models (v2) | usually no (uses own registry) |

Registering unconditionally is cheaper than diagnosing per-case. Make it a
habit in every ad-hoc script.

## Variant: same error from a real import

If you see this outside ad-hoc scripts — i.e. from a normal `import` — the
module is being loaded indirectly and `sys.modules` entry is missing mid-
import. That's a different bug (circular import or a broken loader), not the
ad-hoc trap. Don't apply the fix above to normal imports.
