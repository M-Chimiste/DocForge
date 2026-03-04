"""Row filtering transform."""

from __future__ import annotations

from typing import Any

import pandas as pd

from transforms.base import BaseTransform


class FilterTransform(BaseTransform):
    def can_handle(self, transform_type: str) -> bool:
        return transform_type == "filter"

    def apply(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        column = params.get("column")
        operator = params.get("operator")
        value = params.get("value")

        if not column or not operator or column not in df.columns:
            return df

        ops = {
            "equals": lambda s: s == value,
            "not_equals": lambda s: s != value,
            "contains": lambda s: s.astype(str).str.contains(str(value), na=False),
            "gt": lambda s: pd.to_numeric(s, errors="coerce") > float(value),
            "lt": lambda s: pd.to_numeric(s, errors="coerce") < float(value),
            "gte": lambda s: pd.to_numeric(s, errors="coerce") >= float(value),
            "lte": lambda s: pd.to_numeric(s, errors="coerce") <= float(value),
        }

        op_func = ops.get(operator)
        if op_func is None:
            return df
        return df[op_func(df[column])].reset_index(drop=True)
