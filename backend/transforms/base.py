"""Base classes for data transforms."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import pandas as pd


class BaseTransform(ABC):
    @abstractmethod
    def can_handle(self, transform_type: str) -> bool: ...

    @abstractmethod
    def apply(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame: ...


class TransformRegistry:
    def __init__(self):
        self._transforms: list[BaseTransform] = []

    def register(self, transform: BaseTransform) -> None:
        self._transforms.append(transform)

    def load_plugins(self) -> None:
        """Discover and register third-party transform plugins via entry points."""
        from core.plugin_loader import ENTRY_POINT_GROUPS, discover_plugins

        for transform in discover_plugins(ENTRY_POINT_GROUPS["transforms"]):
            self.register(transform)

    def get_transform(self, transform_type: str) -> BaseTransform:
        for t in self._transforms:
            if t.can_handle(transform_type):
                return t
        raise ValueError(f"No transform found for type: {transform_type}")


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
