# docforge-currency-transform

A DocForge transform plugin that converts numeric column values by a fixed
exchange rate.

## How it works

This plugin registers itself under the `docforge.transforms` entry-point
group with the transform type `currency_convert`.  When a mapping includes
this transform in its chain, the plugin:

1. Reads the specified `column` from the DataFrame.
2. Multiplies every value by `rate`.
3. Optionally renames the column by appending `target_suffix`.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `column` | str | yes | Name of the numeric column to convert |
| `rate` | float | yes | Multiplication factor (exchange rate) |
| `target_suffix` | str | no | Suffix appended to the column name after conversion |

## Example mapping

```json
{
    "marker_id": "m1",
    "data_source": "prices.xlsx",
    "field": "price_usd_eur",
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

## Installation

```bash
pip install -e .
```

After installation, DocForge discovers the plugin automatically -- no
configuration needed.

## Running tests

```bash
pytest tests/
```
