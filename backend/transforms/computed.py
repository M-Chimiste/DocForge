"""Computed field transforms: row totals, date calculations, aggregations."""

from __future__ import annotations

from typing import Any

import pandas as pd

from transforms.base import BaseTransform


class ComputedTransform(BaseTransform):
    def can_handle(self, transform_type: str) -> bool:
        return transform_type == "computed"

    def apply(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        operation = params.get("operation")
        output_col = params.get("output_column", "computed")
        result = df.copy()

        if operation == "row_total":
            cols = [c for c in params.get("columns", []) if c in df.columns]
            if cols:
                result[output_col] = result[cols].apply(pd.to_numeric, errors="coerce").sum(axis=1)

        elif operation == "date_diff":
            start = params.get("start")
            end = params.get("end")
            unit = params.get("unit", "days")
            if start in df.columns and end in df.columns:
                s = pd.to_datetime(result[start], errors="coerce")
                e = pd.to_datetime(result[end], errors="coerce")
                delta = e - s
                if unit == "days":
                    result[output_col] = delta.dt.days

        elif operation == "agg_sum":
            col = params.get("column")
            if col and col in df.columns:
                total = pd.to_numeric(result[col], errors="coerce").sum()
                result[output_col] = total

        elif operation == "agg_mean":
            col = params.get("column")
            if col and col in df.columns:
                mean = pd.to_numeric(result[col], errors="coerce").mean()
                result[output_col] = mean

        elif operation == "agg_count":
            result[output_col] = len(result)

        return result
