"""Date and number formatting transforms."""

from __future__ import annotations

from typing import Any

import pandas as pd

from transforms.base import BaseTransform


class DateFormatTransform(BaseTransform):
    def can_handle(self, transform_type: str) -> bool:
        return transform_type == "format_date"

    def apply(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        column = params.get("column")
        fmt = params.get("format", "%Y-%m-%d")
        if not column or column not in df.columns:
            return df
        result = df.copy()
        result[column] = pd.to_datetime(result[column], errors="coerce").dt.strftime(fmt)
        return result


class NumberFormatTransform(BaseTransform):
    def can_handle(self, transform_type: str) -> bool:
        return transform_type == "format_number"

    def apply(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        column = params.get("column")
        style = params.get("style", "decimal")
        decimals = params.get("decimals", 2)
        prefix = params.get("prefix", "$")

        if not column or column not in df.columns:
            return df

        result = df.copy()
        numeric = pd.to_numeric(result[column], errors="coerce")

        if style == "currency":
            result[column] = numeric.apply(
                lambda x: f"{prefix}{x:,.{decimals}f}" if pd.notna(x) else ""
            )
        elif style == "percentage":
            result[column] = numeric.apply(
                lambda x: f"{x * 100:.{decimals}f}%" if pd.notna(x) else ""
            )
        else:
            result[column] = numeric.apply(lambda x: f"{x:.{decimals}f}" if pd.notna(x) else "")

        return result
