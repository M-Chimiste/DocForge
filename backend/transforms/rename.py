"""Column rename transform."""

from __future__ import annotations

from typing import Any

import pandas as pd

from transforms.base import BaseTransform


class RenameTransform(BaseTransform):
    def can_handle(self, transform_type: str) -> bool:
        return transform_type == "rename"

    def apply(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        columns = params.get("columns", {})
        return df.rename(columns=columns)
