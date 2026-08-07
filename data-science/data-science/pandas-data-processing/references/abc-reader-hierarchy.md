# ABC Reader Hierarchy Pattern

When a data processor needs to support multiple input formats (CSV, Excel, Parquet, JSON),
use an ABC base class + registry factory instead of a monolithic `if/elif` on file extension.

## Shape

```python
from abc import ABC, abstractmethod
from pathlib import Path
import pandas as pd

PathLike = Union[str, Path]

class BaseReader(ABC):
    """Abstract base for all format readers."""
    EXTENSIONS: tuple[str, ...] = ()

    def __init__(self, path: PathLike) -> None:
        self.path = Path(path)

    @abstractmethod
    def read(self) -> pd.DataFrame:
        """Return the file contents as a DataFrame."""
        raise NotImplementedError

    def _validate_columns(self, df: pd.DataFrame, required: list[str]) -> None:
        """Shared validation helper — check required columns exist."""
        missing = [c for c in required if c not in df.columns]
        if missing:
            raise ValueError(f"{self.path.name} missing columns: {missing}")


class CsvReader(BaseReader):
    EXTENSIONS = (".csv",)
    def read(self) -> pd.DataFrame:
        df = pd.read_csv(self.path)
        self._validate_columns(df, ["amount", "category"])
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
        return df


class ExcelReader(BaseReader):
    EXTENSIONS = (".xlsx", ".xls")
    def read(self) -> pd.DataFrame:
        df = pd.read_excel(self.path)
        self._validate_columns(df, ["amount", "category"])
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
        return df


class ParquetReader(BaseReader):
    EXTENSIONS = (".parquet", ".pq")
    def read(self) -> pd.DataFrame:
        df = pd.read_parquet(self.path)
        self._validate_columns(df, ["amount", "category"])
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
        return df


# Registry: extension -> reader class
_READERS: dict[str, type[BaseReader]] = {}

def _register(cls: type[BaseReader]) -> type[BaseReader]:
    for ext in cls.EXTENSIONS:
        _READERS[ext] = cls
    return cls

_register(CsvReader)
_register(ExcelReader)
_register(ParquetReader)


def get_reader(path: PathLike) -> BaseReader:
    """Factory: dispatch to the right reader by file extension."""
    ext = Path(path).suffix.lower()
    try:
        return _READERS[ext](path)
    except KeyError:
        supported = ", ".join(sorted(_READERS))
        raise ValueError(f"Unknown extension '{ext}'. Supported: {supported}")
```

## Why this shape

- **Adding a format = one class + one `_register` call.** No touching `get_reader` or any
  `if/elif` chain. The registry pattern keeps the dispatch logic open for extension but
  closed for modification (OCP).
- **Shared validation in the base class** — `_validate_columns` is reused by all readers,
  avoiding copy-pasted column checks.
- **`EXTENSIONS` class attribute** makes the supported formats self-documenting and drives
  the registry automatically.
- **`get_reader` returns a `BaseReader`** — callers depend on the abstraction, not concrete
  classes. Easy to mock in tests.

## Usage

```python
from readers import get_reader

reader = get_reader("data.csv")   # returns CsvReader
df = reader.read()

# Or for analytics:
from analyze import compute_analytics
total, avg = compute_analytics(df)
```

## Variant: plain-function registry (no ABC) — prefer this when readers are stateless

An ABC earns its place when subclasses share real state or a non-trivial template method. When
each reader is just `path -> DataFrame`/`path -> records` with no instance state, the class is
ceremony: a single-method class is a YAGNI smell. Use a decorator-driven registry of functions.

```python
SourceLoader = Callable[[Path], Iterable[SaleRecord]]

_SOURCES: Registry[SourceLoader] = Registry("data source")
register_source = _SOURCES.register

@register_source("csv")
def load_csv(path: Path) -> list[SaleRecord]:
    ...
```

Adding Excel or an API dump is a **new file** with `@register_source("xlsx")` — no existing
module is edited, which is the actual OCP claim the user is buying.

### Generalize the registry once, use it on every axis

A pipeline usually has more than one extension axis (input format, aggregation, output format).
Writing a bespoke `_READERS` dict per axis is Duplicated Code three times over. Extract ONE
generic `Registry` and instantiate it per axis:

