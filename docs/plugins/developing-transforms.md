# Custom Transforms

Transforms process data between extraction and rendering. They operate on pandas DataFrames and are applied in sequence as part of a mapping's transform pipeline. This guide covers how to build a custom transform plugin.

## Base Class Contract

All transforms must extend `BaseTransform` from `transforms.base`:

```python
from abc import ABC, abstractmethod
from typing import Any
import pandas as pd

class BaseTransform(ABC):
    @abstractmethod
    def can_handle(self, transform_type: str) -> bool:
        """Return True if this transform handles the given type name."""
        ...

    @abstractmethod
    def apply(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        """Apply the transformation to a DataFrame and return the result."""
        ...
```

### `can_handle(transform_type)`

Called by the `TransformRegistry` to determine if this transform handles a given type string.

**Parameters:**

- `transform_type` (`str`) -- The transform type name (e.g., `"currency_convert"`, `"uppercase"`)

**Return:** `True` if this transform handles the given type.

### `apply(df, params)`

Called to apply the transformation. Must return a new DataFrame (do not modify the input in place).

**Parameters:**

- `df` (`pd.DataFrame`) -- The input DataFrame
- `params` (`dict[str, Any]`) -- Transform-specific parameters from the mapping configuration

**Return:** A new `pd.DataFrame` with the transformation applied.

## Example: Currency Convert Transform

The `docforge-currency-transform` example plugin multiplies a numeric column by a conversion rate and optionally renames the column.

```python
from typing import Any
import pandas as pd
from transforms.base import BaseTransform


class CurrencyConvertTransform(BaseTransform):
    """Multiply a numeric column by a conversion rate.

    Parameters
    ----------
    column : str
        Name of the column to convert.
    rate : float
        Multiplication factor (exchange rate).
    target_suffix : str, optional
        If provided, the column is renamed by appending this suffix.
    """

    def can_handle(self, transform_type: str) -> bool:
        return transform_type == "currency_convert"

    def apply(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        column = params.get("column")
        rate = params.get("rate")

        if column is None:
            raise ValueError("currency_convert transform requires a 'column' param")
        if rate is None:
            raise ValueError("currency_convert transform requires a 'rate' param")
        if column not in df.columns:
            raise ValueError(f"Column '{column}' not found in DataFrame")

        result = df.copy()
        result[column] = pd.to_numeric(result[column], errors="coerce") * rate

        target_suffix = params.get("target_suffix")
        if target_suffix:
            new_name = f"{column}{target_suffix}"
            result = result.rename(columns={column: new_name})

        return result
```

## Usage in Mappings

Transforms are specified in the mapping configuration as part of the `transforms` array:

```json
{
  "markerId": "marker_1",
  "dataSource": "financial_data.xlsx",
  "field": "price_usd",
  "sheet": "Sheet1",
  "transforms": [
    {
      "type": "currency_convert",
      "params": {
        "column": "price_usd",
        "rate": 0.92,
        "target_suffix": "_eur"
      }
    }
  ]
}
```

Multiple transforms are applied in sequence by the `TransformPipeline`:

```json
{
  "transforms": [
    {"type": "filter", "params": {"column": "status", "operator": "equals", "value": "active"}},
    {"type": "sort", "params": {"column": "revenue", "ascending": false}},
    {"type": "currency_convert", "params": {"column": "revenue", "rate": 0.92}}
  ]
}
```

## The Transform Pipeline

The `TransformPipeline` class applies transforms in order:

```python
class TransformPipeline:
    """Applies an ordered list of transforms to a DataFrame."""

    def __init__(self, registry: TransformRegistry):
        self._registry = registry

    def apply(self, df: pd.DataFrame, transforms: list[dict]) -> pd.DataFrame:
        result = df.copy()
        for t in transforms:
            transform = self._registry.get_transform(t["type"])
            result = transform.apply(result, t.get("params", {}))
        return result
```

Each transform receives the output of the previous transform, allowing them to be chained.

## Project Structure

```
docforge-currency-transform/
  pyproject.toml
  docforge_currency_transform/
    __init__.py
    transform.py              # CurrencyConvertTransform class
  tests/
    test_transform.py
```

## Entry Point Declaration

In `pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.build_meta"

[project]
name = "docforge-currency-transform"
version = "0.1.0"
description = "DocForge plugin: currency conversion transform."
requires-python = ">=3.12"
dependencies = ["docforge"]

[project.entry-points."docforge.transforms"]
currency_convert = "docforge_currency_transform.transform:CurrencyConvertTransform"
```

The entry point key (`currency_convert`) should match the string your `can_handle()` method checks for.

## Built-in Transform Types

DocForge includes these built-in transforms:

| Type | Description |
|------|-------------|
| `rename` | Rename DataFrame columns |
| `filter` | Filter rows by column value |
| `sort` | Sort rows by column |
| `format_date` | Format date column values |
| `format_number` | Format numeric column values |
| `computed` | Add computed columns from expressions |

Custom transforms should use unique type names that do not conflict with built-in types.

## Testing

```python
import pandas as pd
from docforge_currency_transform.transform import CurrencyConvertTransform

def test_can_handle():
    t = CurrencyConvertTransform()
    assert t.can_handle("currency_convert") is True
    assert t.can_handle("sort") is False

def test_currency_conversion():
    t = CurrencyConvertTransform()
    df = pd.DataFrame({"price_usd": [100.0, 200.0, 300.0]})
    result = t.apply(df, {"column": "price_usd", "rate": 0.92})
    assert result["price_usd"].tolist() == [92.0, 184.0, 276.0]

def test_column_rename():
    t = CurrencyConvertTransform()
    df = pd.DataFrame({"price": [100.0]})
    result = t.apply(df, {"column": "price", "rate": 0.92, "target_suffix": "_eur"})
    assert "price_eur" in result.columns
    assert "price" not in result.columns

def test_missing_column_raises():
    t = CurrencyConvertTransform()
    df = pd.DataFrame({"other": [100.0]})
    try:
        t.apply(df, {"column": "price", "rate": 0.92})
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
```

## Error Handling

Transforms should raise `ValueError` with a descriptive message when:

- Required parameters are missing
- The specified column does not exist in the DataFrame
- The data type is incompatible with the operation

The generation pipeline catches these errors and records them in the generation report as recoverable errors. The affected marker keeps its original content, and generation continues.
