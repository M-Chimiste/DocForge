"""Sort transform (single and multi-column)."""

from __future__ import annotations

from typing import Any

import pandas as pd

from transforms.base import BaseTransform


class SortTransform(BaseTransform):
    def can_handle(self, transform_type: str) -> bool:
        return transform_type == "sort"

    def apply(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        columns = params.get("columns", [])
        ascending = params.get("ascending", True)

        if isinstance(columns, str):
            columns = [columns]
        if isinstance(ascending, bool):
            ascending = [ascending] * len(columns)

        valid_cols = [c for c in columns if c in df.columns]
        if not valid_cols:
            return df

        valid_asc = ascending[: len(valid_cols)]
        return df.sort_values(by=valid_cols, ascending=valid_asc).reset_index(drop=True)
