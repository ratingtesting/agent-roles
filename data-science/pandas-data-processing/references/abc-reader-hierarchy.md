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

## Session evidence

This pattern was used in `C:/Users/Unicorn/kw-qa/20260722T083651Z/2.1-reuse-ladder/control/`
where `readers.py` provides `CsvReader`, `ExcelReader`, `ParquetReader` behind a
`get_reader(path)` factory, and `analyze.py` consumes the DataFrame for sum/avg analytics.
