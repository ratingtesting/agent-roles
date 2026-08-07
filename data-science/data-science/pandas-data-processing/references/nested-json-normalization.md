# Nested JSON Normalization

Concrete worked example for the nested-envelope → flat-DataFrame pattern.

## Problem

Input file `data.json`:
```json
{"items": [{"id": 1, "value": 10, "category": "A"}, {"id": 2, "value": 20, "category": "B"}, {"id": 3, "value": 30, "category": "A"}]}
```

Naïve expectation: `pd.read_json` yields a 3-row frame with columns `id, value, category`.

Actual: it yields a **1-row, 1-column** DataFrame where the single column `items` holds a list (or dict) per cell. The envelope `{"items": ...}` is treated as one record, not unwrapped.

## Fix — two-step normalize

```python
def load(self):
    df = pd.read_json(self.path, typ="frame")   # 1 col "items", dict/list cells
    items = df["items"].tolist()                 # -> list of dicts
    return pd.DataFrame(items)                   # flat 3-row frame
```

Why not `pd.json_normalize` directly? It takes a dict or list, not a file path. You'd need to parse JSON first via `json` module anyway, losing `read_json`'s dtype inference. The `read_json → tolist → DataFrame` chain keeps dtype inference and is one line.

## Alternatives by input shape

| Input shape | Parser | Notes |
|---|---|---|
| `{"items": [...]}` envelope | `pd.read_json → ["items"].tolist() → pd.DataFrame` | This skill's default. Keeps dtype inference. |
| `{"items": [...]}` from already-parsed dict | `pd.json_normalize(data["items"])` | Skips file IO; use when dict already in hand. |
| JSON-LINES (one obj per line, no envelope) | `pd.read_json(path, lines=True)` | `lines=True` is the key; no normalization needed. |
| Deeply nested with nested arrays | `pd.json_normalize(data, record_path="items", meta=["parent_field"])` | `meta` pulls sibling fields into rows. |

## Failure mode if skipped

Aggregating the un-normalized 1-col frame:
```python
df.groupby("category")["value"].sum()  # KeyError: 'category' — column doesn't exist
```
The error is clear, but only if you run it. A session that asserts "should work" without running will ship a broken processor.

## Verification

```python
df = JSONDataProcessor("data.json").load()
assert set(df.columns) == {"id", "value", "category"}, df.columns
assert len(df) == 3
assert df["value"].sum() == 60
```