```python
class Registry(Generic[T]):
    def __init__(self, kind: str) -> None:
        self._kind, self._items = kind, {}

    def register(self, name: str):
        key = name.lower()
        def decorator(item: T) -> T:
            if key in self._items:                       # reject silent shadowing
                raise ValueError(f"[REGISTRY]: {self._kind} '{key}' already registered")
            self._items[key] = item
            return item
        return decorator

    def get(self, name: str) -> T:
        try:
            return self._items[name.lower()]
        except KeyError:
            raise LookupError(
                f"[REGISTRY]: unknown {self._kind} '{name}'. Available: "
                f"{', '.join(sorted(self._items)) or '—'}"
            ) from None

    def names(self) -> list[str]: return sorted(self._items)
    def items(self) -> list[tuple[str, T]]: return list(self._items.items())  # registration order
```

Then: `sources.register_source`, `aggregations.register_aggregation`,
`renderers.register_renderer` — three axes, one implementation.

**Make the driver iterate the registry, not a hardcoded list.** If the CLI/orchestrator loops
over `registry.items()`, a newly registered aggregation shows up in the output with *zero* edits
to the CLI. If the CLI names its sections explicitly, the registry is decoration and you have
not actually achieved open-for-extension.

### Pitfall: `names()` sorted vs `items()` registration order

Easy bug, silently wrong output: implementing `items()` as `[(n, d[n]) for n in self.names()]`
makes the driver emit sections in **alphabetical order of internal keys**, so
`avg_revenue_per_order_by_region` printed before `revenue_by_product` even though the spec
listed revenue first. Keep the two methods distinct:

- `names()` → **sorted** — for help text, error messages, `--list` output (stable and scannable).
- `items()` → **insertion order** (plain `dict` preserves it) — for anything user-visible whose
  sequence is a product decision.

Caught only by reading the actual printed report against the spec's ordering. Diff the real
stdout against the spec's section order before calling the run green.

### Registry error messages should enumerate what IS available

`LookupError: unknown data source 'xlsx'. Available: csv` turns a dead end into a next step, and
it doubles as a runtime assertion that registration actually happened — an empty `Available:`
list means the module defining the readers was never imported.

## Validation belongs at the source boundary, with the row number

Each reader is a trust boundary. Parse-and-validate there, and include the location:

```python
for line_number, row in enumerate(reader, start=2):   # start=2 accounts for the header line
    try:
        yield Record.from_mapping(row)
    except ValueError as exc:
        raise ValueError(f"[SOURCE.CSV]: {path}, line {line_number}: {exc}") from exc
```

`[SOURCE.CSV]: bad.csv, line 2: field 'units' is not an integer: 'abc'` is actionable; a bare
`ValueError: invalid literal for int()` is not. Also check the header up front and name the
missing columns rather than failing per-row.

## Money: Decimal end-to-end, round only at render

When aggregating currency, keep `Decimal` through every computation and quantize **only** in the
renderer (`value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)`). Rounding inside the
aggregation makes totals disagree with the sum of displayed rows. Read CSV numbers straight into
`Decimal(raw_string)` — never via `float`, which reintroduces the drift you were avoiding.

Corollary for tests: assert exact `Decimal` values for raw computations, and assert the formatted
string for rendered output.

## Edge cases to exercise before declaring done

Run these, don't reason about them — each one has bitten this pattern:

| Input | Expected |
|---|---|
| file with header only, zero rows | empty sections, exit 0, **no ZeroDivisionError** in any average |
| one malformed cell | error naming file + line + field, non-zero exit |
| unknown format / unknown aggregation name | `LookupError` listing available names, non-zero exit |
| missing file | readable message, non-zero exit (wrap `OSError` at the reader) |

The empty-input case is the one that most often ships broken: `total / count` in an average
aggregation divides by zero the moment a group is empty or the file has no rows.

## Session evidence

- ABC variant: `C:/Users/Unicorn/kw-qa/20260722T083651Z/2.1-reuse-ladder/control/` —
  `readers.py` with `CsvReader`/`ExcelReader`/`ParquetReader` behind `get_reader(path)`.
- Function-registry variant (three axes, stdlib `csv` + `Decimal`, no pandas):
  `C:/Users/Unicorn/kw-qa/20260728T173540Z/2.1-reuse-ladder/treatment/sales_report/` —
  `registry.py` + `sources.py` + `aggregations.py` + `renderers.py`, CLI iterating the
  aggregation registry. jscpd 2.07% dup, lizard `-C 25` zero warnings, 8 tests green.
