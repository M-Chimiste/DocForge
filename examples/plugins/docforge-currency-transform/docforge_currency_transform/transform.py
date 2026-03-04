"""Currency conversion transform plugin for DocForge.

Multiplies the values in a numeric column by a fixed exchange rate and
optionally renames the column with a target suffix (e.g. ``_EUR``).

Usage in a mapping transform chain::

    {
        "type": "currency_convert",
        "params": {
            "column": "price_usd",
            "rate": 0.92,
            "target_suffix": "_eur"
        }
    }
"""

from __future__ import annotations

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
        For example, ``price`` with ``target_suffix="_eur"`` becomes
        ``price_eur``.
    """

    def can_handle(self, transform_type: str) -> bool:
        return transform_type == "currency_convert"

    def apply(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        column: str | None = params.get("column")
        rate: float | None = params.get("rate")

        if column is None:
            raise ValueError("currency_convert transform requires a 'column' param")
        if rate is None:
            raise ValueError("currency_convert transform requires a 'rate' param")
        if column not in df.columns:
            raise ValueError(f"Column '{column}' not found in DataFrame")

        result = df.copy()
        result[column] = pd.to_numeric(result[column], errors="coerce") * rate

        target_suffix: str | None = params.get("target_suffix")
        if target_suffix:
            new_name = f"{column}{target_suffix}"
            result = result.rename(columns={column: new_name})

        return result
