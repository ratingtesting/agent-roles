---
name: pandas-data-processing
description: Use when building data processing modules with pandas — parsing nested JSON, validating schema, aggregating with groupby, structuring a processor class. Encapsulates load/validate/aggregate patterns and the nested-JSON normalization technique.
version: 0.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [pandas, data-processing, json, aggregation, validation]
    related_skills: [jupyter-live-kernel, verification-before-completion]
---

# pandas Data Processing

## Overview

Build production-grade data processors around pandas: parse → validate → aggregate → summarize. This skill covers the recurring shape — a processor class with small SRP methods, schema validation at trust boundaries, and aggregation to a plain dict. It is NOT a pandas tutorial; it assumes you know `DataFrame`/`Series` basics.

## When to Use

- Building a `DataProcessor` / `JSONDataProcessor` class that parses, validates, and aggregates.
- Ingesting nested JSON (`{"items": [...]}`) into a flat DataFrame.
- Aggregating values grouped by a category column into a summary dict.
- Needing schema validation (required columns, null guards) before aggregation.

Don't use for:
- One-off `df.groupby` in a notebook — just do it inline.
- Streaming/large-file ingestion where pandas is the wrong tool (use `polars`/`duckdb`/chunking).
- ETL pipelines with multiple sources/joins — that's a broader pipeline skill, not this one.

## The Processor Shape

One class, four small methods, one responsibility each (SRP):

```python
class JSONDataProcessor:
    def __init__(self, path): ...   # store path/config, no IO
    def load(self): ...             # parse → DataFrame
    def validate(self, df): ...     # schema + null guards, returns df or raises
    def aggregate(self, df): ...    # groupby → dict
    def summary(self): ...         # orchestrator: load → validate → aggregate
```

Rules:
- `__init__` does NO IO. Pass paths/config, store, return.
- Each method does ONE thing. `summary()` is the only orchestrator.
- `validate` raises on schema violation — do not return `None`/error dicts. Schema failure is a trust-boundary error, not a value.
- Guard clauses (missing columns, nulls) come BEFORE any aggregation mutation.

## Parsing Nested JSON

`pd.read_json` on `{"items": [...]}` returns a **1-column DataFrame of dicts**, not the flat table you want. Normalize:

```python
df = pd.read_json(path, typ="frame")          # 1 col: "items" with dict cells
items = df["items"].tolist()                    # list of dicts
return pd.DataFrame(items)                      # flat frame
```

Alternatives (pick by shape):
- `pd.json_normalize(data["items"])` — works from a parsed dict, skips the read_json round-trip. Use when you already have the dict.
- `pd.read_json(path, lines=True)` — only when the file is JSON-LINES (one object per line), not a nested envelope.

See `references/nested-json-normalization.md` for the concrete worked example and the failure mode.

For multi-format ingestion (CSV/Excel/Parquet) behind a single dispatch, see
`references/abc-reader-hierarchy.md` for the ABC base class + registry factory pattern.

## Schema Validation

At trust boundaries (external file, user input), validate BEFORE aggregating:

```python
REQUIRED_COLUMNS = ("id", "value", "category")

def validate(self, df):
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise SchemaError(f"missing columns: {missing}")
    if df[["id", "value"]].isna().any().any():
        raise SchemaError("null in id or value")
    return df
```

- Custom `SchemaError(ValueError)` — named exception beats generic `ValueError` for callers catching it.
- Check columns first, then nulls (null check on missing columns crashes — order matters).
- `df[cols].isna().any().any()` — double `.any()` collapses frame → Series → scalar bool. Concise and correct.

Do NOT simplify away: validation at trust boundaries is a reuse-ladder exception (see `vibe-loop`).

## Aggregation to Dict

```python
def aggregate(self, df):
    grouped = df.groupby("category", as_index=False)["value"].sum()
    return grouped.set_index("category")["value"].to_dict()
```

- `as_index=False` keeps `category` as a column, then `set_index` → `to_dict()` gives `{category: sum}`. Alternatively `groupby("category")["value"].sum().to_dict()` directly.
- Return a plain `dict`, not a DataFrame — summary consumers want a value, not a frame.

## Verification (non-negotiable)

Before claiming done — run, don't assert:

| Gate | Command |
|------|---------|
| Syntax | `python -m py_compile <file>` |
| Lint | `ruff check <file>` |
| Tests | `python -m pytest -q` |
| Smoke | `python <file>` (prints summary) |

If workspace has no canonical test command, produce fresh evidence via an ad-hoc `hermes-verify-<topic>.py` script under the OS temp dir, run it, clean up, and report as ad-hoc (not suite green). See `verification-before-completion` skill.

## Common Pitfalls

1. **`pd.read_json` on nested envelope returns 1-col of dicts.** Normalize via `.tolist()` → `pd.DataFrame(list)`. See references.

2. **Null check on missing column crashes.** Check column existence BEFORE null checks. Order: missing → nulls.

3. **`groupby(...).sum()` returns a Series with the group key as index, not a dict.** Chain `.to_dict()` to materialize.

4. **Doing IO in `__init__`.** Defers errors and couples construction to filesystem. `__init__` stores path; `load()` does IO.

5. **Returning error dict instead of raising.** Schema failure is a trust-boundary violation — raise `SchemaError`, let callers decide. Returning `{"error": ...}` forces every caller to branch.

6. **Skipping tests because "it's just pandas."** groupby edge cases (empty groups, nulls, single group) bite. One happy-path test + one rejection test per validation rule is the floor.

## Reuse Ladder (before adding code)

- L2 stdlib `json`/`pathlib` for IO glue + serialization — don't reach for pandas for file reads.
- L3 pandas already installed — check `pip show pandas` before installing; no-op if present.
- L5 minimal class — four methods, no base class, no config dataclass for a value that never changes.
- Skip type hints + `pandas-stubs` unless CI enforces mypy (`ponytail:` add when typecheck gated in CI).

## Verification Checklist

- [ ] `python -m py_compile` passes
- [ ] `ruff check` passes (no unused imports — common slip)
- [ ] `pytest -q` passes (≥ happy path + one rejection per validation rule)
- [ ] Smoke run prints expected summary dict
- [ ] Committed to git with descriptive message
